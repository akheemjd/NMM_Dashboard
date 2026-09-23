#!/usr/bin/env python3
"""Collect federal and state motor fuel taxes from the EIA semiannual table.

WHY THIS EXISTS
---------------
The IFTA matrix gives the tax a carrier actually reports and remits, and it
covers the 48 IFTA states plus the 10 provinces. It does not give the statutory
tax a state levies, and it says nothing about the federal rate on top.

EIA publishes both, every January and July, in one table. Together with the IFTA
rates this is what makes a US state page worth reading: the state's own tax is
genuinely state-level data, unlike the diesel price, which EIA only publishes by
district. That distinction is the whole point of the state pages.

SOURCE
------
https://www.eia.gov/petroleum/marketing/monthly/xls/fueltaxes.xlsx

Column layout in the sheet (verified, not assumed):
  col 0  state name
  col 1-4   gasoline: State tax, Other taxes & Fees, Total State, State & Federal
  col 5  blank
  col 6-9   diesel: State tax, Other taxes & Fees, Total State, State & Federal
  col 10 blank
  col 11 notes

Rows 0-4 are the title and the federal block, row 6 is the state header, row 7
is the average, states start at row 8, and the trailing rows are footnotes. The
footnotes are what make column 0 dangerous: a state name and a footnote both
live there, so rows are accepted only when cols 6-9 are numeric.

This file is semiannual, so the "quarter" field is really a half-year. It is
stored as a plain date so nothing downstream has to know that.
"""

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

URL = "https://www.eia.gov/petroleum/marketing/monthly/xls/fueltaxes.xlsx"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

# EIA footnotes sit in the same column as state names, so each name carries a
# "[4]" style marker that has to come off before matching.
FOOTNOTE = re.compile(r"\[\d+\]")

TWO_LETTER = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


def fetch(url=URL):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def num(v):
    """Return a float, or None when the cell is not a number.

    None is the only honest value for a blank cell. Coercing it to 0.0 would
    publish a state as levying no fuel tax at all, which is a claim, not a gap.
    """
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.lower() in ("nan", "none", "--", "-", "na", "n/a", "w"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse(raw):
    import io
    import pandas as pd

    xl = pd.ExcelFile(io.BytesIO(raw))
    # Newest sheet first. Sheet names are "July 2026 (revised)", "January 2026
    # (revised)", ... so a lexical sort puts July above January within a year,
    # and the revision marker sorts after the bare name, which is what we want.
    sheets = sorted(xl.sheet_names, reverse=True)
    name = sheets[0]
    df = pd.read_excel(io.BytesIO(raw), sheet_name=name, header=None)

    def cell(r, c):
        try:
            return df.iat[r, c]
        except Exception:
            return None

    def row_has(r):
        return any(str(cell(r, c) or "").strip() not in ("", "nan") for c in range(12))

    # Locate the federal row and the state header rather than hardcoding 3 and 6,
    # because a layout change would otherwise silently shift every column.
    #
    # Match the label EXACTLY. Row 0 of this sheet is the title "Federal and state
    # motor fuel taxes", so a startswith("federal") test matched the title, took
    # the wrong row, and read an empty cell as the federal diesel rate.
    fed_row = None
    for r in range(min(12, len(df))):
        if str(cell(r, 0) or "").strip().lower() == "federal":
            fed_row = r
            break
    if fed_row is None:
        raise ValueError("no exact 'Federal' row found; the table layout changed")

    head_row = None
    for r in range(fed_row, min(fed_row + 8, len(df))):
        if str(cell(r, 1) or "").strip().lower() == "state tax":
            head_row = r
            break
    if head_row is None:
        raise ValueError("no state header row found; the table layout changed")

    federal = {
        "gasoline_excise": num(cell(fed_row, 1)),
        "gasoline_lust": num(cell(fed_row, 2)),
        "gasoline_total": num(cell(fed_row, 4)),
        "diesel_excise": num(cell(fed_row, 6)),
        "diesel_lust": num(cell(fed_row, 7)),
        "diesel_total": num(cell(fed_row, 9)),
    }
    if federal["diesel_total"] is None:
        raise ValueError("federal diesel total did not parse")

    states = []
    for r in range(head_row + 1, len(df)):
        raw_name = str(cell(r, 0) or "").strip()
        if not raw_name or raw_name.lower().startswith(("1 ", "2 ", "3 ", "4 ", "5 ",
                                                        "note", "source")):
            continue
        clean = FOOTNOTE.sub("", raw_name).strip()
        if clean.lower().startswith("average"):
            continue

        diesel_state = num(cell(r, 6))
        diesel_total_state = num(cell(r, 8))
        diesel_all_in = num(cell(r, 9))
        # Footnotes share column 0 with state names. Requiring the diesel
        # columns to be numeric is what keeps a footnote out of the state list.
        if diesel_state is None and diesel_total_state is None:
            continue

        abbr = TWO_LETTER.get(clean)
        if not abbr:
            # An unrecognised name is left in with abbr=None rather than dropped,
            # and a guard fails the build, so a rename upstream is loud.
            abbr = None

        states.append({
            "name": clean,
            "abbr": abbr,
            "gasoline_state_excise": num(cell(r, 1)),
            "gasoline_other": num(cell(r, 2)),
            "gasoline_total_state": num(cell(r, 3)),
            "gasoline_all_in": num(cell(r, 4)),
            "diesel_state_excise": diesel_state,
            "diesel_other": num(cell(r, 7)),
            "diesel_total_state": diesel_total_state,
            "diesel_all_in": diesel_all_in,
        })

    if len(states) < 45:
        raise ValueError(f"only {len(states)} states parsed; expected 45 or more")

    # The federal figure must reconcile: state total + federal total = all-in.
    # Alabama: 0.3275 + 0.244 = 0.5715. If this drifts, a column has moved.
    checked = 0
    for s in states:
        if s["diesel_total_state"] is not None and s["diesel_all_in"] is not None:
            if abs(s["diesel_total_state"] + federal["diesel_total"]
                   - s["diesel_all_in"]) > 0.0005:
                raise ValueError(
                    f"{s['name']}: state {s['diesel_total_state']} + federal "
                    f"{federal['diesel_total']} != all-in {s['diesel_all_in']}")
            checked += 1
    if checked < 40:
        raise ValueError(f"only {checked} states reconciled; columns may have moved")

    updated = ""
    m = re.search(r"Updated\s+([A-Z][a-z]+ \d{4})", str(cell(1, 0) or ""))
    if m:
        try:
            updated = datetime.strptime(m.group(1), "%B %Y").strftime("%Y-%m-01")
        except ValueError:
            updated = ""

    return {
        "source": "U.S. Energy Information Administration",
        "source_name": "Federal and state motor fuel taxes",
        "source_url": URL,
        "sheet": name,
        "updated": updated or "",
        "fetched_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit": "USD per gallon",
        "federal": federal,
        "states": states,
        "state_count": len(states),
    }


def main():
    print(f"fetching {URL}")
    raw = fetch()
    print(f"  {len(raw):,} bytes")
    payload = parse(raw)
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "us_fuel_tax.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    f_ = payload["federal"]
    print(f"  sheet:        {payload['sheet']}  (updated {payload['updated']})")
    print(f"  federal:      diesel {f_['diesel_total']} / gasoline {f_['gasoline_total']}")
    print(f"  states:       {payload['state_count']}")
    miss = [s["name"] for s in payload["states"] if not s["abbr"]]
    if miss:
        print(f"  no abbreviation matched: {miss}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
