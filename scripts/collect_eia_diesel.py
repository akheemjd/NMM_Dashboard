#!/usr/bin/env python3
"""EIA weekly US diesel collector — national + PADD regions.

Downloads the EIA 'Weekly Retail Gasoline and Diesel Prices' workbook
(psw18vwall.xls), which is keyless, and extracts the Ultra-Low Sulfur
(0-15 ppm) on-highway diesel series from the 'Data 5' sheet. That is the US
analog of the NRCan on-highway diesel survey we already collect.

Requires xlrd (legacy .xls parser):  pip install xlrd
"""
import datetime
import json
import os
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

URL = "https://www.eia.gov/petroleum/gasdiesel/xls/psw18vwall.xls"
UA = "Mozilla/5.0 (compatible; NorthernMileDashboard/1.0; +https://dashboard.northernmilemedia.com)"

# Data 5 columns -> (key, label). Column 0 = date, 1 = US national, then PADDs.
SERIES = {
    1: ("us_national", "U.S."),
    2: ("east_coast", "East Coast (PADD 1)"),
    6: ("midwest", "Midwest (PADD 2)"),
    7: ("gulf_coast", "Gulf Coast (PADD 3)"),
    8: ("rocky_mountain", "Rocky Mountain (PADD 4)"),
    9: ("west_coast", "West Coast (PADD 5)"),
}


def fetch_bytes():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def parse(xls_bytes):
    import xlrd  # deferred: degrade gracefully (record failure) if parser missing
    wb = xlrd.open_workbook(file_contents=xls_bytes)
    sh = wb.sheet_by_name("Data 5")
    r = sh.nrows - 1  # rows are chronological; last row is the latest week
    dt = xlrd.xldate_as_datetime(float(sh.cell_value(r, 0)), wb.datemode)
    values = {}
    for col, (key, _label) in SERIES.items():
        values[key] = round(float(sh.cell_value(r, col)), 3)
    return dt.date().isoformat(), values


def collect_eia_diesel():
    xls_bytes = fetch_bytes()
    date, values = parse(xls_bytes)
    data = {
        "date": date,  # week-ending date (Monday)
        "us_national_usd_gal": values["us_national"],
        "padds_usd_gal": {k: values[k] for k in values if k != "us_national"},
        "unit": "USD per gallon",
        "grade": "Ultra-low sulfur diesel (0-15 ppm), on-highway",
        "source": "U.S. Energy Information Administration weekly retail diesel survey",
        "source_url": URL,
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "eia_diesel.json"), "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"  EIA diesel: US ${values['us_national']}/gal on {date}")
    return data


if __name__ == "__main__":
    collect_eia_diesel()
