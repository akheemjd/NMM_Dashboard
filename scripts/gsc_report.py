#!/usr/bin/env python3
"""Read Search Console performance data with the service account.

    python scripts/gsc_report.py                    # both properties, last 90 days
    python scripts/gsc_report.py --days 480         # full 16 months
    python scripts/gsc_report.py --property domain  # just the Domain property

Answers the questions that decide the site's direction, from data rather than opinion:

  * which queries actually bring people here, and at what average position
  * whether pages get impressions but few clicks (a title/position problem)
    or no impressions at all (a crawl problem)
  * which pages are close enough to the first page that improving them pays

Requires a service account JSON at ~/.hermes/gsc-key.json, whose client_email has been added
as a user on the Search Console property. Verified libraries: google-api-python-client,
google-auth.
"""
import argparse
import json
import os
import sys
from collections import defaultdict

from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY = os.path.expanduser(r"~\.hermes\gsc-key.json")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

PROPERTIES = {
    "domain": "sc-domain:northernmilemedia.com",
    "dashboard": "https://dashboard.northernmilemedia.com/",
}


def client():
    if not os.path.isfile(KEY):
        sys.exit(f"No service account key at {KEY}")
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def query(svc, prop, start, end, dimensions, limit=250):
    out = []
    start_row = 0
    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dimensions,
            "rowLimit": min(25000, limit),
            "startRow": start_row,
        }
        try:
            resp = svc.searchanalytics().query(siteUrl=prop, body=body).execute()
        except Exception as e:
            return None, str(e)
        rows = resp.get("rows", [])
        out.extend(rows)
        if len(rows) < body["rowLimit"] or len(out) >= limit:
            break
        start_row += len(rows)
    return out, None


def fmt(n):
    return f"{n:,.0f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--property", choices=["domain", "dashboard", "both"], default="both")
    ap.add_argument("--out", default=r"C:\tmp\gsc_report.json")
    args = ap.parse_args()

    import datetime
    end = datetime.date.today() - datetime.timedelta(days=3)   # GSC lags ~2-3 days
    start = end - datetime.timedelta(days=args.days)

    svc = client()
    props = ([args.property] if args.property != "both" else list(PROPERTIES))
    result = {}

    for key in props:
        prop = PROPERTIES[key]
        print(f"\n{'=' * 70}\n  {key}  ->  {prop}")
        print(f"  {start} to {end}\n")

        q, err = query(svc, prop, str(start), str(end), ["query"], limit=500)
        if err:
            print(f"  ERROR: {err}")
            print("  (if this is a 403, the service account has not been added as a user")
            print("   on this property, or the Search Console API is not enabled)")
            continue

        p, err2 = query(svc, prop, str(start), str(end), ["page"], limit=500)
        if err2:
            print(f"  pages ERROR: {err2}")
            p = []

        if not q and not p:
            print("  No data. Either the property has no impressions, or the range is empty.")
            result[key] = {"queries": [], "pages": []}
            continue

        tq = sum(r["impressions"] for r in q)
        tc = sum(r["clicks"] for r in q)
        print(f"  TOTAL  impressions {fmt(tq)}   clicks {fmt(tc)}"
              + (f"   CTR {tc / tq * 100:.1f}%" if tq else ""))
        print(f"  distinct queries: {len(q)}   pages with impressions: {len(p)}")

        if q:
            print("\n  top queries by impressions:")
            print(f"    {'query':44} {'impr':>8} {'clicks':>7} {'pos':>6}")
            for r in sorted(q, key=lambda x: -x["impressions"])[:20]:
                print(f"    {r['keys'][0][:44]:44} {fmt(r['impressions']):>8} "
                      f"{fmt(r['clicks']):>7} {r['position']:>6.1f}")

            # The money zone: enough impressions to matter, position close enough to fix.
            near = [r for r in q if 4 <= r["position"] <= 25 and r["impressions"] >= 10]
            if near:
                print(f"\n  NEAR-WINS (position 4-25, >=10 impressions) — {len(near)} queries:")
                for r in sorted(near, key=lambda x: x["position"])[:15]:
                    print(f"    pos {r['position']:5.1f}  {fmt(r['impressions']):>6} impr  {r['keys'][0][:48]}")

        if p:
            print("\n  pages with impressions:")
            for r in sorted(p, key=lambda x: -x["impressions"])[:15]:
                url = r["keys"][0].replace("https://dashboard.northernmilemedia.com", "")
                print(f"    {fmt(r['impressions']):>7} impr {fmt(r['clicks']):>5} clicks "
                      f"pos {r['position']:5.1f}  {url}")

        result[key] = {
            "property": prop,
            "range": [str(start), str(end)],
            "queries": q,
            "pages": p,
            "totals": {"impressions": tq, "clicks": tc},
        }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
