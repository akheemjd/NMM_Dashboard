#!/usr/bin/env python3
"""Comprehensive SEO page builder for all Northern Mile modules.
Generates: schema.org structured data, breadcrumbs, internal linking, FAQ sections, heading hierarchy.
"""
import json, os
from datetime import datetime

BASE = os.path.expanduser("~/northern-mile-dashboard")
DATA = os.path.join(BASE, "data")
DOCS = os.path.join(BASE, "docs")

def load(name):
    path = os.path.join(DATA, name)
    return json.load(open(path)) if os.path.exists(path) else {}

def page_html(path, title, desc, schema_json, content_html, faq_html=""):
    """Generate full HTML page with SEO structure."""
    now = datetime.utcnow().isoformat()[:16].replace('T',' ')
    url = f"https://dashboard.northernmilemedia.com{path}"
    
    # Breadcrumb schema
    schema = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Dashboard", "item": "https://dashboard.northernmilemedia.com/"},
                {"@type": "ListItem", "position": 2, "name": title.split("|")[0].strip(), "item": url}
            ]},
            {"@type": "WebPage", "name": title, "description": desc, "url": url, "dateModified": now, "isPartOf": {"@type": "WebSite", "name": "Northern Mile Media", "url": "https://northernmilemedia.com"}},
            schema_json
        ]
    }, indent=2)
    
    return f'''<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Northern Mile Media">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<script type="application/ld+json">{schema}</script>
<style>
  :root{{--bg:#15171A;--card:#1E2227;--text:#E8EAEC;--muted:#8B939C;--green:#1F6B4A;--amber:#F2A900;--red:#D93A34;--line:#2C3238;--rad:8px}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:Inter,-apple-system,sans-serif;margin:0;line-height:1.6;font-size:0.9375rem}}
  .banner{{background:var(--card);border-bottom:1px solid var(--line);padding:14px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px}}
  .banner .logo{{font-family:'IBM Plex Mono',monospace;font-size:0.8125rem;font-weight:700}}
  .banner nav{{display:flex;gap:16px;flex-wrap:wrap}}
  .banner nav a{{color:var(--muted);text-decoration:none;font-size:0.6875rem;font-weight:500;white-space:nowrap}}
  .banner nav a:hover{{color:var(--text)}}
  .banner nav a.active{{color:var(--amber)}}
  .breadcrumbs{{padding:8px 24px;font-size:0.6875rem;color:var(--muted)}}
  .breadcrumbs a{{color:var(--muted);text-decoration:none}}
  main{{max-width:960px;margin:0 auto;padding:16px 20px 40px}}
  h1{{font-size:1.5rem;margin-bottom:4px}}
  h2{{font-size:1.125rem;margin:28px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
  h3{{font-size:0.9375rem;margin:20px 0 8px}}
  .card{{background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:18px;margin-bottom:12px}}
  .price{{font-size:2.25rem;font-weight:700;font-family:'Barlow Condensed',sans-serif;line-height:1.1}}
  .green{{color:var(--green)}}.amber{{color:var(--amber)}}.red{{color:var(--red)}}.muted{{color:var(--muted);font-size:0.8125rem}}
  table{{width:100%;border-collapse:collapse;font-size:0.875rem}}
  th{{text-align:left;padding:8px 10px;border-bottom:2px solid var(--line);font-size:0.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600}}
  td{{padding:9px 10px;border-bottom:1px solid var(--line)}}.val{{text-align:right;font-family:'IBM Plex Mono',monospace}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}}
  .metric{{background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:14px}}
  .metric-label{{font-size:0.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}
  .metric-value{{font-size:1.5rem;font-weight:700;font-family:'Barlow Condensed',sans-serif}}
  .updated{{text-align:center;font-size:0.75rem;color:var(--muted);padding:16px 0}}
  .cta{{text-align:center;margin:36px 0 20px;padding:28px;background:var(--card);border:2px solid var(--amber);border-radius:var(--rad)}}
  .cta h2{{color:var(--amber);font-size:0.875rem;margin:0 0 8px;text-transform:uppercase;letter-spacing:.08em;border:none;padding:0}}
  .cta p{{margin:0 0 6px}}
  .related{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:24px 0}}
  .related a{{display:block;background:var(--card);border:1px solid var(--line);border-radius:var(--rad);padding:14px;text-decoration:none;color:var(--text);font-weight:500;font-size:0.875rem}}
  .related a:hover{{border-color:var(--amber)}}
  .faq{{margin:24px 0}}
  .faq dt{{font-weight:600;margin-top:16px;color:var(--amber)}}
  .faq dd{{margin:4px 0 0;color:var(--muted);font-size:0.875rem}}
  footer{{text-align:center;padding:24px;font-size:0.625rem;color:var(--muted);border-top:1px solid var(--line)}}
  footer a{{color:var(--muted)}}
  a{{color:var(--amber);text-decoration:none}}
  @media(max-width:700px){{.banner nav{{gap:10px}}h1{{font-size:1.25rem}}}}
</style>
</head>
<body>
<div class="banner">
  <a href="/" class="logo">NORTHERN MILE</a>
  <nav>
    <a href="/fuel-prices/">Fuel</a>
    <a href="/exchange-rate/">FX</a>
    <a href="/border-wait-times/">Border</a>
    <a href="/road-incidents/">Incidents</a>
    <a href="/cargo-theft/">Theft</a>
    <a href="/market-pulse/">Market</a>
    <a href="/industry-news/">News</a>
  </nav>
</div>
<div class="breadcrumbs">
  <a href="/">Dashboard</a> › {title.split("|")[0].strip()}
</div>
<main>
  <article>
    <h1>{title.split("|")[0].strip()}</h1>
    <p class="muted">{desc}</p>
    {content_html}
    {faq_html}
    <div class="updated">Last updated: {now} &middot; Data refreshes every 30 minutes</div>
  </article>

  <div class="cta">
    <h2>Never miss a market move</h2>
    <p>Get fuel prices, border updates, and market shifts in your inbox every Wednesday at 6am.</p>
    <p class="muted"><a href="https://northernmilemedia.com">Sign up for the Northern Mile Brief →</a></p>
  </div>

  <h2>More Canadian trucking data</h2>
  <div class="related">
    <a href="/fuel-prices/">Fuel prices by province →</a>
    <a href="/exchange-rate/">CAD to USD exchange rate →</a>
    <a href="/border-wait-times/">Live border wait times →</a>
    <a href="/road-incidents/">Highway incidents →</a>
    <a href="/cargo-theft/">Cargo theft reports →</a>
    <a href="/market-pulse/">Market indicators →</a>
    <a href="/industry-news/">Industry headlines →</a>
  </div>
</main>
<footer>
  <p>Northern Mile Media &middot; For the people who keep Canada moving &middot; <a href="/">Dashboard</a> &middot; <a href="https://northernmilemedia.com">Blog</a></p>
  <p style="margin-top:6px;">Data from public and government sources. Informational use only. Not financial or dispatch advice.</p>
</footer>
</body>
</html>'''

