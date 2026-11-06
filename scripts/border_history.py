#!/usr/bin/env python3
"""Border history — persist delay_minutes per crossing, per run."""
import json, os
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(ROOT, "data", "history", "border.csv")
FIELDS = ["date", "crossing_id", "delay_minutes", "observation_time"]

# Every observation, not one per day.
#
# border.csv is deliberately one row per crossing per day: the pages, border_trends.json and the
# averages all read it that way, and changing its shape would silently reweight every published
# p90. So the daily rollup stays exactly as it was and this file sits beside it.
#
# It exists because a "wait at 6am Tuesday" forecast needs intraday readings and there are none.
# Measured 2026-11-06: 1,549 rows, 88 days, 55 crossings, and exactly one reading per
# crossing-day, because record_run() drops the whole day and writes the last fetch. The collector
# runs hourly, so 23 of every 24 readings were being thrown away. Anything built on border.csv
# can only ever say what the wait was at whatever hour the collection happened to land.
INTRADAY = os.path.join(ROOT, "data", "history", "border_intraday.csv")
INTRADAY_FIELDS = ["date", "crossing_id", "delay_minutes", "observation_time"]


def _ensure():
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    if not os.path.exists(STORE):
        with open(STORE, "w") as f:
            f.write(",".join(FIELDS) + "\n")


def record_run(crossings, run_date=None):
    """Append one row per crossing. Idempotent per day — re-running overwrites."""
    _ensure()
    if run_date is None:
        run_date = date.today().isoformat()

    # Load existing, drop today's entries
    rows = []
    if os.path.exists(STORE):
        with open(STORE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("date"):
                    continue
                parts = line.split(",", 3)
                if len(parts) >= 2 and parts[0] != run_date:
                    rows.append(line)

    for c in crossings:
        delay = c.get("delay_minutes")
        if delay is None:
            continue
        crossing_id = c.get("id", c.get("name", "unknown"))
        obs_time = c.get("captured_utc", "")
        rows.append(f"{run_date},{crossing_id},{delay},{obs_time}")

    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        f.write(",".join(FIELDS) + "\n")
        for r in sorted(set(rows)):
            f.write(r + "\n")
    os.replace(tmp, STORE)

    _append_intraday(crossings, run_date)


def _append_intraday(crossings, run_date):
    """Append every reading to the intraday store, skipping ones already recorded.

    Kept separate from the daily rollup so a forecast model can see the shape of a day. Nothing
    reads this yet; it is being recorded now because the readings cannot be recovered later.
    """
    seen = set()
    if os.path.exists(INTRADAY):
        with open(INTRADAY) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("date"):
                    seen.add(line)
    else:
        with open(INTRADAY, "w") as f:
            f.write(",".join(INTRADAY_FIELDS) + "\n")

    new_rows = []
    for c in crossings:
        delay = c.get("delay_minutes")
        if delay is None:
            continue
        row = (f"{run_date},{c.get('id', c.get('name', 'unknown'))},{delay},"
               f"{c.get('captured_utc', '')}")
        if row in seen:
            continue
        seen.add(row)
        new_rows.append(row)

    if new_rows:
        with open(INTRADAY, "a") as f:
            for row in new_rows:
                f.write(row + "\n")


def span_days(crossing_id=None):
    """Days of history for a crossing, or max across all if None."""
    if not os.path.exists(STORE):
        return 0
    dates = set()
    with open(STORE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("date,"):
                continue          # the header is not a date; parsing it raised every time
            parts = line.split(",")
            if len(parts) >= 2 and parts[0] and parts[1]:
                cid, d = parts[1], parts[0]
                if crossing_id is None or cid == crossing_id:
                    dates.add(d)
    if len(dates) < 2:
        return 0
    sd = sorted(dates)
    return (datetime.strptime(sd[-1], "%Y-%m-%d") - datetime.strptime(sd[0], "%Y-%m-%d")).days


def delta(crossing_id, days_ago):
    """Change in delay_minutes over N days. None if insufficient history."""
    if not os.path.exists(STORE):
        return None
    target = date.today().isoformat()
    past_target = (date.today() - date.resolution * days_ago).isoformat()
    now_val = past_val = None
    with open(STORE) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[1] == crossing_id:
                try:
                    if parts[0] == target:
                        now_val = int(parts[2])
                    if parts[0] == past_target:
                        past_val = int(parts[2])
                except ValueError:
                    continue
    if now_val is not None and past_val is not None:
        return now_val - past_val
    return None
