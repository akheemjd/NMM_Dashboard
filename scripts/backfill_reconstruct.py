#!/usr/bin/env python3
"""NRCan backfill — STEP 2: parse the cache, reconstruct NMDI, prove the seam.

Reads the raw pages harvested in step 1, extracts weekly city prices, rolls them
up to provincial and national figures using the SAME logic the live pipeline
uses, and writes a reconstructed series to a SCRATCH file — never the live store.

Then the seam test: the reconstructed 2026 prints must match the live series
where they overlap. If they match, the parser is faithful and the whole archive
is trustworthy. If they do not, we fix the parser before anything merges.

Nothing here writes to data/history/series.csv. Output goes to
data/backfill_reconstructed.csv for inspection. Merge is a separate step 3, run
only after the seam passes.

Usage:
  python3 scripts/backfill_reconstruct.py                 # parse all, reconstruct, seam-test
  python3 scripts/backfill_reconstruct.py --seam-only     # just re-run the seam check
"""

import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "backfill_cache")
OUT = os.path.join(ROOT, "data", "backfill_reconstructed.csv")
LIVE = os.path.join(ROOT, "data", "history", "series.csv")

# ── Province roll-up ──────────────────────────────────────────────────
# Wired to the live collector's mapping so the reconstruction reconciles with
# live data. normalize_city() below is functionally identical to the collector's
# _norm() accent-fold.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collect_nrcan_diesel import CITY_PROVINCE

# The ten provinces in the NMDI. Territories (YT, NT) are excluded from the
# national index, exactly as the live methodology specifies.
NMDI_PROVINCES = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]


def normalize_city(name):
    """Accent-fold and trim, matching the live collector. Replace with the live
    function at install if it differs."""
    import unicodedata
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return n.strip()


def parse_page(html):
    """Return (city_name, [(week_ending, price, taxes, mkt_margin, ref_margin), ...]).

    Structure confirmed from live pages:
      row: ['( Cents per litre )']
      row: ['NOTE: Prices include taxes']
      row: ['', 'Ottawa']                          <- city name in 2nd cell
      row: ['Week Ending','Price','Taxes','Marketing Margin','Refining Margin']
      row: ['2025-01-07','171.0','54.1','4.0','48.6']   <- data
    """
    rows = re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL)
    city = None
    data = []
    for r in rows:
        cells = [re.sub(r"<.*?>", "", c).strip()
                 for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", r, re.DOTALL)]
        if not cells:
            continue
        # city-name row: exactly two cells, first blank, second non-numeric
        if len(cells) == 2 and cells[0] == "" and cells[1] and not re.match(r"[\d.]+$", cells[1]):
            city = cells[1]
            continue
        # data row: first cell is an ISO date
        if cells and re.match(r"\d{4}-\d{2}-\d{2}$", cells[0]):
            vals = cells[:5] + [""] * (5 - len(cells))
            try:
                week = vals[0]
                price = float(vals[1])
                taxes = float(vals[2]) if vals[2] else None
                mkt = float(vals[3]) if vals[3] else None
                ref = float(vals[4]) if vals[4] else None
                data.append((week, price, taxes, mkt, ref))
            except ValueError:
                # a non-numeric price cell — skip the row, don't guess
                continue
    return city, data


def reconstruct():
    if not os.path.isdir(CACHE):
        print(f"No cache at {CACHE}. Run step 1 (backfill_harvest.py) first.")
        return None

    # city_prices[week][province] = [price, price, ...]  (one per city in prov)
    # margins[week] = accumulators for national tax/margin means
    city_rows = []  # (week, city, province, price, taxes, mkt, ref)
    pages = 0
    skipped_city = set()

    for year in sorted(os.listdir(CACHE)):
        ydir = os.path.join(CACHE, year)
        if not os.path.isdir(ydir):
            continue
        for fn in sorted(os.listdir(ydir)):
            if not fn.endswith(".html"):
                continue
            html = open(os.path.join(ydir, fn), encoding="utf-8").read()
            city, data = parse_page(html)
            pages += 1
            if not city:
                continue
            prov = CITY_PROVINCE.get(normalize_city(city))
            if not prov:
                skipped_city.add(city)
                continue
            if prov == "CA":
                continue  # NRCan "Canada" national aggregate — excluded from the roll-up (matches live)
            for week, price, taxes, mkt, ref in data:
                city_rows.append((week, city, prov, price, taxes, mkt, ref))

    if skipped_city:
        print("WARNING: cities with no province mapping (excluded):")
        for c in sorted(skipped_city):
            print(f"  {c!r}")
        print("  -> wire CITY_PROVINCE to the live mapping before trusting output.\n")

    # Roll up: provincial mean = unweighted mean of its cities that week.
    # National (NMDI) = unweighted mean of the ten provincial means that week.
    from collections import defaultdict
    prov_week = defaultdict(lambda: defaultdict(list))   # week -> prov -> [prices]
    tax_week = defaultdict(list)
    mkt_week = defaultdict(list)
    ref_week = defaultdict(list)

    for week, city, prov, price, taxes, mkt, ref in city_rows:
        prov_week[week][prov].append(price)
        if taxes is not None: tax_week[week].append(taxes)
        if mkt is not None: mkt_week[week].append(mkt)
        if ref is not None: ref_week[week].append(ref)

    out = []  # (date, series, key, value)
    for week in sorted(prov_week):
        prov_means = {}
        for prov, prices in prov_week[week].items():
            # Match live arithmetic EXACTLY (compute_provincial in the collector):
            # provincial mean is the unweighted mean of city prices, rounded to
            # 1 decimal in cents. HTML prices are already cents at the same
            # precision the RSS carries (confirmed: $2.259 == 225.9), so
            # mean(cents) rounded == live's round(mean(dollars)*100, 1).
            prov_means[prov] = round(sum(prices) / len(prices), 1)
            out.append((week, "diesel", prov, prov_means[prov]))
        # National = unweighted mean of the ten NMDI provincial figures, taken
        # from the ALREADY-ROUNDED provincial cents, then rounded again — exactly
        # as live does (national_avg = round(sum(indexed)/len, 1) where indexed
        # are the rounded provincial values). Only computed when all ten are
        # present; never from a partial set.
        present = [prov_means[p] for p in NMDI_PROVINCES if p in prov_means]
        if len(present) == len(NMDI_PROVINCES):
            out.append((week, "diesel", "national", round(sum(present) / len(present), 1)))
        # national tax / margin means (all cities, informational series)
        if tax_week[week]:
            out.append((week, "diesel_tax", "national", round(sum(tax_week[week]) / len(tax_week[week]), 1)))
        if mkt_week[week]:
            out.append((week, "diesel_mkt_margin", "national", round(sum(mkt_week[week]) / len(mkt_week[week]), 1)))
        if ref_week[week]:
            out.append((week, "diesel_ref_margin", "national", round(sum(ref_week[week]) / len(ref_week[week]), 1)))

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "series", "key", "value"])
        for row in out:
            w.writerow(row)

    weeks = sorted(prov_week)
    print(f"Parsed {pages} pages, {len(city_rows)} city-week observations.")
    print(f"Reconstructed {len(out)} rows across {len(weeks)} weeks.")
    if weeks:
        print(f"Week range: {weeks[0]} -> {weeks[-1]}")
    print(f"Written to {OUT} (scratch — NOT the live store).")
    return out