def write_page(DOCS, path, title, desc, schema, content, faq=''):
    html = page_html(path, title, desc, schema, content, faq)
    os.makedirs(os.path.dirname(os.path.join(DOCS, path.lstrip('/'))), exist_ok=True)
    with open(os.path.join(DOCS, path.lstrip('/') + 'index.html'), 'w') as f:
        f.write(html)

# ============================================
# 1. FUEL PRICES
# ============================================
f = load('fuel.json')
rows = ''
for p in ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']:
    d = f.get('provinces',{}).get(p,{}).get('diesel','—')
    rows += f'<tr><td>{p}</td><td class="val">{d}</td><td class="val">¢/L</td></tr>'
content = f'''<div class="card"><div class="price">{f.get("diesel_national_avg","—")}¢/L</div><p class="muted">Canadian national average diesel price</p></div>
  <h2>Diesel prices by province</h2>
  <table><tr><th>Province</th><th class="val">Diesel (¢/L)</th><th class="val">Unit</th></tr>{rows}</table>
  <p class="muted" style="margin-top:8px;">Prices collected from public fuel surveys. Gasoline prices also available on the <a href="/">main dashboard</a>.</p>'''

faq = '''<div class="faq">
  <h2>Frequently asked questions about Canadian diesel prices</h2>
  <dl>
    <dt>Why are diesel prices different in every province?</dt><dd>Provincial fuel taxes vary significantly. BC has carbon taxes and transit levies. Alberta has the lowest taxes in Canada. Transportation costs to remote areas also affect prices.</dd>
    <dt>How often do these diesel prices update?</dt><dd>Prices refresh every 30 minutes from public fuel surveys across all ten provinces.</dd>
    <dt>Where is diesel cheapest in Canada?</dt><dd>Alberta typically has the lowest diesel prices due to lower provincial fuel taxes and proximity to refineries.</dd>
    <dt>Do these prices include federal carbon tax?</dt><dd>Yes. Prices shown are the pump/rack price including all applicable federal and provincial taxes.</dd>
  </dl>
</div>'''

