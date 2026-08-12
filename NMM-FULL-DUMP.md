# Northern Mile Media — Full System Dump
Generated: $(date)
## 1. Directory Tree
./.backups/cockpit-v3/app.js
./.backups/cockpit-v3/styles.css
./.backups/cockpit-v3/templates/border-wait-times.template.html
./.backups/cockpit-v3/templates/cargo-theft.template.html
./.backups/cockpit-v3/templates/exchange-rate.template.html
./.backups/cockpit-v3/templates/fuel-cost-calculator.template.html
./.backups/cockpit-v3/templates/fuel-prices.template.html
./.backups/cockpit-v3/templates/index.html
./.backups/cockpit-v3/templates/index.template.html
./.backups/cockpit-v3/templates/industry-news.template.html
./.backups/cockpit-v3/templates/market-pulse.template.html
./.backups/cockpit-v3/templates/road-incidents.template.html
./.github/workflows/deploy.yml
./.gitignore
./.hermes/plans/2026-07-24_bulletin-design-exploration.md
./LAUNCH_PLAN.md
./NMM-BRIEF.md
./NMM-FULL-DUMP.md
./NMM-SOURCE-DUMP.md
./assets/app.js
./assets/leaflet.css
./assets/leaflet.js
./assets/styles.css
./cloudflared
./config/thresholds.yaml
./content/backlink-targets.md
./content/blog/2026-07-28-diesel-spread.md
./content/blog/2026-08-04-border-crossings.md
./content/blog/2026-08-04-cargo-theft-canada.md
./content/blog/2026-08-04-market-pulse.md
./content/blog/chart-diesel-spread.html
./content/blog/diesel-spread-chart.png
./content/carousel-brief-claude.md
./content/carousel-friday-fuel-2026-07-31.html
./content/carousel-friday-fuel.md
./content/carousel-market-fx-july28.html
./content/carousel-monday-market.md
./content/carousel-thursday-theft.md
./content/carousel-tuesday-border.md
./content/carousel-wednesday-newsletter.md
./content/claude-blog.md
./content/claude-content-strategy-brief.md
./content/claude-linkedin-page.md
./content/claude-linkedin-personal.md
./content/claude-newsletter.md
./content/claude-project-instructions-full.md
./content/claude-project-instructions-v3.md
./content/claude-project-instructions.md
./content/claude-prompt-newsletter.md
./content/content-samples-reference.md
./content/episodes/blog/001/chart.png
./content/episodes/blog/001/post.md
./content/episodes/newsletter/001/newsletter.md
./content/grain-desk-brief.md
./content/linkedin-dm-tracker.md
./content/linkedin-posts/2026-07-30-thursday-cargo-theft.md
./content/newsletter-issue-002.md
./content/newsletter-issue-003.md
./data/border.json
./data/border.norm.json
./data/calc.json
./data/coverage.json
./data/distances.json
./data/exchange.json
./data/fuel.json
./data/fuel.norm.json
./data/fx.json
./data/fx.norm.json
./data/health.json
./data/history/border.csv
./data/history/series.csv
./data/home.json
./data/home.norm.json
./data/incidents.json
./data/incidents.norm.json
./data/killswitch.json
./data/market.json
./data/market.norm.json
./data/news.json
./data/news.norm.json
./data/nrcan_diesel.json
./data/sponsors.json
./data/theft.json
./data/theft.norm.json
./data/weather.json
./deploy.sh
./docs/.nojekyll
./docs/CNAME
./docs/app.js
./docs/assets/app.js
./docs/assets/leaflet.css
./docs/assets/leaflet.js
./docs/assets/styles.css
./docs/border-wait-times/index.html
./docs/cargo-theft/index.html
./docs/exchange-rate/index.html
./docs/favicon.ico
./docs/fuel-cost-calculator/index.html
./docs/fuel-prices/index.html
./docs/index.html
./docs/industry-news/index.html
./docs/leaflet.css
./docs/leaflet.js
./docs/logo.jpg
./docs/market-pulse/index.html
./docs/methodology/index.html
./docs/methodology/nmdi/index.html
./docs/road-incidents/index.html
./docs/robots.txt
./docs/sitemap.xml
./docs/styles.css
./scripts/border_history.py
./scripts/build_dashboard.py.DEAD
./scripts/build_fuel_page.py
./scripts/build_seo_pages.py
./scripts/build_templates.py
./scripts/chart_builder.py
./scripts/collect_border.py
./scripts/collect_nrcan_diesel.py
./scripts/collector.py
./scripts/coverage.py
./scripts/health_tracker.py
./scripts/history.py
./scripts/incidents.py
./scripts/market_pulse.py
./scripts/normalize.py
./scripts/theft_incidents.py
./server.py
./start.sh
./templates/_subscribe.html
./templates/border-wait-times.template.html
./templates/cargo-theft.template.html
./templates/exchange-rate.template.html
./templates/fuel-cost-calculator.template.html
./templates/fuel-prices.template.html
./templates/index.html
./templates/index.template.html
./templates/industry-news.template.html
./templates/market-pulse.template.html
./templates/methodology.template.html
./templates/road-incidents.template.html
./web/index.html

## 2. Pipeline Commands
```
Deploy cron: cd /home/hermes/northern-mile-dashboard && bash deploy.sh
Manual: python3 scripts/collector.py && python3 scripts/normalize.py && python3 scripts/build_templates.py
```

## .github/workflows/deploy.yml
```
name: Deploy to GitHub Pages

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages-deploy
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs
      - name: Deploy
        id: deploy
        uses: actions/deploy-pages@v4
```

## deploy.sh
```
#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
python3 scripts/collector.py && python3 scripts/normalize.py && python3 scripts/build_templates.py 2>&1
COLLECT_EXIT=$?

# 2. Health check — record status for each source
python3 -c "
import json, os, sys
sys.path.insert(0, 'scripts')
from health_tracker import record_success, record_failure

data_dir = 'data'
sources = {
    'fuel': 'fuel.json',
    'exchange': 'exchange.json', 
    'border': 'border.json',
    'incidents': 'incidents.json',
    'market': 'market.json',
    'news': 'news.json',
    'theft': 'theft.json'
}

for src, filename in sources.items():
    path = os.path.join(data_dir, filename)
    try:
        if os.path.exists(path):
            with open(path) as f:
                d = json.load(f)
            # Check if data has content (not empty)
            if d and (d.get('updated') or d.get('current') or len(d.get('incidents', [])) > 0 or 
                      len(d.get('headlines', [])) > 0 or d.get('diesel_national_avg')):
                record_success(src)
            else:
                record_failure(src, 'Empty data')
        else:
            record_failure(src, 'File missing')
    except Exception as e:
        record_failure(src, str(e))
print('Health recorded.')
" 2>&1

# 3. Copy data skipped — template engine handles everything

# 4. Rebuild both

echo "[5/6] Copying docs..."
mkdir -p docs/v2 docs/assets && cp -r assets/. docs/assets/
echo "[6/6] Deploying..."
# Commit and push
echo "=== Git push ==="
git add -A
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
git push origin master || echo "  Push failed — check GitHub auth"
echo "Done."
```

## config/thresholds.yaml
```
# Northern Mile — Materiality Thresholds v1 (provisional, recalibrate week 8)
# Every threshold here is a starting point. Replace with real distributions at week 8.

diesel_weekly:
  unit: cents_per_litre
  mention_floor: 1.0
  lead_floor: 3.0
  alert_floor: 6.0
  sigma_material: 1.0
  sigma_lead: 2.0
  sigma_alert: 2.5
  display_decimals: 1
  drift_periods: [4, 8, 12]
  drift_consistency: 0.75

diesel_spread:
  unit: cents_per_litre
  mention_floor: 2.0
  lead_floor: 5.0
  alert_condition: "12-month maximum"
  display_decimals: 1

usdcad_daily:
  unit: percent_change
  mention_floor: 0.2
  lead_floor: 0.5
  alert_floor: 1.0
  display_decimals: 2
  round_handle_alerts: [1.35, 1.40, 1.45]

border_wait:
  unit: minutes
  mention_floor: 10
  lead_floor: 20
  alert_floor: 45
  alert_sustain: 60   # minutes sustained at alert level
  alert_absolute: 90   # absolute commercial wait
  baseline_window: 4   # compare to 4-week same-weekday baseline

road_incidents:
  core_corridors: ["401", "QEW", "Hwy 1", "Hwy 5", "Hwy 16", "A-20"]
  lane_restriction_floor: 4      # hours — anything below is noise
  closure_material: true          # any full closure on core corridor is material
  closure_alert: 6               # hours — full closure ≥ this is alert

cargo_theft:
  any_incident_material: true    # any confirmed incident is material
  require_verified_source: true  # unverified reports are never published

market_pulse:
  unit: percent_change_wow
  mention_floor: 2.0
  lead_floor: 5.0
  alert_floor: 8.0
  display_decimals: 1

# Verb-magnitude mapping
verbs:
  noise: ["held", "unchanged", "flat", "steady"]
  notable: ["edged up", "edged down", "ticked up", "ticked down", "drifted"]
  material: ["rose", "fell", "climbed", "dropped", "gained", "lost"]
  alert: ["jumped", "surged", "plunged", "spiked"]
  forbidden_noise: ["rose", "fell", "climbed", "dropped", "jumped", "surged", "plunged", "spiked", "soared"]
  forbidden_notable: ["jumped", "surged", "plunged", "spiked", "soared"]
```

