#!/usr/bin/env python3
"""Diesel analysis and a scored forecast for the next print.

First cut of the analysis product. Everything here is computed from data/history/series.csv,
which holds NRCan's weekly print per jurisdiction since 2016-01-05. Nothing is estimated by hand
and every number the report states can be re-derived with this file.

The point of the backtest is not to look clever. It is to publish the number that says whether the
forecast is worth anything: three naive baselines, scored on the last two years, with the winner
named. A forecast that cannot beat last week's price is not a forecast, it is a decoration.
"""
import csv
import json
import os
import statistics
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SERIES = os.path.join(ROOT, "data", "history", "series.csv")
OUT_DIR = os.path.join(ROOT, "data", "forecasts")
CHART = os.path.join(ROOT, "docs", "assets", "diesel-forecast.png")

TOLERANCE = 2.0        # a print within this many cents counts as called
HOLDOUT_WEEKS = 104    # score the last two years
TANK_LITRES = 400      # stated assumption for the cost translation, not a measured value


def load(series="diesel", key="national"):
    rows = []
    with open(SERIES, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["series"] == series and r["key"] == key:
                rows.append((date.fromisoformat(r["date"]), float(r["value"])))
    rows.sort()
    return rows


def models(hist):
    """The baselines, each given only the data that existed at the time."""
    out = {}
    out["last print"] = hist[-1]
    out["same week last year"] = hist[-52] if len(hist) >= 52 else hist[-1]
    for n in (4, 8):
        window = hist[-n:]
        out[f"mean of last {n}"] = sum(window) / len(window)
    # Drift: the last print carried forward by the average weekly move. This is the cheapest way
    # to test whether the series has momentum at all, and it is the honest rival to "no change".
    if len(hist) >= 14:
        drift = (hist[-1] - hist[-14]) / 13
        out["last print + 13w drift"] = hist[-1] + drift
    return out


def score(rows):
    """Walk forward over the holdout. Every model sees only prior prints."""
    start = len(rows) - HOLDOUT_WEEKS
    errs = {}
    hits = {}
    for i in range(start, len(rows)):
        hist = [v for _, v in rows[:i]]
        actual = rows[i][1]
        for name, point in models(hist).items():
            e = point - actual
            errs.setdefault(name, []).append(e)
            hits.setdefault(name, []).append(abs(e) <= TOLERANCE)
    table = []
    for name in errs:
        e = errs[name]
        table.append({
            "model": name,
            "mae": round(sum(abs(x) for x in e) / len(e), 2),
            "bias": round(sum(e) / len(e), 2),
            "hit_rate": round(100 * sum(hits[name]) / len(hits[name])),
            "n": len(e),
        })
    table.sort(key=lambda r: r["mae"])
    return table, errs


def main():
    rows = load()
    values = [v for _, v in rows]
    last_date, last_value = rows[-1]

    # ---- description -------------------------------------------------------
    year_ago = next(v for d, v in reversed(rows) if d <= last_date - timedelta(days=364))
    five = values[-260:]
    ten = values
    rank = sum(1 for v in five if v <= last_value) / len(five) * 100
    peak = max(ten)
    trough = min(ten)
    print("=== WHERE DIESEL IS ===")
    print(f"prints            {len(rows)} weekly, {rows[0][0]} to {last_date}")
    print(f"latest            {last_value} cents/litre")
    print(f"a year ago        {year_ago} cents/litre")
    print(f"5y percentile     {rank:.0f}th of {len(five)} weekly prints")
    print(f"10y range         {trough} to {peak}")

    # ---- seasonality -------------------------------------------------------
    by_month = {}
    for d, v in rows:
        by_month.setdefault(d.month, []).append(v)
    print("\n=== SEASONAL SHAPE (mean print by month, all years) ===")
    means = {m: sum(v) / len(v) for m, v in by_month.items()}
    for m in sorted(means, key=lambda m: means[m]):
        print(f"  month {m:02d}  {means[m]:.1f}  (n={len(by_month[m])})")

    # ---- backtest ----------------------------------------------------------
    table, errs = score(rows)
    print(f"\n=== BACKTEST, LAST {HOLDOUT_WEEKS} PRINTS ===")
    print(f"{'model':24s} {'MAE':>6s} {'bias':>7s} {'within 2c':>10s}")
    for r in table:
        print(f"{r['model']:24s} {r['mae']:6.2f} {r['bias']:7.2f} {r['hit_rate']:9d}%")

    best = table[0]
    residuals = sorted(abs(x) for x in errs[best["model"]])
    q80 = residuals[int(0.80 * (len(residuals) - 1))]

    # ---- forecast ----------------------------------------------------------
    hist = values
    point = models(hist)[best["model"]]
    lo, hi = point - q80, point + q80
    next_print = last_date + timedelta(days=7)

    print("\n=== NEXT PRINT ===")
    print(f"for               {next_print}")
    print(f"model             {best['model']} (best of {len(table)} on {best['n']} scored prints)")
    print(f"point             {point:.1f} cents/litre")
    print(f"80% band          {lo:.1f} to {hi:.1f}")
    print(f"band width        {hi - lo:.1f} cents/litre")
    print(f"on a {TANK_LITRES} litre fill  the band is worth {((hi - lo) * TANK_LITRES / 100):.0f} dollars")

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = date.today().isoformat()
    ledger = {
        "issued": stamp,
        "series": "diesel/national",
        "target_date": next_print.isoformat(),
        "model": best["model"],
        "point": round(point, 1),
        "band_80": [round(lo, 1), round(hi, 1)],
        "backtest": table,
        "sample": {"prints": len(rows), "from": rows[0][0].isoformat(),
                   "to": last_date.isoformat(), "scored": best["n"]},
        "tolerance_cents": TOLERANCE,
    }
    path = os.path.join(OUT_DIR, f"diesel-{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=1)
    print(f"\nledger written    {path}")

    try:
        chart(rows, next_print, point, lo, hi, stamp)
        print(f"chart written     {CHART}")
    except Exception as e:  # a chart is nice to have, the numbers are the product
        print(f"chart skipped: {e}")


def chart(rows, next_print, point, lo, hi, stamp):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    dates = [d for d, _ in rows]
    vals = [v for _, v in rows]
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=150)
    ax.plot(dates, vals, color="#0f172a", linewidth=1.6)
    ax.fill_between([dates[-1], next_print], [vals[-1], lo], [vals[-1], hi],
                    color="#94a3b8", alpha=0.45)
    ax.plot([next_print], [point], "o", color="#0f172a", markersize=6)
    ax.vlines(next_print, lo, hi, color="#64748b", linewidth=2, alpha=0.75)
    ax.annotate(f"{point:.1f}", (next_print, point), textcoords="offset points",
                xytext=(8, 4), fontsize=10, color="#0f172a")
    ax.annotate(f"{lo:.1f} to {hi:.1f}", (next_print, lo), textcoords="offset points",
                xytext=(8, -14), fontsize=8, color="#475569")
    ax.set_xlim(right=next_print + timedelta(days=150))
    ax.axhline(statistics.median(vals), color="#cbd5e1", linewidth=0.9, linestyle=":")
    ax.annotate("10y median", (dates[0], statistics.median(vals)), fontsize=8,
                color="#64748b", textcoords="offset points", xytext=(2, 4))
    ax.set_title("National diesel, weekly print, and the next print with its 80% band",
                 fontsize=12, loc="left", color="#0f172a")
    ax.set_ylabel("cents per litre")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.7)
    fig.text(0.01, 0.01, f"Northern Mile Media. {stamp}. "
             f"Source: weekly retail diesel survey, national average.",
             fontsize=7, color="#64748b")
    fig.tight_layout()
    os.makedirs(os.path.dirname(CHART), exist_ok=True)
    fig.savefig(CHART, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