schema = {"@type": "Dataset", "name": "Canadian Diesel Prices", "description": "Live diesel prices for all 10 Canadian provinces", "temporalCoverage": datetime.utcnow().strftime("%Y-%m-%d"), "spatialCoverage": {"@type": "Country", "name": "Canada"}}
write_page(DOCS, '/fuel-prices/', 'Canadian Diesel Prices by Province — Live Updates | Northern Mile',
    'Live diesel prices for every Canadian province. National average, BC, Alberta, Ontario diesel costs. Updated every 30 minutes from public fuel surveys.',
    schema, content, faq)

# ============================================
# 2. EXCHANGE RATE
# ============================================
ex = load('exchange.json')
fx = ex.get('current', ex.get('close','—'))
chg = ex.get('change','—')
up = isinstance(chg, str) and chg.startswith('+') or (isinstance(chg,(int,float)) and chg>0)
content = f'''<div class="card">
    <div class="price">{fx}</div>
    <p class="muted">Canadian Dollar to US Dollar</p>
    <p class="{'green' if up else 'red'}" style="font-size:0.9375rem;font-weight:600;">{chg} {'↑' if up else '↓'}</p>
  </div>
  <p class="muted">CAD/USD exchange rate from Bank of Canada. Impacts cross-border freight rates, fuel imports, equipment purchases, and US lane profitability.</p>
  <div class="grid">
    <div class="metric"><div class="metric-label">Day high</div><div class="metric-value">{ex.get('day_high','—')}</div></div>
    <div class="metric"><div class="metric-label">Day low</div><div class="metric-value">{ex.get('day_low','—')}</div></div>
  </div>'''
faq = '''<div class="faq">
  <h2>How the exchange rate affects Canadian trucking</h2>
  <dl>
    <dt>How does a weak Canadian dollar affect cross-border loads?</dt><dd>When CAD drops against USD, Canadian exports become cheaper for US buyers. Cross-border freight demand increases. Canadian carriers running US lanes get paid in USD, which converts to more CAD.</dd>
    <dt>How does the exchange rate affect diesel costs?</dt><dd>Oil is priced in USD. A weaker loonie means Canadian carriers pay more in CAD for the same barrel of oil, which pushes diesel prices higher.</dd>
    <dt>How often does this rate update?</dt><dd>Every 30 minutes from Bank of Canada close data.</dd>
  </dl>
</div>'''
write_page(DOCS, '/exchange-rate/', 'CAD to USD Exchange Rate — Live Canadian Dollar | Northern Mile',
    'Live CAD/USD exchange rate for Canadian trucking and cross-border freight. Bank of Canada data, updated every 30 minutes.',
    {"@type": "Dataset", "name": "CAD/USD Exchange Rate"}, content, faq)

# ============================================
# 3. BORDER WAIT TIMES
# ============================================
b = load('border.json')
rows = ''
for bx in b.get('crossings',[]):
    delay_min = bx.get('delay_minutes',0)
    cls = 'amber' if delay_min>0 else 'green'
    delay = f'{delay_min} min' if delay_min>0 else 'No delay'
    live = bx.get('live_updated','') or bx.get('source','')
    rows += f'<tr><td><strong>{bx["name"]}</strong><br><span class="muted">{bx.get("route","")} &middot; {bx.get("highway","")}</span></td><td class="val {cls}">{delay}</td><td class="muted">{live}</td></tr>'
content = f'''<p class="muted">Commercial truck wait times at Canada-US land border crossings. Data from CBSA, updated every 30 minutes.</p>
  <table><tr><th>Crossing</th><th class="val">Commercial delay</th><th>Last reported</th></tr>{rows}</table>
  <p class="muted" style="margin-top:8px;">Crossings with FAST lanes: most ports. Queenston-Lewiston and Thousand Islands do not have FAST — commercial shares the traveller lane.</p>'''