## scripts/collector.py
```python
#!/usr/bin/env python3
"""Northern Mile Dashboard - Data Collector
Fetches live Canadian trucking data from free public sources.
Run via cron every 15-60 minutes.
"""

import json
import os
import sys
import urllib.request
import re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

# Import market pulse collector
sys.path.insert(0, os.path.dirname(__file__))
from market_pulse import collect_market_pulse
from collect_nrcan_diesel import collect as collect_fuel
from incidents import collect_incidents
from health_tracker import record_success, record_failure

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ── Canadian trucking hub cities with coords ──
CITIES = {
    "Vancouver": (49.28, -123.12, "America/Vancouver"),
    "Calgary": (51.04, -114.07, "America/Edmonton"),
    "Edmonton": (53.55, -113.49, "America/Edmonton"),
    "Winnipeg": (49.90, -97.14, "America/Winnipeg"),
    "Toronto": (43.70, -79.42, "America/Toronto"),
    "Montreal": (45.51, -73.56, "America/Toronto"),
    "Moncton": (46.09, -64.78, "America/Moncton"),
}

# ── Key border crossings ──
BORDER_CROSSINGS = [
    "Windsor-Detroit", "Fort Erie-Buffalo", "Lacolle-Champlain",
    "Coutts-Sweetgrass", "Pacific Highway-Blaine", "Emerson-Pembina",
]

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "NorthernMileDashboard/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def fetch_text(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; NorthernMileDashboard/1.0)"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")

def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def collect_exchange_rate():
    """USD/CAD from Bank of Canada (free, no key)."""
    try:
        data = fetch_json("https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?recent=30")
        obs = data["observations"]
        rates = []
        for o in obs:
            rates.append({
                "date": o["d"],
                "rate": round(float(o["FXUSDCAD"]["v"]), 4)
            })
        current = rates[-1]["rate"]
        prev = rates[0]["rate"] if len(rates) > 1 else current
        change = round(current - prev, 4)
        change_pct = round((change / prev) * 100, 2) if prev else 0

        save("exchange", {
            "current": current,
            "change": change,
            "change_pct": change_pct,
            "history": rates,
            "updated": datetime.now(timezone.utc).isoformat(),
        })
        print(f"  USD/CAD: {current} ({change:+.4f})")
    except Exception as e:
        print(f"  Exchange rate failed: {e}")


def collect_weather():
    """Weather for key cities via Open-Meteo (free, no key)."""
    results = {}
    for city, (lat, lon, tz) in CITIES.items():
        try:
            url = (f"https://api.open-meteo.com/v1/forecast?"
                   f"latitude={lat}&longitude={lon}"
                   f"&current=temperature_2m,wind_speed_10m,wind_gusts_10m,weather_code"
                   f"&timezone={tz}")
            data = fetch_json(url)
            c = data["current"]
            weather_codes = {
                0: "Clear", 1: "Clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Fog", 51: "Drizzle", 53: "Drizzle",
                55: "Drizzle", 61: "Rain", 63: "Rain", 65: "Heavy rain",
                71: "Snow", 73: "Snow", 75: "Heavy snow", 77: "Snow",
                80: "Showers", 81: "Showers", 82: "Heavy showers",
                85: "Snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
            }
            results[city] = {
                "temp": c["temperature_2m"],
                "wind": c["wind_speed_10m"],
                "gust": c.get("wind_gusts_10m", c["wind_speed_10m"]),
                "condition": weather_codes.get(c["weather_code"], "Unknown"),
                "code": c["weather_code"],
            }
        except Exception as e:
            print(f"  Weather {city}: {e}")
            results[city] = {"error": str(e)}

    save("weather", {
        "cities": results,
        "updated": datetime.now(timezone.utc).isoformat(),
    })
    print(f"  Weather: {len(results)} cities")


def collect_news():
    """Industry headlines from free RSS feeds with dates and categories."""
    feeds = [
        ("Truck News", "https://www.trucknews.com/feed/"),
        ("Trucking Info", "https://www.truckinginfo.com/rss/news/"),
        ("The Trucker", "https://www.thetrucker.com/feed/"),
    ]

    # Category keyword mapping
    categories = {
        "regulations": ["regulation", "compliance", "fmcsa", "dot", "hours of service", "eld", "mandate", "rule", "law", "legislation", "mto", "transport canada", "cbsa"],
        "markets": ["rate", "freight", "spot", "contract", "pricing", "volume", "demand", "capacity", "import", "export", "trade", "economy"],
        "equipment": ["truck", "trailer", "engine", "electric", "ev", "autonomous", "safety system", "maintenance", "tire", "part"],
        "business": ["merger", "acquisition", "earnings", "revenue", "profit", "ipo", "invest", "ceo", "cfo", "president", "appoints", "names", "layoff", "expansion"],
        "technology": ["software", "platform", "digital", "automation", "telematics", "gps", "tracking", "visibility", "ai ", "artificial intelligence"],
        "drivers": ["driver", "recruitment", "retention", "wage", "shortage", "training", "workforce", "labour"],
        "safety": ["safety", "crash", "accident", "collision", "inspection", "cvsa", "blitz", "brake"],
    }
    # Canadian signal keywords for flag_canadian
    canada_words = [
        "canada", "canadian", "ontario", "quebec", "alberta", "british columbia",
        "manitoba", "saskatchewan", "nova scotia", "new brunswick", "pei",
        "newfoundland", "yukon", "nunavut", "toronto", "montreal", "vancouver",
        "calgary", "edmonton", "ottawa", "winnipeg", "halifax", "cvor", "ifta",
        "cbsa", "nrcan", "transport canada", "mto", "saaq",
    ]

    headlines = []
    for source, url in feeds:
        try:
            xml_text = fetch_text(url, timeout=15)
            root = ET.fromstring(xml_text)
            items = root.findall(".//item")

            for item in items[:8]:  # top 8 per feed
                title = ""
                link = ""
                pub_date = ""
                cats = []
                for child in item:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag == "title" and not title:
                        title = (child.text or "").strip()
                    elif tag == "link" and not link:
                        link = child.text or child.get("href", "") or ""
                    elif tag in ("pubDate", "dc:date") and not pub_date:
                        pub_date = (child.text or "").strip()
                    elif tag == "category" and child.text:
                        cats.append(child.text.strip())

                if not title:
                    continue

                # Auto-categorize from title
                title_lower = title.lower()
                matched = []
                for cat, keywords in categories.items():
                    if any(kw in title_lower for kw in keywords):
                        matched.append(cat)
                if not matched:
                    matched = ["industry"]

                # Parse date for sorting
                try:
                    dt = parsedate_to_datetime(pub_date)
                    date_iso = dt.isoformat()
                except Exception:
                    dt = datetime(1970,1,1,tzinfo=timezone.utc)
                    date_iso = None
                
                # Canadian flag
                title_lower = title.lower()
                is_canadian = source in ("Truck News", "Today's Trucking") or any(kw in title_lower for kw in canada_words)
                
                headlines.append({
                    "source": source,
                    "title": title,
                    "link": link,
                    "date": pub_date,
                    "date_iso": date_iso,
                    "categories": matched[:2],
                    "flag_canadian": is_canadian,
                    "_sort_dt": dt,
                })
        except Exception as e:
            print(f"  News {source}: {e}")

    # Sort by date (most recent first), then limit
    # Sort by parsed date, then dedupe by normalized title
    headlines.sort(key=lambda h: h.get("_sort_dt", datetime(1970,1,1,tzinfo=timezone.utc)), reverse=True)
    
    # Dedupe: drop near-duplicate titles
    def norm_title(t):
        return re.sub(r"[^a-z0-9 ]", "", t.lower().split("|")[0].strip())
    seen = set()
    deduped = []
    for h in headlines:
        nt = norm_title(h["title"])
        if nt not in seen:
            seen.add(nt)
            deduped.append(h)
    # Reserved slots: 6 Canadian-flagged first, then fill by date
    canadian_items = [h for h in deduped if h.get("flag_canadian")]
    other_items = [h for h in deduped if not h.get("flag_canadian")]
    headlines = canadian_items[:6] + other_items
    headlines = headlines[:15]
    
    # Remove internal sort key
    for h in headlines:
        h.pop("_sort_dt", None)

        # Health tracking
    try:
        from health_tracker import record_success, record_failure
        if headlines:
            record_success("news", len(headlines))
        else:
            record_failure("news", "No headlines collected")
    except Exception:
        pass
    
    save("news", {
        "headlines": headlines,
        "count": len(headlines),
        "updated": datetime.now(timezone.utc).isoformat(),
    })
    print(f"  News: {len(headlines)} headlines from {len(feeds)} sources")


def collect_border():
    """Update border crossing data and refresh blitz calendar.
    CBSA and CBP wait time APIs are behind paywalls.
    This updates the static border.json metadata.
    """
    try:
        with open(os.path.join(DATA_DIR, "border.json")) as f:
            border_data = json.load(f)
    except Exception:
        border_data = {"crossings": [], "blitz_dates": []}

    # Update timestamp
    border_data["updated"] = datetime.now(timezone.utc).isoformat()

    # Keep blitz dates current (remove passed dates)
    now = datetime.now(timezone.utc).date()
    if border_data.get("blitz_dates"):
        border_data["blitz_dates"] = [
            b for b in border_data["blitz_dates"]
            if datetime.fromisoformat(b["date"]).date() >= now
        ]

    save("border", border_data)
    crossings = len(border_data.get("crossings", []))
    blitzes = len(border_data.get("blitz_dates", []))
    print(f"  Border: {crossings} crossings, {blitzes} upcoming blitz dates")


if __name__ == "__main__":
    print(f"=== Northern Mile Collector {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

    collect_exchange_rate()
    collect_market_pulse()
    collect_incidents()
    collect_fuel()
    collect_news()
    collect_border()

    # Coverage report
    from coverage import write as write_coverage
    import json as _json, os as _os
    DATA = _os.path.dirname(_os.path.abspath(__file__)).replace("scripts", "data")

    def _count(path):
        try:
            with open(_os.path.join(DATA, path)) as f:
                d = _json.load(f)
            if path == "fuel.json":
                return len(d.get("provinces", {})) + 1
            if path == "exchange.json":
                return 1 if d.get("current") else 0
            if path == "border.json":
                return len(d.get("crossings", []))
            if path == "theft.json":
                return len(d.get("incidents", []))
            if path == "incidents.json":
                return len(d.get("incidents", []))
        except Exception:
            return 0
        return 0

    def _latest(path):
        try:
            with open(_os.path.join(DATA, path)) as f:
                d = _json.load(f)
            # Use print_date (source publication date) if available, else fetch date
            obs = d.get("print_date") or d.get("updated")
            if obs:
                from datetime import datetime
                try:
                    return datetime.strptime(obs, "%a, %d %b %Y").strftime("%Y-%m-%d")
                except Exception:
                    return obs[:10] if obs else None
            return None
        except Exception:
            return None

    def _theft_completeness():
        """Count how many theft records have each field populated vs null."""
        try:
            with open(_os.path.join(DATA, "theft.json")) as f:
                d = _json.load(f)
            incs = d.get("incidents", [])
        except Exception:
            incs = []
        if not incs:
            return {}
        fields = ["province", "value_cad", "commodity_type", "incident_date", "location", "title"]
        result = {}
        for field in fields:
            count = 0
            for i in incs:
                if field == "province":
                    loc = i.get("location", "")
                    parts = loc.split(",")
                    count += 1 if len(parts) >= 2 else 0
                elif field == "value_cad":
                    val = i.get("value", "")
                    count += 1 if val and ("$" in str(val) or "CAD" in str(val)) else 0
                elif field == "commodity_type":
                    title = i.get("title", "")
                    count += 1 if title else 0
                elif field == "incident_date":
                    count += 1 if i.get("date") else 0
                elif field == "location":
                    count += 1 if i.get("location") else 0
                elif field == "title":
                    count += 1 if i.get("title") else 0
            result[field] = count
        return result

    # Record border history
    try:
        from border_history import record_run
        b = _json.load(open(_os.path.join(DATA, "border.json")))
        record_run(b.get("crossings", []))
    except Exception:
        pass

    # Theft uses theft.json, not incidents.json
    theft_recs = _count("theft.json")
    theft_obs = _latest("theft.json")
    theft_comp = _theft_completeness()

    write_coverage(
        fuel_records=_count("fuel.json"),
        fx_records=_count("exchange.json"),
        border_records=_count("border.json"),
        theft_records=theft_recs,
        fuel_obs=_latest("fuel.json"),
        fx_obs=_latest("exchange.json"),
        border_obs=_latest("border.json"),
        theft_obs=theft_obs,
    )

    # Inject field_completeness
    cov_path = _os.path.join(DATA, "coverage.json")
    if _os.path.exists(cov_path):
        with open(cov_path) as f:
            cov = _json.load(f)
        cov["categories"]["theft"]["field_completeness"] = theft_comp
        with open(cov_path, "w") as f:
            _json.dump(cov, f, indent=2)

    print(f"\nDone. Data saved to {DATA_DIR}/")
```

