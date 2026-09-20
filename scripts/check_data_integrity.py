#!/usr/bin/env python3
"""Data invariants the pages depend on.

Every defect this file guards against had the same shape: it rendered cleanly
and did nothing. The chrome guard passed, the link check passed, the build
exited 0, and the site published a wrong number for weeks.

1. A lookback must never return the newest observation. history.value_at()
   anchored its target to today, and the diesel series is weekly, so the
   nearest point to "7 days ago" was the newest print itself and every 7-day
   delta computed to exactly 0.0.

2. The chart's headline value must equal the national average cited on the
   same page. They disagreed (249.2 charted, 267.1 cited four lines below)
   because a source revision never propagated through the history store.

3. The published spread must be the ten-province figure normalize.py computes,
   and low/high must be the extremes of those ten provinces. Recomputing over
   all twelve jurisdictions in fuel.json produced a second, different spread on
   the same property.

Run: python scripts/check_data_integrity.py
Exit 0 = clean, 1 = violation.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import history  # noqa: E402

INDEX_PROVINCES = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]

PAIRS = (
    ("diesel", "national"), ("diesel", "AB"), ("diesel", "QC"),
    ("fx", "usd_cad"), ("eia", "national"),
)


def _load(name):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"GUARD FATAL: could not read {name}: {e}")
        return None


def check_lookback_not_latest():
    """A lookback has to compare against something older than the newest point."""
    bad = []
    for series, key in PAIRS:
        now = history.latest(series, key)
        if now is None:
            continue
        for n in (7, 30):
            then = history.value_at(series, key, n)
            if then is not None and then == now:
                bad.append(f"{series}/{key} {n}d returned the newest value "
                           f"({now}) as its own comparator")
    return bad


def check_chart_matches_headline():
    """The chart's latest point must equal the published national average."""
    chart, fuel = _load("chart_data.json"), _load("fuel.json")
    if chart is None or fuel is None:
        return ["could not load chart_data.json / fuel.json"]

    c_latest = (chart.get("meta") or {}).get("latest")
    f_nat = fuel.get("diesel_national_avg")
    if c_latest is None or f_nat is None:
        return []
    try:
        if abs(float(c_latest) - float(f_nat)) > 0.05:
            return [f"chart latest {c_latest} != fuel national {f_nat}. "
                    f"Pages cite one figure and chart the other."]
    except (TypeError, ValueError):
        return [f"non-numeric: chart latest {c_latest!r}, fuel national {f_nat!r}"]
    return []


def check_spread_definition():
    """Spread must be high minus low over the ten index provinces."""
    fuel, norm = _load("fuel.json"), _load("fuel.norm.json")
    if fuel is None or norm is None:
        return ["could not load fuel.json / fuel.norm.json"]

    nf = norm.get("fuel") if isinstance(norm.get("fuel"), dict) else norm
    out = []

    spread, low, high = nf.get("spread"), nf.get("low"), nf.get("high")
    if None not in (spread, low, high):
        try:
            calc = round(float(high) - float(low), 1)
            if abs(calc - float(spread)) > 0.15:
                out.append(f"spread {spread} != high {high} - low {low} ({calc})")
        except (TypeError, ValueError):
            out.append(f"non-numeric spread/low/high: {spread!r}/{low!r}/{high!r}")

    provs = fuel.get("provinces") or {}
    vals = {c: (provs.get(c) or {}).get("diesel") for c in INDEX_PROVINCES}
    vals = {k: v for k, v in vals.items() if v is not None}
    if vals:
        lo_c = min(vals, key=vals.get)
        hi_c = max(vals, key=vals.get)
        if nf.get("low_code") and nf["low_code"] != lo_c:
            out.append(f"low_code is {nf['low_code']} but the ten-province low is "
                       f"{lo_c} ({vals[lo_c]}). A territory may have leaked in.")
        if nf.get("high_code") and nf["high_code"] != hi_c:
            out.append(f"high_code is {nf['high_code']} but the ten-province high "
                       f"is {hi_c} ({vals[hi_c]})")
    return out


CHECKS = (
    ("lookback never returns the newest point", check_lookback_not_latest),
    ("chart headline agrees with the cited average", check_chart_matches_headline),
    ("spread uses the ten-province definition", check_spread_definition),
)


def main():
    failures = []
    for name, fn in CHECKS:
        bad = fn()
        if bad:
            print(f"GUARD FATAL: {name}")
            for b in bad:
                print(f"  - {b}")
            failures += bad
        else:
            print(f"GUARD OK: {name}")

    if failures:
        print(f"\nGUARD FATAL: {len(failures)} data integrity violation(s)")
        return 1
    print("\nGUARD OK: data integrity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
