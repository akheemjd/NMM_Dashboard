#!/usr/bin/env python3
"""Normalize collector data into exact template-fillable format (v3 — matches kit data shapes)."""
import json, os, time
from datetime import datetime
from history import snapshot, delta, average, span_days

def clip(text, limit=110):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "\u2026"

DATA = os.path.expanduser("~/northern-mile-dashboard/data")

# ── Materiality band classification ──
import yaml
_thresh_path = os.path.join(os.path.dirname(DATA), "config", "thresholds.yaml")
with open(_thresh_path) as tf:
    thresh = yaml.safe_load(tf)
if not thresh or "verbs" not in thresh:
    raise ValueError(f"thresholds.yaml at {_thresh_path} loaded empty or malformed")
print(f"  thresholds loaded: {len(thresh)} series")

def classify_band(change, series, thresh):
    """Classify a data point into noise/notable/material/alert band."""
    if not thresh or series not in thresh:
        return "notable"
    t = thresh[series]
    abs_change = abs(change)
    if abs_change >= t.get("alert_floor", 99):
        return "alert"
    if abs_change >= t.get("lead_floor", 99):
        return "material"
    if abs_change >= t.get("mention_floor", 99):
        return "notable"
    return "noise"

def get_verb(band, direction, thresh):
    """Return the appropriate verb for a given band and direction."""
    if not thresh or "verbs" not in thresh:
        return "changed"
    dir_key = "down" if direction < 0 else "up" if direction > 0 else "flat"
    verbs = thresh["verbs"].get(band, ["held"])
    if dir_key == "flat":
        return "held"
    # Simple heuristic — take the first directional verb
    for v in verbs:
        if ("up" in v and direction > 0) or ("down" in v and direction < 0):
            return v
    return verbs[0] if verbs else "changed"


def load(name):
    p = os.path.join(DATA, name + ".json" if not name.endswith(".json") else name)
    return json.load(open(p)) if os.path.exists(p) else {}

def write(name, data):
    with open(os.path.join(DATA, name + ".json"), "w") as f:
        json.dump(data, f, indent=2)

from datetime import timezone

def now_fmt():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

raw_fuel = load("fuel.json")
raw_ex = load("exchange.json")
raw_border = load("border.json")
raw_inc = load("incidents.json")
raw_theft = load("theft.json")
raw_market = load("market.json")
raw_news = load("news.json")
raw_dist = load("distances.json")

ts = now_fmt()
ts_iso = now_iso()
build_version = str(int(time.time()))  # cache-busting, fresh each build
provs = raw_fuel.get("provinces", {})
fuel_nat = raw_fuel.get("diesel_national_avg")
if fuel_nat is None:
    raise ValueError("fuel.json has no diesel_national_avg — refusing to build")

from datetime import datetime as _dt, timezone as _tz

MAX_STALENESS_DAYS = {"fuel": 10}

_print_date = raw_fuel.get("print_date")
_pd = None
if _print_date:
    try:
        _pd = _dt.strptime(_print_date, "%a, %d %b %Y").date()
        _age = (_dt.now(_tz.utc).date() - _pd).days
        if _age > MAX_STALENESS_DAYS["fuel"]:
            raise ValueError(
                f"fuel.json print_date {_print_date} is {_age} days old, "
                f"ceiling is {MAX_STALENESS_DAYS['fuel']} — refusing to build"
            )
        print(f"  fuel data age: {_age} days (print date {_print_date})")
    except ValueError as _e:
        if "refusing to build" in str(_e):
            raise
        print(f"  WARNING: could not parse print_date {_print_date!r}")
else:
    raise ValueError("fuel.json has no print_date — refusing to build")

# Calc data (needed by home page)
calc_cities = raw_dist.get("cities", [])
calc_distances = raw_dist.get("distances", {})

