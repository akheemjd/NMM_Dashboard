#!/usr/bin/env python3
"""Normalize collector data into exact template-fillable format (v3 — matches kit data shapes)."""
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

raw_fuel = load("fuel.json")
raw_ex = load("exchange.json")
raw_border = load("border.json")
raw_inc = load("incidents.json")
raw_theft = load("theft.json")
raw_market = load("market.json")
raw_news = load("news.json")

ts = now_fmt()
provs = raw_fuel.get("provinces", {})
fuel_nat = raw_fuel.get("diesel_national_avg", 171.9)

# ===== FUEL =====
d_vals = [(c, provs.get(c,{}).get("diesel",0)) for c in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]]
d_sorted = sorted(d_vals, key=lambda x: x[1])
fuel_top = []
for code, price in d_sorted[:6]:
    fuel_top.append({
        "code": code,
        "name": {"BC":"British Columbia","AB":"Alberta","SK":"Saskatchewan","MB":"Manitoba","ON":"Ontario","QC":"Quebec","NB":"New Brunswick","NS":"Nova Scotia","PE":"PEI","NL":"Newfoundland"}[code],
        "price": f"{price:.1f}",
        "change": "—",
        "change_class": "flat",
    })

fuel = {
    "national_diesel": f"{fuel_nat:.1f}",
    "change_7d": "—",
    "low_code": d_sorted[0][0], "low": f"{d_sorted[0][1]:.1f}",
    "high_code": d_sorted[-1][0], "high": f"{d_sorted[-1][1]:.1f}",
    "spread": f"{d_sorted[-1][1]-d_sorted[0][1]:.1f}",
    "fuel_top": fuel_top,
}

# ===== BORDER =====
crossings = raw_border.get("crossings", [])
heavy = sum(1 for c in crossings if c.get("delay_minutes", 0) > 15)
moderate = sum(1 for c in crossings if 1 <= c.get("delay_minutes", 0) <= 15)
closed = 0
gauge_class = "warn" if heavy > 0 else "ok"

# Sort crossings by delay
cross_sorted = sorted(crossings, key=lambda c: c.get("delay_minutes", 0), reverse=True)
min_cross = cross_sorted[-1] if cross_sorted else {}
max_cross = cross_sorted[0] if cross_sorted else {}
min_d = max(min_cross.get("delay_minutes", 0), 0)
max_d = max(max_cross.get("delay_minutes", 0), 0)

border = {
    "gauge_class": gauge_class,
    "heavy_count": heavy,
    "moderate_count": moderate,
    "closed_count": closed,
    "min_name": min_cross.get("name","—"),
    "min_wait": f"{min_d} min" if min_d > 0 else "No delay",
    "max_name": max_cross.get("name","—"),
    "max_wait": f"{max_d} min" if max_d > 0 else "No delay",
}

# Top-level border_rows for home template
border_rows = []
for c in crossings[:8]:
    d = c.get("delay_minutes", 0)
    if d > 15: cls = "heavy"
    elif d > 0: cls = "mod"
    else: cls = "ok"
    wait = f"{d} min" if d > 0 else "No delay"
    border_rows.append({
        "name": c.get("name",""),
        "sub": f"{c.get('route','')} · {c.get('highway','')}" + (" · FAST" if c.get("fast_lanes") else ""),
        "wait": wait,
        "status_label": "Heavy" if d>15 else "Moderate" if d>0 else "Flowing",
        "status_class": cls,
        "url": "/border-wait-times/",
    })

# ===== FX =====
fx_rate = raw_ex.get("current") or raw_ex.get("close", 1.32)
fx_chg = raw_ex.get("change", 0)
try: fx_chg = float(fx_chg)
except: fx_chg = 0
direction = "weaker CAD" if fx_chg > 0 else "stronger CAD" if fx_chg < 0 else ""

fx = {
    "usd_cad": f"{fx_rate:.4f}",
    "direction": direction,
    "change": f"{'+' if fx_chg>0 else ''}{fx_chg:.4f}",
}

# ===== INCIDENTS =====
incidents_raw = raw_inc.get("incidents", [])
incidents_list = []
for i in incidents_raw[:20]:
    sev = i.get("severity","")
    cls = "heavy" if sev == "closed" else "mod" if sev == "heavy" else "ok"
    incidents_list.append({
        "road": i.get("highway","") or i.get("description","")[:40],
        "what": i.get("description","")[:80],
        "severity_label": sev or "Moderate",
        "severity_class": cls,
        "url": "/road-incidents/",
    })

incidents = {
    "none": len(incidents_list) == 0,
    "active_count": len(incidents_list),
    "gauge_class": "good" if len(incidents_list) == 0 else "warn",
    "status_line": "monitored corridors clear" if len(incidents_list) == 0 else f"{len(incidents_list)} active",
    "incidents": incidents_list,
}

# ===== MARKET =====
market = []
mk = raw_market
for name, note, cls in [
    ("Monthly GDP", "More output = more freight", "down"),
    ("Diesel vs baseline", "Fuel is 25-35% of operating cost", "up"),
]:
    val = mk.get("gdp","—") if "GDP" in name else mk.get("diesel_vs_baseline","—")
    market.append({"name": name, "note": note, "value": str(val), "value_class": cls})

# ===== THEFT =====
theft = []
for t in raw_theft.get("incidents", [])[:8]:
    theft.append({
        "title": t.get("title", t.get("description",""))[:60],
        "value": f"${t.get('value','0')}" if not str(t.get('value','')).startswith('$') else str(t.get('value','0')),
        "meta": f"{t.get('date','')} · {t.get('location','')}" if t.get('date') else str(t.get('location','')),
        "url": "/cargo-theft/",
    })

# ===== NEWS =====
news = []
for n in raw_news.get("headlines", [])[:10]:
    news.append({
        "category": n.get("source","Industry"),
        "headline": n.get("title","")[:120],
        "url": n.get("url","#"),
    })

# ===== ASSEMBLE HOME =====
home = {
    "updated_at": ts,
    "border": border,
    "fuel": fuel,
    "fx": fx,
    "incidents": incidents,
    "border_rows": border_rows,
    "market": market,
    "theft": theft,
    "news": news,
}

write("home.norm", home)
write("fuel.norm", {"fuel": fuel, "updated_at": ts})
write("border.norm", {"border": border, "border_rows": border_rows, "updated_at": ts, "captured_at": ts})
write("fx.norm", {"fx": fx, "updated_at": ts})
write("incidents.norm", {"incidents": incidents, "updated_at": ts})
write("theft.norm", {"theft": theft, "updated_at": ts})
write("market.norm", {"market": market, "updated_at": ts})
write("news.norm", {"news": news, "updated_at": ts})

print(f"Normalized at {ts}: home ({len(home)} keys) + 7 pages")
