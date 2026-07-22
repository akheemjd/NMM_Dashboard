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
raw_dist = load("distances.json")

ts = now_fmt()
provs = raw_fuel.get("provinces", {})
fuel_nat = raw_fuel.get("diesel_national_avg", 171.9)

# Calc data (needed by home page)
calc_cities = raw_dist.get("cities", [])
calc_distances = raw_dist.get("distances", {})

# ===== FUEL =====
d_vals = [(c, provs.get(c,{}).get("diesel",0)) for c in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]]
d_sorted = sorted(d_vals, key=lambda x: x[1])
fuel_top = []
provinces_data = []
names = {"BC":"British Columbia","AB":"Alberta","SK":"Saskatchewan","MB":"Manitoba","ON":"Ontario","QC":"Quebec","NB":"New Brunswick","NS":"Nova Scotia","PE":"PEI","NL":"Newfoundland"}
for i, (code, price) in enumerate(d_sorted):
    diff = price - fuel_nat
    vs_val = f"{diff:+.1f}" if diff else "0.0"
    vs_cls = "lo" if diff < 0 else "hi" if diff > 0 else ""
    row_cls = "lo" if i == 0 else "hi" if i == len(d_sorted)-1 else ""
    provinces_data.append({
        "code": code,
        "name": names[code],
        "price": f"{price:.1f}",
        "change": "—",
        "change_class": "flat",
        "vs_national": vs_val,
        "vs_class": vs_cls,
        "rowclass": row_cls,
    })
fuel_top = provinces_data[:6]

prices = {c: p for c, p in d_vals}  # home page shows top 6

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

# Crossing rows for border page (crossings loop) + home page
border_rows = []
crossings_for_page = []
for c in crossings[:12]:
    d = c.get("delay_minutes", 0)
    if d > 15: cls = "heavy"
    elif d > 0: cls = "mod"
    else: cls = "ok"
    wait = f"{d} min" if d > 0 else "No delay"
    wait_num = str(d) if d > 0 else "0"
    ts = c.get("live_updated", "") or c.get("updated", "")
    if ts and len(ts) >= 16:
        ts = ts[:16].replace("T"," ")
    elif not ts:
        ts = "recent"
    
    item = {
        "name": c.get("name",""),
        "sub": f"{c.get('route','')} · {c.get('highway','')}" + (" · FAST" if c.get("fast_lanes") else ""),
        "wait": wait,
        "status_label": "Heavy" if d>15 else "Moderate" if d>0 else "Flowing",
        "status_class": cls,
        "url": "/border-wait-times/",
        "captured_at": ts,
    }
    border_rows.append(item)
    crossings_for_page.append(item)

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
for i in incidents_raw[:2]:
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
mk_indicators = raw_market.get("indicators", [])
dir_summary = raw_market.get("direction_summary", "")
for ind in mk_indicators[:6]:
    direction = ind.get("direction", "flat")
    cls = "up" if direction == "up" else "down" if direction == "down" else "flat"
    # Build a useful one-line note
    detail = ind.get("detail", "")
    note = detail if detail else ind.get("what_it_means", "")[:60]
    market.append({
        "name": ind.get("label", ind.get("name", "")),
        "note": note,
        "value": str(ind.get("value", "—")),
        "value_class": cls,
    })

# ===== THEFT =====
theft = []
for t in raw_theft.get("incidents", [])[:8]:
    val = t.get("value","0")
    if isinstance(val, (int,float)) and val >= 1000:
        val_str = f"${val/1000:,.0f}K"
    elif isinstance(val, (int,float)):
        val_str = f"${val:,}"
    else:
        val_str = f"${val}" if not str(val).startswith("$") else str(val)
    
    # Try to split title into commodity context
    title = t.get("title", t.get("description",""))[:60]
    location = t.get("location","")
    prevention = "Secure overnight parking · GPS tracking"  # default
    commodity = t.get("commodity", t.get("type", "Mixed freight"))
    
    theft.append({
        "title": title,
        "value": val_str,
        "date": t.get("date", "Recent"),
        "location": location,
        "commodity": commodity,
        "prevention": prevention,
        "url": "/cargo-theft/",
    })