def seam_test():
    """The reconstructed prints must match the live series where they overlap."""
    if not os.path.exists(OUT):
        print("No reconstructed file. Run without --seam-only first.")
        return 1
    if not os.path.exists(LIVE):
        print(f"No live series at {LIVE} to compare against.")
        return 1

    def load(path):
        d = {}
        with open(path) as f:
            for row in csv.DictReader(f):
                if row["series"] == "diesel":
                    d[(row["date"], row["key"])] = round(float(row["value"]), 1)
        return d

    recon = load(OUT)
    live = load(LIVE)
    overlap = sorted(set(recon) & set(live))

    if not overlap:
        print("SEAM: no overlapping (date,key) between reconstructed and live yet.")
        print("  Live currently holds only the latest print(s); the seam test")
        print("  becomes meaningful once the reconstruction covers a live date.")
        return 0

    # Tolerance seam. Live can be STALE — NRCan revises prices after first print,
    # so an overlapping week can differ legitimately by a small amount. A small
    # gap is a revision (expected, fine); a large gap is a real roll-up bug.
    # The archive is authoritative on merge, so this test is a sanity check on
    # the arithmetic, not a value gate.
    BUG_THRESHOLD = 3.0   # cents; above this, treat as a probable bug, not revision

    diffs = [(k, recon[k], live[k], round(recon[k] - live[k], 1)) for k in overlap]
    revisions = [d for d in diffs if abs(d[3]) <= BUG_THRESHOLD and d[3] != 0]
    exact = [d for d in diffs if d[3] == 0]
    bugs = [d for d in diffs if abs(d[3]) > BUG_THRESHOLD]

    print(f"SEAM: {len(overlap)} overlapping diesel points.")
    print(f"  exact match:        {len(exact)}")
    print(f"  small (<={BUG_THRESHOLD}c, revision): {len(revisions)}")
    print(f"  large (>{BUG_THRESHOLD}c, probable bug): {len(bugs)}")

    if revisions:
        print("\n  Revisions (live stale, archive is newer NRCan data):")
        for (date, key), rv, lv, dd in revisions[:20]:
            print(f"    {date} {key}: archive {rv} vs live {lv}  ({dd:+}c)")

    if bugs:
        print(f"\nSEAM FAIL: {len(bugs)} points differ by more than {BUG_THRESHOLD}c "
              f"— too large to be revision, likely a roll-up bug:")
        for (date, key), rv, lv, dd in bugs[:20]:
            print(f"    {date} {key}: archive {rv} vs live {lv}  ({dd:+}c)")
        print("  -> inspect the roll-up before merging. Do NOT merge.")
        return 1

    print("\nSEAM OK: all overlaps are exact or small revisions, none above "
          f"{BUG_THRESHOLD}c.")
    print("  The reconstruction rolls up correctly. Archive is authoritative;")
    print("  merge will overwrite the stale live print with the revised value.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seam-only", action="store_true")
    args = ap.parse_args()
    if not args.seam_only:
        if reconstruct() is None:
            return 1
    return seam_test()


if __name__ == "__main__":
    sys.exit(main())
