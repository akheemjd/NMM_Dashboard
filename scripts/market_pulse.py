import urllib.request, io, zipfile, csv, json, os
from datetime import datetime, timezone

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
        # Compare to a rough baseline of 165 cents
        baseline = 165
        fuel_pct = round((diesel_avg - baseline) / baseline * 100, 1)

        pulse["indicators"].append({
            "name": "Fuel Cost",
            "label": "Diesel vs baseline",
            "value": f"{diesel_avg:.1f}¢/L",
            "detail": f"{fuel_pct:+.1f}% vs 165¢ baseline",
            "direction": "down" if fuel_pct < 0 else "up",
            "source": "Industry surveys",
            "what_it_means": "Fuel is typically 25-35% of operating costs. Above baseline = margin pressure."
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
        # Rough baseline
        fx_baseline = 1.35
        fx_pct = round((rate - fx_baseline) / fx_baseline * 100, 1)
        direction = "down" if fx_pct < 0 else "up"
        pulse["indicators"].append({
            "name": "CAD Impact",
            "label": "USD/CAD vs 1.35 baseline",
            "value": f"{rate:.4f}",
            "detail": f"{fx_pct:+.1f}% — {'weaker CAD' if direction=='up' else 'stronger CAD'}",
            "direction": direction,
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
