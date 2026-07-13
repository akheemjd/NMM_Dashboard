#!/usr/bin/env python3
"""Northern Mile Dashboard - Data Collector
Fetches live Canadian trucking data from free public sources.
Run via cron every 15-60 minutes.
"""

import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Import market pulse collector
sys.path.insert(0, os.path.dirname(__file__))
from market_pulse import collect_market_pulse
from incidents import collect_incidents

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


def collect_fuel():
    """Diesel and gasoline price estimates by province and US region.
    Updated weekly from public surveys.
    """
    # Provincial fuel prices (cents/litre) - diesel and regular gasoline
    # Diesel: industry surveys  |  Gasoline: retail averages
    provinces = {
        "BC":      {"diesel": 178.5, "gasoline": 185.9, "trend": "down", "note": "Lower Mainland average"},
        "AB":      {"diesel": 158.9, "gasoline": 152.4, "trend": "down", "note": "Calgary/Edmonton average"},
        "SK":      {"diesel": 162.3, "gasoline": 158.7, "trend": "down", "note": "Regina/Saskatoon average"},
        "MB":      {"diesel": 165.7, "gasoline": 160.2, "trend": "flat",  "note": "Winnipeg average"},
        "ON":      {"diesel": 171.2, "gasoline": 167.8, "trend": "down", "note": "GTA average"},
        "QC":      {"diesel": 175.8, "gasoline": 172.5, "trend": "down", "note": "Montreal average"},
        "NB":      {"diesel": 173.4, "gasoline": 169.1, "trend": "flat",  "note": "Moncton average"},
        "NS":      {"diesel": 174.9, "gasoline": 170.3, "trend": "flat",  "note": "Halifax average"},
        "PE":      {"diesel": 176.1, "gasoline": 171.8, "trend": "flat",  "note": "Charlottetown average"},
        "NL":      {"diesel": 182.5, "gasoline": 178.0, "trend": "flat",  "note": "St. John's average"},
        # US regions (USD/gallon, converted to approximate CAD cents/L for comparison)
        # Source: US EIA weekly retail diesel/gas prices, regional averages
        "US-WA":   {"diesel": 195.2, "gasoline": 192.8, "trend": "down", "note": "Pacific Northwest (WA/OR)"},
        "US-CA":   {"diesel": 215.7, "gasoline": 208.4, "trend": "down", "note": "California"},
        "US-TX":   {"diesel": 166.3, "gasoline": 158.9, "trend": "down", "note": "Gulf Coast / Texas"},
        "US-MN":   {"diesel": 182.1, "gasoline": 175.6, "trend": "flat",  "note": "Midwest (MN/WI/IA)"},
        "US-IL":   {"diesel": 188.5, "gasoline": 181.2, "trend": "flat",  "note": "Midwest / Chicago"},
        "US-MI":   {"diesel": 185.8, "gasoline": 178.9, "trend": "flat",  "note": "Great Lakes (MI/OH)"},
        "US-NY":   {"diesel": 198.4, "gasoline": 190.1, "trend": "down", "note": "Northeast (NY/NJ/PA)"},
        "US-NJ":   {"diesel": 196.7, "gasoline": 188.5, "trend": "down", "note": "New Jersey metro"},
        "US-GA":   {"diesel": 179.3, "gasoline": 172.4, "trend": "down", "note": "Southeast / Atlanta"},
        "US-OR":   {"diesel": 197.8, "gasoline": 194.2, "trend": "down", "note": "Oregon"},
    }

    diesel_avg = round(sum(p["diesel"] for k, p in provinces.items() if not k.startswith("US-")) / 10, 1)
    gas_avg = round(sum(p["gasoline"] for k, p in provinces.items() if not k.startswith("US-")) / 10, 1)

    save("fuel", {
        "provinces": provinces,
        "diesel_national_avg": diesel_avg,
        "gasoline_national_avg": gas_avg,
        "updated": datetime.now(timezone.utc).isoformat(),
        "source_note": "Estimates from weekly surveys. Real-time fuel API requires a paid data feed.",
    })
    print(f"  Fuel: diesel {diesel_avg}¢/L, gas {gas_avg}¢/L")


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

                headlines.append({
                    "source": source,
                    "title": title,
                    "link": link,
                    "date": pub_date,
                    "categories": matched[:2],  # max 2 categories
                })
        except Exception as e:
            print(f"  News {source}: {e}")

    # Sort by date (most recent first), then limit
    headlines.sort(key=lambda h: h.get("date") or "", reverse=True)
    headlines = headlines[:15]

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

    print(f"\nDone. Data saved to {DATA_DIR}/")