## scripts/collect_nrcan_diesel.py
```python
#!/usr/bin/env python3
"""NRCan diesel price collector — scrapes the RSS feed for 60+ Canadian locations.
Fetches NRCan weekly diesel survey via RSS (productID=5).
Runs: every 30 min via collector pipeline."""

import json, os, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# City → Province mapping
CITY_PROVINCE = {
    "Abbotsford": "BC", "Barrie": "ON", "Bathurst": "NB", "Brandon": "MB",
    "Brantford": "ON", "Calgary": "AB", "Campbellton": "NB", "Charlottetown": "PE",
    "Chicoutimi": "QC", "Corner Brook": "NL", "Drummondville": "QC",
    "Edmonton": "AB", "Edmundston": "NB", "Fort St. John": "BC",
    "Fredericton": "NB", "Gander": "NL", "Gaspe": "QC", "Gatineau": "QC",
    "Grand Falls": "NB", "Grande Prairie": "AB", "Guelph": "ON",
    "Halifax": "NS", "Hamilton": "ON", "Kamloops": "BC", "Kelowna": "BC",
    "Kentville": "NS", "Kingston": "ON", "Kitchener": "ON",
    "Labrador City": "NL", "Lethbridge": "AB", "Lloydminster": "AB",
    "London": "ON", "Miramichi": "NB", "Moncton": "NB", "Montreal": "QC",
    "Moose Jaw": "SK", "New Glasgow": "NS", "North Bay": "ON",
    "Oshawa": "ON", "Ottawa": "ON", "Peterborough": "ON",
    "Prince Albert": "SK", "Prince George": "BC", "Quebec": "QC",
    "Red Deer": "AB", "Regina": "SK", "Rimouski": "QC", "Saint John": "NB",
    "Sarnia": "ON", "Saskatoon": "SK", "Sault Ste Marie": "ON",
    "Sherbrooke": "QC", "St. Catharines": "ON", "St. John's": "NL",
    "Sudbury": "ON", "Sussex": "NB", "Sydney": "NS", "Thunder Bay": "ON",
    "Timmins": "ON", "Toronto": "ON", "Trois-Rivieres": "QC",
    "Truro": "NS", "Val d'Or": "QC", "Vancouver": "BC", "Victoria": "BC",
    "Whitehorse": "YT", "Windsor": "ON", "Winnipeg": "MB",
    "Woodstock": "NB", "Yarmouth": "NS", "Yellowknife": "NT",
    "Canada": "CA",
}

# All location IDs for diesel RSS feed
LOCATION_IDS = [
    90,91,36,16,92,8,82,43,32,46,69,10,37,70,34,45,31,98,99,100,93,
    39,26,5,6,71,72,94,73,11,74,20,38,35,28,97,75,24,95,18,76,14,4,
    29,9,12,77,33,58,13,22,30,27,44,21,78,40,23,25,17,79,42,80,2,3,
    1,19,15,81,41,7,66
]

PROVINCE_NAMES = {
    "BC": "British Columbia", "AB": "Alberta", "SK": "Saskatchewan",
    "MB": "Manitoba", "ON": "Ontario", "QC": "Quebec", "NB": "New Brunswick",
    "NS": "Nova Scotia", "PE": "Prince Edward Island", "NL": "Newfoundland and Labrador",
    "YT": "Yukon", "NT": "Northwest Territories",
}

def fetch_rss():
    """Fetch diesel RSS feed for current year."""
    year = datetime.now().year
    ids = ",".join(str(i) for i in LOCATION_IDS)
    url = f"https://www2.nrcan.gc.ca/eneene/sources/pripri/webfeed_e.cfm?priceYear={year}&productID=5&locationID={ids}"
    
    req = urllib.request.Request(url, headers={"User-Agent": "NorthernMile/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return ET.fromstring(resp.read().decode("utf-8", errors="replace"))


def parse_prices(root):
    """Parse RSS items into {city: price_dollars_per_litre} dict.
    Returns (prices, pub_date) — pub_date is the most recent past print from <pubDate>."""
    from datetime import datetime
    
    prices = {}
    
    # Find the most recent pubDate that is not in the future
    now = datetime.now()
    all_dates = []
    for item in root.findall(".//item"):
        pub_el = item.find("pubDate")
        if pub_el is not None and pub_el.text:
            try:
                dt = datetime.strptime(pub_el.text.strip(), "%a, %d %b %Y")
                all_dates.append((dt, pub_el.text.strip()))
            except Exception:
                pass
    past_dates = sorted([(dt, s) for dt, s in all_dates if dt <= now], reverse=True)
    pub_date = past_dates[0][1] if past_dates else None
    
    for item in root.findall(".//item"):
        title_el = item.find("title")
        desc_el = item.find("description")
        
        if title_el is None or desc_el is None:
            continue
        
        city = title_el.text.strip()
        try:
            price = float(desc_el.text.strip().replace("$", ""))
        except (ValueError, AttributeError):
            continue
        
        # Only keep most recent entry per city
        if city not in prices:
            prices[city] = price
    
    return prices, pub_date


def compute_provincial(prices):
    """Average city prices into provincial + national figures."""
    provinces = {}
    
    for city, price in prices.items():
        prov = CITY_PROVINCE.get(city)
        if not prov or prov == "CA":
            continue
        
        if prov not in provinces:
            provinces[prov] = []
        provinces[prov].append(price)
    
    # Compute averages and convert to cents/L
    result = {}
    for prov, vals in provinces.items():
        avg_dollars = sum(vals) / len(vals)
        avg_cents = round(avg_dollars * 100, 1)
        result[prov] = {
            "diesel": avg_cents,
            "gasoline": None,  # separate feed for gasoline
            "trend": "flat",
            "note": f"NRCan survey — {len(vals)} locations",
        }
    
    # National average — 10 freight-relevant provinces only
    # YT and NT are collected but excluded: equal-weighting distorts the index
    INDEX_PROVINCES = ["BC","AB","SK","MB","ON","QC","NB","NS","PE","NL"]
    indexed = [result[p]["diesel"] for p in INDEX_PROVINCES
               if result.get(p, {}).get("diesel") is not None]
    national_avg = round(sum(indexed) / len(indexed), 1) if indexed else 171.9
    
    return result, national_avg


def collect():
    """Main collector — fetch NRCan data and save fuel.json."""
    try:
        root = fetch_rss()
        prices, pub_date = parse_prices(root)
        provinces, national_avg = compute_provincial(prices)
        
        save_data = {
            "provinces": provinces,
            "diesel_national_avg": national_avg,
            "gasoline_national_avg": None,
            "updated": datetime.now(timezone.utc).isoformat(),
            "print_date": pub_date,
            "source": "Natural Resources Canada weekly diesel survey",
            "location_count": len(prices),
        }
        
        path = os.path.join(DATA_DIR, "fuel.json")
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(path, "w") as f:
            json.dump(save_data, f, indent=2, default=str)
        
        print(f"  NRCan diesel: {national_avg}c/L · {len(prices)} locations · {len(provinces)} provinces")
        
        # Also save a "nrcan" reference for reconciliation
        ref_path = os.path.join(DATA_DIR, "nrcan_diesel.json")
        with open(ref_path, "w") as f:
            json.dump({
                "prices": {c: round(p*100, 1) for c,p in prices.items()},
                "national_avg": national_avg,
                "locations": len(prices),
                "updated": datetime.now(timezone.utc).isoformat(),
                "source": "NRCan RSS feed — productID=5",
            }, f, indent=2, default=str)
        
        return True
    except Exception as e:
        print(f"  NRCan diesel failed: {e}")
        return False


if __name__ == "__main__":
    collect()
```

## scripts/collect_border.py
```python
#!/usr/bin/env python3
"""Collect CBSA border wait times from public JSON endpoint."""
import json, urllib.request, os
from datetime import datetime

CBSA_URL = "https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.json"
OUT = os.path.expanduser("~/northern-mile-dashboard/data/border.json")

# Load existing border data
existing = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        existing = json.load(f)

# Map CBSA port names to our crossing IDs
# CBSA port name → crossing ID
CBSA_MAP = [
    ("Ambassador Bridge", "windsor-detroit"),
    ("Blue Water Bridge", "sarnia-port-huron"),
    ("Peace Bridge", "fort-erie-buffalo"),
    ("Queenston Lewiston", "queenston-lewiston"),
    ("Lacolle", "lacolle-champlain"),
    ("St-Bernard-de-Lacolle", "lacolle-champlain"),
    ("Thousand Islands", "lansdowne-alexandria"),
    ("Coutts", "coutts-sweetgrass"),
    ("Pacific Highway", "pacific-blaine"),
    ("Emerson", "emerson-pembina"),
]

req = urllib.request.Request(CBSA_URL, headers={"User-Agent": "NorthernMileMedia/1.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8-sig").split("//")[0])
except Exception as e:
    print(f"CBSA fetch failed: {e}")
    data = {"waitTimes": []}

# Update crossing data
updated = datetime.utcnow().isoformat()
live_count = 0

for cbsa in data.get("waitTimes", []):
    name = cbsa.get("poe-name", "")
    # Match CBSA name against our map
    matched = None
    for cbsa_name, our_id in CBSA_MAP:
        if cbsa_name.lower() in name.lower():
            matched = our_id
            break
    
    if matched:
        for crossing in existing.get("crossings", []):
            if crossing["id"] == matched:
                comm_delay = cbsa.get("poe-comm-delay", 0)
                trav_delay = cbsa.get("poe-trav-delay", 0)
                # Parse string delays like "3 minutes"
                if isinstance(comm_delay, str):
                    try: comm_delay = int(comm_delay.split()[0])
                    except: comm_delay = -5
                if isinstance(trav_delay, str):
                    try: trav_delay = int(trav_delay.split()[0])
                    except: trav_delay = -5
                
                if comm_delay >= 0:
                    delay_min = comm_delay
                    status = "Live"
                    delay_str = f"{delay_min} min" if delay_min > 0 else "No delay"
                elif trav_delay >= 0:
                    delay_min = trav_delay
                    status = "Live"
                    delay_str = f"{delay_min} min" if delay_min > 0 else "No delay"
                else:
                    status = "Live"
                    delay_str = "Check CBSA"
                    delay_min = 0
                
                crossing["status"] = status
                crossing["delay"] = delay_str
                crossing["delay_minutes"] = delay_min
                crossing["live_updated"] = cbsa.get("poe-updated", "")
                crossing["source"] = "cbsa"
                live_count += 1
                break

existing["updated"] = updated
existing["source_note"] = f"Live CBSA data. {live_count}/{len(CBSA_MAP)} crossings updated."

with open(OUT, "w") as f:
    json.dump(existing, f, indent=2)

print(f"Border updated: {live_count}/{len(CBSA_MAP)} crossings live from CBSA")
```

