#!/usr/bin/env python3
"""Build border wait time trends page.

Reads data/history/border.csv → computes statistics per crossing → writes:
  data/border_trends.json   (statistics for other scripts/API consumers)
  docs/border-trends/index.html (the rendered HTML page)

Uses gen_templates.py's fill() engine so pages share the exact same header/nav/footer/seo as every other NMM page.
Requires content/border-trends.md with at least 400 chars of human-written prose.
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
TMPL = os.path.join(ROOT, "templates")
CONTENT = os.path.join(ROOT, "content")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402

MIN_PROSE_CHARS = 400  # ~60 words; below this the page doesn't justify itself


def load_json(name):
    """Load a JSON file from the data directory by short name."""
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def load_border_csv():
    """Return list of dicts with keys: date, crossing_id, delay_minutes, observation_time."""
    path = os.path.join(DATA, "history", "border.csv")
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            rows.append({
                "date": row["date"],
                "crossing_id": row["crossing_id"],
                "delay_minutes": int(row["delay_minutes"]),
                "observation_time": row.get("observation_time", ""),
            })
    return rows


def percentile(values, p):
    """Linear-interpolation percentile."""
    if not values:
        return 0
    s = sorted(values)
    k = (len(s) - 1) * (p / 100)
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return round(s[f] * (c - k) + s[c] * (k - f), 1)


def analyze_crossing(rows, crossing_id):
    """Statistics for one crossing across all historical observations."""
    delays = [r["delay_minutes"] for r in rows if r["crossing_id"] == crossing_id]
    if not delays:
        return None

    days_covered = len(set(r["date"] for r in rows if r["crossing_id"] == crossing_id))
    observations = len(delays)

    # Hourly pattern (UTC)
    hourly = defaultdict(lambda: {"sum": 0, "count": 0})
    for r in rows:
        if r["crossing_id"] != crossing_id:
            continue
        obs = r.get("observation_time", "")
        try:
            dt = datetime.fromisoformat(obs)
            hour = dt.hour
            hourly[hour]["sum"] += r["delay_minutes"]
            hourly[hour]["count"] += 1
        except (ValueError, TypeError):
            pass

    hourly_avg = {}
    for h in range(24):
        cnt = hourly[h]["count"]
        avg = round(hourly[h]["sum"] / cnt) if cnt else None
        hourly_avg[str(h)] = {"avg": avg, "count": cnt}

    # Day-of-week pattern
    daily = defaultdict(lambda: {"sum": 0, "count": 0})
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for r in rows:
        if r["crossing_id"] != crossing_id:
            continue
        try:
            d = date.fromisoformat(r["date"])
            dow = str(d.weekday())
            daily[dow]["sum"] += r["delay_minutes"]
            daily[dow]["count"] += 1
        except (ValueError, KeyError):
            pass

    daily_avg = {}
    for d in range(7):
        cnt = daily[str(d)]["count"]
        avg = round(daily[str(d)]["sum"] / cnt) if cnt else None
        daily_avg[str(d)] = {"avg": avg, "count": cnt, "label": day_labels[d]}

    return {
        "id": crossing_id,
        "avg_delay": round(sum(delays) / len(delays)),
        "min_delay": min(delays),
        "max_delay": max(delays),
        "p50": percentile(delays, 50),
        "p75": percentile(delays, 75),
        "p90": percentile(delays, 90),
        "observations": observations,
        "days_covered": days_covered,
        "hourly": hourly_avg,
        "daily": daily_avg,
    }


def severity_class(avg):
    """Return CSS class based on average wait time severity."""
    if avg >= 45:
        return "alert"
    elif avg >= 20:
        return "notable"
    elif avg >= 5:
        return "mention"
    else:
        return "normal"


CROSSING_NAMES = {
    "coutts-sweetgrass": "Coutts–Sweetgrass",
    "emerson-pembina": "Emerson–Pembina",
    "fort-erie-buffalo": "Fort Erie–Buffalo",
    "lacolle-champlain": "Lacolle–Champlain",
    "lansdowne-alexandria": "Lansdowne–Alexandria",
    "pacific-blaine": "Pacific Highway",
    "queenston-lewiston": "Queenston–Lewiston",
    "sarnia-port-huron": "Blue Water Bridge",
    "windsor-detroit": "Ambassador Bridge",
}


def build_table_rows(trends):
    """Generate table rows for summary table."""
    rows_html = ""
    crossings_list = sorted(trends["crossings"].items(), key=lambda x: -x[1]["avg_delay"])
    for cid, stats in crossings_list:
        name = CROSSING_NAMES.get(cid, cid.replace("-", " ").title())
        avg = stats["avg_delay"]
        p75 = stats["p75"]
        p90 = stats["p90"]
        cls = severity_class(avg)
        rows_html += f'''      <tr class="{cls}">
        <td><strong>{name}</strong></td>
        <td>{avg} min</td>
        <td>{p75} min</td>
        <td>{p90} min</td>
        <td>{stats["observations"]} records</td>
        <td>{stats["days_covered"]} days</td>
      </tr>\n'''
    return rows_html


def load_prose():
    """Load human-written prose for the page. Must be >400 chars."""
    path = os.path.join(CONTENT, "border-trends.md")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No prose at {path}. Border trends pages require a writer paragraph.")
    with open(path) as f:
        prose = f.read().strip()
    body = re.sub(r"<!--.*?-->", "", prose, flags=re.DOTALL).strip()
    if len(body) < MIN_PROSE_CHARS:
        raise ValueError(f"Prose body is {len(body)} chars, minimum {MIN_PROSE_CHARS}. Too thin.")
    return prose

def main():
    print("=== Border Trends ===")
    rows = load_border_csv()
    if not rows:
        print("  No border history data found. Skipping.")
        return

    # Analyze each crossing
    crossings = defaultdict(list)
    for r in rows:
        crossings[r["crossing_id"]].append(r)

    trends = {"generated": datetime.now().isoformat(), "crossings": {}}
    total_days = set()
    total_observations = 0
    max_delay_by_crossing = {}

    for cid, crecs in crossings.items():
        stats = analyze_crossing(rows, cid)
        if stats:
            trends["crossings"][cid] = stats
            total_days.update(r["date"] for r in crecs)
            total_observations += stats["observations"]
            max_delay_by_crossing[cid] = stats["max_delay"]

    days_covered = len(total_days)
    crossings_count = len(trends["crossings"])

    # Load minimal data needed for template placeholders
    home_data = load_json("home.norm.json") if os.path.exists(os.path.join(DATA, "home.norm.json")) else {}
    updated_at = home_data.get("updated_at", datetime.now().strftime("%H:%M"))
    updated_iso = home_data.get("updated_iso", "")
    build_version = str(int(datetime.now().timestamp()))

    # Write JSON data file
    out_data = os.path.join(DATA, "border_trends.json")
    with open(out_data, "w") as f:
        json.dump(trends, f, indent=2)
    print(f"  data/border_trends.json written ({crossings_count} crossings, {total_observations} obs)")

    # Render HTML page
    template_path = os.path.join(TMPL, "border-trends.template.html")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template missing: {template_path}")

    with open(template_path) as f:
        template = f.read()

    prose = load_prose()

    table_rows = build_table_rows(trends)

    # Build hourly pattern mini-charts (simple text-based)
    hourly_charts_html = ""
    for cid, stats in sorted(trends["crossings"].items(), key=lambda x: -x[1]["avg_delay"])[:3]:
        name = CROSSING_NAMES.get(cid, cid.replace("-", " ").title())
        hourly = stats.get("hourly", {})
        chart_lines = []
        for h in range(0, 24, 4):
            info = hourly.get(str(h), {})
            avg = info.get("avg")
            count = info.get("count", 0)
            bar = "█" * min(avg, 20) if avg and avg > 0 else "░"
            label = f"{h:>2d}"
            chart_lines.append(f"<div class='hour-row'><span>{label}</span><span class='bar'>{bar}</span><span>{count} obs</span></div>")
        hourly_charts_html += f"""      <div class="viz-card">
        <h3 class="viz-title">{name} — hourly</h3>
        <p class="viz-sub">Average delay by hour · █ heavy ░ light</p>
        {''.join(chart_lines)}
      </div>
