#!/usr/bin/env python3
"""EIA weekly US diesel collector — all 11 published districts.

Downloads the EIA 'Weekly Retail Gasoline and Diesel Prices' workbook
(psw18vwall.xls), which is keyless, and extracts the Ultra-Low Sulfur
(0-15 ppm) on-highway diesel series from the 'Data 5' sheet. That is the US
analog of the NRCan on-highway diesel survey we already collect.

ALL ELEVEN, NOT SIX
-------------------
The 'Data 5' sheet carries 12 columns: a date, then eleven diesel series. The
collector previously read six of them (national plus the five PADDs) and simply
ignored columns 3, 4, 5, 10 and 11, which are the three PADD 1 sub-regions,
California, and the West Coast excluding California.

Those five are the only additional US diesel geography that exists. EIA does not
price diesel by state, so this is the complete set and there is nothing further
to chase:

  col  1  NUS    U.S. national          col  7  R30  Gulf Coast (PADD 3)
  col  2  R10    East Coast (PADD 1)    col  8  R40  Rocky Mountain (PADD 4)
  col  3  R1X    New England (PADD 1A)  col  9  R50  West Coast (PADD 5)
  col  4  R1Y    Central Atlantic (1B)  col 10  SCA  California
  col  5  R1Z    Lower Atlantic (1C)    col 11  R5XCA West Coast ex-California
  col  6  R20    Midwest (PADD 2)

A BLANK IS NOT A ZERO
---------------------
R5XCA is empty for the first years of the series and a district can be blank in
any given week. A blank cell means EIA did not publish that week, not that diesel
was free, so it becomes None and stays None through to the template. Writing 0.0
here would put "$0.00 a gallon" in front of a driver.

Requires xlrd (legacy .xls parser):  pip install xlrd
"""
import datetime
import json
import os
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

URL = "https://www.eia.gov/petroleum/gasdiesel/xls/psw18vwall.xls"
UA = ("Mozilla/5.0 (compatible; NorthernMileDashboard/1.0; "
      "+https://dashboard.northernmilemedia.com)")

# Column -> (key, label, padd). Order matters: the PADD key is what the US state
# pages use to find their own district's price.
SERIES = {
    1: ("us_national", "U.S.", None),
    2: ("east_coast", "East Coast (PADD 1)", "R10"),
    3: ("new_england", "New England (PADD 1A)", "R1X"),
    4: ("central_atlantic", "Central Atlantic (PADD 1B)", "R1Y"),
    5: ("lower_atlantic", "Lower Atlantic (PADD 1C)", "R1Z"),
    6: ("midwest", "Midwest (PADD 2)", "R20"),
    7: ("gulf_coast", "Gulf Coast (PADD 3)", "R30"),
    8: ("rocky_mountain", "Rocky Mountain (PADD 4)", "R40"),
    9: ("west_coast", "West Coast (PADD 5)", "R50"),
    10: ("california", "California", "SCA"),
    11: ("west_coast_ex_california", "West Coast excluding California", "R5XCA"),
}

# State -> PADD, per EIA's own regional definitions. 50 states plus DC = 51.
# A state page shows its district's price and SAYS it is a district price; this
# map is what makes that attribution correct rather than guessed.
STATE_PADD = {
    # PADD 1A New England
    "CT": "new_england", "ME": "new_england", "MA": "new_england",
    "NH": "new_england", "RI": "new_england", "VT": "new_england",
    # PADD 1B Central Atlantic
    "DE": "central_atlantic", "DC": "central_atlantic", "MD": "central_atlantic",
    "NJ": "central_atlantic", "NY": "central_atlantic", "PA": "central_atlantic",
    # PADD 1C Lower Atlantic
    "FL": "lower_atlantic", "GA": "lower_atlantic", "NC": "lower_atlantic",
    "SC": "lower_atlantic", "VA": "lower_atlantic", "WV": "lower_atlantic",
    # PADD 2 Midwest
    "IL": "midwest", "IN": "midwest", "IA": "midwest", "KS": "midwest",
    "KY": "midwest", "MI": "midwest", "MN": "midwest", "MO": "midwest",
    "NE": "midwest", "ND": "midwest", "OH": "midwest", "OK": "midwest",
    "SD": "midwest", "TN": "midwest", "WI": "midwest",
    # PADD 3 Gulf Coast
    "AL": "gulf_coast", "AR": "gulf_coast", "LA": "gulf_coast",
    "MS": "gulf_coast", "NM": "gulf_coast", "TX": "gulf_coast",
    # PADD 4 Rocky Mountain
    "CO": "rocky_mountain", "ID": "rocky_mountain", "MT": "rocky_mountain",
    "UT": "rocky_mountain", "WY": "rocky_mountain",
    # PADD 5 West Coast
    "AK": "west_coast", "AZ": "west_coast", "CA": "california",
    "HI": "west_coast", "NV": "west_coast", "OR": "west_coast",
    "WA": "west_coast",
}


def fetch_bytes():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def _value(sh, row, col):
    """A blank cell is None. It is never 0.

    xlrd gives '' for an empty cell. float('') raises, which would abort the
    whole collect; float(0) would publish a fake price. Neither is acceptable.
    """
    try:
        raw = sh.cell_value(row, col)
    except Exception:
        return None
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    return round(v, 3) if v > 0 else None


def parse(xls_bytes):
    import xlrd  # deferred: degrade gracefully (record failure) if parser missing
    wb = xlrd.open_workbook(file_contents=xls_bytes)
    sh = wb.sheet_by_name("Data 5")

    # Walk back from the end to the newest row that actually carries a national
    # figure. The final row can be a partially published week.
    row = None
    for r in range(sh.nrows - 1, 2, -1):
        if _value(sh, r, 1) is not None:
            row = r
            break
    if row is None:
        raise ValueError("no row in 'Data 5' carried a national diesel price")

    dt = xlrd.xldate_as_datetime(float(sh.cell_value(row, 0)), wb.datemode)

    values = {}
    for col, (key, _label, _padd) in SERIES.items():
        values[key] = _value(sh, row, col)
    if values["us_national"] is None:
        raise ValueError("latest row has no national price")

    return dt.date().isoformat(), values


def collect_eia_diesel():
    xls_bytes = fetch_bytes()
    date, values = parse(xls_bytes)
    districts = {k: v for k, v in values.items() if k != "us_national"}
    data = {
        "date": date,  # week-ending date (Monday)
        "us_national_usd_gal": values["us_national"],
        "padds_usd_gal": districts,  # kept: existing pages read this key
        "districts": {
            key: {
                "price_usd_gal": values[key],
                "label": label,
                "padd": padd,
            }
            for _col, (key, label, padd) in SERIES.items() if key != "us_national"
        },
        "state_padd": STATE_PADD,
        "unit": "USD per gallon",
        "grade": "Ultra-low sulfur diesel (0-15 ppm), on-highway",
        "source": "U.S. Energy Information Administration weekly retail diesel survey",
        "source_url": URL,
        "note": ("EIA publishes diesel by district, not by state. State pages show "
                 "the figure for the district the state sits in, and say so."),
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "eia_diesel.json"), "w") as f:
        json.dump(data, f, indent=2, default=str)

    published = sum(1 for v in districts.values() if v is not None)
    blank = [k for k, v in districts.items() if v is None]
    print(f"  EIA diesel: US ${values['us_national']}/gal on {date}")
    print(f"  districts published: {published} of {len(districts)}"
          + (f"  (blank: {', '.join(blank)})" if blank else ""))
    return data


if __name__ == "__main__":
    collect_eia_diesel()
