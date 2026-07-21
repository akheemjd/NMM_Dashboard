#!/usr/bin/env python3
"""Normalize collector data into template-fillable format (v2 — nested by module).
Outputs /data/{home,fuel,fx,border,incidents,theft,market,news}.json
"""
import json, os
from datetime import datetime

DATA = os.path.expanduser("~/northern-mile-dashboard/data")

def load(name):
    p = os.path.join(DATA, name + ".json" if not name.endswith(".json") else name)
    return json.load(open(p)) if os.path.exists(p) else {}

def write(name, data):
    with open(os.path.join(DATA, name + ".json"), "w") as f:
        json.dump(data, f, indent=2)

def now_fmt(): return datetime.utcnow().strftime("%Y-%m-%d %H:%M")
def fmt_ts(ts):
    if not ts: return "—"
    return ts[:16].replace("T"," ")

def change_str(val):
    """Format change: '▲ 0.5' or '▼ 0.4' with class"""
    try: v = float(val)
    except: return "—", ""
    if v > 0: return f"▲ {abs(v):.1f}", "up"
    elif v < 0: return f"▼ {abs(v):.1f}", "down"
    return "unchanged", "flat"

# Load raw data
raw_fuel = load("fuel.json")
raw_ex = load("exchange.json")
raw_border = load("border.json")
raw_inc = load("incidents.json")
raw_theft = load("theft.json")
raw_market = load("market.json")
raw_news = load("news.json")
raw_dist = load("distances.json")

ts = now_fmt()
provs = raw_fuel.get("provinces", {})
fuel_nat = raw_fuel.get("diesel_national_avg", 171.9)

# ===== FUEL DATA =====
fuel_top = []
for c in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]:
    p = provs.get(c, {}).get("diesel", 0)
    chg = 0  # placeholder — real change from history
    chg_str, chg_cls = change_str(chg)
    fuel_top.append({
        "code": c,
        "name": {"BC":"British Columbia","AB":"Alberta","SK":"Saskatchewan","MB":"Manitoba","ON":"Ontario","QC":"Quebec","NB":"New Brunswick","NS":"Nova Scotia","PE":"PEI","NL":"Newfoundland"}[c],
        "price": f"{p:.1f}",
        "change": chg_str,
        "change_class": chg_cls,
    })

d_vals = [provs.get(c,{}).get("diesel",0) for c in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]]

fuel_data = {
    "national_diesel": f"{fuel_nat:.1f}",
    "change_7d": "—",  # needs history
    "low_code": "AB", "low": f"{min(d_vals):.1f}",
    "high_code": "NL", "high": f"{max(d_vals):.1f}",
    "spread": f"{max(d_vals)-min(d_vals):.1f}",
    "fuel_top": fuel_top,
    "updated_at": ts,
}

# ===== BORDER DATA =====
crossings = raw_border.get("crossings", [])
heavy = sum(1 for c in crossings if c.get("delay_minutes", 0) > 15)
moderate = sum(1 for c in crossings if 1 <= c.get("delay_minutes", 0) <= 15)
closed = sum(1 for c in crossings if c.get("delay_minutes", 0) < 0)
gauge_class = "warn" if heavy > 0 else "ok"

border_rows = []
for c in crossings:
    d = c.get("delay_minutes", 0)
    delay_cls = "wait" if d > 15 else "flow" if d > 0 else "ok"
    border_rows.append({
        "name": c.get("name",""),
        "route": c.get("route",""),
        "delay": f"{d} min" if d > 0 else "No delay",
        "delay_class": delay_cls,
        "fast": "FAST" if c.get("fast_lanes") else "",
    })

border_data = {
    "gauge_class": gauge_class,
    "heavy_count": heavy,
    "moderate_count": moderate,
    "closed_count": closed,
    "crossings": crossings,
    "border_rows": border_rows,
    "updated_at": ts,
}

# ===== HOME =====
home = {
    "updated_at": ts,
    "border": border_data,
    "fuel": fuel_data,
}

write("home", home)
write("fuel", {"fuel": fuel_data, "updated_at": ts})
write("border", {"border": border_data, "updated_at": ts})
write("fx", {"updated_at": ts})
write("incidents", {"incidents": raw_inc.get("incidents", []), "updated_at": ts})
write("theft", {"theft": raw_theft.get("incidents", []), "hotspots": raw_theft.get("hotspots", []), "updated_at": ts})
write("market", {"updated_at": ts})
write("news", {"news": raw_news.get("headlines", []), "updated_at": ts})

print(f"Normalized at {ts}: home + 7 page stubs")