# ===== FUEL =====
INDEX_PROVINCES = ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]
_missing = [c for c in INDEX_PROVINCES if provs.get(c, {}).get("diesel") is None]
if _missing:
    raise ValueError(f"fuel.json missing index provinces: {_missing} — refusing to build")
d_vals = [(c, provs[c]["diesel"]) for c in INDEX_PROVINCES]
d_sorted = sorted(d_vals, key=lambda x: x[1])

# Percentile within the provincial price range (0 = cheapest, 100 = dearest).
_lo = d_sorted[0][1]
_hi = d_sorted[-1][1]
_span = _hi - _lo


def _pct(v):
    if _span == 0:
        return 50.0
    return round(min(max((v - _lo) / _span * 100, 0), 100), 1)


def _fmt_delta(v):
    """Never render a fabricated zero. None means not enough history."""
    if v is None:
        return "n/a"
    return f"{v:+.1f}"


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
        "pct": _pct(price),
        "change": _fmt_delta(delta("diesel", code, 7)),
        "change_class": (
            "flat" if delta("diesel", code, 7) is None
            else "up" if delta("diesel", code, 7) > 0
            else "down" if delta("diesel", code, 7) < 0
            else "flat"
        ),
        "vs_national": vs_val,
        "vs_class": vs_cls,
        "rowclass": row_cls,
    })
fuel_top = provinces_data[:6]

prices = {c: p for c, p in d_vals}  # home page shows top 6

_d7 = delta("diesel", "national", 7)
_d30 = delta("diesel", "national", 30)


if _d7 is None:
    _band_7d = "noise"
else:
    _band_7d = classify_band(_d7, "diesel_weekly", thresh)

if _d7 is None:
    _change_7d_class = "flat"
elif _d7 > 0:
    _change_7d_class = "up"
elif _d7 < 0:
    _change_7d_class = "down"
else:
    _change_7d_class = "flat"