faq = '''<div class="faq">
  <h2>Border crossing FAQ for truckers</h2>
  <dl>
    <dt>Which border crossings have FAST lanes for commercial trucks?</dt><dd>Ambassador Bridge, Blue Water Bridge, Peace Bridge, Lacolle, Coutts, Pacific Highway, and Emerson all have FAST dedicated lanes. Queenston-Lewiston and Thousand Islands do not.</dd>
    <dt>How are wait times measured?</dt><dd>CBSA reports actual delays in minutes at each crossing. Delays are for commercial traffic where available; otherwise traveller delays are shown.</dd>
    <dt>When are crossings busiest?</dt><dd>Monday mornings and Thursday/Friday afternoons typically see the highest commercial volumes. Holiday weekends increase delays at all crossings.</dd>
    <dt>How often do border wait times update?</dt><dd>We check CBSA every 30 minutes. Last reported times are shown alongside each crossing.</dd>
  </dl>
</div>'''
write_page(DOCS, '/border-wait-times/', 'Canada-US Border Wait Times — Live Commercial Delays | Northern Mile',
    'Live Canada-US border wait times for commercial trucks. CBSA data at Ambassador Bridge, Blue Water, Peace Bridge, Lacolle, Coutts. Updated every 30 minutes.',
    {"@type": "Dataset", "name": "Canada-US Border Wait Times"}, content, faq)

# ============================================
# 4. ROAD INCIDENTS
# ============================================
inc = load('incidents.json')
rows = ''
for i in inc.get('incidents',[])[:20]:
    rows += f'<tr><td>{i.get("description","—")[:80]}</td><td>{i.get("highway","—")}</td><td class="val">{i.get("severity","—")}</td></tr>'
content = f'''<p class="muted">Active highway incidents affecting commercial truck routes across Canada. Ontario 511, DriveBC, and provincial highway data.</p>
  <table><tr><th>Incident</th><th>Highway</th><th class="val">Severity</th></tr>{rows}</table>'''
write_page(DOCS, '/road-incidents/', 'Canadian Highway Incidents — Road Closures & Delays | Northern Mile',
    'Live Canadian highway incidents for truckers. Road closures, accidents, construction delays across Ontario, BC, Alberta, Quebec. Updated every 30 minutes.',
    {"@type": "Dataset", "name": "Canadian Road Incidents"}, content)

# ============================================
# 5. CARGO THEFT
# ============================================
th = load('theft.json')
rows = ''
for t in th.get('incidents',[])[:10]:
    rows += f'<tr><td>{t.get("title",t.get("description","—"))[:60]}</td><td>{t.get("location","—")}</td><td class="val red">${t.get("value","—")}</td></tr>'
content = f'''<h2>Recent cargo theft incidents</h2>
  <table><tr><th>Incident</th><th>Location</th><th class="val">Value</th></tr>{rows}</table>
  <h2>High-risk areas</h2>
  <div class="grid">''' + ''.join(f'<div class="metric"><div class="metric-label">{h["city"]}</div><div class="metric-value" style="font-size:0.9375rem;">{h["note"]}</div></div>' for h in th.get('hotspots',[])) + '</div>'
faq = '''<div class="faq">
  <h2>Cargo theft FAQ</h2>
  <dl>
    <dt>Where is cargo theft most common in Canada?</dt><dd>The Greater Toronto Area accounts for the highest volume. Montreal is second. Calgary, Edmonton, and Vancouver also see regular incidents.</dd>
    <dt>What types of loads are targeted most?</dt><dd>Electronics, meat and food products, building materials, and consumer goods are the most commonly stolen.</dd>
    <dt>How can carriers protect their loads?</dt><dd>Park in secure, well-lit lots. Use GPS tracking. Avoid leaving loaded trailers unattended overnight in high-risk zones.</dd>
  </dl>
</div>'''
write_page(DOCS, '/cargo-theft/', 'Canadian Cargo Theft Reports — Incidents & Hotspots | Northern Mile',
    'Cargo theft tracking for Canadian trucking. Recent incidents, hotspots in Toronto, Montreal, Calgary. Free for fleet operators and dispatchers.',
    {"@type": "Dataset", "name": "Canadian Cargo Theft Incidents"}, content, faq)

