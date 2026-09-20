#!/usr/bin/env python3
"""Northern Mile Dashboard — Weekly Macro Brief Builder.

Combines dashboard JSON feeds + news category signals into a structured
writing brief for the NMM blog writer. Runs weekly (Sunday evenings).

Output: ~/northern-mile-dashboard/content/briefs/brief_YYYY-MM-DD.md
Format: Markdown with clear sections, data values, angles, suggested keywords."""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"
BRIEF_DIR = Path(__file__).parent.parent / "content" / "briefs"


def load_json(name):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def days_since(source, max_age=None):
    """Return days since last update for a given source dict."""
    updated = source.get("updated", source.get("observation_date", source.get("print_date", "")))
    if isinstance(updated, str) and len(updated) >= 10:
        try:
            dt = datetime.strptime(updated[:10], "%Y-%m-%d")
            return (datetime.now(timezone.utc).date() - dt.date()).days
        except Exception:
            pass
    return 999


def format_price(diesel_data):
    """Extract national average and key province data for briefing."""
    if not diesel_data:
        return {"status": "No fuel data available"}
    
    provinces = diesel_data.get("provinces", {})
    if not provinces:
        return {"status": "No provincial data"}
    
    # National average = mean of index provinces
    avg_prices = []
    details = []
    for code, info in provinces.items():
        price = info.get("diesel")
        if price is None:
            continue
        province_names = {
            "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba",
            "NB": "New Brunswick", "NL": "Newfoundland and Labrador",
            "NS": "Nova Scotia", "NT": "Northwest Territories",
            "NU": "Nunavut", "ON": "Ontario", "PE": "Prince Edward Island",
            "QC": "Quebec", "SK": "Saskatchewan", "YT": "Yukon",
        }
        pname = province_names.get(code, code)
        avg_prices.append(price)
        details.append((pname, round(price, 1)))
    
    if not avg_prices:
        return {"status": "No valid prices"}
    
    # Index provinces only (exclude YT/NT per methodology)
    index_provinces = ["AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"]
    index_values = [info.get("diesel", 0) for code, info in provinces.items() 
                    if code in index_provinces and info.get("diesel")]
    national_avg = round(sum(index_values) / len(index_values), 1) if index_values else None
    
    highest = max(details, key=lambda x: x[1])
    lowest = min(details, key=lambda x: x[1])
    
    print_date = diesel_data.get("print_date", diesel_data.get("updated", "").split("T")[0])
    
    return {
        "print_date": print_date,
        "national_avg": national_avg,
        "highest": highest,
        "lowest": lowest,
        "all_provinces": details,
        "spread": round(highest[1] - lowest[1], 1),
        "locations": diesel_data.get("count", diesel_data.get("cities_count", "n/a")),
    }


def format_fx(exchange_data):
    """Extract exchange rate context."""
    if not exchange_data:
        return {"status": "No FX data"}
    
    current = exchange_data.get("current")
    change_pct = exchange_data.get("change_pct", 0)
    obs_date = exchange_data.get("observation_date", "")
    
    direction = "CAD weakening" if change_pct > 0 else "CAD strengthening" if change_pct < 0 else "CAD steady"
    
    # Historical context from history
    history = exchange_data.get("history", [])
    high_30 = max([h["rate"] for h in history[-30:]] if history else [0])
    low_30 = min([h["rate"] for h in history[-30:]] if history else [0])
    
    return {
        "current": current,
        "obs_date": obs_date,
        "change_pct": change_pct,
        "direction": direction,
        "30d_high": round(high_30, 4) if high_30 else None,
        "30d_low": round(low_30, 4) if low_30 else None,
        "cad_impact_note": "Every dollar US costs Canadian truckers more at the pump",
    }