# Hotspots from theft data
hotspots = []
risk_labels = {"high": "High risk", "medium": "Moderate", "low": "Low"}
for h in raw_theft.get("hotspots", []):
    risk = h.get("risk", "medium")
    hotspots.append({
        "area": h.get("city", "GTA"),
        "count": risk_labels.get(risk, risk.title()),
        "value": h.get("note", "—")[:60],
    })
if not hotspots:
    hotspots = [
        {"area": "Greater Toronto Area", "count": "High risk", "value": "Highest cargo theft volume in Canada"},
        {"area": "Montreal", "count": "High risk", "value": "Second highest. Port and Saint-Laurent zones"},
        {"area": "Calgary/Edmonton", "count": "Moderate", "value": "Nisku, Balzac, and Acheson parks"},
        {"area": "Vancouver", "count": "Moderate", "value": "Port area. Delta and Surrey"},
    ]

# ===== NEWS =====
news = []
for n in raw_news.get("headlines", [])[:10]:
    news.append({
        "category": n.get("source","Industry"),
        "headline": n.get("title","")[:120],
        "url": n.get("link", n.get("url","#")),
    })

news_home = news[:2]  # home shows 2, news page shows all


# ===== SPONSOR PLACEHOLDERS =====
sponsor_page = None
sponsor_border = None

# Build theft JSON early (needed by home page too)
theft_json = []
for t in raw_theft.get("incidents", [])[:30]:
    val = t.get("value",0)
    theft_json.append({
        "title": t.get("title", t.get("description",""))[:60],
        "location": str(t.get("location","")),
        "value": "${:,}".format(val) if isinstance(val, (int,float)) else str(val),
        "lat": t.get("lat", 0),
        "lng": t.get("lng", 0),
        "date": str(t.get("date",""))[:10],
        "method": str(t.get("method",""))[:80],
        "prevention": str(t.get("prevention",""))[:100],
        "source_url": t.get("source_url", ""),
        "business": str(t.get("business",""))[:80],
    })


# ===== ASSEMBLE HOME =====
home = {
    "updated_at": ts,
    "border": border,
    "fuel": fuel,
    "provinces": provinces_data,
    "fx": fx,
    "incidents": incidents,
    "border_rows": border_rows,
    "market": market,
    "theft": theft,
    "news": news_home,
    "theft_home_json": json.dumps(theft_json),
    "calc_cities": json.dumps(calc_cities),
    "calc_distances": json.dumps(calc_distances),
    "sponsor_page": sponsor_page,
    "sponsor_border": sponsor_border,
}

write("home.norm", home)
write("fuel.norm", {"fuel": fuel, "provinces": provinces_data, "updated_at": ts})
write("border.norm", {"border": border, "border_rows": border_rows, "crossings": crossings_for_page, "updated_at": ts, "captured_at": ts})
write("fx.norm", {"fx": fx, "updated_at": ts})
# Build raw incidents JSON array for the map
inc_json = []
for i in raw_inc.get("incidents", [])[:50]:
    sev = i.get("severity", "").lower()
    if sev in ("closed", "closure"): sc = "closed"
    elif sev in ("heavy", "major", "high"): sc = "heavy"
    else: sc = "mod"
    # Format timestamps
    start_ts = i.get("start", 0)
    end_ts = i.get("end", 0)
    if start_ts and isinstance(start_ts, (int,float)) and start_ts > 1000000000:
        from datetime import datetime
        start_str = datetime.utcfromtimestamp(start_ts).strftime("%b %d %H:%M")
        end_str = datetime.utcfromtimestamp(end_ts).strftime("%b %d %H:%M") if (end_ts and end_ts > 1000000000) else ""
    else:
        start_str = str(start_ts) if start_ts else ""
        end_str = str(end_ts) if end_ts else ""
    
    inc_json.append({
        "lat": i.get("lat", 0),
        "lng": i.get("lng", 0),
        "road": i.get("highway", ""),
        "direction": i.get("direction", ""),
        "severity_class": sc,
        "severity_label": i.get("severity", "Moderate").title(),
        "what": i.get("description", "")[:80],
        "event_type": i.get("event_type", "").replace("accidentsandincidents","Collision").replace("roadwork","Roadwork").title(),
        "lanes": i.get("lanes", ""),
        "closed": i.get("closure", False),
        "province": i.get("province", ""),
        "clearance": start_str,
        "end_time": end_str,
        "detour": i.get("detour", ""),
        "source_url": "",
    })

