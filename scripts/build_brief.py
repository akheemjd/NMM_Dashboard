#!/usr/bin/env python3
"""Build the NMM data brief.

The data brief is the single source of truth for every number the content
writer (the `writer` Hermes profile) uses. It contains ONLY numbers, bands,
and source labels — no prose, no headlines, no interpretation. The writer
turns this into copy; it never computes a figure that isn't here.
"""
import json
import os
import re
from datetime import datetime, date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def excise_status(print_date_str):
    """Federal diesel excise (4c/L) suspended Apr 20 - Sep 7 2026. Derived from print date."""
    suspend_start = date(2026, 4, 20)
    suspend_end = date(2026, 9, 7)
    try:
        pd = datetime.strptime(print_date_str, "%a, %d %b %Y").date()
    except (ValueError, TypeError):
        return "unknown"
    if suspend_start <= pd <= suspend_end:
        return "suspended (4c/L federal excise - resumes Sep 8, 2026)"
    return "active (4c/L federal excise applied)"


def pending_corrections():
    """Read content/corrections.md; return pending entries as field dicts."""
    path = os.path.join(ROOT, "content", "corrections.md")
    if not os.path.exists(path):
        return []
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"\n## ", text)[1:]
    out = []
    for b in blocks:
        if "status: pending" not in b.lower():
            continue
        f = {}
        for line in b.splitlines():
            m = re.match(r"(what|before|after|scope):\s*(.*)", line.strip(), re.I)
            if m:
                f[m.group(1).lower()] = m.group(2).strip()
        out.append(f)
    return out


