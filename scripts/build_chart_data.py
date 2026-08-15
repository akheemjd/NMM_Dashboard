#!/usr/bin/env python3
"""Extract chart data from the history store for the diesel chart.

Reads data/history/series.csv and writes data/chart_data.json — the national
diesel weekly series the chart embeds. Runs in the build BEFORE build_templates,
so the generated pages can inject the JSON.

Kept separate from history.py on purpose: history.py is the write/query API the
collector uses; this is a read-only build-time extract for the front end. It
reads the CSV directly rather than importing history.py so a chart change can
never affect the snapshot path.

Emits one series today (national diesel). Provincial series for sparklines are a
later addition — the structure below extends to them without a rewrite.
"""

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, "data", "history", "series.csv")
OUT = os.path.join(ROOT, "data", "chart_data.json")


def main():
    if not os.path.exists(STORE):
        print(f"chart_data: no store at {STORE} — writing empty payload")
        with open(OUT, "w") as f:
            json.dump({"diesel_national": []}, f)
        return 0

    national = []
    with open(STORE, newline="") as f:
        for row in csv.reader(f):
            if len(row) != 4:
                continue
            date, series, key, value = (c.strip() for c in row)
            if series == "diesel" and key == "national":
                try:
                    national.append({"d": date, "v": round(float(value), 1)})
                except ValueError:
                    continue

    national.sort(key=lambda p: p["d"])

    meta_extra = {}
    if national:
        from datetime import datetime as _dt
        vals = [p["v"] for p in national]
        lo = min(national, key=lambda p: p["v"])
        hi = max(national, key=lambda p: p["v"])
        latest = national[-1]
        latest_pct = round(sum(1 for v in vals if v <= latest["v"]) / len(vals) * 100)
        meta_extra = {
            "avg": round(sum(vals) / len(vals), 1),
            "low_date": _dt.strptime(lo["d"], "%Y-%m-%d").strftime("%b %Y"),
            "high_date": _dt.strptime(hi["d"], "%Y-%m-%d").strftime("%b %Y"),
            "latest": latest["v"],
            "latest_pct": latest_pct,
            "latest_band": ("near record high" if latest_pct >= 90 else "near record low" if latest_pct <= 10 else ""),
        }

    payload = {
        "diesel_national": national,
        # metadata the chart caption can use without recomputing
        "meta": {
            "count": len(national),
            "first": national[0]["d"] if national else None,
            "last": national[-1]["d"] if national else None,
            "min": min((p["v"] for p in national), default=None),
            "max": max((p["v"] for p in national), default=None),
            **meta_extra,
        },
    }

    with open(OUT, "w") as f:
        json.dump(payload, f, separators=(",", ":"))

    m = payload["meta"]
    print(f"chart_data: {m['count']} national diesel points, "
          f"{m['first']} to {m['last']}, {m['min']}-{m['max']}c/L -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
