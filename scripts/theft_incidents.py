#!/usr/bin/env python3
"""Collect cargo theft incidents from news RSS feeds.
Filters for theft-related headlines, extracts location, and geocodes.
"""

import json, os, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FEEDS = [
    ("Inside Logistics", "https://www.insidelogistics.ca/feed/"),
    ("Canadian Trucking Alliance", "https://cantruck.ca/feed/"),
]

UA = "Mozilla/5.0 (compatible; NorthernMileDashboard/1.0; +https://dashboard.northernmilemedia.com)"

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

def parse_date(s):
    """Parse an RSS pubDate string into a timezone-aware datetime, or None."""
    if not s:
        return None
    s = s.strip()
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    try:
        return parsedate_to_datetime(s)
    except Exception:
        pass
    return None

def collect_theft_incidents():
    """Search RSS feeds for cargo theft stories and geocode them."""
    
    theft_keywords = [
        "cargo theft", "stolen cargo", "stolen trailer", "stolen truck",
        "freight theft", "trailer theft", "cargo stolen", "load stolen",
        "cargo crime", "cargo heist", "theft ring", "stolen freight",
        "cargo thieves", "theft of", "steal cargo", "steal freight",
        "steal trailer", "stolen load", "truck theft", "hijack",
        "cargo robbery", "warehouse theft", "yard theft"
    ]

    incidents = []
    feed_status = []

    for source, url in FEEDS:
        status = "unknown"
        items_seen = 0
        matched = 0
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            xml_text = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", errors="replace")
            status = 200
            root = ET.fromstring(xml_text)
            items = root.findall(".//item")
            items_seen = len(items)

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

                # Canada only. A US theft story is not our beat and the
                # geocoder will happily place it in a same-named city.
                canada_words = [
                    "canada", "canadian", "ontario", "quebec", "alberta",
                    "british columbia", "manitoba", "saskatchewan",
                    "nova scotia", "new brunswick", "newfoundland",
                    "toronto", "montreal", "vancouver", "calgary",
                    "edmonton", "ottawa", "winnipeg", "halifax", "brampton",
                    "mississauga", "peel", "surrey", "delta", "laval",
                    "opp", "rcmp", "sûreté", "surete",
                ]
                if not any(w in combined for w in canada_words):
                    continue

                # Try to geocode from title + description
                coords = geocode_city(combined)
                if not coords:
                    # Try just the title
                    coords = geocode_city(title_lower)

                lat, lng = coords if coords else (None, None)

                if not link:
                    continue

                incidents.append({
                    "title": title,
                    "source_url": link,
                    "date": pub_date,
                    "source": source,
                    "keywords": matched_keywords[:3],
                    "location": "",
                    "lat": lat,
                    "lng": lng,
                    "geocoded": bool(coords),
                })
                matched += 1
        except Exception as e:
            status = str(e)
            print(f"  Theft {source}: {e}")

        feed_status.append({
            "name": source,
            "url": url,
            "status": status,
            "items_seen": items_seen,
            "matched": matched,
        })

    # Load existing data and merge new matches (accumulate, don't replace)
    targets = []
    tips = []
    existing_incidents = []
    try:
        with open(os.path.join(DATA_DIR, "theft.json")) as f:
            existing = json.load(f)
            existing_incidents = existing.get("incidents", [])
            targets = existing.get("top_targets", [])
            tips = existing.get("prevention", [])
    except Exception:
        pass

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=90)
    seen = set()
    merged = []

    def keepable(rec):
        url = rec.get("source_url")
        if not url:
            return None
        d = parse_date(rec.get("date"))
        if d is None or d < cutoff:
            return None
        return d

    for rec in existing_incidents:
        if keepable(rec) is None:
            continue
        seen.add(rec["source_url"])
        merged.append(rec)

    first_seen = now.isoformat()
    for rec in incidents:
        if keepable(rec) is None:
            continue
        if rec["source_url"] in seen:
            continue
        rec["first_seen"] = first_seen
        seen.add(rec["source_url"])
        merged.append(rec)

    # Sort newest first by parsed publication date
    merged.sort(
        key=lambda r: parse_date(r.get("date")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    path = os.path.join(DATA_DIR, "theft.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "incidents": merged,
            "feeds": feed_status,
            "top_targets": targets,
            "prevention": tips,
            "source": "industry news feeds",
            "updated": now.isoformat(),
        }, f, indent=2, default=str)

    with_coords = sum(1 for i in merged if i.get("lat"))
    print(f"  Cargo Theft: {len(merged)} incidents, {with_coords} geocoded")

if __name__ == "__main__":
    collect_theft_incidents()
