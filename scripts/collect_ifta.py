#!/usr/bin/env python3
"""Collect the official IFTA fuel tax matrix.

WHY THIS EXISTS
---------------
IFTA, Inc. publishes the authoritative quarterly fuel tax rate for every
jurisdiction in one machine-readable file. It is free, it covers all 10 Canadian
provinces and 48 US states, and it goes back to 1Q2017:

    https://www.iftach.org/taxmatrix/charts/3Q2026.csv

It is also the only all-jurisdiction compliance dataset that exists in one
place. Everything else in this space (weight limits, permits, seasonal
restrictions) is fragmented across 50+ government portals, which is why this is
the cleanest first cut at a compliance reference layer.

WHAT THE FILE LOOKS LIKE
------------------------
Two header rows (fuel type, then a sub-label), then two rows PER JURISDICTION:

    ALBERTA #14,U.S.,$ 0.3519 ,...
    ,Can,$ 0.1300 ,...

The U.S. row is the rate for US-licensed carriers and the Can row is for
Canadian-licensed carriers. They differ because some provinces charge a
different rate by licensee jurisdiction, and collapsing them into one number
would be wrong for roughly a third of the jurisdictions.

Rate cells are dollar-prefixed, sometimes "$-" meaning no tax, and carry
trailing whitespace. Dollar signs and blanks are normalised here, and a genuinely
absent value stays None so it cannot read as a zero tax rate.

Source: IFTA, Inc. (International Fuel Tax Association) quarterly Tax Matrix.
"""
import csv
import io
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "ifta.json")
BASE = "https://www.iftach.org/taxmatrix/charts/{q}Q{y}.csv"

CANADIAN = {
    "ALBERTA", "BRITISH COLUMBIA", "MANITOBA", "NEW BRUNSWICK", "NEWFOUNDLAND",
    "NOVA SCOTIA", "ONTARIO", "PRINCE EDWARD ISLAND", "QUEBEC", "SASKATCHEWAN",
    "YUKON", "NORTHWEST TERRITORIES", "NUNAVUT",
}
CA_CODES = {
    "ALBERTA": "AB", "BRITISH COLUMBIA": "BC", "MANITOBA": "MB",
    "NEW BRUNSWICK": "NB", "NEWFOUNDLAND": "NL", "NOVA SCOTIA": "NS",
    "ONTARIO": "ON", "PRINCE EDWARD ISLAND": "PE", "QUEBEC": "QC",
    "SASKATCHEWAN": "SK", "YUKON": "YT", "NORTHWEST TERRITORIES": "NT",
    "NUNAVUT": "NU",
}

# Column indices from the observed header:
# 0=jurisdiction 1=currency 2=Gasoline 3=Special Diesel 4=Gasohol ...
COL_GASOLINE = 2
COL_DIESEL = 3


def current_quarter(today=None):
    d = today or date.today()
    return (d.month - 1) // 3 + 1, d.year


def parse_rate(cell):
    """'$ 0.3519 ' -> 0.3519 ; '$-' -> 0.0 ; '' or junk -> None.

    None is not 0.0. A jurisdiction with no published rate is different from one
    that levies no tax, and only one of those is safe to display as a number.
    """
    if cell is None:
        return None
    s = str(cell).replace("$", "").replace(",", "").strip()
    if s in ("", "-", "--", "n/a", "N/A"):
        return 0.0 if s == "-" else None
    try:
        return round(float(s), 4)
    except ValueError:
        return None


