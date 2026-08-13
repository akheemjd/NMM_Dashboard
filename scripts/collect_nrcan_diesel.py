#!/usr/bin/env python3
"""NRCan diesel price collector — scrapes the RSS feed for 60+ Canadian locations.
Fetches NRCan weekly diesel survey via RSS (productID=5).
Runs: every 30 min via collector pipeline."""

import json, os, sys, urllib.request, xml.etree.ElementTree as ET
import unicodedata
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

def _norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").strip()

CITY_PROVINCE_NORM = {_norm(k): v for k, v in CITY_PROVINCE.items()}

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
        
        # Guard: a repeated title with a different price signals a same-named
        # location collision (two distinct cities sharing a name). Fail loudly.
        if city in prices and prices[city] != price:
            raise ValueError(
                f"Duplicate NRCan city title with differing price: {city} "
                f"({prices[city]} vs {price})"
            )
        if city not in prices:
            prices[city] = price
    
    return prices, pub_date


def compute_provincial(prices):
    """Average city prices into provincial + national figures."""
    # Hard-fail on any city that doesn't resolve to a province (accent-normalized).
    unmapped = [c for c in prices if _norm(c) not in CITY_PROVINCE_NORM]
    if unmapped:
        raise ValueError(f"Unmapped NRCan cities: {unmapped}")

    provinces = {}
    for city, price in prices.items():
        prov = CITY_PROVINCE_NORM[_norm(city)]
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
    if len(indexed) != len(INDEX_PROVINCES):
        missing = [p for p in INDEX_PROVINCES if p not in result]
        raise ValueError(f"NMDI requires all 10 index provinces, missing: {missing}")
    national_avg = round(sum(indexed) / len(indexed), 1)
    
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
        if not os.path.exists(os.path.join(DATA_DIR, "fuel.json")):
            raise
        print("  Keeping last good fuel.json on disk. Staleness will be reported by coverage.")
        return False


if __name__ == "__main__":
    collect()