## scripts/incidents.py
```python
#!/usr/bin/env python3
"""Collect road incidents from provincial 511 APIs.
Ontario 511 and BC DriveBC provide free, open incident data.
"""

import json, os, urllib.request
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def collect_incidents():
    incidents = []

    # Ontario 511
    try:
        data = fetch_json("https://511on.ca/api/v2/get/event?format=json")
        for ev in data:
            # Filter to trucking-relevant: closures, construction, collisions
            etype = (ev.get("EventType") or "").lower()
            subtype = (ev.get("EventSubType") or "").lower()
            desc = (ev.get("Description") or "")

            # Only keep incidents that affect trucking
            relevant = any(w in etype or w in subtype or w in desc.lower()
                         for w in ["closure", "collision", "accident", "construction",
                                   "incident", "hazard", "roadwork", "emergency"])

            if relevant and ev.get("Latitude") and ev.get("Longitude"):
                incidents.append({
                    "id": f"ON-{ev['ID']}",
                    "province": "ON",
                    "highway": ev.get("RoadwayName", ""),
                    "direction": ev.get("DirectionOfTravel", ""),
                    "description": desc,
                    "event_type": etype,
                    "severity": ev.get("Severity", ""),
                    "closure": ev.get("IsFullClosure", False),
                    "lanes": ev.get("LanesAffected", ""),
                    "lat": float(ev["Latitude"]),
                    "lng": float(ev["Longitude"]),
                    "start": ev.get("StartDate"),
                    "end": ev.get("PlannedEndDate"),
                    "updated": ev.get("LastUpdated"),
                })
    except Exception as e:
        print(f"  ON 511: {e}")

    # BC DriveBC
    try:
        data = fetch_json("https://api.open511.gov.bc.ca/events?format=json&status=ACTIVE")
        for ev in data.get("events", []):
            headline = (ev.get("headline") or "").lower()
            desc = (ev.get("description") or "")

            # Only trucking-relevant
            relevant = any(w in headline or w in desc.lower()
                         for w in ["closure", "collision", "accident", "construction",
                                   "incident", "hazard", "roadwork", "emergency", "debris"])

            if relevant:
                # Extract coordinates from geography
                lat, lng = None, None
                geo = ev.get("geography", {})
                if geo.get("type") == "Point" and geo.get("coordinates"):
                    lng, lat = geo["coordinates"]

                if lat and lng:
                    roads = ev.get("roads", [])
                    road_name = roads[0] if roads else ""
                    incidents.append({
                        "id": ev["id"],
                        "province": "BC",
                        "highway": road_name,
                        "direction": "",
                        "description": ev.get("description", headline),
                        "event_type": headline,
                        "severity": ev.get("severity", ""),
                        "closure": "closed" in headline or "closure" in headline,
                        "lanes": "",
                        "lat": lat,
                        "lng": lng,
                        "start": ev.get("created"),
                        "end": "",
                        "updated": ev.get("updated"),
                    })
    except Exception as e:
        print(f"  BC DriveBC: {e}")

    # Normalize timestamps and sort
    for i in incidents:
        ts = i.get("updated")
        if isinstance(ts, str):
            try:
                i["_sort_ts"] = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except:
                i["_sort_ts"] = 0
        elif isinstance(ts, (int, float)):
            i["_sort_ts"] = float(ts)
        else:
            i["_sort_ts"] = 0

    incidents.sort(key=lambda i: i["_sort_ts"], reverse=True)
    incidents = incidents[:50]

    # Remove sort key
    for i in incidents:
        i.pop("_sort_ts", None)

    path = os.path.join(DATA_DIR, "incidents.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "incidents": incidents,
            "total": len(incidents),
            "updated": datetime.now(timezone.utc).isoformat(),
            "sources": ["Ontario 511", "BC DriveBC"],
        }, f, indent=2, default=str)

    print(f"  Incidents: {len(incidents)} road events (ON + BC)")

if __name__ == "__main__":
    collect_incidents()
```

## scripts/normalize.py
```python
#!/usr/bin/env python3
"""Normalize collector data into exact template-fillable format (v3 — matches kit data shapes)."""
import json, os, time
from datetime import datetime
from history import snapshot, delta, average, span_days

def clip(text, limit=110):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "\u2026"

# ── Materiality band classification ──
import yaml
thresh = {}
try:
    with open(os.path.join(os.path.dirname(DATA), "config", "thresholds.yaml")) as tf:
        thresh = yaml.safe_load(tf)
except: pass

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
build_version = str(int(time.time()))  # cache-busting, fresh each build
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
    "series": "NMDI",
    "national_nmdi": f"{fuel_nat:.1f}",
    
    "change_7d": "—",
    "change_7d_band": "noise",
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
    cls = "up" if direction == "up" else "down" if direction == "down" else "flat"
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

theft_home = theft[:3]  # home shows 3

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
sponsor_fuel = None
sponsor_fx = None
sponsor_incidents = None
sponsor_theft = None
sponsor_market = None
sponsor_news = None

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
write("fuel.norm", {"fuel": fuel, "provinces": provinces_data, "updated_at": ts})
write("border.norm", {"border": border, "border_rows": border_rows, "crossings": crossings_for_page, "updated_at": ts,
    "build_version": build_version, "captured_at": ts})
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
        "road": i.get("highway","") if isinstance(i.get("highway"), str) else str(i.get("highway",{}).get("name","")),
        "direction": i.get("direction", ""),
        "severity_class": sc,
        "severity_label": ("Closed" if i.get("event_type") == "closures" else "Collision" if i.get("event_type") == "accidentsandincidents" else "Minor"),
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
    })

write("incidents.norm", {
    "incidents": incidents,
    "incidents_json": json.dumps(inc_json),
    "coming_roadwork": coming_roadwork,
    "updated_at": ts,
    "build_version": build_version,
})
write("theft.norm", {"theft": theft_home, "hotspots": hotspots, "theft_json": json.dumps(theft_json), "updated_at": ts})
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
    "build_version": build_version,
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
        "code": code,
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
        "code": code,
        "name": names[code],
        "pump": f"{pump:.1f}",
        "tax_portion": f"{tax_portion}",
        "per_100l": f"${per_100l:.2f}",
    })

write("fuel.norm", {"fuel": fuel, "fx": fx, "provinces": provinces_data, "border_fuel": border_fuel, "tax": tax, "ifta": ifta, "updated_at": ts})

# Snapshots — idempotent, per calendar day
snapshot("diesel", "national", fuel_nat)
for code, p in provs.items():
    snapshot("diesel", code, p.get("diesel"))

print(f"Normalized at {ts}: home ({len(home)} keys) + 7 pages")
```

## scripts/build_templates.py
```python
#!/usr/bin/env python3
"""Template fill engine v2 — .template.html files, nested tokens, loops, optionals, conditionals."""
import json, os, re, shutil
from datetime import datetime

BASE = os.path.expanduser("~/northern-mile-dashboard")
TMPL = os.path.join(BASE, "templates")
DATA = os.path.join(BASE, "data")
DOCS = os.path.join(BASE, "docs")
ASSETS = os.path.join(BASE, "assets")

def load_json(name):
    p = os.path.join(DATA, name + ".json")
    return json.load(open(p)) if os.path.exists(p) else {}

def resolve_token(data, token):
    """Resolve nested tokens like fuel.national_diesel, border.gauge_class"""
    parts = token.split(".")
    val = data
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        elif isinstance(val, list):
            # For loop context: item.key
            return val
        else:
            return None
    return val

def fill(template, data):
    """Fill a template with data."""

    # 1. LOOP blocks — expand first so loop item tokens aren't overwritten
    template = fill_loops(template, data)

    # 2. OPTIONAL blocks — keep only if key exists and is truthy
    template = fill_optionals(template, data)

    # 3. IF blocks — keep if condition true
    template = fill_ifs(template, data)

    # 4. Resolve {{nested.tokens}} AFTER loops/optionals/ifs
    def replace_token(match):
        key = match.group(1)
        val = resolve_token(data, key)
        if val is None:
            return ""  # clean missing tokens silently
        if isinstance(val, (dict, list)):
            return match.group(0)  # leave complex objects for loops
        return str(val)

    template = re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_token, template)

    # 5. Build meta
    template = template.replace("{{updated_at}}", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
    template = template.replace("{{build_id}}", datetime.utcnow().strftime("%Y%m%d%H%M%S"))

    return template

def fill_loops(template, data):
    for match in re.finditer(r'<!--LOOP:(\w+(?:\.\w+)*)-->(.*?)<!--/LOOP:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        items = resolve_token(data, key)
        if not isinstance(items, list):
            items = []
        expanded = ""
        for item in items:
            block = inner
            if isinstance(item, dict):
                # Replace {{key}} within loop with item's keys
                for k, v in item.items():
                    block = block.replace("{{" + k + "}}", str(v) if not isinstance(v, (dict, list)) else "")
            expanded += block
        template = template.replace(match.group(0), expanded)
    return template

def fill_optionals(template, data):
    for match in re.finditer(r'<!--OPTIONAL:(\w+(?:\.\w+)*)-->(.*?)<!--/OPTIONAL:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        val = resolve_token(data, key)
        if val:
            template = template.replace(match.group(0), inner)
        else:
            template = template.replace(match.group(0), "")
    return template

def fill_ifs(template, data):
    for match in re.finditer(r'<!--IF:(\w+(?:\.\w+)*)-->(.*?)<!--/IF:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        val = resolve_token(data, key)
        if val:
            template = template.replace(match.group(0), inner)
        else:
            template = template.replace(match.group(0), "")
    return template

def build_page(name, data):
    """Build one page from template + data."""
    tmpl_path = os.path.join(TMPL, name + ".template.html")
    if not os.path.exists(tmpl_path):
        print(f"  SKIP: /{name}/ (no template)")
        return None

    with open(tmpl_path) as f:
        template = f.read()

    # Inject shared CSS/JS inline
    css_path = os.path.join(ASSETS, "styles.css")
    if os.path.exists(css_path) and "styles.css" not in template:
        with open(css_path) as f:
            template = template.replace("</head>", "<style>\n" + f.read() + "\n</style>\n</head>")

    js_path = os.path.join(ASSETS, "app.js")
    if os.path.exists(js_path) and "app.js" not in template:
        with open(js_path) as f:
            template = template.replace("</body>", "<script>\n" + f.read() + "\n</script>\n</body>")

    html = fill(template, data)

    # Write output
    dir_name = "" if name == "index" else name
    # methodology goes to /methodology/nmdi/ for permanent URL
    if name == "methodology":
        dir_name = "methodology/nmdi"
    out_dir = os.path.join(DOCS, dir_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(html)

    return len(html)

def build_all():
    print(f"Build started: {datetime.utcnow().isoformat()[:19]}")

    # Copy static assets
    for f in ["styles.css", "app.js", "leaflet.css", "leaflet.js"]:
        src = os.path.join(ASSETS, f) if os.path.exists(os.path.join(ASSETS, f)) else os.path.join(BASE, "docs", f)
        dst = os.path.join(DOCS, f)
        if os.path.exists(src) and src != dst:
            shutil.copy2(src, dst)

    # Load all data
    home_data = load_json("home.norm")
    page_data = {
        "index": home_data,
        "fuel-prices": load_json("fuel.norm"),
        "exchange-rate": load_json("fx.norm"),
        "border-wait-times": load_json("border.norm"),
        "road-incidents": load_json("incidents.norm"),
        "cargo-theft": load_json("theft.norm"),
        "market-pulse": load_json("market.norm"),
        "industry-news": load_json("news.norm"),
        "fuel-cost-calculator": {**load_json("fx.norm"), **load_json("fuel.norm")},
        "methodology": load_json("home.norm"),
    }

    built = []
    for name in page_data:
        sz = build_page(name, page_data[name])
        if sz:
            built.append(f"  /{name if name != 'index' else ''} ({sz:,} bytes)")

    print(f"Built {len(built)} pages")
    for b in built:
        print(b)

if __name__ == "__main__":
    build_all()
```

