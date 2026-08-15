#!/usr/bin/env python3
"""NRCan backfill — STEP 3: merge the reconstruction into the live store.

Run ONLY after step 2's seam test passes (exact or small-revision, no bugs).

The reconstruction is authoritative: NRCan revises prices after first print, so
where the archive overlaps the live series, the archive's value wins — it is the
corrected figure. This overwrites the stale live print(s) and fills all history
back to 2016.

Safety:
  * Backs up the live series.csv before touching it.
  * Only touches series 'diesel' and the diesel_* margin series it reconstructed.
    Any other series in the live store (fx, etc.) is preserved untouched.
  * First-write-wins semantics are irrelevant here — this is a deliberate,
    authoritative overwrite of diesel history from a verified source.
  * Idempotent: running twice produces the same store.

Usage:
  python3 scripts/backfill_merge.py --dry-run     # show what would change
  python3 scripts/backfill_merge.py               # do it (after dry-run looks right)
"""

import argparse
import csv
import os
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECON = os.path.join(ROOT, "data", "backfill_reconstructed.csv")
LIVE = os.path.join(ROOT, "data", "history", "series.csv")

# Series the backfill owns and may overwrite. Everything else in live is kept.
BACKFILL_SERIES = {"diesel", "diesel_tax", "diesel_mkt_margin", "diesel_ref_margin"}


def load(path):
    rows = []
    if os.path.exists(path):
        with open(path) as f:
            rows = list(csv.DictReader(f))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(RECON):
        print(f"No reconstruction at {RECON}. Run step 2 first.")
        return 1
    if not os.path.exists(LIVE):
        print(f"No live series at {LIVE}.")
        return 1

    recon = load(RECON)
    live = load(LIVE)

    # Index the reconstruction by (date, series, key).
    recon_idx = {(r["date"], r["series"], r["key"]): r["value"] for r in recon}

    # Keep every live row that the backfill does NOT own. Drop live diesel rows
    # that the reconstruction will replace, so the archive is authoritative.
    kept = []
    replaced = 0
    for r in live:
        if r["series"] in BACKFILL_SERIES:
            k = (r["date"], r["series"], r["key"])
            if k in recon_idx:
                replaced += 1
                continue  # archive will supply this; drop the stale live row
            # a live diesel row with no archive counterpart — keep it (e.g. a
            # print more recent than the archive's last week)
            kept.append(r)
        else:
            kept.append(r)  # fx and anything else — untouched

    merged = kept + [
        {"date": d, "series": s, "key": k, "value": v}
        for (d, s, k), v in recon_idx.items()
    ]
    # stable sort: date, then series, then key
    merged.sort(key=lambda r: (r["date"], r["series"], r["key"]))

    live_diesel = sum(1 for r in live if r["series"] in BACKFILL_SERIES)
    new_diesel = sum(1 for r in merged if r["series"] in BACKFILL_SERIES)
    other = sum(1 for r in merged if r["series"] not in BACKFILL_SERIES)

    print(f"Live store:      {len(live)} rows ({live_diesel} diesel/margin, {len(live)-live_diesel} other)")
    print(f"Reconstruction:  {len(recon)} rows")
    print(f"Stale live rows replaced by archive: {replaced}")
    print(f"Merged store:    {len(merged)} rows ({new_diesel} diesel/margin, {other} other preserved)")

    dates = sorted({r["date"] for r in merged if r["series"] == "diesel"})
    if dates:
        print(f"Diesel history range after merge: {dates[0]} -> {dates[-1]} ({len(dates)} weeks)")

    if args.dry_run:
        print("\nDRY RUN — nothing written. Re-run without --dry-run to apply.")
        return 0

    # Back up, then write atomically.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = LIVE + f".pre-backfill-{stamp}"
    shutil.copy2(LIVE, backup)
    print(f"\nBacked up live series to {backup}")

    tmp = LIVE + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "series", "key", "value"])
        w.writeheader()
        for r in merged:
            w.writerow({k: r[k] for k in ("date", "series", "key", "value")})
    os.replace(tmp, LIVE)
    print(f"Merged {len(merged)} rows into {LIVE}")
    print("Diesel history now spans the full archive. fx and other series preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