def fetch_quarter(q, y):
    url = BASE.format(q=q, y=y)
    req = urllib.request.Request(url, headers={
        "User-Agent": "NorthernMileDashboard/1.0 (+https://dashboard.northernmilemedia.com/)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8-sig"), url


def parse_matrix(text):
    rows = list(csv.reader(io.StringIO(text)))
    jurs = {}
    order = []
    last = None
    for row in rows[3:]:
        if not row or not any(c.strip() for c in row):
            continue
        name = row[0].strip()
        currency = (row[1] if len(row) > 1 else "").strip()

        # The 'Can' row for each jurisdiction leaves column 0 BLANK, so the name
        # carries forward from the row above:
        #     ALBERTA #14,U.S.,$ 0.3519 ...
        #     ,Can,$ 0.1300 ...
        # Skipping blank-name rows (the first version did) silently dropped every
        # Canadian-licensed rate on the matrix, which then read as "no rate
        # published" rather than a parse failure.
        if name:
            last = name
        elif last is None:
            continue
        else:
            name = last
        if currency.lower() not in ("u.s.", "us", "can"):
            continue

        # Country suffixes like "ALBERTA #14" carry the IFTA jurisdiction number.
        clean = name.split("#")[0].strip()
        num = name.split("#")[-1].strip() if "#" in name else ""

        # Three states publish a SEPARATE surcharge row on top of their base rate
        # (Indiana, Kentucky, Virginia), spelled "INDIANA SurChg". That is an
        # additional charge on certain fuel types, not a 51st jurisdiction, and
        # listing it as one would both inflate the count and misstate the rate.
        # It is kept beside its parent state instead.
        is_surcharge = clean.lower().endswith("surchg") or "surchg" in clean.lower()
        if is_surcharge:
            clean = clean[:clean.lower().rindex("surchg")].strip()

        j = jurs.setdefault(clean, {"name": clean, "ifta_number": None,
                                    "us": {}, "ca": {}, "surcharge": {}})
        if clean not in order:
            order.append(clean)
        if num.isdigit() and j["ifta_number"] is None:
            j["ifta_number"] = int(num)

        bucket = "us" if currency.lower().startswith("u") else "ca"
        rates = {
            "gasoline": parse_rate(row[COL_GASOLINE] if len(row) > COL_GASOLINE else None),
            "diesel": parse_rate(row[COL_DIESEL] if len(row) > COL_DIESEL else None),
        }
        if is_surcharge:
            j["surcharge"][bucket] = rates
        else:
            j[bucket] = rates
    return [jurs[n] for n in order]


def collect_ifta():
    today = date.today()
    q, y = current_quarter(today)

    used_q, used_y, text, url = None, None, None, None
    # The current quarter's file may not be posted yet on the first day of a
    # quarter, so walk back one quarter before giving up.
    for offset in (0, 1):
        qq, yy = q, y
        if offset:
            qq -= 1
            if qq == 0:
                qq, yy = 4, y - 1
        try:
            text, url = fetch_quarter(qq, yy)
            used_q, used_y = qq, yy
            break
        except Exception as e:
            print(f"  IFTA {qq}Q{yy} unavailable: {e}")

    if text is None:
        raise RuntimeError("no IFTA matrix could be fetched")

    jurs = parse_matrix(text)
    for j in jurs:
        j["is_canadian"] = j["name"] in CANADIAN
        j["code"] = CA_CODES.get(j["name"])
        j["has_us_rate"] = bool(j["us"])
        j["has_ca_rate"] = bool(j["ca"])

    can = [j for j in jurs if j["is_canadian"]]
    us = [j for j in jurs if not j["is_canadian"]]
    with_diesel = [j for j in jurs
                   if (j["us"].get("diesel") is not None
                       or j["ca"].get("diesel") is not None)]

    # Health: a parse that yields jurisdiction rows but no diesel rates at all
    # means the CSV layout changed. That is a failure, not a quiet success.
    try:
        from health_tracker import record_success, record_failure
        if with_diesel:
            record_success("ifta")
        else:
            record_failure("ifta", "Matrix parsed but no diesel rates found — layout may have changed")
    except Exception as e:
        print(f"  ifta health tracking failed: {e}")

    payload = {
        "quarter": f"{used_q}Q{used_y}",
        "quarter_requested": f"{q}Q{y}",
        "jurisdictions": jurs,
        "counts": {
            "total": len(jurs),
            "canadian": len(can),
            "us": len(us),
            "with_diesel_rate": len(with_diesel),
        },
        "source": "IFTA, Inc. quarterly Tax Matrix",
        "source_url": url,
        "source_note": ("IFTA publishes a rate for US-licensed and Canadian-licensed "
                        "carriers separately where they differ, so both are kept."),
        "fetched_date": today.isoformat(),
        "captured_utc": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"  IFTA: {len(jurs)} jurisdictions ({len(can)} CA, {len(us)} US) "
          f"for {used_q}Q{used_y}, {len(with_diesel)} with a diesel rate")
    return payload


if __name__ == "__main__":
    collect_ifta()
