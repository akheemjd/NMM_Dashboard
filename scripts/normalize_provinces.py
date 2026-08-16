#!/usr/bin/env python3
"""Province page normalizer.

Reads the city-level NRCan sidecar (data/nrcan_diesel.json) and the province
aggregates (data/fuel.json), and emits data/provinces.norm.json — one render
block per configured province.

Design rules, consistent with the rest of the pipeline:
  - No invented values. Every number here is either read from NRCan or derived
    arithmetically from NRCan figures on this page.
  - Hard failure over silent fallback. Missing input, stale input, or an
    unmapped city stops the build.
  - Prose is human. This script emits data only; the build script requires a
    hand-written prose file per province.
"""

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

sys.path.insert(0, HERE)
from collect_nrcan_diesel import CITY_PROVINCE  # noqa: E402

# Accent-safe lookup, same approach as the collector.
try:
    from collect_nrcan_diesel import _norm, CITY_PROVINCE_NORM
except ImportError:  # collector predates the accent fix
    import unicodedata

    def _norm(s):
        return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").strip()

    CITY_PROVINCE_NORM = {_norm(k): v for k, v in CITY_PROVINCE.items()}

# Provinces that get a page. Start small; add codes as prose is written.
PROVINCE_PAGES = ["ON", "AB"]

PROVINCE_NAMES = {
    "BC": "British Columbia",
    "AB": "Alberta",
    "SK": "Saskatchewan",
    "MB": "Manitoba",
    "ON": "Ontario",
    "QC": "Quebec",
    "NB": "New Brunswick",
    "NS": "Nova Scotia",
    "PE": "Prince Edward Island",
    "NL": "Newfoundland and Labrador",
}

SLUGS = {
    "BC": "british-columbia",
    "AB": "alberta",
    "SK": "saskatchewan",
    "MB": "manitoba",
    "ON": "ontario",
    "QC": "quebec",
    "NB": "new-brunswick",
    "NS": "nova-scotia",
    "PE": "prince-edward-island",
    "NL": "newfoundland-and-labrador",
}

# A province page is only honest if it has enough survey cities to show a
# spread. Single-city provinces (PE) would render a spread of 0.0.
MIN_CITIES = 3


def load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        raise FileNotFoundError(f"required input missing: {path}")
    with open(path) as f:
        return json.load(f)


def signed(v):
    return f"{v:+.1f}"


def build_province(code, city_prices, national, print_date, build_version):
    """Assemble one province's render block."""
    name = PROVINCE_NAMES[code]

    cities = sorted(
        [(c, p) for c, p in city_prices.items() if CITY_PROVINCE_NORM.get(_norm(c)) == code],
        key=lambda x: x[1],
    )
    if len(cities) < MIN_CITIES:
        raise ValueError(
            f"{code}: {len(cities)} survey cities, need at least {MIN_CITIES} "
            f"for a spread to mean anything"
        )

    prices = [p for _, p in cities]
    prov_mean = round(sum(prices) / len(prices), 1)
    low_city, low_price = cities[0]
    high_city, high_price = cities[-1]
    spread = round(high_price - low_price, 1)
    vs_nat = round(prov_mean - national, 1)

    rows = []
    for city, price in cities:
        delta = round(price - prov_mean, 1)
        rows.append(
            {
                "city": city,
                "price": f"{price:.1f}",
                "vs_prov": signed(delta),
                # Cost frame: above the provincial mean is the expensive side.
                "vs_class": "up" if delta > 0 else ("down" if delta < 0 else "flat"),
            }
        )

    return {
        "code": code,
        "name": name,
        "slug": SLUGS[code],
        "price": f"{prov_mean:.1f}",
        "national": f"{national:.1f}",
        "vs_national": signed(vs_nat),
        "vs_national_class": "up" if vs_nat > 0 else ("down" if vs_nat < 0 else "flat"),
        "vs_national_word": "above" if vs_nat > 0 else ("below" if vs_nat < 0 else "level with"),
        "vs_national_abs": f"{abs(vs_nat):.1f}",
        "city_count": str(len(cities)),
        "low_city": low_city,
        "low_price": f"{low_price:.1f}",
        "high_city": high_city,
        "high_price": f"{high_price:.1f}",
        "spread": f"{spread:.1f}",
        "print_date": print_date,
        "build_version": build_version,
        "cities": rows,
    }


def main():
    fuel = load("fuel.json")
    sidecar = load("nrcan_diesel.json")

    city_prices = sidecar.get("prices") or {}
    if not city_prices:
        raise ValueError("nrcan_diesel.json has no prices — refusing to build province pages")

    national = fuel.get("diesel_national_avg")
    if national is None:
        raise ValueError("fuel.json has no diesel_national_avg")

    print_date = fuel.get("print_date")
    if not print_date:
        raise ValueError("fuel.json has no print_date — every figure on a province page is dated")

    build_version = fuel.get("build_version") or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    unmapped = [c for c in city_prices if _norm(c) not in CITY_PROVINCE_NORM]
    if unmapped:
        raise ValueError(f"unmapped cities in sidecar: {unmapped}")

    # Reuse the standard pages' build timestamps so the coherence guard sees one
    # identical footer across all eleven pages. Fall back to a fresh stamp only
    # if home.norm is missing.
    home = load("home.norm.json")
    updated_at = home.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    updated_iso = home.get("updated_iso") or datetime.now(timezone.utc).isoformat()

    out = {}
    for code in PROVINCE_PAGES:
        if code not in PROVINCE_NAMES:
            raise ValueError(f"{code} is not an index province")
        blk = build_province(code, city_prices, national, print_date, build_version)
        blk["updated_at"] = updated_at
        blk["updated_iso"] = updated_iso
        out[code] = blk

    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "print_date": print_date,
        "national": f"{national:.1f}",
        "build_version": build_version,
        "provinces": out,
    }

    path = os.path.join(DATA, "provinces.norm.json")
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"provinces.norm.json written — {len(out)} provinces, print {print_date}")
    for code, blk in out.items():
        print(
            f"  {code}: {blk['price']}c/L over {blk['city_count']} cities · "
            f"spread {blk['spread']} ({blk['low_city']} {blk['low_price']} → "
            f"{blk['high_city']} {blk['high_price']}) · vs national {blk['vs_national']}"
        )


if __name__ == "__main__":
    main()