## scripts/coverage.py
```python
#!/usr/bin/env python3
"""Coverage report — tracks data freshness for every collector, every run."""
import json, os
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COVERAGE_PATH = os.path.join(ROOT, "data", "coverage.json")
HISTORY_CSV = os.path.join(ROOT, "data", "history", "series.csv")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def empty_block():
    return {
        "records": 0,
        "history_days": 0,
        "latest_observation": None,
        "staleness_days": None,
        "comparable_7d": False,
        "comparable_yoy": False,
    }


def history_span(series, key):
    """Days between oldest and newest snapshot for this series/key."""
    if not os.path.exists(HISTORY_CSV):
        return 0
    pts = []
    with open(HISTORY_CSV) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 4 and parts[1] == series and parts[2] == key:
                try:
                    pts.append(datetime.fromisoformat(parts[0]).date())
                except ValueError:
                    continue
    if len(pts) < 2:
        return 0
    pts.sort()
    return (pts[-1] - pts[0]).days


def has_snapshot_near(series, key, days_ago, tolerance=3):
    """True if a snapshot exists within tolerance of N days ago."""
    if not os.path.exists(HISTORY_CSV):
        return False
    target = date.today() - date.resolution * days_ago
    with open(HISTORY_CSV) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 4 and parts[1] == series and parts[2] == key:
                try:
                    d = datetime.fromisoformat(parts[0]).date()
                    if abs((d - target).days) <= tolerance:
                        return True
                except ValueError:
                    continue
    return False


def compute(records, series, key, latest_obs):
    """Build a category block from collected data."""
    block = empty_block()
    block["records"] = records
    block["history_days"] = history_span(series, key)
    block["latest_observation"] = latest_obs
    if latest_obs:
        try:
            obs_date = date.fromisoformat(latest_obs[:10])
            block["staleness_days"] = (date.today() - obs_date).days
        except (ValueError, TypeError):
            block["staleness_days"] = None
    block["comparable_7d"] = has_snapshot_near(series, key, 7)
    block["comparable_yoy"] = has_snapshot_near(series, key, 365, tolerance=10)
    
    # Border: add quantitative_field
    if series == "border":
        block["quantitative_field"] = "delay_minutes"
    
    # Theft: add field_completeness (computed by caller)
    if series == "theft":
        block["field_completeness"] = {}
    
    return block


def write(fuel_records, fx_records, border_records, theft_records,
          fuel_obs=None, fx_obs=None, border_obs=None, theft_obs=None):
    """Write the full coverage report. Called by collectors."""
    report = {
        "generated_at": now_iso(),
        "categories": {
            "fuel":   compute(fuel_records,   "diesel",  "national", fuel_obs),
            "fx":     compute(fx_records,     "fx",      "usd_cad",  fx_obs),
            "border": compute(border_records, "border",  "all",      border_obs),
            "theft":  compute(theft_records,  "theft",   "incidents", theft_obs),
        }
    }
    os.makedirs(os.path.dirname(COVERAGE_PATH), exist_ok=True)
    with open(COVERAGE_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


def validate():
    """Build assertion: fail if any category missing or incomplete."""
    if not os.path.exists(COVERAGE_PATH):
        raise AssertionError("coverage.json missing — no collectors ran")
    with open(COVERAGE_PATH) as f:
        report = json.load(f)
    required = ["fuel", "fx", "border", "theft"]
    fields = ["records", "history_days", "latest_observation",
              "staleness_days", "comparable_7d", "comparable_yoy"]
    border_extras = ["quantitative_field"]
    theft_extras = ["field_completeness"]
    for cat in required:
        if cat not in report.get("categories", {}):
            raise AssertionError(f"coverage.json missing category: {cat}")
        for field in fields:
            if field not in report["categories"][cat]:
                raise AssertionError(f"coverage.json missing field {cat}.{field}")
        if cat == "border":
            for f in border_extras:
                if f not in report["categories"][cat]:
                    raise AssertionError(f"coverage.json missing border field {f}")
        if cat == "theft":
            for f in theft_extras:
                if f not in report["categories"][cat]:
                    raise AssertionError(f"coverage.json missing theft field {f}")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        try:
            validate()
            print("coverage.json: valid")
        except AssertionError as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Standalone run: dump current state
        if os.path.exists(COVERAGE_PATH):
            print(json.dumps(json.load(open(COVERAGE_PATH)), indent=2))
        else:
            print("No coverage report yet")
```

## scripts/border_history.py
```python
#!/usr/bin/env python3
"""Border history — persist delay_minutes per crossing, per run."""
import json, os
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(ROOT, "data", "history", "border.csv")
FIELDS = ["date", "crossing_id", "delay_minutes", "observation_time"]


def _ensure():
    os.makedirs(os.path.dirname(STORE), exist_ok=True)
    if not os.path.exists(STORE):
        with open(STORE, "w") as f:
            f.write(",".join(FIELDS) + "\n")


def record_run(crossings, run_date=None):
    """Append one row per crossing. Idempotent per day — re-running overwrites."""
    _ensure()
    if run_date is None:
        run_date = date.today().isoformat()

    # Load existing, drop today's entries
    rows = []
    if os.path.exists(STORE):
        with open(STORE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("date"):
                    continue
                parts = line.split(",", 3)
                if len(parts) >= 2 and parts[0] != run_date:
                    rows.append(line)

    for c in crossings:
        delay = c.get("delay_minutes")
        if delay is None:
            continue
        crossing_id = c.get("id", c.get("name", "unknown"))
        obs_time = c.get("live_updated", "")
        rows.append(f"{run_date},{crossing_id},{delay},{obs_time}")

    tmp = STORE + ".tmp"
    with open(tmp, "w") as f:
        f.write(",".join(FIELDS) + "\n")
        for r in sorted(set(rows)):
            f.write(r + "\n")
    os.replace(tmp, STORE)


def span_days(crossing_id=None):
    """Days of history for a crossing, or max across all if None."""
    if not os.path.exists(STORE):
        return 0
    dates = set()
    with open(STORE) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 2:
                cid, d = parts[1], parts[0]
                if crossing_id is None or cid == crossing_id:
                    dates.add(d)
    if len(dates) < 2:
        return 0
    sd = sorted(dates)
    return (datetime.strptime(sd[-1], "%Y-%m-%d") - datetime.strptime(sd[0], "%Y-%m-%d")).days


def delta(crossing_id, days_ago):
    """Change in delay_minutes over N days. None if insufficient history."""
    if not os.path.exists(STORE):
        return None
    target = date.today().isoformat()
    past_target = (date.today() - date.resolution * days_ago).isoformat()
    now_val = past_val = None
    with open(STORE) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[1] == crossing_id:
                try:
                    if parts[0] == target:
                        now_val = int(parts[2])
                    if parts[0] == past_target:
                        past_val = int(parts[2])
                except ValueError:
                    continue
    if now_val is not None and past_val is not None:
        return now_val - past_val
    return None
```

## scripts/history.py
```python
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
```

