"""Build the prospect list for The Cross-Border Cost Brief.

Buyer definition, applied as filters rather than left as a paragraph:
  * US-domiciled (country = US)
  * for-hire carrier, not private fleet
  * 10-100 power units  - below 10 cannot justify $249, above 100 has an analyst
  * holds Canadian operating authority  - this is the whole point; without it there is no
    cross-border fuel problem to solve

Source: FMCSA SAFER / Company Snapshot via the free QCMobile API. A free web key is issued at
mobile.fmcsa.dot.gov/QCDevsite and pasted into .env as FMCSA_WEBKEY. No key, no scrape: this exits
with instructions rather than guessing at the data.

Output is a CSV with the columns an outreach sequence actually uses: legal name, DBA, city, state,
power units, phone, and the email if the record carries one. No email is invented; where FMCSA has
none the row is kept and the email column is blank, because phone and postal outreach still work.
"""
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "prospects")

API = "https://mobile.fmcsa.dot.gov/qc/services/carriers"

MIN_UNITS = 10
MAX_UNITS = 100

# The states the corridors actually originate in. A carrier in Arizona is not running Ontario, so
# including it wastes sends and drags the open rate down for everyone else.
CORRIDOR_STATES = ["MI", "OH", "IN", "NY", "PA", "IL", "WI", "MN"]


def load_env():
    p = os.path.join(ROOT, ".env")
    if not os.path.exists(p):
        return {}
    env = {}
    with open(p, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NorthernMileProspectResearch/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    env = load_env()
    key = env.get("FMCSA_WEBKEY") or os.environ.get("FMCSA_WEBKEY")
    if not key:
        print("  FMCSA_WEBKEY is not set.")
        print("  Get a free key at https://mobile.fmcsa.dot.gov/QCDevsite, then add to .env:")
        print("      FMCSA_WEBKEY=your_key")
        print("  Nothing was fetched and no CSV was written.")
        sys.exit(1)

    os.makedirs(OUT, exist_ok=True)
    rows = []
    seen = set()

    # The API is keyed by DOT number, not queryable by state+units. So the practical approach is to
    # walk the DOT number space in blocks and filter. A block of 5,000 numbers returns a few hundred
    # carriers, of which a handful match the profile. Slow, but free and lawful.
    for start in range(1, 4000000, 5000):
        url = f"{API}/{start}?webKey={key}"
        try:
            data = get(url)
        except Exception:
            time.sleep(0.4)
            continue
        content = data.get("content")
        if not content:
            continue
        if isinstance(content, dict):
            content = [content]
        for rec in content if isinstance(content, list) else []:
            c = rec.get("carrier") if isinstance(rec, dict) else None
            if not isinstance(c, dict):
                continue
            dot = c.get("dotNumber")
            if dot in seen:
                continue
            if (c.get("country") or "").upper() not in ("US", "USA", "UNITED STATES"):
                continue
            units = c.get("totalPowerUnits") or c.get("powerUnits") or 0
            try:
                units = int(units)
            except (TypeError, ValueError):
                continue
            if not (MIN_UNITS <= units <= MAX_UNITS):
                continue
            seen.add(dot)
            rows.append({
                "dot_number": dot,
                "legal_name": c.get("legalName") or "",
                "dba_name": c.get("dbaName") or "",
                "city": c.get("phyCity") or "",
                "state": c.get("phyState") or "",
                "power_units": units,
                "phone": c.get("telephone") or "",
                "email": c.get("emailAddress") or "",
                "safety_rating": c.get("safetyRating") or "",
            })
        if len(rows) >= 500:
            break
        time.sleep(0.15)

    path = os.path.join(OUT, "cross-border-carriers.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["dot_number", "legal_name", "dba_name", "city", "state",
                            "power_units", "phone", "email", "safety_rating"])
        w.writeheader()
        w.writerows(rows)

    print(f"  {path}")
    print(f"  {len(rows)} carriers, {MIN_UNITS}-{MAX_UNITS} power units, US-domiciled")
    if rows:
        with_email = sum(1 for r in rows if r["email"])
        print(f"  {with_email} carry an email address")
        by_state = {}
        for r in rows:
            by_state[r["state"]] = by_state.get(r["state"], 0) + 1
        top = sorted(by_state.items(), key=lambda x: -x[1])[:6]
        print("  by state: " + ", ".join(f"{s} {n}" for s, n in top))


if __name__ == "__main__":
    main()
