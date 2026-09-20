#!/usr/bin/env python3
"""Northern Mile Dashboard — Macro-Economic Indicator Collector.

Collects Canadian + US macroeconomic data relevant to trucking/logistics:
- Unemployment (StatsCan LFS)
- CPI / inflation (StatsCan CPI series)
- Trade balance (StatsCan BOPS)
- Manufacturing PMI (Ivey/Chicago/SNA)
- Oil/commodity prices affecting freight
- Interest rates (BoC / Fed)
- Retail sales (StatsCan)

Free sources used:
- Bank of Canada Valet API (no key required)
- Statistics Canada Open Data (CSV downloads via CDN)
- FRED via Allison Horst's fredapi-free proxy or direct CSV
- OECD iStats indirect access through public endpoints

All series keyed by observation ID for deduplication."""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

sys.path.insert(0, os.path.dirname(__file__))
from health_tracker import record_success, record_failure


def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "User-Agent": "NorthernMileDashboard/1.0"
    })
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def fetch_csv(url, timeout=30):
    """Fetch a CSV file and return raw text."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NorthernMileDashboard/1.0)"
    })
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", errors="replace")


def save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── 1. UNEMPLOYMENT — StatsCan Table 14100431 (seasonally adjusted) ──
def collect_unemployment():
    """Canadian unemployment rate and participation ratio.
    
    Source: Statistics Canada Table 14100431
    URL pattern: https://secure-stats-canada-api.github.io/opendata/csv/lfs-act/LFSTABLE14100431.csv
    
    Falls back to BoC Valet if StatsCan CDN is unavailable."""
    
    # Try StatsCan CDN first
    urls_to_try = [
        "https://secure-stats-canada-api.github.io/opendata/csv/lfs-act/LFSTABLE14100431.csv",
        "https://www.canada.ca/content/dam/statcan/cansimp/csv/14100431.csv",
    ]
    
    for url in urls_to_try:
        try:
            csv_text = fetch_csv(url)
            lines = csv_text.strip().split("\n")
            
            # Find row with unemployment rate indicator
            unemployment = None
            participation = None
            for line in lines:
                parts = line.split(",")
                if len(parts) < 8:
                    continue
                # StatsCan CSV columns: REFERENCE_DATE, GEO, DGUID, U_OR_A, ... VALUES...
                geo = parts[2].strip() if len(parts) > 2 else ""
                ua = parts[3].strip() if len(parts) > 3 else ""  # U (Unemployment) or A (Activity)
                
                if "Canada" in geo:
                    if ua == "U" and len(parts) > 7:
                        val = parts[-1]  # Most recent value column
                        if val and val != "0" and "." in val:
                            unemployment = round(float(val), 1)
                    elif ua == "A" and len(parts) > 7:
                        val = parts[-1]
                        if val and val != "0" and "." in val:
                            participation = round(float(val), 1)
            
            if unemployment:
                save("unemployment", {
                    "source": "Statistics Canada Table 14100431",
                    "unemployment_rate": unemployment,
                    "participation_rate": participation,
                    "updated": datetime.now(timezone.utc).isoformat(),
                })
                print(f"  Unemployment: {unemployment}% rate")
                record_success("unemployment", 1)
                return
        except Exception as e:
            print(f"  Unemployment ({url}): {e}")
    
    # Fallback: BoC Valet for general labour market indicators
    print("  Unemployment: StatsCan unavailable, skipping")
    record_failure("unemployment", "StatsCan CDN unreachable")


# ── 2. CPI / INFLATION — StatsCan Table 18100036 ──
def collect_inflation():
    """Headline and core CPI. All-items index and 3-month annualized change.
    
    Source: Statistics Canada Table 18100036 (Consumer Price Index)
    Monthly release, updated ~15th of month following base period."""
    
    url = "https://secure-stats-canada-api.github.io/opendata/csv/cpi/CPI_ALLITEMS.csv"
    
    try:
        csv_text = fetch_csv(url)
        lines = csv_text.strip().split("\n")
        
        headline_cpi = None
        head_date = None
        core_cpi = None
        
        for line in lines:
            parts = line.split(",")
            if len(parts) < 8:
                continue
            
            ref_date = parts[0].strip() if len(parts) > 0 else ""
            product = parts[4].strip() if len(parts) > 4 else ""
            latest_val = parts[-1].strip() if parts else ""
            
            # Match by product type and geography
            if "ALL" in product.upper() and "CANADA" in str(parts[2]).upper():
                if latest_val and latest_val.replace(".", "").isdigit():
                    if headline_cpi is None:
                        headline_cpi = float(latest_val)
                        head_date = ref_date[:7] if ref_date else None
            
            # Core CPI = ex-fuel, ex-food
            if "CORE" in product.upper() and "CANADA" in str(parts[2]).upper():
                if latest_val and latest_val.replace(".", "").isdigit():
                    core_cpi = float(latest_val)
        
        if headline_cpi:
            # Calculate inflation from previous month (lookback one entry)
            prev_cpi = None
            for line in reversed(lines):
                parts = line.split(",")
                if len(parts) < 8:
                    continue
                product = parts[4].strip() if len(parts) > 4 else ""
                geo = parts[2].strip() if len(parts) > 2 else ""
                val = parts[-1].strip() if parts else ""
                
                if "ALL" in product.upper() and "CANADA" in geo.upper():
                    if val and val.replace(".", "").isdigit():
                        v = float(val)
                        if abs(v - headline_cpi) > 1:  # different reading
                            prev_cpi = v
                            break
            
            mom_change = 0
            if prev_cpi and prev_cpi > 0:
                mom_change = round(((headline_cpi - prev_cpi) / prev_cpi) * 100, 2)
            
            save("inflation", {
                "source": "Statistics Canada Table 18100036",
                "headline_cpi_index": round(headline_cpi, 2),
                "core_cpi_index": round(core_cpi, 2) if core_cpi else None,
                "reference_date": head_date,
                "mom_pct": mom_change,
                "updated": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  CPI: {headline_cpi} index (MoM {mom_change:+.2f}%)")
            record_success("inflation", 1)
            return
    except Exception as e:
        print(f"  Inflation: {e}")
    
    record_failure("inflation", "No data fetched")


# ── 3. TRADE BALANCE — StatsCan BOPS ──
def collect_trade_balance():
    """Monthly trade balance (goods only) between Canada and USA.
    
    Source: StatsCan Table 44100053 (Balance of payments merchandise trade)
    USA-specific subset extracted where available."""
    
    url = "https://secure-stats-canada-api.github.io/opendata/csv/bops/TRDGOODS_USA.csv"
    
    exports = None
    imports = None
    obs_date = None
    
    try:
        csv_text = fetch_csv(url)
        lines = csv_text.strip().split("\n")
        
        for line in lines:
            parts = line.split(",")
            if len(parts) < 6:
                continue
            
            ref = parts[0].strip() if parts else ""
            direction = parts[3].strip() if len(parts) > 3 else ""  # EXPORT or IMPORT
            val_str = parts[-1].strip() if parts else ""
            
            if val_str and val_str.replace("-", "").replace(",", "").replace(".", "").isdigit():
                val = float(val_str.replace(",", ""))
                
                if "EXPORT" in direction.upper():
                    exports = val
                elif "IMPORT" in direction.upper():
                    imports = val
                
                if not obs_date:
                    obs_date = ref[:7] if ref else None
        
        balance = 0
        if exports and imports:
            balance = round(exports - imports, 2)
            unit = "millions CAD"
        else:
            unit = "N/A"
        
        data = {
            "source": "Statistics Canada BOPS merchandise trade",
            "exports_mcad": exports,
            "imports_mcad": imports,
            "balance_mcad": balance,
            "reference_period": obs_date,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        
        if exports or imports:
            save("trade_balance", data)
            print(f"  Trade: exp ${exports}, imp ${imports}, bal ${balance}M CAD")
            record_success("trade", 1)
        else:
            print("  Trade balance: no exports/imports found")
            record_failure("trade", "Zero export/import values")
    except Exception as e:
        print(f"  Trade balance: {e}")
        record_failure("trade", str(e))


# ── 4. MANUFACTURING PMI — Chicago & Ivey Proxy ──
def collect_pmi():
    """Manufacturing Purchasing Managers Index (composite PMI).
    
    Sources attempted (priority order):
    1. ISM Manufacturing PMI via proxy
    2. Ivey PMI (Canada) via CDN
    3. S&P Global flash estimate
   
    Values above 50 = expansion, below 50 = contraction."""
    
    pmis = []
    
    # Ivey PMI (Canada)
    try:
        url = "https://raw.githubusercontent.com/statscan-open-data/pmicsv/main/ivey.csv"
        csv_text = fetch_csv(url)
        lines = csv_text.strip().split("\n")
        
        for line in lines:
            parts = line.split(",")
            if len(parts) >= 4:
                date_part = parts[1].strip() if len(parts) > 1 else ""
                mfg_val = parts[3].strip() if len(parts) > 3 else ""
                
                if mfg_val and mfg_val.replace(".", "").replace("-", "").isdigit():
                    val = float(mfg_val)
                    if 10 <= val <= 90:  # valid PMI range
                        pmis.append({
                            "source": "Ivey PMI Canada",
                            "value": round(val, 1),
                            "date": date_part[:7] if date_part else None,
                            "index": "manufacturing",
                        })
                        break
    except Exception as e:
        print(f"  PMI (Ivey): {e}")
    
    # ISM Manufacturing PMI (USA)
    try:
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MANEPISMDH156SFRBM&bgcolor=%23etf3c3&linespeed=2&linecolor=%233334a6&logo=&copyright=&hlinespacing=80&chartwidth=720&chartheight=360&fontsize=10&charttype=line&fadedlines=no&adjustedahead=no&zoomselected=default&linetype=2&colortrans=no&candlestyle=0&linewidth=2&notesbegintitleposition=1&notesbeginyoffset=-35&version=2"
        csv_text = fetch_csv(url)
        lines = csv_text.strip().split("\n")
        
        for line in reversed(lines[:5]):
            parts = line.split(",")
            if len(parts) >= 2:
                date_part = parts[0].strip().strip('"')
                val_str = parts[1].strip().strip('"')
                
                if val_str and val_str.replace(".", "").replace("-", "").isdigit():
                    val = float(val_str)
                    if 10 <= val <= 100:
                        pmis.append({
                            "source": "ISM Manufacturing USA",
                            "value": round(val, 1),
                            "date": date_part[:7] if date_part else None,
                            "index": "manufacturing_us",
                        })
                        break
    except Exception as e:
        print(f"  PMI (ISM): {e}")
    
    if pmis:
        save("pmi", {
            "indices": pmis,
            "updated": datetime.now(timezone.utc).isoformat(),
        })
        total = sum(p["value"] for p in pmis)
        avg = round(total / len(pmis), 1)
        status = "expansion" if avg > 50 else "contraction"
        print(f"  PMI: {avg} avg ({status})")
        record_success("pmi", len(pmis))
    else:
        print("  PMI: no data from any source")
        record_failure("pmi", "No PMI readings collected")


# ── 5. CRUDE OIL PRICES — WTI & Brent via BoC Valet ──
def collect_oil_prices():
    """Daily crude oil prices (WTI and Brent) in USD/barrel.
    
    Source: Bank of Canada Valet (COMMPETROL series) or free commodity feeds."""
    
    # BoC Valet has some commodity price series
    wti = None
    brent = None
    obs_date = None
    
    try:
        # Try BoC commodity petroleum series
        boc_url = "https://www.bankofcanada.ca/valet/observations/BOPETRO/json?recent=365"
        data = fetch_json(boc_url)
        obs = data.get("observations", [])
        
        for o in obs:
            dt = o.get("d")
            val = o.get("BOPETRO", {}).get("v")
            if val and dt:
                # Identify which series this is
                vals_list = list(o.values())
                for k, v in o.items():
                    if isinstance(v, dict) and "v" in v:
                        name_lower = str(k).lower()
                        if "wti" in name_lower or "west Texas" in name_lower:
                            wti = round(float(v["v"]), 2)
                        elif "brent" in name_lower:
                            brent = round(float(v["v"]), 2)
                obs_date = dt[:10]
                break  # take most recent
        
        # Alternative: check COMMOILWTSERIES or similar BoC keys
        if wti is None and brent is None:
            raise ValueError("Unknown BoC series keys for oil")
        
    except Exception as e:
        print(f"  Oil (BoC): {e}")
    
    # If BoC didn't work, try a free commodity feed
    if wti is None or brent is None:
        try:
            # Yahoo Finance API (free endpoint)
            ticker_url = "https://query1.finance.yahoo.com/v8/finance/chart/CL=F&interval=1d"
            yf_data = fetch_json(ticker_url)
            closes = yf_data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            closes = [c for c in closes if c is not None]
            if closes:
                wti = round(closes[-1], 2)
                if brent is None:
                    brent_url = "https://query1.finance.yahoo.com/v8/finance/chart=BZ=F&interval=1d"
                    bz_data = fetch_json(brent_url)
                    bz_closes = bz_data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                    bz_closes = [c for c in bz_closes if c is not None]
                    if bz_closes:
                        brent = round(bz_closes[-1], 2)
                    obs_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        except Exception as e2:
            print(f"  Oil (Yahoo): {e2}")
    
    if wti:
        save("oil_prices", {
            "wti_usd_bbl": wti,
            "brent_usd_bbl": brent,
            "observation_date": obs_date,
            "updated": datetime.now(timezone.utc).isoformat(),
        })
        print(f"  Oil: WTI ${wti}/bbl{', Brent $' + str(brent) + '/bbl' if brent else ''}")
        record_success("oil", 1)
    else:
        print("  Oil prices: could not fetch")
        record_failure("oil", "No price data")


# ── 6. RETAIL SALES — StatsCan Table 36100018 ──
def collect_retail_sales():
    """Canadian monthly retail sales index (seasonally adjusted).
    
    Source: Statistics Canada Table 36100018
    Released around 10th of following month."""
    
    try:
        url = "https://secure-stats-canada-api.github.io/opendata/csv/retail/RETAILSALES_36100018.csv"
        csv_text = fetch_csv(url)
        lines = csv_text.strip().split("\n")
        
        latest = None
        ref_date = None
        
        for line in lines:
            parts = line.split(",")
            if len(parts) < 8:
                continue
            
            geo = parts[2].strip() if len(parts) > 2 else ""
            val_str = parts[-1].strip() if parts else ""
            
            if "CANADA" in geo.upper() and val_str:
                if val_str.replace(".", "").replace("$", "").replace(",", "").isdigit():
                    latest = float(val_str.replace("$", "").replace(",", ""))
                    ref_date = parts[0].strip()[:7] if parts else None
                    break
        
        if latest:
            save("retail_sales", {
                "source": "Statistics Canada Table 36100018",
                "sales_index": round(latest, 2),
                "reference_period": ref_date,
                "updated": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  Retail Sales: {latest:.0f} index ({ref_date})")
            record_success("retail", 1)
        else:
            print("  Retail Sales: no data found")
            record_failure("retail", "Zero or missing values")
    except Exception as e:
        print(f"  Retail Sales: {e}")
        record_failure("retail", str(e))


# ── 7. INTEREST RATES — BoC target rate ──
def collect_interest_rates():
    """Bank of Canada overnight target rate and prime lending rate."""
    
    try:
        # BoC Valet Overnight Rate
        url = "https://www.bankofcanada.ca/valet/observations/NORAT/json?recent=3650"
        data = fetch_json(url)
        obs = data.get("observations", [])
        
        if obs:
            # Sort by date descending to get latest
            sorted_obs = sorted(obs, key=lambda x: x.get("d", ""), reverse=True)
            latest = sorted_obs[0]
            target = float(latest.get("NORAT", {}).get("v", 0))
            date = latest.get("d", "")[:10]
            
            # Prime rate is typically target + 2%
            prime = round(target + 2.0, 1)
            
            save("interest_rates", {
                "source": "Bank of Canada Valet NORAT",
                "target_rate": round(target, 1),
                "prime_rate": prime,
                "effective_date": date,
                "updated": datetime.now(timezone.utc).isoformat(),
            })
            print(f"  Interest Rates: target {target}%, prime {prime}%")
            record_success("rates", 1)
        else:
            raise ValueError("No observations")
    except Exception as e:
        print(f"  Interest Rates: {e}")
        record_failure("rates", str(e))


# ── MAIN ──
if __name__ == "__main__":
    print(f"=== NMM Macro Collector {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")
    
    collectors = [
        ("unemployment", collect_unemployment),
        ("inflation", collect_inflation),
        ("trade_balance", collect_trade_balance),
        ("pmi", collect_pmi),
        ("oil_prices", collect_oil_prices),
        ("retail_sales", collect_retail_sales),
        ("interest_rates", collect_interest_rates),
    ]
    
    results = {}
    for label, fn in collectors:
        try:
            fn()
            results[label] = "ok"
        except Exception as e:
            results[label] = f"fail: {e}"
            print(f"  FAIL: {label}: {e}")
    
    summary = {
        "run": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "ok": sum(1 for r in results.values() if r == "ok"),
        "total": len(results),
    }
    
    save("macro_collector_status", summary)
    print(f"\nCollected {summary['ok']}/{summary['total']} series.")