## scripts/market_pulse.py
```python
import urllib.request, io, zipfile, csv, json, os, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from history import span_days, average

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def fetch_zip_csv(url, timeout=15):
    data = urllib.request.urlopen(url, timeout=timeout).read()
    z = zipfile.ZipFile(io.BytesIO(data))
    return z.read(z.namelist()[0]).decode('utf-8')

def collect_market_pulse():
    """Market pulse using StatsCan GDP, fuel trends, and exchange rate data.
    Provides freight demand indicators and operating cost snapshot.
    """
    pulse = {
        "indicators": [],
        "rates_snapshot": {},
        "updated": datetime.now(timezone.utc).isoformat(),
        "note": "Public data from Statistics Canada, Bank of Canada, and industry surveys."
    }

    # 1. Monthly GDP growth (StatsCan table 36100434)
    try:
        csv_text = fetch_zip_csv("https://www150.statcan.gc.ca/n1/tbl/csv/36100434-eng.zip")
        lines = [l for l in csv_text.split('\n') if l.strip()]
        # Find: Canada, All industries, Seasonally adjusted, chained 2017 dollars
        gdp_rows = []
        for l in lines:
            if 'Canada' not in l: continue
            if 'All industries' not in l: continue
            if 'Seasonally adjusted' not in l: continue
            if 'Chained (2017) dollars' not in l: continue
            gdp_rows.append(l)

        if gdp_rows:
            # Parse values - they're in column 12 (VALUE)
            gdp_data = []
            for r in gdp_rows[-13:]:  # last 13 months
                parts = r.split('","')
                date = parts[0].strip('"')
                val_str = parts[12].strip('"')
                try:
                    val = float(val_str)
                    gdp_data.append({"date": date, "value": val})
                except ValueError:
                    continue

            if len(gdp_data) >= 2:
                current = gdp_data[-1]["value"]
                prev = gdp_data[-2]["value"]
                mom_change = round((current - prev) / prev * 100, 1) if prev else 0
                pulse["indicators"].append({
                    "name": "GDP Growth",
                    "label": "Monthly GDP",
                    "value": f"{mom_change:+.1f}%",
                    "detail": f"${current/1000:.0f}B (chained 2017)",
                    "direction": "up" if mom_change > 0 else "down",
                    "source": "Statistics Canada",
                    "what_it_means": "Broadest measure of economic activity. GDP growth = more freight moving."
                })

                # YoY
                if len(gdp_data) >= 13:
                    yoy_val = gdp_data[-13]["value"]
                    yoy_change = round((current - yoy_val) / yoy_val * 100, 1) if yoy_val else 0
                    pulse["indicators"].append({
                        "name": "GDP YoY",
                        "label": "Year-over-year",
                        "value": f"{yoy_change:+.1f}%",
                        "direction": "up" if yoy_change > 0 else "down",
                        "source": "Statistics Canada",
                        "what_it_means": "Longer-term freight demand trend."
                    })
    except Exception as e:
        print(f"  GDP: {e}")

    # 2. Fuel cost pressure (from our fuel data)
    try:
        with open(os.path.join(DATA_DIR, "fuel.json")) as f:
            fuel = json.load(f)
        diesel_avg = fuel.get("diesel_national_avg", 0)
        # Fuel cost per 1,000 km — self-updating, no baseline constant
        BURN = 35  # L/100km, loaded highway
        cost_1000km = round(diesel_avg * BURN * 10 / 100, 2)

        pulse["indicators"].append({
            "name": "Fuel Cost",
            "label": "Fuel cost per 1,000 km",
            "value": f"${cost_1000km:,.0f}",
            "detail": f"At {diesel_avg:.1f}¢/L and {BURN} L/100km",
            "direction": "up" if diesel_avg > 200 else "down",
            "source": "NRCan weekly diesel survey",
            "what_it_means": "Per-1,000km fuel cost at current diesel prices. Used directly in rate quotes."
        })

        # Regional spread
        provinces = fuel.get("provinces", {})
        if "BC" in provinces and "AB" in provinces:
            spread = provinces["BC"]["diesel"] - provinces["AB"]["diesel"]
            pulse["indicators"].append({
                "name": "Fuel Spread",
                "label": "BC vs AB diesel spread",
                "value": f"{spread:.1f}¢/L",
                "direction": "up" if spread > 20 else "down",
                "source": "Industry surveys",
                "what_it_means": "Wide gaps create arbitrage on cross-province lanes. BC diesel runs higher than AB."
            })
    except Exception as e:
        print(f"  Fuel pulse: {e}")

    # 3. Exchange rate impact
    try:
        with open(os.path.join(DATA_DIR, "exchange.json")) as f:
            fx = json.load(f)
        rate = fx.get("current", 0)
        # Guarded: only show when 30 days of history exist
        if span_days("fx", "usd_cad") >= 30:
            avg30 = average("fx", "usd_cad", 30)
            if avg30 is not None:
                pulse["indicators"].append({
                    "name": "CAD Impact",
                    "label": "USD/CAD vs 30-day average",
                    "value": f"{rate:.4f}",
                    "detail": f"{(rate - avg30):+.4f} vs 30-day avg {avg30:.4f}",
                    "direction": "up" if rate > avg30 else "down",
                    "source": "Bank of Canada",
                    "what_it_means": "Weaker CAD = more competitive cross-border exports, higher input costs. Stronger CAD = cheaper US equipment/parts."
                })
    except Exception as e:
        print(f"  Exchange pulse: {e}")

    # 4. Rates snapshot - operating cost indicators
    pulse["rates_snapshot"] = {
        "fuel_pct_of_ops": "25-35%",
        "current_diesel": diesel_avg,
        "usd_cad": rate if 'rate' in dir() else 0,
        "note": "Rate data from DAT/Loadlink requires paid subscription. These are operating cost indicators that drive rate floors."
    }

    # Add direction summary
    ups = sum(1 for i in pulse["indicators"] if i.get("direction") == "up")
    downs = sum(1 for i in pulse["indicators"] if i.get("direction") == "down")
    total = len(pulse["indicators"])
    pulse["direction_summary"] = f"{ups}/{total} indicators trending up"

    save_path = os.path.join(DATA_DIR, "market.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(save_path, "w") as f:
        json.dump(pulse, f, indent=2, default=str)

    print(f"  Market Pulse: {len(pulse['indicators'])} indicators ({pulse['direction_summary']})")

if __name__ == "__main__":
    collect_market_pulse()
```

## scripts/health_tracker.py
```python
#!/usr/bin/env python3
"""Health tracker for Northern Mile data sources.
Import and call record_success() or record_failure() after each source collection.
On 2 consecutive failures, writes an alert to data/alerts.json.
"""
import json, os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
HEALTH_PATH = os.path.join(DATA_DIR, 'health.json')
ALERTS_PATH = os.path.join(DATA_DIR, 'alerts.json')

def _load():
    if os.path.exists(HEALTH_PATH):
        with open(HEALTH_PATH) as f:
            return json.load(f)
    return {"sources": {}, "updated": None}

def _save(h):
    h['updated'] = datetime.now(timezone.utc).isoformat()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HEALTH_PATH, 'w') as f:
        json.dump(h, f, indent=2)

def _add_alert(source, last_success, error):
    """Append an alert to data/alerts.json for the digest to report."""
    os.makedirs(DATA_DIR, exist_ok=True)
    alerts = []
    if os.path.exists(ALERTS_PATH):
        with open(ALERTS_PATH) as f:
            alerts = json.load(f)
    alerts.append({
        'source': source,
        'last_success': last_success,
        'error': str(error)[:200],
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    # Keep last 50 alerts
    with open(ALERTS_PATH, 'w') as f:
        json.dump(alerts[-50:], f, indent=2)

def record_success(source):
    h = _load()
    h['sources'][source] = {
        'last_success': datetime.now(timezone.utc).isoformat(),
        'last_attempt': datetime.now(timezone.utc).isoformat(),
        'consecutive_failures': 0,
        'status': 'ok'
    }
    _save(h)

def record_failure(source, error=None):
    h = _load()
    s = h['sources'].get(source, {
        'last_success': None,
        'last_attempt': None,
        'consecutive_failures': 0,
        'status': 'unknown'
    })
    s['last_attempt'] = datetime.now(timezone.utc).isoformat()
    s['consecutive_failures'] = s.get('consecutive_failures', 0) + 1
    s['status'] = 'failing'
    if s['consecutive_failures'] >= 2:
        s['status'] = 'alert'
        _add_alert(source, s.get('last_success'), error)
    h['sources'][source] = s
    _save(h)

def get_status():
    """Return {source: {status, consecutive_failures, last_success}} for digest."""
    h = _load()
    result = {}
    for src, s in h.get('sources', {}).items():
        result[src] = {
            'status': s.get('status', 'unknown'),
            'consecutive_failures': s.get('consecutive_failures', 0),
            'last_success': s.get('last_success')
        }
    return result

def get_alerts(since_last_digest=True):
    """Return recent alerts. If since_last_digest, filter to unacknowledged."""
    if not os.path.exists(ALERTS_PATH):
        return []
    with open(ALERTS_PATH) as f:
        alerts = json.load(f)
    return alerts[-10:]  # Latest 10

def acknowledge_alerts():
    """Clear alerts after digest has reported them."""
    if os.path.exists(ALERTS_PATH):
        os.remove(ALERTS_PATH)

if __name__ == '__main__':
    # Quick status check
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        status = get_status()
        for src, s in status.items():
            print(f"{src}: {s['status']} (failures: {s['consecutive_failures']})")
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("Recording test success...")
        record_success('fuel')
        print("Recording test failure...")
        record_failure('news', 'Test error')
        record_failure('news', 'Test error 2 — should trigger alert')
        print("Alerts:", get_alerts())
    else:
        print("Usage: health_tracker.py [status|test]")
```