# ============================================
# 6. MARKET PULSE
# ============================================
mk = load('market.json')
content = '''<div class="grid">
  <div class="metric"><div class="metric-label">GDP Growth</div><div class="metric-value">''' + str(mk.get('gdp','—')) + '''</div><p class="muted">Monthly</p></div>
  <div class="metric"><div class="metric-label">Freight Trend</div><div class="metric-value">''' + str(mk.get('freight_trend','—')) + '''</div><p class="muted">Year-over-year</p></div>
  <div class="metric"><div class="metric-label">Diesel vs Baseline</div><div class="metric-value">''' + str(mk.get('diesel_vs_baseline','—')) + '''</div><p class="muted">Current spread</p></div>
  <div class="metric"><div class="metric-label">BC vs AB Spread</div><div class="metric-value">''' + str(mk.get('bc_ab_spread','—')) + '''</div><p class="muted">Provincial gap</p></div>
</div>'''
write_page(DOCS, '/market-pulse/', 'Canadian Trucking Market Indicators — GDP, Freight & Fuel | Northern Mile',
    'Canadian trucking market indicators: GDP growth, freight trends, diesel vs baseline, BC-AB fuel spread. Economic data for fleet operators.',
    {"@type": "Dataset", "name": "Canadian Trucking Market Indicators"}, content)

# ============================================
# 7. INDUSTRY NEWS
# ============================================
news = load('news.json')
rows = ''
for n in news.get('headlines',[])[:20]:
    rows += f'<tr><td><a href="{n.get("url","#")}" target="_blank" rel="noopener">{n.get("title","—")[:100]}</a></td><td class="muted">{n.get("source","—")}</td></tr>'
content = f'''<table><tr><th>Headline</th><th>Source</th></tr>{rows}</table>
  <p class="muted" style="margin-top:8px;">Headlines from Canadian and US trucking trade press. Click any story to read the full article on the publisher's site.</p>'''
write_page(DOCS, '/industry-news/', 'Canadian Trucking Industry News — Latest Headlines | Northern Mile',
    'Latest Canadian trucking news headlines. Fuel prices, regulations, border updates, labor, and market reports. Updated continuously.',
    {"@type": "NewsMediaOrganization", "name": "Northern Mile Media"}, content)

# ============================================
# 8. FUEL CALCULATOR
# ============================================
content = '''<div class="card">
    <p>The fuel cost calculator lets you estimate the diesel or gasoline cost for any trucking lane across Canada and the US.</p>
    <p class="muted" style="margin-top:8px;">23 cities. 500+ lane combinations. Live diesel and gas prices. Efficiency adjustable from 20 to 60 L/100km.</p>
    <p style="margin-top:12px;"><a href="/">Open the calculator on the main dashboard →</a></p>
  </div>
  <h2>Sample lane costs</h2>
  <p class="muted">Based on national average diesel at ''' + str(load('fuel.json').get('diesel_national_avg','—')) + '''¢/L at 35 L/100km:</p>
  <table>
    <tr><th>Route</th><th class="val">Distance</th><th class="val">Est. fuel cost</th></tr>
    <tr><td>Vancouver → Toronto</td><td class="val">4,390 km</td><td class="val">$2,642</td></tr>
    <tr><td>Calgary → Winnipeg</td><td class="val">1,330 km</td><td class="val">$800</td></tr>
    <tr><td>Toronto → Montreal</td><td class="val">540 km</td><td class="val">$325</td></tr>
    <tr><td>Vancouver → Seattle</td><td class="val">230 km</td><td class="val">$138</td></tr>
  </table>'''
write_page(DOCS, '/fuel-cost-calculator/', 'Trucking Fuel Cost Calculator — Canadian & US Lanes | Northern Mile',
    'Calculate fuel costs for any Canadian or US trucking lane. 23 cities, live diesel prices, per-trip estimates. Free for dispatchers and owner-operators.',
    {"@type": "SoftwareApplication", "name": "Fuel Cost Calculator", "applicationCategory": "BusinessApplication"}, content)

def write_page(DOCS, path, title, desc, schema, content, faq=""):
    html = page_html(path, title, desc, schema, content, faq)
    os.makedirs(os.path.dirname(os.path.join(DOCS, path.lstrip('/'))), exist_ok=True)
    with open(os.path.join(DOCS, path.lstrip('/') + 'index.html'), 'w') as f:
        f.write(html)
    print(f"  {path} ({len(html):,} bytes)")

print("SEO pages with full markup:")
for p in ['/fuel-prices/','/exchange-rate/','/border-wait-times/','/road-incidents/','/cargo-theft/','/market-pulse/','/industry-news/','/fuel-cost-calculator/']:
    path = os.path.join(DOCS, p.lstrip('/'), 'index.html')
    print(f"  {p} ({os.path.getsize(path):,} bytes)")
