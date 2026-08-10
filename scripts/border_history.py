#!/usr/bin/env python3
"""Border history — persist delay_minutes per crossing, per run."""
import json, os
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(ROOT, "data", "history", "border.csv")
FIELDS = ["date", "crossing_id", "delay_minutes", "observation_time"]


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
        obs_time = c.get("live_updated", "")
        rows.append(f"{run_date},{crossing_id},{delay},{obs_time}")

    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        f.write(",".join(FIELDS) + "\n")
        for r in sorted(set(rows)):
            f.write(r + "\n")
    os.replace(tmp, STORE)


def span_days(crossing_id=None):
    """Days of history for a crossing, or max across all if None."""
    if not os.path.exists(STORE):
        return 0
    dates = set()
    with open(STORE) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
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