## scripts/theft_incidents.py
```python
#!/usr/bin/env python3
"""Collect cargo theft incidents from news RSS feeds.
Filters for theft-related headlines, extracts location, and geocodes.
"""

import json, os, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# Canadian city coordinate lookup
CITY_COORDS = {
    "toronto": (43.70, -79.42), "brampton": (43.69, -79.76), "mississauga": (43.59, -79.64),
    "montreal": (45.51, -73.56), "laval": (45.58, -73.75),
    "calgary": (51.04, -114.07), "edmonton": (53.55, -113.49),
    "vancouver": (49.28, -123.12), "surrey": (49.10, -122.83), "delta": (49.09, -123.06),
    "winnipeg": (49.90, -97.14), "ottawa": (45.42, -75.70),
    "hamilton": (43.26, -79.87), "london": (42.98, -81.25),
    "quebec": (46.81, -71.21), "halifax": (44.65, -63.58),
    "saskatoon": (52.16, -106.67), "regina": (50.45, -104.61),
    "moncton": (46.09, -64.78), "st john": (45.27, -66.06),
    "windsor": (42.31, -83.04), "kitchener": (43.45, -80.49),
    "oshawa": (43.90, -78.86), "barrie": (44.39, -79.69),
    "kelowna": (49.89, -119.50), "abbotsford": (49.06, -122.33),
    "st catharines": (43.16, -79.25), "guelph": (43.54, -80.25),
    "kingston": (44.23, -76.48), "thunder bay": (48.38, -89.25),
    "sudbury": (46.49, -80.99), "sherbrooke": (45.40, -71.89),
    "saskatoon": (52.16, -106.67), "regina": (50.45, -104.61),
    "north york": (43.76, -79.41), "etobicoke": (43.64, -79.57),
    "scarborough": (43.78, -79.26), "markham": (43.86, -79.34),
    "vaughan": (43.84, -79.51), "richmond hill": (43.88, -79.44),
    "oakville": (43.45, -79.68), "burlington": (43.33, -79.80),
    "milton": (43.51, -79.88), "ajax": (43.85, -79.02),
    "pickering": (43.84, -79.09), "whitby": (43.88, -78.94),
    "newmarket": (44.06, -79.46), "cambridge": (43.36, -80.31),
    "waterloo": (43.46, -80.52), "brantford": (43.14, -80.26),
    "niagara falls": (43.10, -79.06), "peterborough": (44.31, -78.32),
    "sarnia": (42.97, -82.41), "sault ste marie": (46.52, -84.35),
    "north bay": (46.31, -79.46), "timmins": (48.48, -81.33),
    "cornwall": (45.02, -74.73), "brockville": (44.59, -75.68),
    "belleville": (44.16, -77.38), "pembroke": (45.82, -77.11),
    "prince george": (53.92, -122.75), "kamloops": (50.67, -120.34),
    "nanaimo": (49.16, -123.94), "victoria": (48.43, -123.37),
    "chilliwack": (49.16, -121.95), "maple ridge": (49.22, -122.60),
    "coquitlam": (49.28, -122.79), "burnaby": (49.25, -122.97),
    "richmond": (49.17, -123.14), "langley": (49.10, -122.66),
    "lethbridge": (49.69, -112.83), "red deer": (52.27, -113.81),
    "medicine hat": (50.04, -110.68), "grande prairie": (55.17, -118.80),
    "fort mcmurray": (56.73, -111.38), "wood buffalo": (56.73, -111.38),
    "airdrie": (51.29, -114.01), "st albert": (53.63, -113.63),
    "brandon": (49.85, -99.95), "steinbach": (49.53, -96.68),
    "thompson": (55.74, -97.86), "portage la prairie": (49.97, -98.29),
    "moose jaw": (50.39, -105.53), "prince albert": (53.20, -105.75),
    "yorkton": (51.21, -102.46), "north battleford": (52.78, -108.30),
    "swift current": (50.29, -107.80), "estevan": (49.14, -102.99),
    "weyburn": (49.67, -103.85), "lloydminster": (53.28, -110.00),
    "gatineau": (45.48, -75.70), "longueuil": (45.53, -73.51),
    "trois rivieres": (46.35, -72.55), "saguenay": (48.42, -71.07),
    "levis": (46.80, -71.18), "terrebonne": (45.70, -73.63),
    "saint jean sur richelieu": (45.31, -73.26),
    "repetigny": (45.74, -73.45), "drummondville": (45.88, -72.49),
    "granby": (45.40, -72.73), "saint hyacinthe": (45.62, -72.95),
    "shawinigan": (46.57, -72.75), "rimouski": (48.45, -68.53),
    "saint john": (45.27, -66.06), "fredericton": (45.96, -66.64),
    "bathurst": (47.62, -65.65), "miramichi": (47.03, -65.51),
    "edmundston": (47.37, -68.33), "campbellton": (48.01, -66.67),
    "sydney": (46.14, -60.19), "truro": (45.37, -63.28),
    "new glasgow": (45.59, -62.64), "charlottetown": (46.24, -63.13),
    "summerside": (46.39, -63.79), "corner brook": (48.95, -57.95),
    "mount pearl": (47.52, -52.79), "conception bay south": (47.51, -52.99),
    "grand falls windsor": (48.94, -55.66), "gander": (48.95, -54.61),
    "labrador city": (52.94, -66.91), "happy valley goose bay": (53.30, -60.33),
    "yellowknife": (62.45, -114.37), "whitehorse": (60.72, -135.05),
    "iqaluit": (63.75, -68.52), "innisfil": (44.30, -79.58),
}

def geocode_city(text):
    """Extract city name from text and return coordinates."""
    text_lower = text.lower()
    # Try longer city names first
    for city in sorted(CITY_COORDS.keys(), key=len, reverse=True):
        if city in text_lower:
            return CITY_COORDS[city]
    return None

def collect_theft_incidents():
    """Search RSS feeds for cargo theft stories and geocode them."""
    
    feeds = [
        ("Truck News", "https://www.trucknews.com/feed/"),
        ("Trucking Info", "https://www.truckinginfo.com/rss/news/"),
        ("The Trucker", "https://www.thetrucker.com/feed/"),
    ]

    theft_keywords = [
        "cargo theft", "stolen cargo", "stolen trailer", "stolen truck",
        "freight theft", "trailer theft", "cargo stolen", "load stolen",
        "cargo crime", "cargo heist", "theft ring", "stolen freight",
        "cargo thieves", "theft of", "steal cargo", "steal freight",
        "steal trailer", "stolen load", "truck theft", "hijack",
        "cargo robbery", "warehouse theft", "yard theft"
    ]

    incidents = []
    
    for source, url in feeds:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            xml_text = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
            root = ET.fromstring(xml_text)
            items = root.findall(".//item")

            for item in items:
                title = ""
                link = ""
                pub_date = ""
                desc = ""
                for child in item:
                    tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    if tag == "title" and not title:
                        title = (child.text or "").strip()
                    elif tag == "link" and not link:
                        link = child.text or child.get("href", "") or ""
                    elif tag in ("pubDate",) and not pub_date:
                        pub_date = (child.text or "").strip()
                    elif tag == "description" and not desc:
                        desc = (child.text or "").strip()

                if not title:
                    continue

                # Check for theft keywords
                title_lower = title.lower()
                desc_lower = desc.lower()
                combined = title_lower + " " + desc_lower

                matched_keywords = [kw for kw in theft_keywords if kw in combined]
                if not matched_keywords:
                    continue

                # Try to geocode from title + description
                coords = geocode_city(combined)
                if not coords:
                    # Try just the title
                    coords = geocode_city(title_lower)

                lat, lng = coords if coords else (None, None)

                incidents.append({
                    "title": title,
                    "link": link,
                    "date": pub_date,
                    "source": source,
                    "keywords": matched_keywords[:3],
                    "lat": lat,
                    "lng": lng,
                })
        except Exception as e:
            print(f"  Theft {source}: {e}")

    # Load existing hotspot data
    hotspots = []
    targets = []
    tips = []
    try:
        with open(os.path.join(DATA_DIR, "theft.json")) as f:
            existing = json.load(f)
            hotspots = existing.get("hotspots", [])
            targets = existing.get("top_targets", [])
            tips = existing.get("prevention", [])
    except Exception:
        pass

    # Sort by date
    incidents.sort(key=lambda i: i.get("date") or "", reverse=True)

    path = os.path.join(DATA_DIR, "theft.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "hotspots": hotspots,
            "incidents": incidents[:15],
            "top_targets": targets,
            "prevention": tips,
            "source": "Équité Association, Insurance Bureau of Canada, industry news",
            "updated": datetime.now(timezone.utc).isoformat(),
        }, f, indent=2, default=str)

    with_coords = sum(1 for i in incidents if i.get("lat"))
    print(f"  Cargo Theft: {len(incidents)} incidents, {with_coords} geocoded")

if __name__ == "__main__":
    collect_theft_incidents()
```

## data/coverage.json
```json
{
  "generated_at": "2026-08-11T23:41:59.012591+00:00",
  "categories": {
    "fuel": {
      "records": 13,
      "history_days": 6,
      "latest_observation": "2026-08-11",
      "staleness_days": 0,
      "comparable_7d": true,
      "comparable_yoy": false
    },
    "fx": {
      "records": 1,
      "history_days": 0,
      "latest_observation": "2026-08-11",
      "staleness_days": 0,
      "comparable_7d": false,
      "comparable_yoy": false
    },
    "border": {
      "records": 9,
      "history_days": 0,
      "latest_observation": "2026-08-11",
      "staleness_days": 0,
      "comparable_7d": false,
      "comparable_yoy": false,
      "quantitative_field": "delay_minutes"
    },
    "theft": {
      "records": 8,
      "history_days": 0,
      "latest_observation": "2026-07-13",
      "staleness_days": 29,
      "comparable_7d": false,
      "comparable_yoy": false,
      "field_completeness": {
        "province": 8,
        "value_cad": 8,
        "commodity_type": 8,
        "incident_date": 8,
        "location": 8,
        "title": 8
      }
    }
  }
}```

## data/fuel.json
```json
{
  "provinces": {
    "QC": {
      "diesel": 250.0,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 8 locations"
    },
    "NB": {
      "diesel": 233.8,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 10 locations"
    },
    "NS": {
      "diesel": 227.4,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 6 locations"
    },
    "NL": {
      "diesel": 227.9,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 4 locations"
    },
    "PE": {
      "diesel": 233.0,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 1 locations"
    },
    "YT": {
      "diesel": 219.2,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 1 locations"
    },
    "BC": {
      "diesel": 229.1,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 7 locations"
    },
    "NT": {
      "diesel": 205.1,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 1 locations"
    },
    "AB": {
      "diesel": 200.4,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 6 locations"
    },
    "SK": {
      "diesel": 200.7,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 4 locations"
    },
    "MB": {
      "diesel": 208.7,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 2 locations"
    },
    "ON": {
      "diesel": 211.5,
      "gasoline": null,
      "trend": "flat",
      "note": "NRCan survey \u2014 19 locations"
    }
  },
  "diesel_national_avg": 222.2,
  "gasoline_national_avg": null,
  "updated": "2026-08-11T14:54:33.368941+00:00",
  "print_date": "Tue, 11 Aug 2026",
  "source": "Natural Resources Canada weekly diesel survey",
  "location_count": 72
}```

## data/border.json
```json
{
  "crossings": [
    {
      "id": "windsor-detroit",
      "name": "Ambassador Bridge",
      "route": "Windsor, ON \u2014 Detroit, MI",
      "highway": "ON-3 / I-75",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Busiest Canada-US commercial crossing. 8,000+ trucks/day.",
      "camera_url": "https://www.ambassadorbridge.com/traffic-cameras/",
      "status_url": "https://www.ambassadorbridge.com/",
      "authority": "Detroit International Bridge Company",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "18:15 EDT",
      "source": "cbsa"
    },
    {
      "id": "sarnia-port-huron",
      "name": "Blue Water Bridge",
      "route": "Sarnia, ON \u2014 Port Huron, MI",
      "highway": "ON-402 / I-69",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Second busiest Ontario-Michigan crossing. Twin spans, one per direction.",
      "camera_url": "https://www.bluewaterbridge.ca/traffic-cameras/",
      "status_url": "https://www.bluewaterbridge.ca/",
      "authority": "Federal Bridge Corporation",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "19:15 EDT",
      "source": "cbsa"
    },
    {
      "id": "fort-erie-buffalo",
      "name": "Peace Bridge",
      "route": "Fort Erie, ON \u2014 Buffalo, NY",
      "highway": "QEW / I-190",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Major Ontario-New York crossing. 5,000+ trucks/day.",
      "camera_url": "https://www.peacebridge.com/traffic-cameras/",
      "status_url": "https://www.peacebridge.com/",
      "authority": "Buffalo and Fort Erie Public Bridge Authority",
      "status": "Live",
      "delay": "37 min",
      "delay_minutes": 37,
      "live_updated": "19:20 EDT",
      "source": "cbsa"
    },
    {
      "id": "queenston-lewiston",
      "name": "Queenston-Lewiston Bridge",
      "route": "Queenston, ON \u2014 Lewiston, NY",
      "highway": "ON-405 / I-190",
      "commercial": true,
      "fast_lanes": false,
      "nexus": true,
      "hours": "24/7",
      "notes": "Alternative to Peace Bridge. Commercial trucks allowed, less congested.",
      "camera_url": "https://www.niagarafallsbridges.com/traffic-cameras/",
      "status_url": "https://www.niagarafallsbridges.com/",
      "authority": "Niagara Falls Bridge Commission",
      "status": "Live",
      "delay": "8 min",
      "delay_minutes": 8,
      "live_updated": "19:20 EDT",
      "source": "cbsa"
    },
    {
      "id": "lacolle-champlain",
      "name": "Lacolle Border Crossing",
      "route": "Lacolle, QC \u2014 Champlain, NY",
      "highway": "A-15 / I-87",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Busiest Quebec-New York crossing. Key corridor to eastern US.",
      "camera_url": "",
      "status_url": "",
      "authority": "CBSA / CBP",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "17:23 EDT",
      "source": "cbsa"
    },
    {
      "id": "coutts-sweetgrass",
      "name": "Coutts-Sweetgrass",
      "route": "Coutts, AB \u2014 Sweetgrass, MT",
      "highway": "AB-4 / I-15",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Busiest Alberta-Montana crossing. Key corridor to US Midwest.",
      "camera_url": "",
      "status_url": "",
      "authority": "CBSA / CBP",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "16:15 MDT",
      "source": "cbsa"
    },
    {
      "id": "pacific-blaine",
      "name": "Pacific Highway Crossing",
      "route": "Surrey, BC \u2014 Blaine, WA",
      "highway": "BC-15 / WA-543",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Busiest commercial crossing west of the Rockies.",
      "camera_url": "https://images.drivebc.ca/bchighwaycam/pub/html/www/index.html",
      "status_url": "https://drivebc.ca/",
      "authority": "CBSA / CBP",
      "status": "Live",
      "delay": "20 min",
      "delay_minutes": 20,
      "live_updated": "16:20 PDT",
      "source": "cbsa"
    },
    {
      "id": "emerson-pembina",
      "name": "Emerson-Pembina",
      "route": "Emerson, MB \u2014 Pembina, ND",
      "highway": "MB-75 / I-29",
      "commercial": true,
      "fast_lanes": true,
      "nexus": true,
      "hours": "24/7",
      "notes": "Busiest Manitoba crossing. I-29 corridor to US Midwest.",
      "camera_url": "",
      "status_url": "",
      "authority": "CBSA / CBP",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "17:15 CDT",
      "source": "cbsa"
    },
    {
      "id": "lansdowne-alexandria",
      "name": "Thousand Islands Bridge",
      "route": "Lansdowne, ON \u2014 Alexandria Bay, NY",
      "highway": "ON-137 / I-81",
      "commercial": true,
      "fast_lanes": false,
      "nexus": true,
      "hours": "24/7",
      "notes": "Key eastern Ontario crossing. Good alternative to Lacolle.",
      "camera_url": "",
      "status_url": "https://www.tibridge.com/",
      "authority": "Thousand Islands Bridge Authority",
      "status": "Live",
      "delay": "No delay",
      "delay_minutes": 0,
      "live_updated": "18:15 EDT",
      "source": "cbsa"
    }
  ],
  "blitz_dates": [
    {
      "name": "CVSA Brake Safety Week",
      "date": "2026-08-23",
      "note": "Focused brake system inspections"
    }
  ],
  "source_note": "Live CBSA data. 11/10 crossings updated.",
  "updated": "2026-08-11T23:41:59.283279"
}```

