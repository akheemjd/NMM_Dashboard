#!/usr/bin/env python3
"""Generate SEO landing pages for all Northern Mile dashboard modules."""
import json, os
from datetime import datetime

BASE = os.path.expanduser("~/northern-mile-dashboard")
DATA = os.path.join(BASE, "data")
DOCS = os.path.join(BASE, "docs")

def load(name):
    path = os.path.join(DATA, name)
    return json.load(open(path)) if os.path.exists(path) else {}

def write_page(path, title, desc, body):
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | Northern Mile</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://dashboard.northernmilemedia.com{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<style>
  :root{{--bg:#15171A;--card:#1E2227;--text:#E8EAEC;--muted:#8B939C;--green:#1F6B4A;--amber:#F2A900;--red:#D93A34;--line:#2C3238;--rad:8px}}
  body{{background:var(--bg);color:var(--text);font-family:Inter,-apple-system,sans-serif;margin:0;line-height:1.5}}
  .banner{{background:var(--card);border-bottom:1px solid var(--line);padding:16px 24px;display:flex;justify-content:space-between;align-items:center}}
  .banner h1{{font-size:1rem;margin:0}} .banner a{{color:var(--muted);font-size:0.75rem;text-decoration:none}}
  main{{max-width:900px;margin:0 auto;padding:24px 20px}}
  h2{{font-size:1rem;margin:24px 0 12px}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:16px;margin-bottom:10px}}
  .price{{font-size:2rem;font-weight:700;font-family:'Barlow Condensed',sans-serif}}
  .green{{color:var(--green)}}.amber{{color:var(--amber)}}.red{{color:var(--red)}}
  .muted{{color:var(--muted);font-size:0.75rem}}
  table{{width:100%;border-collapse:collapse;font-size:0.875rem}}
  th{{text-align:left;padding:8px;border-bottom:2px solid var(--line);font-size:0.625rem;text-transform:uppercase;color:var(--muted)}}
  td{{padding:8px;border-bottom:1px solid var(--line)}}.val{{text-align:right;font-family:'IBM Plex Mono',monospace}}
  .updated{{text-align:center;font-size:0.75rem;color:var(--muted);padding:16px}}
  .cta{{text-align:center;margin:32px 0;padding:24px;background:var(--card);border:2px solid var(--amber);border-radius:var(--rad)}}
  .cta h3{{color:var(--amber);font-size:0.8125rem;margin:0 0 8px;text-transform:uppercase}}
  footer{{text-align:center;padding:24px;font-size:0.625rem;color:var(--muted);border-top:1px solid var(--line)}}
  a{{color:var(--amber);text-decoration:none}}
</style>
</head>
<body>
<div class="banner">
  <h1>{title}</h1>
  <a href="/">← Dashboard</a>
</div>
<main>
{body}
  <div class="updated">Updated {datetime.utcnow().isoformat()[:16].replace('T',' ')}</div>
  <div class="cta">
    <h3>Never miss a market move</h3>
    <p style="margin:0 0 4px;">Get fuel prices, border updates, and market shifts in your inbox every Wednesday.</p>
    <p class="muted" style="margin-top:8px;"><a href="https://northernmilemedia.com">Sign up for the Northern Mile Brief →</a></p>
  </div>
</main>
<footer>&copy; 2026 Northern Mile Media &middot; Data from public sources &middot; Informational use only</footer>
</body>
</html>'''
    os.makedirs(os.path.dirname(os.path.join(DOCS, path.lstrip("/") + "index.html")), exist_ok=True)
    with open(os.path.join(DOCS, path.lstrip("/") + "index.html"), "w") as f:
        f.write(html)

# === 1. Fuel Prices ===
f = load('fuel.json')
rows = ''
provinces = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']
for p in provinces:
    d = f.get('provinces',{}).get(p,{}).get('diesel','—')
    rows += f'<tr><td>{p}</td><td class="val">{d}</td><td class="val">¢/L</td></tr>\n'
write_page('/fuel-prices/', 'Canadian Diesel Prices by Province — Live Updates',
    'Live diesel prices for every Canadian province. BC, Alberta, Ontario, Quebec and more. Updated daily. Free.',
    f'''<p class="muted">National average diesel price: <strong style="color:var(--text);">{f.get("diesel_national_avg","—")}¢/L</strong></p>
    <table><tr><th>Province</th><th class="val">Diesel (¢/L)</th><th class="val">Unit</th></tr>{rows}</table>''')

# === 2. Exchange Rate ===
ex = load('exchange.json')
fx = ex.get('current', ex.get('close','—'))
chg = ex.get('change','—')
up = isinstance(chg, str) and chg.startswith('+') or (isinstance(chg,(int,float)) and chg>0)
write_page('/exchange-rate/', 'CAD to USD Exchange Rate — Live Canadian Dollar',
    'Live CAD/USD exchange rate. Canadian dollar to US dollar. Updated from Bank of Canada. Free.',
    f'''<div class="card"><div class="price">{fx}</div><p class="muted">Canadian Dollar to US Dollar</p><p class="{'green' if up else 'red'}">{chg}</p></div>
    <p class="muted">Impacts cross-border freight rates, fuel costs, and equipment imports. A weaker loonie means Canadian exports are more competitive.</p>''')

# === 3. Road Incidents ===
inc = load('incidents.json')
rows = ''
for i in inc.get('incidents',[])[:20]:
    rows += f'<tr><td>{i.get("description","")[:60]}</td><td>{i.get("highway","—")}</td><td class="val">{i.get("severity","—")}</td></tr>\n'
write_page('/road-incidents/', 'Canadian Highway Incidents — Live Road Closures & Delays',
    'Live Canadian highway incidents for truckers. Road closures, accidents, construction delays. Ontario 511, DriveBC, and more.',
    f'''<p class="muted">Active highway incidents affecting commercial truck routes. Check before you dispatch.</p>
    <table><tr><th>Incident</th><th>Highway</th><th class="val">Severity</th></tr>{rows}</table>''')

# === 4. Cargo Theft ===
th = load('theft.json')
rows = ''
for t in th.get('incidents',[])[:10]:
    rows += f'<tr><td>{t["title"][:50]}</td><td>{t.get("location","—")}</td><td class="val red">${t.get("value","—")}</td></tr>\n'
hotspots = ''.join(f'<tr><td>{h["city"]}</td><td>{h["note"]}</td></tr>\n' for h in th.get('hotspots',[]))
write_page('/cargo-theft/', 'Canadian Cargo Theft Reports — Live Incidents & Hotspots',
    'Cargo theft incidents and hotspots across Canada. Toronto, Montreal, Calgary, Vancouver. Free tracking for truckers and fleet operators.',
    f'''<h2>Recent Incidents</h2>
    <table><tr><th>Incident</th><th>Location</th><th class="val">Value</th></tr>{rows}</table>
    <h2>Hotspots</h2>
    <table><tr><th>City</th><th>Risk</th></tr>{hotspots}</table>''')

# === 5. Market Pulse ===
mk = load('market.json')
indicators = [
    ('GDP Growth', mk.get('gdp','—'), 'Monthly'),
    ('Freight Trend', mk.get('freight_trend','—'), 'Year-over-year'),
    ('Diesel vs Baseline', mk.get('diesel_vs_baseline','—'), 'Current spread'),
    ('BC vs AB Spread', mk.get('bc_ab_spread','—'), 'Current gap'),
]
rows = ''.join(f'<tr><td>{n}</td><td class="val">{v}</td><td>{p}</td></tr>\n' for n,v,p in indicators)
write_page('/market-pulse/', 'Canadian Trucking Market Indicators — GDP, Freight, Fuel Trends',
    'Canadian trucking market indicators: GDP growth, freight trends, diesel prices, and provincial fuel spreads. Free data.',
    f'''<table><tr><th>Indicator</th><th class="val">Value</th><th>Period</th></tr>{rows}</table>''')

# === 6. Industry News ===
news = load('news.json')
rows = ''
for n in news.get('headlines',[])[:15]:
    rows += f'<tr><td><a href="{n.get("url","#")}" target="_blank">{n["title"][:80]}</a></td><td class="muted">{n.get("source","—")}</td></tr>\n'
write_page('/industry-news/', 'Canadian Trucking Industry News — Latest Headlines',
    'Latest Canadian trucking industry news and headlines. Fuel prices, regulations, border updates, and market reports.',
    f'''<table><tr><th>Headline</th><th>Source</th></tr>{rows}</table>''')

# === 7. Fuel Cost Calculator ===
write_page('/fuel-cost-calculator/', 'Trucking Fuel Cost Calculator — Canadian & US Lane Rates',
    'Calculate fuel costs for any Canadian and US trucking lane. 23 cities, real-time diesel prices, per-mile and per-trip estimates.',
    '''<p class="muted">Calculate your fuel cost for any lane using live diesel prices. Available on the <a href="/">main dashboard</a>.</p>
    <div class="card"><p>Select your route and fuel type on the dashboard for a live calculation with 23 Canadian and US cities.</p></div>''')

print("7 SEO pages generated:")
for p in ['/fuel-prices/','/exchange-rate/','/road-incidents/','/cargo-theft/','/market-pulse/','/industry-news/','/fuel-cost-calculator/']:
    path = os.path.join(DOCS, p.lstrip('/'), 'index.html')
    print(f"  {p} ({os.path.getsize(path)} bytes)")