"""

    # Daily pattern charts
    daily_charts_html = ""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for cid, stats in sorted(trends["crossings"].items(), key=lambda x: -x[1]["avg_delay"])[:3]:
        name = CROSSING_NAMES.get(cid, cid.replace("-", " ").title())
        daily = stats.get("daily", {})
        chart_lines = []
        for d in range(7):
            info = daily.get(str(d), {})
            avg = info.get("avg")
            count = info.get("count", 0)
            bar = "█" * min(avg, 20) if avg and avg > 0 else "░"
            label = day_names[d][:3]
            chart_lines.append(f"<div class='day-row'><span>{label}</span><span class='bar'>{bar}</span><span>{count} obs</span></div>")
        daily_charts_html += f"""      <div class="viz-card">
        <h3 class="viz-title">{name} — day of week</h3>
        <p class="viz-sub">Average delay by weekday · █ heavy ░ light</p>
        {''.join(chart_lines)}
      </div>
"""

    # Top alerts (highest P90)
    top_alerts = sorted(trends["crossings"].items(), key=lambda x: x[1]["p90"], reverse=True)[:5]
    alert_lines = []
    for cid, stats in top_alerts:
        name = CROSSING_NAMES.get(cid, cid.replace("-", " ").title())
        p90 = stats["p90"]
        cls = severity_class(p90)
        alert_lines.append(f'<div class="r {cls}"><span class="k">{name}</span><span class="v">P90: {p90} min</span></div>')

    data = {
        "crossings_count": crossings_count,
        "days_covered": days_covered,
        "observations_total": total_observations,
        "updated_at": updated_at,
        "updated_iso": updated_iso,
        "build_version": build_version,
        "table_rows": table_rows,
        "prose": prose,
        "top_alerts": "\n".join(alert_lines),
        "hourly_charts": hourly_charts_html,
        "daily_charts": daily_charts_html,
        # Cross-reference data for other scripts
        "max_delays": max_delay_by_crossing,
    }

    html = fill(template, data)

    leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:") if t in html]
    if leftover:
        raise ValueError(f"Unresolved template markup: {leftover}")

    out_dir = os.path.join(DOCS, "border-trends")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(html)
    print(f"  docs/border-trends/index.html written ({os.path.getsize(out_path)} bytes)")


if __name__ == "__main__":
    main()
