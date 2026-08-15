#!/usr/bin/env python3
"""NRCan diesel history harvester — STEP 1 of the backfill.

Fetches the annual city price tables from prices_bycity_e.cfm, one city-year at a
time, politely and resumably, caching each page to disk. It writes NOTHING to the
live store. Its only output is a folder of raw HTML pages under data/backfill_cache/.

Design guarantees, in order of importance:
  * Never touches the live series.csv or any live data. Only fills the cache dir.
  * One request at a time, never parallel.
  * A real delay between requests (default 5s, jittered), so NRCan is never hammered.
  * Fetched exactly once: a city-year already on disk is skipped. Re-running
    resumes rather than re-fetching.
  * Stops dead on any unexpected response and reports, rather than retrying in a
    loop. Never routes around a block.

Usage:
  python3 scripts/backfill_harvest.py --from 2006 --to 2026
  python3 scripts/backfill_harvest.py --from 2024 --to 2026        # smaller test
  python3 scripts/backfill_harvest.py --from 2025 --to 2025 --limit 3   # tiny probe

Run it again any time — it picks up where it left off. Nothing it does is
destructive, and nothing it does is live.
"""

import argparse
import os
import random
import sys
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "backfill_cache")
BASE = "https://www2.nrcan.gc.ca/eneene/sources/pripri/prices_bycity_e.cfm"
UA = "Mozilla/5.0 (NMM backfill harvester; northernmilemedia.com; contact northernmilemedia@gmail.com)"

# The 72 unique NRCan diesel city location IDs. Iterate these, NOT the 100 RSS
# items (some cities appear twice in the feed). Province is resolved later from
# the city NAME read out of each page, exactly as the live collector does — this
# list is only the fetch set.
LOCATION_IDS = [
    90,91,36,16,92,8,82,43,32,46,69,10,37,70,34,45,31,98,99,100,93,
    39,26,5,6,71,72,94,73,11,74,20,38,35,28,97,75,24,95,18,76,14,4,
    29,9,12,77,33,58,13,22,30,27,44,21,78,40,23,25,17,79,42,80,2,3,
    1,19,15,81,41,7,66
]


def cache_path(year, loc):
    d = os.path.join(CACHE, str(year))
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"loc_{loc}.html")


def looks_valid(html):
    """A real price table page. Anything else means stop and report."""
    if len(html) < 500:
        return False, "page too short (<500 bytes)"
    low = html.lower()
    if "week ending" not in low:
        return False, "no 'Week Ending' header — not a price table"
    if "cents per litre" not in low:
        return False, "no 'Cents per litre' label — unexpected page"
    return True, ""


def fetch(year, loc, delay, jitter):
    url = f"{BASE}?priceYear={year}&productID=5&locationID={loc}&frequency=W"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            if r.status != 200:
                return None, f"HTTP {r.status}"
            html = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return None, f"HTTPError {e.code}"
    except urllib.error.URLError as e:
        return None, f"URLError {e.reason}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

    ok, why = looks_valid(html)
    if not ok:
        return None, why
    return html, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="y0", type=int, required=True)
    ap.add_argument("--to", dest="y1", type=int, required=True)
    ap.add_argument("--delay", type=float, default=5.0, help="seconds between requests")
    ap.add_argument("--jitter", type=float, default=1.5, help="max random extra seconds")
    ap.add_argument("--limit", type=int, default=0, help="cap cities per year (0 = all), for testing")
    args = ap.parse_args()

    years = list(range(args.y0, args.y1 + 1))
    ids = LOCATION_IDS[: args.limit] if args.limit else LOCATION_IDS
    total = len(years) * len(ids)

    already = 0
    for y in years:
        for loc in ids:
            if os.path.exists(cache_path(y, loc)):
                already += 1

    print(f"Harvest plan: {len(years)} years x {len(ids)} cities = {total} pages")
    print(f"Already cached: {already}. To fetch: {total - already}.")
    est = (total - already) * (args.delay + args.jitter / 2)
    print(f"Estimated time at {args.delay}s+jitter: ~{est/60:.0f} min.")
    print(f"Cache dir: {CACHE}")
    print("This writes nothing to the live store. Ctrl-C is safe — rerun resumes.\n")

    fetched = 0
    skipped = 0
    for y in years:
        for loc in ids:
            path = cache_path(y, loc)
            if os.path.exists(path):
                skipped += 1
                continue

            html, err = fetch(y, loc, args.delay, args.jitter)
            if err:
                # Stop dead. Do not retry, do not continue past an unexpected
                # response — report and let a human look.
                print(f"\nSTOP at year={y} loc={loc}: {err}")
                print(f"Fetched {fetched} this run, {skipped} already cached.")
                print("Nothing live was touched. Investigate, then rerun to resume.")
                return 1

            # Atomic write so a kill mid-write cannot leave a truncated page.
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(html)
            os.replace(tmp, path)
            fetched += 1

            done = fetched + skipped
            if fetched % 10 == 0 or done == total:
                print(f"  {done}/{total}  (fetched {fetched}, cached {skipped})")

            time.sleep(args.delay + random.uniform(0, args.jitter))

    print(f"\nDone. Fetched {fetched} new, {skipped} already cached.")
    print(f"All pages under {CACHE}. Nothing live was modified.")
    print("Next: step 2 parses the cache, reconstructs NMDI, and proves the seam.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
