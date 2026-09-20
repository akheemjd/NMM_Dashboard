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
    """Record value for a date.

    First write wins for settled history, so a mid-week rebuild cannot rewrite
    a past observation.

    The NEWEST date is deliberately the exception. NRCan revises a print after
    publishing it, and the series has to follow the correction. Under a strict
    first-write-wins the 15 September print stayed at its original 249.2 while
    every other surface on the site quoted the revised 267.1 from the same
    feed, so the homepage chart contradicted its own citation four lines below
    it, and nothing errored for weeks.
    """
    if value is None:
        return
    try:
        value = float(value)
    except (TypeError, ValueError):
        return

    day = (when or date.today()).isoformat()
    rows = _load()

    newest = max((r["date"] for r in rows
                  if r["series"] == series and r["key"] == key), default=None)

    for r in rows:
        if r["date"] == day and r["series"] == series and r["key"] == key:
            if day != newest:
                return  # settled history — keep the original value
            if r["value"] == f"{value:.4f}":
                return  # unchanged
            r["value"] = f"{value:.4f}"  # accept the revision to the live point
            _write(rows)
            return

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
    """Value closest to N days before the NEWEST observation, within tolerance.

    Anchored to the newest observation, not to today. The diesel series is
    weekly, so "today minus 7" never lands on a data point: it fell two days
    from the newest print, inside the tolerance, and this function returned the
    newest value as its own comparator. Every 7-day delta on the site computed
    to exactly 0.0, in text and as zero-width bars.

    Excluding the newest point is the other half of the fix. A lookback has to
    compare against something genuinely older than the latest observation, or
    "change over the period" is always zero by construction.
    """
    pts = _points(series, key)
    if len(pts) < 2:
        return None
    newest = pts[-1][0]
    target = newest - timedelta(days=days_ago)
    best, best_gap = None, None
    for d, v in pts:
        if d >= newest:
            continue
        gap = abs((d - target).days)
        if best_gap is None or gap < best_gap:
            best, best_gap = v, gap
    return best if best_gap is not None and best_gap <= tolerance else None


def delta(series, key, days_ago, tolerance=3, ndigits=1):
    """Change from N observations back to the newest. None if history is short.

    ndigits matters more than it looks. Diesel moves in cents, so one decimal
    is right, but USD/CAD moves in the fourth decimal: a 0.0093 move rounded to
    one place is 0.0, which reads as "the loonie did not move". Callers working
    in a finer unit have to say so.
    """
    now, then = latest(series, key), value_at(series, key, days_ago, tolerance)
    if now is None or then is None:
        return None
    return round(now - then, ndigits)


def average(series, key, days, ndigits=1):
    """Mean over the trailing calendar window. None if fewer than 14 points.

    ndigits exists for the same reason it does on delta(). Diesel moves in
    cents, so one decimal is right, but USD/CAD moves in the fourth decimal:
    round(1.3868, 1) is 1.4, which made the home page report a 30-day FX
    comparison of "+0.0002 vs 30-day avg 1.4000" against a true mean of 1.3868
    and a true gap of +0.0138, understating it about 67 times. Callers working
    in a finer unit have to say so.
    """
    cutoff = date.today() - timedelta(days=days)
    vals = [v for d, v in _points(series, key) if d >= cutoff]
    return round(sum(vals) / len(vals), ndigits) if len(vals) >= 14 else None


def average_obs(series, key, n, ndigits=1):
    """Mean of the last n observations. None if fewer than n exist.

    The FX module defines its "30-day average" as the trailing 21 business
    days, and a calendar window over the same period contains a different set
    of observations. Computing it both ways put two different 30-day FX
    averages on the site at once (1.3864 in fx.norm.json, 1.3868 in
    market.json). Count observations, not days, when matching that figure.
    """
    pts = [v for _, v in _points(series, key)]
    if len(pts) < n:
        return None
    return round(sum(pts[-n:]) / n, ndigits)