write("incidents.norm", {
    "incidents": incidents,
    "incidents_json": json.dumps(inc_json),
    "updated_at": ts,
})
write("theft.norm", {"theft": theft, "hotspots": hotspots, "theft_json": json.dumps(theft_json), "updated_at": ts})
# Direction summary for market page
dir_summary = raw_market.get("direction_summary", "")
rates = raw_market.get("rates_snapshot", {})

write("market.norm", {
    "market": market,
    "direction_summary": dir_summary,
    "fuel_pct_of_ops": rates.get("fuel_pct_of_ops", "25-35%"),
    "current_diesel": rates.get("current_diesel", "—"),
    "usd_cad": rates.get("usd_cad", "—"),
    "updated_at": ts,
})
write("news.norm", {"news": news, "updated_at": ts})


# ===== BORDER FUEL (US states) =====
us_states = {
    "WA": {"name": "Washington", "usd_gal": 3.89},
    "NY": {"name": "New York", "usd_gal": 3.95},
    "MI": {"name": "Michigan", "usd_gal": 3.82},
    "MT": {"name": "Montana", "usd_gal": 3.75},
    "ND": {"name": "North Dakota", "usd_gal": 3.72},
    "ME": {"name": "Maine", "usd_gal": 3.98},
}
border_pairs = [
    ("BC", "WA"), ("AB", "MT"), ("SK", "MT"),
    ("MB", "ND"), ("ON", "MI"), ("ON", "NY"),
    ("QC", "NY"), ("NB", "ME"),
]
border_fuel = []
for prov_code, state_code in border_pairs:
    if prov_code not in prices or state_code not in us_states:
        continue
    prov_price = prices[prov_code]
    state = us_states[state_code]
    usd_gal = state["usd_gal"]
    cad_litre = round(usd_gal * fx_rate / 3.785, 1)
    diff = round(cad_litre - prov_price, 1)
    verdict = f"Save {abs(diff):.1f}c/L" if diff < 0 else f"+{diff:.1f}c/L more"
    border_fuel.append({
        "prov_code": prov_code,
        "state_code": state_code,
        "prov_name": names.get(prov_code, prov_code),
        "prov_price": f"{prov_price:.1f}",
        "state_name": state["name"],
        "state_cad": f"{cad_litre:.1f}",
        "state_usd": f"{usd_gal:.2f}",
        "verdict": verdict,
    })

# fuel.norm written at end with tax+ifta


# ===== TAX BREAKDOWN (approximate) =====
tax = []
# Approximate tax breakdown per province (base + carbon + fuel_tax + sales = pump)
prov_tax_approx = {
    "BC":  (72, 18, 15, 9),
    "AB":  (72, 14, 9,  0),
    "SK":  (72, 14, 10, 6),
    "MB":  (72, 14, 11, 7),
    "ON":  (72, 14, 10, 8),
    "QC":  (72, 14, 14, 10),
    "NB":  (72, 14, 12, 10),
    "NS":  (72, 14, 12, 10),
    "PE":  (72, 14, 12, 10),
    "NL":  (72, 14, 13, 10),
}
for code in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]:
    if code not in prices or code not in prov_tax_approx:
        continue
    base, carbon, fuel_tax, sales = prov_tax_approx[code]
    pump = prices[code]
    tax.append({
        "name": names[code],
        "base": str(base),
        "carbon": str(carbon),
        "fuel_tax": str(fuel_tax),
        "sales": str(sales),
        "pump": f"{pump:.1f}",
    })

# ===== IFTA REFERENCE =====
ifta = []
for code in ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]:
    if code not in prices or code not in prov_tax_approx:
        continue
    base, carbon, fuel_tax, sales = prov_tax_approx[code]
    pump = prices[code]
    tax_portion = carbon + fuel_tax + sales
    per_100l = round(tax_portion * 100 / 100, 1)
    ifta.append({
        "name": names[code],
        "pump": f"{pump:.1f}",
        "tax_portion": f"{tax_portion}",
        "per_100l": f"${per_100l:.2f}",
    })

write("fuel.norm", {"fuel": fuel, "fx": fx, "provinces": provinces_data, "border_fuel": border_fuel, "tax": tax, "ifta": ifta, "updated_at": ts})

print(f"Normalized at {ts}: home ({len(home)} keys) + 7 pages")