fuel = {
    "national_diesel": f"{fuel_nat:.1f}",
    "series": "NMDI",
    "national_nmdi": f"{fuel_nat:.1f}",
    "print_date": _print_date,
    "national_pct": _pct(fuel_nat),

    "change_7d": _fmt_delta(_d7),
    "change_7d_band": _band_7d,
    "change_7d_class": _change_7d_class,
    "change_30d": _fmt_delta(_d30),
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
    cap_ts = c.get("live_updated", "") or c.get("updated", "")
    if cap_ts and len(cap_ts) >= 16:
        cap_ts = cap_ts[:16].replace("T"," ")
    elif not cap_ts:
        cap_ts = "recent"
    
    item = {
        "name": c.get("name",""),
        "sub": f"{c.get('route','')} · {c.get('highway','')}" + (" · FAST" if c.get("fast_lanes") else ""),
        "wait": wait,
        "status_label": "Heavy" if d>15 else "Moderate" if d>0 else "Flowing",
        "status_class": cls,
        "url": "/border-wait-times/",
        "captured_at": cap_ts,
    }
    border_rows.append(item)
    crossings_for_page.append(item)

# ===== FX =====
fx_rate = raw_ex.get("current")
if fx_rate is None:
    raise ValueError("exchange.json has no current rate — refusing to build")
fx_chg = raw_ex.get("change", 0)
try: fx_chg = float(fx_chg)
except: fx_chg = 0
direction = "weaker CAD" if fx_chg > 0 else "stronger CAD" if fx_chg < 0 else ""

fx = {
    "usd_cad": f"{fx_rate:.4f}",
    "direction": direction,
    "change": f"{'+' if fx_chg>0 else ''}{fx_chg:.4f}",
}

# FX context gauges — computed from exchange.json history where available.
_fx_hist = raw_ex.get("history", [])
if isinstance(_fx_hist, list) and _fx_hist:
    _fx_rates = [h["rate"] for h in _fx_hist if isinstance(h, dict) and h.get("rate") is not None]
    if len(_fx_rates) >= 2:
        _avg30 = round(sum(_fx_rates) / len(_fx_rates), 4)
        fx["vs_baseline"] = f"{fx_rate - _avg30:+.4f}"
    else:
        fx["vs_baseline"] = "—"
else:
    fx["vs_baseline"] = "—"

# 52-week high/low need 52 weeks of history. exchange.json carries 30 days.
fx["high_52w"] = "—"
fx["low_52w"] = "—"

# ===== INCIDENTS =====
# Already sorted above
import time
now_ts = int(time.time())
raw_sorted = sorted(raw_inc.get("incidents", []), key=lambda x: int(x.get("start", 0)) if isinstance(x.get("start"), (int,float)) else 0, reverse=True)
incidents_raw = raw_sorted
incidents_active = [i for i in incidents_raw if i.get("event_type","") in ("accidentsandincidents","closures")]
incidents_list = []
for i in incidents_active[:2]:  # home shows 2 collisions/closures
    sev = i.get("severity","")
    cls = "heavy" if sev == "closed" else "mod" if sev == "heavy" else "ok"
    incidents_list.append({
        "road": i.get("highway","") or i.get("description","")[:40],
        "what": clip(i.get("description",""), 80),
        "severity_label": ("Closed" if i.get("event_type") == "closures" else "Collision" if i.get("event_type") == "accidentsandincidents" else "Minor"),
        "severity_class": cls,
        "url": "/road-incidents/",
    })

incidents = {
"none": len(incidents_list) == 0,
    "active_count": len(incidents_active),
    "gauge_class": "good" if len(incidents_active) == 0 else "warn",
    "status_line": "all corridors clear" if len(incidents_active) == 0 else ", ".join(list(dict.fromkeys(i.get("highway","")[:8] for i in incidents_active[:4] if i.get("highway")))),
    "incidents": incidents_list,
}

# ===== MARKET =====
market = []
mk_indicators = raw_market.get("indicators", [])
dir_summary = raw_market.get("direction_summary", "")
for ind in mk_indicators[:6]:
    direction = ind.get("direction", "flat")
    # Market indicators mix cost and growth series, where "up" means the
    # opposite thing in each. Neutral until sentiment is modelled properly.
    cls = "flat"
    # Build a useful one-line note
    detail = ind.get("detail", "")
    note = detail if detail else clip(ind.get("what_it_means", ""), 60)
    market.append({
        "name": ind.get("label", ind.get("name", "")),
        "note": note,
        "value": str(ind.get("value", "—")),
        "value_class": cls,
    })

# ===== THEFT =====
theft = []
for t in raw_theft.get("incidents", [])[:8]:
    if not t.get("source_url"):
        continue
    theft.append({
        "title": t.get("title", "")[:110],
        "date": str(t.get("date", ""))[:16],
        "source": t.get("source", ""),
        "source_url": t.get("source_url", ""),
    })

theft_home = theft[:3]

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
sponsor_fuel = None
sponsor_fx = None
sponsor_incidents = None
sponsor_theft = None
sponsor_market = None
sponsor_news = None

# Build theft JSON early (needed by home page too)
theft_json = []
for t in raw_theft.get("incidents", [])[:30]:
    if not t.get("source_url") or not t.get("geocoded"):
        continue
    theft_json.append({
        "title": t.get("title", "")[:110],
        "lat": t.get("lat"),
        "lng": t.get("lng"),
        "date": str(t.get("date", ""))[:16],
        "source": t.get("source", ""),
        "source_url": t.get("source_url", ""),
    })


# ===== ASSEMBLE HOME =====
home = {
    "updated_at": ts,
    "updated_iso": ts_iso,
    "build_version": build_version,
    "border": border,
    "fuel": fuel,
    "provinces": provinces_data,
    "fx": fx,
    "incidents": incidents,
    "border_rows": border_rows,
    "market": market,
    "theft": theft_home,
    "news": news_home,
    "theft_home_json": json.dumps(theft_json),
    "calc_cities": json.dumps(calc_cities),
    "calc_distances": json.dumps(calc_distances),
    "sponsor_page": sponsor_page,
    "sponsor_border": sponsor_border,
    "sponsor_fuel": sponsor_fuel,
    "sponsor_fx": sponsor_fx,
    "sponsor_incidents": sponsor_incidents,
    "sponsor_theft": sponsor_theft,
    "sponsor_market": sponsor_market,
    "sponsor_news": sponsor_news,
}

write("home.norm", home)
write("fuel.norm", {"fuel": fuel, "provinces": provinces_data, "updated_at": ts, "updated_iso": ts_iso, "build_version": build_version})
write("border.norm", {"border": border, "border_rows": border_rows, "crossings": crossings_for_page, "updated_at": ts,
    "updated_iso": ts_iso, "build_version": build_version, "captured_at": ts})
write("fx.norm", {"fx": fx, "updated_at": ts, "updated_iso": ts_iso, "build_version": build_version})
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
        "road": i.get("highway","") if isinstance(i.get("highway"), str) else str(i.get("highway",{}).get("name","")),
        "direction": i.get("direction", ""),
        "severity_class": sc,
        "severity_label": ("Closed" if sc == "closed" else "Heavy" if sc == "heavy" else "Collision" if i.get("event_type") == "accidentsandincidents" else "Minor"),
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

coming_roadwork = []
for i in raw_sorted:
    start = i.get("start", 0) or 0
    if not isinstance(start,(int,float)) or start < now_ts: continue
    end = i.get("end", 0)
    from datetime import datetime as dt2
    start_str = dt2.utcfromtimestamp(int(start)).strftime("%b %d")
    end_str = dt2.utcfromtimestamp(int(end)).strftime("%b %d") if end and isinstance(end,(int,float)) else ""
    hwy = i.get("highway","")
    if isinstance(hwy, dict): hwy = hwy.get("name","")
    coming_roadwork.append({
        "road": str(hwy),
        "what": clip(i.get("description",""), 55),
        "when": start_str + (" - " + end_str if end_str else ""),
        "lanes": i.get("lanes",""),
        "lat": i.get("lat"),
        "lng": i.get("lng"),
    })

write("incidents.norm", {
    "incidents": incidents,
    "incidents_json": json.dumps(inc_json),
    "coming_roadwork": coming_roadwork,
    "roadwork_json": json.dumps(coming_roadwork),
    "updated_at": ts,
    "updated_iso": ts_iso,
    "build_version": build_version,
})
write("theft.norm", {"theft": theft_home, "theft_none": len(theft) == 0, "theft_json": json.dumps(theft_json), "updated_at": ts, "updated_iso": ts_iso, "build_version": build_version})
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
    "updated_iso": ts_iso,
    "build_version": build_version,
})
write("news.norm", {"news": news, "updated_at": ts, "updated_iso": ts_iso, "build_version": build_version})

write("fuel.norm", {"fuel": fuel, "fx": fx, "provinces": provinces_data, "updated_at": ts, "updated_iso": ts_iso, "build_version": build_version})

# Snapshots — idempotent, per calendar day.
# Diesel is keyed to the NRCan print date (not the build date) so the
# weekly survey figure lands on its own print date and holds there.
snapshot("diesel", "national", fuel_nat, when=_pd)
for code, p in provs.items():
    snapshot("diesel", code, p.get("diesel"), when=_pd)

# FX: snapshot against the observation date, not today, so a stale
# collector cannot backfill a weekend with Friday's rate.
_fx_obs = raw_ex.get("observation_date")
if _fx_obs and fx_rate is not None:
    from datetime import date as _date
    snapshot("fx", "usd_cad", fx_rate, when=_date.fromisoformat(_fx_obs))

# Border and theft are deliberately not snapshotted. Border carries no
# dated observation time, and theft has no live collector. Snapshotting
# either would manufacture a history that does not exist.

print(f"Normalized at {ts}: home ({len(home)} keys) + 7 pages")
