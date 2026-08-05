"""
history.py — daily snapshot store for Northern Mile series.

Drop-in, no dependencies, no database. One CSV, one row per series/key/day.
Safe to call on every build: writes are idempotent within a calendar day,
so the 30-minute cron will not bloat the file.

    from history import snapshot, delta, average, span_days

    snapshot("diesel", "national", 224.8)
    d7 = delta("diesel", "national", 7)      # -> float or None
    avg = average("diesel", "national", 365) # -> float or None

Every read helper returns None when there is not enough history yet.
Callers must handle None — that is what keeps the page from rendering
an empty or misleading tile before the series has accumulated.
"""

import csv
import os
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "..", "data", "history", "series.csv")
FIELDS = ["date", "series", "key", "value"]


def _ensure():
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    if not os.path.exists(STORE):
        with open(STORE, "w", newline="") as f:
            csv.DictWriter(f, FIELDS).writeheader()


def _load():
    _ensure()
    with open(STORE, newline="") as f:
        return list(csv.DictReader(f))


def _write(rows):
    tmp = STORE + ".tmp"
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, STORE)  # atomic — a killed build cannot corrupt the store


def snapshot(series, key, value, when=None):
    """Record value for today. Re-running the same day overwrites, never appends."""
    if value is None:
        return
    try:
        value = float(value)
    except (TypeError, ValueError):
        return

    day = (when or date.today()).isoformat()
    rows = _load()
    for r in rows:
        if r["date"] == day and r["series"] == series and r["key"] == key:
            r["value"] = f"{value:.4f}"
            break
    else:
        rows.append({"date": day, "series": series, "key": key,
                     "value": f"{value:.4f}"})
    rows.sort(key=lambda r: (r["series"], r["key"], r["date"]))
    _write(rows)


def _points(series, key):
    out = []
    for r in _load():
        if r["series"] == series and r["key"] == key:
            try:
                out.append((datetime.fromisoformat(r["date"]).date(),
                            float(r["value"])))
            except (ValueError, TypeError):
                continue
    return sorted(out)


def span_days(series, key):
    """How many days of history exist. Use this to decide what to display."""
    pts = _points(series, key)
    return (pts[-1][0] - pts[0][0]).days if len(pts) >= 2 else 0


def latest(series, key):
    pts = _points(series, key)
    return pts[-1][1] if pts else None


def value_at(series, key, days_ago, tolerance=3):
    """Value closest to N days back, within tolerance days. None if no match."""
    pts = _points(series, key)
    if not pts:
        return None
    target = date.today() - timedelta(days=days_ago)
    best, best_gap = None, None
    for d, v in pts:
        gap = abs((d - target).days)
        if best_gap is None or gap < best_gap:
            best, best_gap = v, gap
    return best if best_gap is not None and best_gap <= tolerance else None


def delta(series, key, days_ago, tolerance=3):
    """Change from N days ago to now. None if history is too short."""
    now, then = latest(series, key), value_at(series, key, days_ago, tolerance)
    if now is None or then is None:
        return None
    return round(now - then, 1)


def average(series, key, days):
    """Mean over the trailing window. None if fewer than 14 points."""
    cutoff = date.today() - timedelta(days=days)
    vals = [v for d, v in _points(series, key) if d >= cutoff]
    return round(sum(vals) / len(vals), 1) if len(vals) >= 14 else None