## data/theft.json
```json
{
  "hotspots": [
    {"city": "Toronto / GTA", "province": "ON", "lat": 43.70, "lng": -79.42, "risk": "high", "note": "Highest cargo theft volume in Canada."},
    {"city": "Montreal", "province": "QC", "lat": 45.51, "lng": -73.56, "risk": "high", "note": "Second highest. Port and Saint-Laurent zones."},
    {"city": "Calgary", "province": "AB", "lat": 51.04, "lng": -114.07, "risk": "medium", "note": "Increasing. Balzac and Foothills."},
    {"city": "Edmonton", "province": "AB", "lat": 53.55, "lng": -113.49, "risk": "medium", "note": "Nisku and Acheson parks."},
    {"city": "Vancouver", "province": "BC", "lat": 49.28, "lng": -123.12, "risk": "medium", "note": "Port area. Delta and Surrey."},
    {"city": "Winnipeg", "province": "MB", "lat": 49.90, "lng": -97.14, "risk": "low", "note": "Emerging. CentrePort area."}
  ],
  "incidents": [
    {
      "title": "Electronics load",
      "value": "$250,000",
      "date": "2026-07-08",
      "location": "Brampton, ON",
      "business": "Secured carrier yard — Rutherford Rd & Steeles area",
      "method": "Yard break-in overnight",
      "prevention": "High-security padlocks on all parked trailers. Motion-activated lighting. CCTV with remote monitoring.",
      "lat": 43.69,
      "lng": -79.76
    },
    {
      "title": "47 trailers recovered in theft ring bust",
      "value": "$4,000,000",
      "date": "2026-06-28",
      "location": "Greater Montreal, QC",
      "business": "Multiple industrial yards — Saint-Laurent and Anjou",
      "method": "Organized theft ring — coordinated yard hits",
      "prevention": "GPS tracking on all trailers. Geofence alerts when equipment leaves yard after hours.",
      "lat": 45.51,
      "lng": -73.56
    },
    {
      "title": "Reefer load — meat products",
      "value": "$85,000",
      "date": "2026-06-15",
      "location": "Mississauga, ON",
      "business": "Truck stop — Dixie Rd & 401 corridor",
      "method": "Stolen while driver inside truck stop",
      "prevention": "Never leave loaded reefer unattended at unsecured stops. Use attended parking or secured yards only.",
      "lat": 43.59,
      "lng": -79.64
    },
    {
      "title": "Consumer electronics — US-bound",
      "value": "$180,000",
      "date": "2026-06-02",
      "location": "Delta, BC",
      "business": "Industrial yard — Annacis Island",
      "method": "Trailer stolen from yard with fictitious paperwork",
      "prevention": "Verify carrier credentials before releasing loads. Call references. Check insurance and authorities.",
      "lat": 49.09,
      "lng": -123.06
    },
    {
      "title": "Identity theft pickup",
      "value": "$90,000",
      "date": "2026-05-18",
      "location": "Calgary, AB",
      "business": "Freight broker load — cross-dock facility",
      "method": "Fictitious pickup — stolen carrier credentials",
      "prevention": "Always verify MC number and insurance. Call the carrier directly using publicly listed number, not the one provided.",
      "lat": 51.04,
      "lng": -114.07
    },
    {
      "title": "Building materials — two trailers",
      "value": "$120,000",
      "date": "2026-05-05",
      "location": "Laval, QC",
      "business": "Industrial park — Autoroute 440 corridor",
      "method": "Coordinated yard hit — fencing cut",
      "prevention": "King pin locks on all trailers. Perimeter fencing inspections. Overnight security patrols.",
      "lat": 45.58,
      "lng": -73.75
    },
    {
      "title": "Three reefers — food products",
      "value": "$300,000",
      "date": "2026-04-22",
      "location": "Nisku, AB",
      "business": "Nisku industrial yard — 41 Ave SW",
      "method": "Weekend break-in — fence cut, trucks driven out",
      "prevention": "Weekend security patrols. Air brake valve locks. GPS on all power units and trailers.",
      "lat": 53.55,
      "lng": -113.49
    },
    {
      "title": "Five trailers — mixed freight",
      "value": "$210,000",
      "date": "2026-04-08",
      "location": "Winnipeg, MB",
      "business": "CentrePort industrial area",
      "method": "Serial thefts — unlocked trailers",
      "prevention": "Gladhand locks and king pin locks on all parked trailers. Report suspicious activity immediately.",
      "lat": 49.90,
      "lng": -97.14
    }
  ],
  "top_targets": [
    "Electronics and appliances",
    "Food and beverages (reefer loads)",
    "Building materials and metals",
    "Clothing and footwear",
    "Auto parts and tires"
  ],
  "source": "Équité Association, Insurance Bureau of Canada, industry reports",
  "updated": "2026-07-13T18:00:00+00:00"
}
```

## data/exchange.json
```json
{
  "current": 1.4206,
  "change": 0.0279,
  "change_pct": 2.0,
  "history": [
    {
      "date": "2026-08-11",
      "rate": 1.3927
    },
    {
      "date": "2026-08-10",
      "rate": 1.3942
    },
    {
      "date": "2026-08-07",
      "rate": 1.3943
    },
    {
      "date": "2026-08-06",
      "rate": 1.4018
    },
    {
      "date": "2026-08-05",
      "rate": 1.4026
    },
    {
      "date": "2026-08-04",
      "rate": 1.4068
    },
    {
      "date": "2026-07-31",
      "rate": 1.4029
    },
    {
      "date": "2026-07-30",
      "rate": 1.4014
    },
    {
      "date": "2026-07-29",
      "rate": 1.4083
    },
    {
      "date": "2026-07-28",
      "rate": 1.4102
    },
    {
      "date": "2026-07-27",
      "rate": 1.4114
    },
    {
      "date": "2026-07-24",
      "rate": 1.4093
    },
    {
      "date": "2026-07-23",
      "rate": 1.4083
    },
    {
      "date": "2026-07-22",
      "rate": 1.4088
    },
    {
      "date": "2026-07-21",
      "rate": 1.4095
    },
    {
      "date": "2026-07-20",
      "rate": 1.4054
    },
    {
      "date": "2026-07-17",
      "rate": 1.4014
    },
    {
      "date": "2026-07-16",
      "rate": 1.4038
    },
    {
      "date": "2026-07-15",
      "rate": 1.4049
    },
    {
      "date": "2026-07-14",
      "rate": 1.4067
    },
    {
      "date": "2026-07-13",
      "rate": 1.4145
    },
    {
      "date": "2026-07-10",
      "rate": 1.4146
    },
    {
      "date": "2026-07-09",
      "rate": 1.4169
    },
    {
      "date": "2026-07-08",
      "rate": 1.4174
    },
    {
      "date": "2026-07-07",
      "rate": 1.4199
    },
    {
      "date": "2026-07-06",
      "rate": 1.4219
    },
    {
      "date": "2026-07-03",
      "rate": 1.4201
    },
    {
      "date": "2026-07-02",
      "rate": 1.4181
    },
    {
      "date": "2026-06-30",
      "rate": 1.421
    },
    {
      "date": "2026-06-29",
      "rate": 1.4206
    }
  ],
  "updated": "2026-08-11T23:41:51.717611+00:00"
}```

## Git Log
```
7ab2a575 Auto-update 2026-08-11 19:41
1d242b26 Auto-update 2026-08-11 19:11
22ac2d61 Auto-update 2026-08-11 18:41
32ed0840 Auto-update 2026-08-11 18:10
92a3f9d3 Auto-update 2026-08-11 17:39
4023085e Auto-update 2026-08-11 17:08
d1a17e76 Auto-update 2026-08-11 16:37
3c8d9e7e Auto-update 2026-08-11 16:05
a8294419 Auto-update 2026-08-11 15:34
cb70993a Auto-update 2026-08-11 15:03
59531514 Auto-update 2026-08-11 14:32
b49964f2 Auto-update 2026-08-11 14:01
6fae6361 Auto-update 2026-08-11 13:30
be23ee2a Auto-update 2026-08-11 12:58
d65d1dc4 Auto-update 2026-08-11 12:28
5f78ebb4 Auto-update 2026-08-11 11:56
148c7b00 Auto-update 2026-08-11 11:25
dc4835de Auto-update 2026-08-11 10:54
24a7fdd9 Auto-update 2026-08-11 10:23
129eb0d7 Auto-update 2026-08-11 09:52
```