def format_border(border_data):
    """Extract border congestion signals."""
    crossings = border_data.get("crossings", [])
    if not crossings:
        return {"status": "No border data"}
    
    commercial = [c for c in crossings if c.get("commercial")]
    sorted_by_delay = sorted(commercial, key=lambda c: c.get("delay_minutes", 0), reverse=True)
    
    alerts = []
    clear_ports = []
    for c in sorted_by_delay:
        name = c.get("name", c.get("id", "unknown"))
        delay = c.get("delay_minutes", 0)
        route = c.get("route", "")
        tag = c.get("tag", "")
        
        info = f"{name}"
        if delay == 0:
            clear_ports.append(info)
        elif delay >= 45:
            alerts.append(f"{name}: {delay} min (ALERT)")
        elif delay >= 20:
            alerts.append(f"{name}: {delay} min ({'NOTABLE' if delay >= 30 else 'NOTICE'})")
        else:
            alerts.append(f"{name}: {delay} min")
    
    return {
        "alerts": alerts[:5],
        "clear_ports": clear_ports[:5],
        "total_crossings": len(crossings),
        "commercial_count": len(commercial),
    }


def analyze_news_categories(news_data):
    """Categorize news headlines by topic and flag significant themes."""
    if not news_data or "headlines" not in news_data:
        return []
    
    headlines = news_data.get("headlines", [])
    categories = {}
    canadian_headlines = []
    international_headlines = []
    
    for h in headlines:
        title = h.get("title", "")
        source = h.get("source", "")
        cats = h.get("categories", [])
        is_canadian = h.get("flag_canadian", False)
        date = h.get("date", "")
        
        entry = {
            "title": title,
            "source": source,
            "date": date,
            "canadian": is_canadian,
            "categories": cats,
        }
        
        if is_canadian:
            canadian_headlines.append(entry)
        else:
            international_headlines.append(entry)
        
        for cat in cats:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(title)
    
    return {
        "total": len(headlines),
        "canadian_count": len(canadian_headlines),
        "international_count": len(international_headlines),
        "by_category": categories,
        "top_canadian": canadian_headlines[:5],
        "top_international": international_headlines[:3],
        "emerging_themes": _identify_themes(categories, headlines),
    }


def _identify_themes(categories, headlines):
    """Identify recurring themes across headlines."""
    themes = []
    
    # Flatten all categories into topic→titles mapping
    flat_cats = {}
    for cat_key, title_list in categories.items():
        if isinstance(title_list, list):
            flat_cats[cat_key] = title_list
        elif isinstance(title_list, dict):
            for sublist in title_list.values():
                if isinstance(sublist, list):
                    flat_cats.setdefault(cat_key, []).extend(sublist)
    
    # Rate/freight/pricing theme
    market_titles = flat_cats.get("markets", [])
    if len(market_titles) >= 2:
        themes.append({
            "topic": "Freight & Pricing",
            "angle": "Market forces shifting rates and capacity",
            "evidence": market_titles[:3],
            "dashboard_link": "/freight-barometer/",
        })
    
    # Regulatory/policy theme
    regulation_titles = flat_cats.get("regulations", [])
    if regulation_titles:
        themes.append({
            "topic": "Regulations & Policy",
            "angle": "New rules affecting compliance and operations",
            "evidence": regulation_titles[:2],
            "dashboard_link": "/methodology/nmdi/",
        })
    
    # Economy/macro theme
    business_titles = flat_cats.get("business", [])
    if business_titles:
        themes.append({
            "topic": "Economy & Business",
            "angle": "Broader economic developments impacting trucking",
            "evidence": business_titles[:2],
            "dashboard_link": "/",
        })
    
    return themes


def format_incidents(incidents_data):
    """Extract major incidents affecting trucking."""
    incidents = incidents_data.get("incidents", [])
    major = []
    for inc in incidents:
        sev = str(inc.get("severity", "")).upper()
        desc = inc.get("description", "")
        if sev in ("MAJOR", "CRITICAL") or "wildfire" in desc.lower():
            prov = inc.get("province", "?")
            hwy = inc.get("highway", {})
            if isinstance(hwy, dict):
                hwy = hwy.get("name", "")
            else:
                hwy = hwy or ""
            major.append({
                "province": prov,
                "highway": hwy,
                "description": desc[:120],
                "severity": sev,
            })
    return major[:5]