def main():
    fuel_norm = load("fuel.norm.json")
    fuel = fuel_norm.get("fuel", {})
    provinces = fuel_norm.get("provinces") or []
    fx = load("fx.norm.json").get("fx", {})
    border = load("border.norm.json")
    market = load("market.norm.json")
    incidents = load("incidents.norm.json")
    theft = load("theft.json")

    # --- incidents live in an embedded JSON string ---
    inc_raw = incidents.get("incidents_json", "[]")
    inc_list = json.loads(inc_raw) if isinstance(inc_raw, str) else (inc_raw or [])
    sev = {}
    corridors = {}
    for it in inc_list:
        s = it.get("severity_class") or "mod"
        sev[s] = sev.get(s, 0) + 1
        c = (it.get("road") or "Other").strip()
        corridors[c] = corridors.get(c, 0) + 1
    top_corridors = sorted(corridors.items(), key=lambda kv: -kv[1])[:6]

    rw = incidents.get("coming_roadwork") or []

    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = []
    a = lines.append
    a(f"# NMM Data Brief - {today}")
    a("")
    a("Numbers and bands only. No prose, no interpretation.")
    a("The writer quotes exactly these figures - never computes or invents others.")
    a("Every figure carries its source label.")
    a("")
    corr = pending_corrections()
    if corr:
        a("## Pending corrections - correct these in the next issue")
        for c in corr:
            a(f"- We published '{c.get('before', '?')}'; correct is '{c.get('after', '?')}'. {c.get('what', '')} [{c.get('scope', '')}]")
        a("Include a short dated 'Correction:' note in the next issue for each. Do not silently drop them.")
        a("")
    a("## Diesel - Natural Resources Canada weekly diesel survey")
    a(f"- Print date: {fuel.get('print_date', 'n/a')}")
    a(f"- National average (NMDI): {fuel.get('national_diesel', 'n/a')} c/L")
    a(f"- 7-day change: {fuel.get('change_7d', 'n/a')} c/L  ->  band: {fuel.get('change_7d_band', 'n/a')}")
    a(f"- 30-day change: {fuel.get('change_30d', 'n/a')} c/L")
    a(f"- Cheapest: {fuel.get('low_code', 'n/a')} {fuel.get('low', 'n/a')} c/L")
    a(f"- Dearest: {fuel.get('high_code', 'n/a')} {fuel.get('high', 'n/a')} c/L")
    a(f"- Spread: {fuel.get('spread', 'n/a')} c/L")
    a(f"- Excise: {excise_status(fuel.get('print_date'))}")
    a("- Provinces (code / name / price c/L / 7d change / vs national):")
    for p in provinces:
        a(f"  - {p.get('code')} {p.get('name')}  {p.get('price')}  {p.get('change')}  {p.get('vs_national')}")
    a("")
    a("## Foreign exchange - Bank of Canada Valet API")
    a(f"- USD/CAD: {fx.get('usd_cad', 'n/a')}  ({fx.get('direction', 'n/a')})")
    a(f"- Today: {fx.get('change', 'n/a')}  ({fx.get('band_pct', 'n/a')})  ->  band: {fx.get('band', 'n/a')}")
    a(f"- 7-day: {fx.get('change_7d', 'n/a')}  ({fx.get('change_7d_pct', 'n/a')})")
    a(f"- 30-day: {fx.get('change_30d', 'n/a')}  ({fx.get('change_30d_pct', 'n/a')})")
    a(f"- 1-year: {fx.get('change_1y', 'n/a')}  ({fx.get('change_1y_pct', 'n/a')})")
    a(f"- 52-week high: {fx.get('high_52w', 'n/a')} ({fx.get('high_52w_date', 'n/a')})")
    a(f"- 52-week low: {fx.get('low_52w', 'n/a')} ({fx.get('low_52w_date', 'n/a')})")
    a(f"- Position in 52-week range: {fx.get('range_pct', 'n/a')}")
    a(f"- 30-day average: {fx.get('avg_30d', 'n/a')}")
    a(f"- US$100 -> C${fx.get('usd_100', 'n/a')}  |  US$1,000 -> C${fx.get('usd_1000', 'n/a')}  |  C$1,000 -> US${fx.get('cad_1000', 'n/a')}")
    a("")
    a("## Border wait times - CBSA (Canada Border Services Agency)")
    b = border.get("border", {})
    a(f"- Status: {b.get('gauge_class', 'n/a')}  ({b.get('heavy_count', 0)} heavy, {b.get('moderate_count', 0)} moderate, {b.get('closed_count', 0)} closed)")
    a(f"- Longest wait: {b.get('max_name', 'n/a')} - {b.get('max_wait', 'n/a')}")
    a(f"- Shortest: {b.get('min_name', 'n/a')} - {b.get('min_wait', 'n/a')}")
    a("- Crossings (name / wait / status):")
    for c in (border.get("crossings") or [])[:9]:
        a(f"  - {c.get('name')}  {c.get('wait')}  {c.get('status_label')}")
    a("")
    a("## Market pulse")
    a(f"- Direction summary: {market.get('direction_summary', 'n/a')}")
    for m in (market.get("market") or []):
        a(f"- {m.get('name')}: {m.get('value')}  ({m.get('note', '')})")
    a(f"- Fuel as % of operating cost: {market.get('fuel_pct_of_ops', 'n/a')}")
    a("")
    a("## Road incidents")
    a(f"- Incidents listed: {len(inc_list)}")
    a(f"- Scheduled roadwork: {len(rw)}")
    a("- By corridor: " + (", ".join(f"{c} {n}" for c, n in top_corridors) if top_corridors else "none"))
    a("- By severity: " + (", ".join(f"{k} {v}" for k, v in sorted(sev.items())) if sev else "none"))
    a("")
    a("## Cargo theft - NMM incident tracker")
    ti = theft.get("incidents") or []
    a(f"- Recent incidents (last 12 months): {len(ti)}")
    for f in (theft.get("feeds") or []):
        a(f"- Feed {f.get('name')}: status {f.get('status')}, {f.get('items_seen')} items seen, {f.get('matched')} matched")
    a("")
    a("## Materiality bands (reference)")
    a("- Diesel: noise < 1.0c  |  notable 1.0-2.9c  |  material 3.0-5.9c  |  alert >= 6.0c")
    a("- FX: noise < 0.2%  |  notable 0.2-0.49%  |  material 0.5-0.99%  |  alert >= 1.0%")

    out = "\n".join(lines) + "\n"

    os.makedirs(DATA, exist_ok=True)
    out_path = os.path.join(DATA, f"brief-{today}.md")
    with open(out_path, "w") as f:
        f.write(out)
    print(f"Wrote {out_path} ({len(out)} chars)")


if __name__ == "__main__":
    main()