def generate_brief(today_override=None):
    """Build the complete weekly brief."""
    today = today_override or datetime.now(timezone.utc).date()
    date_str = today.isoformat()
    
    print(f"=== Generating Weekly Brief {date_str} ===\n")
    
    # Load all data
    fuel = load_json("fuel")
    exchange = load_json("exchange")
    border = load_json("border")
    news = load_json("news")
    incidents_data = load_json("incidents")
    eia = load_json("eia_diesel")
    border_trends = load_json("border_trends")
    home = load_json("home.norm.json")
    
    # Build sections
    sections = []
    
    # ── Section 1: Diesel Prices ──
    fuel_info = format_price(fuel)
    fx_info = format_fx(exchange)
    sections.append(("DIESEL PRICES", "", fuel_info))
    
    # USD/CAD impact calc
    cad_impact = None
    if fx_info.get("current") and fuel_info.get("national_avg"):
        usd_cad = fx_info["current"]
        fuel_cpl = fuel_info["national_avg"]
        cost_per_100km_usd = round(usd_cad * fuel_cpl * 0.35 / 100, 2)  # rough estimate
        # Better: calculate direct CAD cost
        cad_cost_per_km = round(fuel_cpl / 100, 2)
        cad_impact = {
            "usd_cad": usd_cad,
            "diesel_per_km_ca": cad_cost_per_km,
            "per_1000km_ca": round(fuel_cpl * 10, 1),  # cents → dollars per 1000L, then scale
        }
    
    # ── Section 2: Border Status ──
    border_info = format_border(border)
    sections.append(("BORDER WAIT TIMES", "Current congestion levels", border_info))
    
    # ── Section 3: Economic Signals ──
    econ_signals = []
    
    # Exchange rate angle
    if fx_info.get("current"):
        econ_signals.append({
            "signal": "CAD/USD",
            "value": f'{fx_info["current"]} ({fx_info["direction"]}, {fx_info["change_pct"]:+.2f}%)',
            "trucking_impact": f"{'CAD weakening hurts fuel purchasing power' if fx_info['change_pct'] > 0 else 'CAD strength softens pump pressure'} against crude priced in USD",
        })
    
    # US diesel comparison
    if eia.get("us_national_usd_gal"):
        econ_signals.append({
            "signal": "US Diesel (EIA)",
            "value": f"${eia['us_national_usd_gal']}/gal on {eia.get('effective_date', 'n/a')}",
            "trucking_impact": "Cross-border rate negotiation leverage",
        })
    
    # Border volume signal
    if border_info.get("total_crossings", 0) > 0:
        slow_ports = [a for a in border_info.get("alerts", []) if "min" in a and "ALERT" not in a and "NOTABLE" not in a]
        if len(slow_ports) >= 3:
            econ_signals.append({
                "signal": "Border Congestion",
                "value": f"{len(slow_ports)}+ ports experiencing delays",
                "trucking_impact": "Schedule reliability degrading, carrier capacity tightening eastbound",
            })
    
    sections.append(("ECONOMIC SIGNALS", "Macro factors affecting trucking", econ_signals))
    
    # ── Section 4: News & Policy Theme Analysis ──
    news_analysis = analyze_news_categories(news)
    sections.append(("NEWS & POLICY THEMES", "What's moving this week", news_analysis))
    
    # ── Section 5: Active Incidents ──
    active_majors = format_incidents(incidents_data)
    sections.append(("ACTIVE INCIDENTS", "Road closures disrupting freight", active_majors))
    
    # ── Generate blog angles ──
    angles = _generate_angles(fuel_info, fx_info, border_info, econ_signals, news_analysis, active_majors, date_str)
    
    # ── Suggested keywords ──
    keywords = _suggest_keywords(fuel_info, fx_info, border_info, news_analysis)
    
    # ── Write brief file ──
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    brief_path = BRIEF_DIR / f"brief_{date_str}.md"
    
    content = _format_brief(date_str, sections, angles, keywords, fuel_info, fx_info, border_info, news_analysis)
    
    with open(brief_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  Brief written to {brief_path}")
    print(f"  Angles generated: {len(angles)}")
    print(f"  Keywords: {', '.join(keywords)}")
    
    return str(brief_path), angles, keywords


def _generate_angles(fuel, fx, border, econ, news, majors, date_str):
    """Generate 3-5 story angles based on data conditions."""
    angles = []
    
    # Angle 1: Fuel price movement
    if fuel.get("national_avg"):
        spread = fuel.get("spread", 0)
        if spread >= 10:
            angles.append({
                "headline": "Canada's diesel price gap is wider than ever — where are you paying the most?",
                "focus": "Provincial dispersion analysis",
                "data_used": ["diesel_spread", "provincial_rankings"],
                "angle_text": f"Nationwide spread of {spread}¢/L between cheapest ({fuel['lowest'][0]} at {fuel['lowest'][1]}¢/L) and most expensive ({fuel['highest'][0]} at {fuel['highest'][1]}¢/L). That gap matters more than the national average.",
            })
        elif spread >= 5:
            angles.append({
                "headline": "Diesel prices holding steady — but the map still tells half the story",
                "focus": "Stability with regional nuance",
                "data_used": ["diesel_national", "regional_comparison"],
                "angle_text": f"National average at {fuel['national_avg']}¢/L. Moderate spread of {spread}¢/L suggests supply chains are functioning but local dynamics persist.",
            })
        else:
            angles.append({
                "headline": "Diesel prices flat — what's keeping pumps stable this week",
                "focus": "Price stability analysis",
                "data_used": ["diesel_stable"],
                "angle_text": f"All provinces clustered within {spread}¢/L. Supply-demand balance at near-term equilibrium.",
            })
    
    # Angle 2: CAD/FX impact on fuel
    if fx.get("current") and abs(fx.get("change_pct", 0)) > 0.3:
        direction = fx.get("direction", "")
        angles.append({
            "headline": f"Canadian dollar shifts {abs(fx.get('change_pct', 0)):.1f}% — what it means at the pump",
            "focus": "FX impact on diesel costs",
            "data_used": ["fx_change_pct", "usd_cad_rate"],
            "angle_text": f"CAD moved {direction} against USD. At {fx['current']}, every barrel of crude imported costs {'more' if fx['change_pct'] > 0 else 'less'} in Canadian terms. Cross-reference with NRCan data for full picture.",
        })
    
    # Angle 3: Border congestion + logistics
    alert_count = len([a for a in border.get("alerts", []) if "ALERT" in a])
    if alert_count >= 2:
        angles.append({
            "headline": "Multiple border ports showing critical wait times — schedule your hauls accordingly",
            "focus": "Border disruption logistics",
            "data_used": ["border_alerts", "port_delays"],
            "angle_text": f"{alert_count} ports flagged with ALERT-level delays. If you haul US-bound freight, consider alternate routes or timing adjustments.",
        })
    
    # Angle 4: News-driven (policy/tariffs/trade)
    if news.get("emerging_themes"):
        for theme in news["emerging_themes"]:
            if theme["topic"] in ("Regulations & Policy", "Economy & Business"):
                angles.append({
                    "headline": theme["angle"].capitalize(),
                    "focus": theme["topic"],
                    "data_used": ["news_categories", "canadian_headlines"],
                    "angle_text": theme["angle"],
                })
    
    # Angle 5: Week-at-a-glance
    data_refs = []
    if fuel.get("national_avg"):
        data_refs.append("diesel_national")
    if fx.get("current"):
        data_refs.append("fx_rate")
    total_crossings = border.get("total_crossings", border.get("commercial_count", 0))
    if total_crossings:
        data_refs.append("border_status")
    if not data_refs:
        data_refs = ["dashboard_feeds"]
    
    angles.append({
        "headline": "Week-in-review: fuel, borders, and the numbers that matter for truckers",
        "focus": "Weekly roundup",
        "data_used": data_refs,
        "angle_text": f"Fuel: {fuel.get('print_date', 'n/a')}, national avg {fuel.get('national_avg', 'n/a')}¢/L. FX: {fx.get('current')} on {fx.get('obs_date', 'n/a')}. Borders: {total_crossings} crossings tracked.",
    })
    
    return angles


def _suggest_keywords(fuel, fx, border, news):
    """Suggest search-targeting keywords based on current data."""
    kw = []
    
    if fuel.get("national_avg"):
        kw.append(f"canada diesel price")
        kw.append(f"diesel price today")
        kw.append(f"truck fuel cost calculator")
    
    if fx.get("current") and abs(fx.get("change_pct", 0)) > 0.2:
        kw.append("cad usd exchange rate")
        kw.append("canadian dollar trucking")
    
    if border.get("alerts"):
        kw.append("border wait times")
        kw.append("ambassador bridge wait time")
        kw.append("canada us border crossing")
    
    # From news themes
    themes = news.get("emerging_themes", [])
    for t in themes:
        if "Tariff" in t["topic"] or "Trade" in t["topic"]:
            kw.append("tariffs canada trucking")
            kw.append("us canada trade policy")
        if "Regulation" in t["topic"]:
            kw.append("trucking regulations canada")
            kw.append("hours of service changes")
        if "Economy" in t["topic"]:
            kw.append("economic outlook trucking")
    
    return list(dict.fromkeys(kw))[:8]


def _format_brief(date_str, sections, angles, keywords, fuel, fx, border, news):
    """Format the brief as markdown."""
    lines = []
    lines.append("# WEEKLY MACRO BRIEF")
    lines.append(f"**Date:** {date_str}")
    lines.append(f"**Generated by:** NMM Macro Pipeline\n")
    
    lines.append("---\n")
    lines.append("## DATA STATUS\n")
    
    data_sources = {
        "NRCan Diesel": fuel.get("print_date", fuel.get("updated", "")[:10]) if fuel else "MISSING",
        "Bank of Canada FX": fx.get("observation_date", "") if fx else "MISSING",
        "CBSA Border": border.get("crossings", [{}])[0].get("captured_utc", "")[:10] if border.get("crossings") else "MISSING",
        "RSS News": news.get("updated", "")[:10] if news else "MISSING",
        "Incidents": incidents_status(),
    }
    
    lines.append("| Source | Last Update | Status |")
    lines.append("|--------|-------------|--------|")
    for src, val in data_sources.items():
        age = check_age(val)
        status = "FRESH" if int(age) <= 7 else "STALE" if int(age) <= 30 else "CRITICAL"
        lines.append(f"| {src} | {val or 'Unknown'} | {status} |")
    
    lines.append("\n---\n")
    
    for section_name, subtitle, section_data in sections:
        lines.append(f"## {section_name}")
        if subtitle:
            lines.append(f"*{subtitle}*\n")
        
        if section_name == "DIESEL PRICES":
            lines.append(f"**Print Date:** {section_data.get('print_date', 'n/a')}")
            lines.append(f"**National Average:** {section_data.get('national_avg', 'n/a')}¢/L\n")
            
            if section_data.get("highest"):
                lines.append(f"**Highest:** {section_data['highest'][0]} — {section_data['highest'][1]}¢/L")
                lines.append(f"**Lowest:** {section_data['lowest'][0]} — {section_data['lowest'][1]}¢/L")
                lines.append(f"**Spread:** {section_data.get('spread', 'n/a')}¢/L\n")
            
            lines.append("**All Provinces:**")
            lines.append("| Province | Price (¢/L) |")
            lines.append("|----------|-------------|")
            for name, price in sorted(section_data.get("all_provinces", []), key=lambda x: -x[1]):
                lines.append(f"| {name} | {price} |")
            lines.append("")
        
        elif section_name == "BORDER WAIT TIMES":
            if section_data.get("alerts"):
                lines.append("**Ports with Delays:**")
                for a in section_data["alerts"]:
                    lines.append(f"- {a}")
                lines.append("")
            if section_data.get("clear_ports"):
                lines.append("**Clear Ports:**")
                for p in section_data["clear_ports"]:
                    lines.append(f"- {p}")
                lines.append("")
        
        elif section_name == "ECONOMIC SIGNALS":
            if isinstance(section_data, list):
                for sig in section_data:
                    lines.append(f"- **{sig['signal']}:** {sig['value']}")
                    lines.append(f"  → {sig['trucking_impact']}")
                lines.append("")
        
        elif section_name == "NEWS & POLICY THEMES":
            if isinstance(section_data, dict):
                lines.append(f"**Total Headlines:** {section_data.get('total', 0)} ({section_data.get('canadian_count', 0)} Canadian-flagged)\n")
                
                if section_data.get("emerging_themes"):
                    lines.append("**Emerging Themes:**")
                    for theme in section_data["emerging_themes"]:
                        lines.append(f"\n### {theme['topic']}")
                        lines.append(f"**Angle:** {theme['angle']}")
                        if theme.get("dashboard_link"):
                            lines.append(f"**Dashboard Page:** {theme['dashboard_link']}")
                        
                        lines.append("**Evidence:**")
                        for evidence_title in theme.get("evidence", [])[:2]:
                            lines.append(f'- "{evidence_title}"')
                
                lines.append("\n**Top Canadian Headlines:**")
                for h in section_data.get("top_canadian", [])[:3]:
                    lines.append(f'- [{h["source"]}] {h["title"]}')
        
        elif section_name == "ACTIVE INCIDENTS":
            if section_data:
                for inc in section_data:
                    lines.append(f"- **[{inc['severity']}]** {inc['province']} {inc['highway']}: {inc['description']}")
                lines.append("")
            else:
                lines.append("*No active major incidents.*\n")
    
    lines.append("---\n")
    
    # Blog angles
    lines.append("## BLOG ANGLE OPTIONS\n")
    lines.append("Select ONE angle per article. Each angle includes a headline suggestion, data to cite, and writing notes.\n")
    
    for i, angle in enumerate(angles[:4], 1):
        lines.append(f"### Angle {i}: {angle['headline']}\n")
        lines.append(f"**Focus:** {angle['focus']}")
        lines.append(f"**Data used:** {', '.join(angle['data_used'])}")
        lines.append(f"**Writing notes:** {angle['angle_text']}")
        lines.append(f"**Suggested keyword:** {keywords[i-1] if i <= len(keywords) else keywords[-1] if keywords else 'generic'}")
        lines.append("")
    
    # Keywords
    lines.append("---\n")
    lines.append("## SEO KEYWORDS\n")
    lines.append(", ".join(keywords))
    lines.append("")
    
    # Content type recommendation
    lines.append("---\n")
    lines.append("## CONTENT TYPE RECOMMENDATION\n")
    lines.append(f"Primary article: {angles[0]['focus'] if angles else 'weekly roundup'}")
    lines.append(f"Suggested length: 1,000–1,500 words")
    lines.append(f"Publish day: Wednesday morning (best engagement window)")
    lines.append(f"Internal links: /fuel-prices/, /border-wait-times/, /freight-barometer/\n")
    
    return "\n".join(lines)


def incidents_status():
    try:
        import json as _json
        path = DATA_DIR / "incidents.json"
        if path.exists():
            with open(path) as f:
                d = _json.load(f)
            return d.get("updated", "")[:10]
    except Exception:
        pass
    return "Unknown"


def check_age(date_str):
    if not date_str:
        return 999
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return (datetime.now(timezone.utc).date() - dt).days
    except Exception:
        return 999


if __name__ == "__main__":
    import sys
    
    override_date = None
    if len(sys.argv) > 1:
        try:
            override_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            pass
    
    path, angles, keywords = generate_brief(override_date)
    print(f"\nBrief ready at: {path}")
    print(f"Angles available: {len(angles)}")
