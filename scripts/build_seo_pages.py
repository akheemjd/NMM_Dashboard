#!/usr/bin/env python3
"""Build all Northern Mile SEO pages from canonical template. Single-source design tokens, shared components."""
import json, os
from datetime import datetime

DATA = os.path.expanduser("~/northern-mile-dashboard/data")
DOCS = os.path.expanduser("~/northern-mile-dashboard/docs")
now = datetime.utcnow().isoformat()[:16].replace('T',' ')

def load(name):
    with open(f"{DATA}/{name}") as f: return json.load(f)

# ===== SHARED TEMPLATE =====
CSS = '''/* DESIGN TOKENS */
:root{--bg:#15171A;--surface-1:#1E2227;--surface-2:#25282E;--border:#2C3238;--radius-card:8px;--radius-chip:12px;
--text-primary:#E8EAEC;--text-body:#8B939C;--text-muted:#6B7279;
--amber:#F2A900;--green:#1F6B4A;--red:#D93A34}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
*{font-variant-numeric:tabular-nums}
body{background:var(--bg);color:var(--text-body);font-family:'Inter',-apple-system,sans-serif;font-size:.875rem;line-height:1.55;-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:6px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
*{scrollbar-width:thin;scrollbar-color:var(--border) var(--bg)}
a{color:var(--amber);text-decoration:none}

.header{background:var(--bg);border-bottom:1px solid var(--border);padding:0 24px;display:flex;align-items:center;justify-content:center;height:56px}
.header h1{font-size:.8125rem;font-weight:700;color:var(--text-primary);font-family:'IBM Plex Mono',monospace;letter-spacing:.02em}
.nav{background:var(--bg);border-bottom:1px solid var(--border);padding:0 24px;display:flex;justify-content:center;gap:24px;overflow-x:auto;overflow-y:hidden;white-space:nowrap;-webkit-overflow-scrolling:touch}
.nav a{color:var(--text-muted);text-decoration:none;font-size:.6875rem;font-weight:600;padding:8px 0;border-bottom:2px solid transparent;flex-shrink:0}
.nav a:hover,.nav a:focus-visible{color:var(--text-primary);border-color:var(--text-primary)}
.nav a.active{color:var(--amber);border-color:var(--amber)}
.breadcrumb{max-width:1200px;margin:0 auto;padding:10px 20px 6px;font-size:.625rem;color:var(--text-muted)}
.breadcrumb a{color:var(--text-muted)}
.updated{text-align:center;font-size:.75rem;color:var(--text-muted);padding:24px 0 8px;font-family:'IBM Plex Mono',monospace}
.cta{text-align:center;margin:32px auto;padding:28px 24px;background:var(--surface-1);border:1px solid var(--amber);border-radius:var(--radius-card);max-width:480px}
.cta-eyebrow{color:var(--amber);font-size:.6875rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}
.cta-body{color:var(--text-primary);font-size:.9375rem;margin:0 0 6px}
.cta-sub{color:var(--text-muted);font-size:.75rem;margin-top:8px}
.related{margin:32px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.related a{display:block;background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px;text-decoration:none;color:var(--text-primary);font-weight:500;font-size:.8125rem;text-align:center}
.related a:hover{border-color:var(--amber)}
.footer{text-align:center;padding:24px;font-size:.625rem;color:var(--text-muted);border-top:1px solid var(--border);font-family:'IBM Plex Mono',monospace}
.footer a{color:var(--text-muted)}

main{max-width:1200px;margin:0 auto;padding:12px 20px 48px}
h2{font-size:1rem;font-weight:600;color:var(--text-primary);margin:32px 0 12px}
h2:first-of-type{margin-top:4px}
p.intro{color:var(--text-muted);font-size:.8125rem;margin-bottom:16px}

.hero{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:24px 28px;margin-bottom:20px;display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}
.hp{font-size:3.5rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;line-height:1;color:var(--text-primary)}
.hp span{font-size:1.125rem;color:var(--text-muted);font-weight:400}
.hm{flex:1;min-width:200px}
.hl{font-size:.625rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:4px;font-weight:600;font-family:'IBM Plex Mono',monospace}
.hs{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.hst{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-chip);padding:12px 16px;min-width:100px}
.hsv{font-size:1.125rem;font-weight:600;font-family:'Barlow Condensed',sans-serif}
.hsl{font-size:.5625rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;font-family:'IBM Plex Mono',monospace;margin-top:2px}

.metric-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:28px}
.mc{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px}
.mc-code{font-size:.75rem;font-weight:600;font-family:'IBM Plex Mono',monospace;color:var(--text-muted)}
.mc-name{font-size:.6875rem;color:var(--text-muted);margin:2px 0 8px}
.mc-val{font-size:1.75rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;color:var(--text-primary);line-height:1.1}
.mc-val span{font-size:.6875rem;color:var(--text-muted);font-weight:400}
.mc-delta{font-size:.625rem;margin-top:6px;color:var(--amber)}.mc-delta.neg{color:var(--green)}

table{width:100%;border-collapse:collapse;font-size:.8125rem}
th{text-align:left;padding:8px 12px;border-bottom:2px solid var(--border);font-size:.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);font-weight:600;font-family:'IBM Plex Mono',monospace}
td{padding:9px 12px;border-bottom:1px solid var(--border)}td.val{text-align:right;font-family:'IBM Plex Mono',monospace;color:var(--text-primary)}
td a{color:var(--amber)}

.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:28px}
.cp{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:20px}.cp h2:first-child{margin-top:0}

.callout-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.sc{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px;display:flex;flex-direction:column;justify-content:space-between}
.sc-r{font-size:.8125rem;font-weight:500;color:var(--text-primary)}
.sc-r span{display:block;font-size:.6875rem;color:var(--text-muted);font-weight:400;margin-top:2px}
.sc-d{font-size:.6875rem;color:var(--text-muted);margin-top:4px}
.sc-a{font-size:1.375rem;font-weight:600;color:var(--green);font-family:'Barlow Condensed',sans-serif;margin-top:10px}
.sc-a.red{color:var(--red)}

.cht{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:20px;margin-bottom:28px}
.cht-l{font-size:.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin-bottom:12px;font-weight:600;font-family:'IBM Plex Mono',monospace}

.faq{margin:32px 0}.faq dt{font-weight:600;margin-top:24px;padding-top:16px;border-top:1px solid var(--border);color:var(--amber);font-size:.9375rem}
.faq dd{margin:8px 0 0;color:var(--text-body);font-size:.875rem;line-height:1.6}

@media(max-width:700px){.hero{flex-direction:column;padding:20px}.hp{font-size:2.5rem}.metric-grid{grid-template-columns:repeat(2,1fr)}.callout-grid{grid-template-columns:1fr}.g2{grid-template-columns:1fr}.nav{gap:16px}}
'''

def build_nav(active_page):
    links = [('Home','/'),('Fuel','/fuel-prices/'),('FX','/exchange-rate/'),('Border','/border-wait-times/'),
             ('Incidents','/road-incidents/'),('Theft','/cargo-theft/'),('Market','/market-pulse/'),
             ('News','/industry-news/'),('Calc','/fuel-cost-calculator/')]
    return '\n'.join(f'<a href="{p}" class="{"active" if p==active_page else ""}">{n}</a>' for n,p in links)

def build_related(exclude):
    pages = [('exchange-rate','CAD to USD'),('border-wait-times','Border wait times'),('road-incidents','Road incidents'),
             ('cargo-theft','Cargo theft'),('market-pulse','Market indicators'),('industry-news','Industry headlines'),
             ('fuel-prices','Diesel prices')]
    return '\n'.join(f'<a href="/{p}/">{l} &rarr;</a>' for p,l in pages if '/'+p+'/' != exclude)

def write_page(path, title, desc, breadcrumb, hero_html, body_html, faq_html):
    nav = build_nav(path)
    related = build_related(path)
    html = f'''<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} | Northern Mile</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com{path}">
<meta property="og:title" content="{title} | Northern Mile">
<meta property="og:description" content="{desc}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="header"><a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><h1>NORTHERN MILE MEDIA</h1></a></div>
<nav class="nav">{nav}</nav>
<div class="breadcrumb"><a href="/">Dashboard</a> &rsaquo; {breadcrumb}</div>

<main>
  {hero_html}
  {body_html}
  {faq_html}

  <div class="updated">Last updated: {now} &middot; Data refreshes every 30 minutes</div>

  <div class="cta"><div class="cta-eyebrow">Get the Northern Mile Brief</div>
  <div class="cta-body">Fuel prices, border updates, and market shifts every Wednesday at 6am.</div>
  <div class="cta-sub"><a href="https://northernmilemedia.com">Sign up free &rarr;</a></div></div>

  <h2 style="text-align:center;">More data</h2>
  <div class="related">{related}</div>
</main>

<div class="footer"><p>Northern Mile Media &middot; For the people who keep Canada moving</p><p style="margin-top:4px;">Data from public sources. Informational use only.</p></div>
</body></html>'''
    os.makedirs(os.path.join(DOCS, path.lstrip('/')), exist_ok=True)
    with open(os.path.join(DOCS, path.lstrip('/') + 'index.html'), 'w') as f:
        f.write(html)
    return len(html)

# ==============================
# 2. EXCHANGE RATE
# ==============================
ex = load('exchange.json')
fx = ex.get('current') or ex.get('close', 1.32)
chg = ex.get('change', 0)
try: chg = float(chg)
except: chg = 0
up = chg > 0
arrow = '&uarr;' if up else '&darr;' if chg < 0 else '&mdash;'
sign = '+' if chg > 0 else '' if chg < 0 else ''
chg_color = 'var(--green)' if chg < 0 else 'var(--amber)' if chg > 0 else 'var(--text-muted)'

hero = f'''<div class="hero"><div><div class="hl">CAD to USD</div><div class="hp">{fx}<span>USD</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv" style="color:{chg_color}">{sign}{abs(chg):.4f}</div><div class="hsl">Change {arrow}</div></div>
<div class="hst"><div class="hsv" style="color:{chg_color}">{"Weaker" if up else "Stronger" if chg<0 else "Steady"}</div><div class="hsl">Loonie direction</div></div>
</div></div></div>'''

body = f'''<h2>What the exchange rate means for trucking</h2>
<div class="g2">
<div class="cp"><h2>Cross-border freight</h2>
<p class="intro">When CAD weakens against USD, Canadian exports become cheaper for US buyers. Cross-border southbound freight demand rises. Canadian carriers running US lanes get paid in USD &mdash; which converts to more CAD.</p>
<p class="intro">A weaker loonie means the same US lane pays better in Canadian dollars. Right now at {fx}, a $5,000 USD load converts to ${5000*fx:,.0f} CAD.</p></div>
<div class="cp"><h2>Input costs</h2>
<p class="intro">Oil is priced in USD. When the loonie weakens, Canadian carriers pay more in CAD for fuel. Equipment and parts imported from the US also cost more.</p>
<p class="intro">The exchange rate cuts both ways: better revenue on US lanes, higher costs at home.</p></div></div>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>How does the exchange rate affect my cross-border loads?</dt><dd>US brokers pay in USD. When CAD is weak, every dollar earned converts to more Canadian dollars. At {fx}, a $1,000 USD load is ${1000*fx:,.0f} CAD. A year ago at 1.25, it was $1,250 CAD &mdash; that&rsquo;s ${int((fx-1.25)*1000):,} more today.</dd>
<dt>Why does a weak loonie increase diesel prices?</dt><dd>Oil trades in USD globally. When CAD drops, refiners pay more in Canadian dollars for the same barrel of crude. That cost flows through to the pump.</dd>
<dt>How often does the rate update?</dt><dd>Every 30 minutes from Bank of Canada.</dd>
</dl></div>'''

sz = write_page('/exchange-rate/', 'CAD to USD Exchange Rate', 'Live CAD/USD exchange rate for Canadian trucking and cross-border freight. Bank of Canada data, updated every 30 minutes.', 'FX', hero, body, '')
print(f"FX page: {sz:,} bytes")

# ==============================
# 3. BORDER WAIT TIMES
# ==============================
b = load('border.json')
crossings = b.get('crossings', [])
live = sum(1 for c in crossings if c.get('source') == 'cbsa')
border_rows = ''
for c in crossings:
    d = c.get('delay_minutes', 0)
    cls = 'amber' if d > 0 else 'green'
    delay = f'{d} min' if d > 0 else 'No delay'
    fast = 'FAST' if c.get('fast_lanes') else 'No FAST'
    border_rows += f'<tr><td><strong>{c["name"]}</strong><br><span style="color:var(--text-muted);font-size:.6875rem;">{c.get("route","")} &middot; {c.get("highway","")} &middot; {fast}</span></td><td class="val" style="color:var(--{cls});">{delay}</td><td style="color:var(--text-muted);font-size:.6875rem;">{c.get("live_updated","") or c.get("source","")}</td></tr>'

hero = f'''<div class="hero"><div><div class="hl">Commercial border delays</div><div class="hp">{live}/{len(crossings)}<span> live</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv" style="color:var(--green);">{live}/{len(crossings)}</div><div class="hsl">CBSA live</div></div>
<div class="hst"><div class="hsv" style="color:var(--amber);">{sum(1 for c in crossings if not c.get('fast_lanes'))}</div><div class="hsl">No FAST lanes</div></div>
</div></div></div>'''

body = f'''<h2>Canada-US border crossings</h2>
<p class="intro">Commercial truck wait times from CBSA. {live} of {len(crossings)} crossings reporting live data. Refreshed every 30 minutes.</p>
<table><thead><tr><th>Crossing</th><th class="val">Commercial delay</th><th>Last report</th></tr></thead>{border_rows}</table>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>Which crossings have FAST lanes?</dt><dd>Ambassador Bridge, Blue Water Bridge, Peace Bridge, Lacolle, Coutts, Pacific Highway, and Emerson all have FAST dedicated commercial lanes. Queenston-Lewiston and Thousand Islands do not &mdash; commercial traffic shares the traveller lane.</dd>
<dt>How are wait times measured?</dt><dd>CBSA reports actual delays in minutes. Commercial delays are shown where available. The pill shows &ldquo;Live&rdquo; for real-time data.</dd>
<dt>When are crossings busiest?</dt><dd>Monday mornings and Thursday/Friday afternoons see the highest commercial volumes. Holiday weekends increase delays at all crossings.</dd>
</dl></div>'''

sz = write_page('/border-wait-times/', 'Canada-US Border Wait Times', 'Live Canada-US border wait times for commercial trucks. CBSA data at every major crossing. Free.', 'Border', hero, body, '')
print(f"Border page: {sz:,} bytes")

# ==============================
# 4. ROAD INCIDENTS
# ==============================
inc = load('incidents.json')
incidents = inc.get('incidents', [])
inc_rows = ''
for i in incidents[:20]:
    inc_rows += f'<tr><td>{i.get("description","—")[:80]}</td><td>{i.get("highway","—")}</td><td class="val">{i.get("severity","—")}</td></tr>'

hero = f'''<div class="hero"><div><div class="hl">Active highway incidents</div><div class="hp">{len(incidents)}<span> reported</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv" style="color:var(--amber);">{len(incidents)}</div><div class="hsl">Active</div></div>
</div></div></div>'''

body = f'''<h2>Highway incidents across Canada</h2>
<p class="intro">Road closures, accidents, and construction affecting commercial truck routes. Data from Ontario 511, DriveBC, and provincial highway authorities.</p>
<table><thead><tr><th>Incident</th><th>Highway</th><th class="val">Severity</th></tr></thead>{inc_rows}</table>
<p class="intro" style="margin-top:12px;">Color-coded by severity. Full map with interactive markers on the <a href="/">main dashboard</a>.</p>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>How current is this data?</dt><dd>Incidents are pulled from provincial highway condition feeds every 30 minutes.</dd>
<dt>Which provinces are covered?</dt><dd>Ontario, British Columbia, Alberta, Quebec, and Manitoba highway data. Coverage expanding to all provinces.</dd>
<dt>How do I check a specific highway?</dt><dd>Use the interactive map on the <a href="/">main dashboard</a> to zoom to any region.</dd>
</dl></div>'''

sz = write_page('/road-incidents/', 'Canadian Highway Incidents', 'Live Canadian highway incidents for truckers. Road closures, accidents, construction delays. Free.', 'Incidents', hero, body, '')
print(f"Incidents page: {sz:,} bytes")

# ==============================
# 5. CARGO THEFT
# ==============================
th = load('theft.json')
thefts = th.get('incidents', [])
hotspots = th.get('hotspots', [])
theft_rows = ''
for t in thefts[:10]:
    v = t.get('value', '—')
    theft_rows += f'<tr><td>{t.get("title",t.get("description","—"))[:60]}</td><td>{t.get("location","—")}</td><td class="val" style="color:var(--red);">${v}</td></tr>'
hotspot_cards = '\n'.join(f'<div class="mc"><div class="mc-code">{h["city"]}</div><div class="mc-name">High-risk zone</div><div class="mc-val" style="font-size:1rem;">{h["note"][:60]}</div></div>' for h in hotspots[:6])

hero = f'''<div class="hero"><div><div class="hl">Recent cargo theft</div><div class="hp">{len(thefts)}<span> incidents</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv" style="color:var(--red);">{sum(1 for t in thefts if 'Toronto' in str(t.get('location','')) or 'GTA' in str(t.get('location','')) or 'Brampton' in str(t.get('location','')) or 'Mississauga' in str(t.get('location','')))}</div><div class="hsl">GTA incidents</div></div>
<div class="hst"><div class="hsv" style="color:var(--red);">{len(hotspots)}</div><div class="hsl">Hotspots</div></div>
</div></div></div>'''

body = f'''<h2>Recent incidents</h2>
<table><thead><tr><th>Incident</th><th>Location</th><th class="val">Value</th></tr></thead>{theft_rows}</table>

<h2>High-risk areas</h2>
<div class="metric-grid">{hotspot_cards}</div>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>Where is cargo theft most common?</dt><dd>The Greater Toronto Area accounts for the highest volume. Montreal is second. Calgary, Edmonton, and Vancouver also see regular incidents.</dd>
<dt>What loads are targeted?</dt><dd>Electronics, meat and food products, building materials, and consumer goods are most commonly stolen.</dd>
<dt>How can carriers protect their loads?</dt><dd>Park in secure, well-lit lots. Use GPS tracking. Avoid leaving loaded trailers unattended overnight in high-risk zones.</dd>
</dl></div>'''

sz = write_page('/cargo-theft/', 'Canadian Cargo Theft Reports', 'Cargo theft tracking for Canadian trucking. Incidents, hotspots in Toronto, Montreal, Calgary. Free for fleet operators.', 'Theft', hero, body, '')
print(f"Theft page: {sz:,} bytes")

# ==============================
# 6. MARKET PULSE
# ==============================
mk = load('market.json')
hero = f'''<div class="hero"><div><div class="hl">Canadian trucking market</div><div class="hp">4<span> indicators</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv" style="color:var(--amber);">{mk.get('gdp','—')}</div><div class="hsl">GDP growth</div></div>
<div class="hst"><div class="hsv">{mk.get('freight_trend','—')}</div><div class="hsl">Freight trend</div></div>
<div class="hst"><div class="hsv">{mk.get('diesel_vs_baseline','—')}</div><div class="hsl">Diesel vs baseline</div></div>
<div class="hst"><div class="hsv">{mk.get('bc_ab_spread','—')}</div><div class="hsl">BC-AB spread</div></div>
</div></div></div>'''

market_indicators = [
    ('GDP Growth', mk.get('gdp','—'), 'Monthly', 'Canadian economic output. Strong GDP means more freight to move.'),
    ('Freight Trend', mk.get('freight_trend','—'), 'Year-over-year', 'Direction of freight volumes. Up means more loads. Down means softer demand.'),
    ('Diesel vs Baseline', mk.get('diesel_vs_baseline','—'), 'Current', 'How current diesel prices compare to historical baseline. Above baseline squeezes margins.'),
    ('BC-AB Fuel Spread', mk.get('bc_ab_spread','—'), 'Current', 'The gap between Canada\'s most and least expensive diesel provinces.'),
]
indicator_rows = '\n'.join(f'<tr><td><strong>{n}</strong><br><span style="color:var(--text-muted);font-size:.6875rem;">{d}</span></td><td class="val">{v}</td><td>{p}</td></tr>' for n,v,p,d in market_indicators)

body = f'''<h2>Market indicators</h2>
<table><thead><tr><th>Indicator</th><th class="val">Value</th><th>Period</th></tr></thead>{indicator_rows}</table>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>What do these indicators tell me?</dt><dd>They give a real-time snapshot of Canadian trucking economics. GDP shows overall demand. Freight trend shows whether volumes are growing or shrinking. The fuel indicators show cost pressures on carriers.</dd>
<dt>How often do they update?</dt><dd>GDP monthly from Statistics Canada. Freight trend and fuel indicators update every 30 minutes from our live data pipeline.</dd>
</dl></div>'''

sz = write_page('/market-pulse/', 'Canadian Trucking Market Indicators', 'Canadian trucking market indicators: GDP growth, freight trends, diesel vs baseline, BC-AB fuel spread. Free.', 'Market', hero, body, '')
print(f"Market page: {sz:,} bytes")

# ==============================
# 7. INDUSTRY NEWS
# ==============================
news = load('news.json')
headlines = news.get('headlines', [])
news_rows = ''
for n in headlines[:20]:
    news_rows += f'<tr><td><a href="{n.get("url","#")}" target="_blank" rel="noopener">{n.get("title","—")[:100]}</a></td><td style="color:var(--text-muted);font-size:.6875rem;">{n.get("source","—")}</td></tr>'

hero = f'''<div class="hero"><div><div class="hl">Industry headlines</div><div class="hp">{len(headlines)}<span> stories</span></div></div></div>'''

body = f'''<h2>Latest from Canadian trucking</h2>
<p class="intro">Headlines from Canadian and US trucking trade press. Updated continuously.</p>
<table><thead><tr><th>Headline</th><th>Source</th></tr></thead>{news_rows}</table>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>Where do these headlines come from?</dt><dd>Canadian and US trucking trade publications. Click any headline to read the full article on the publisher&rsquo;s site.</dd>
<dt>How often do headlines update?</dt><dd>Continuously throughout the day.</dd>
</dl></div>'''

sz = write_page('/industry-news/', 'Canadian Trucking Industry News', 'Latest Canadian trucking news headlines. Fuel prices, regulations, border updates, labor, market reports.', 'News', hero, body, '')
print(f"News page: {sz:,} bytes")

# ==============================
# 8. FUEL COST CALCULATOR
# ==============================
f = load('fuel.json')
nat = f.get('diesel_national_avg', 171.9)
d = load('distances.json')
cities = len(d.get('cities', []))
routes_count = len(d.get('distances', {}))

hero = f'''<div class="hero"><div><div class="hl">Lane fuel calculator</div><div class="hp">{cities}<span> cities</span></div></div>
<div class="hm"><div class="hs">
<div class="hst"><div class="hsv">{routes_count}</div><div class="hsl">Routes</div></div>
<div class="hst"><div class="hsv" style="color:var(--amber);">{nat}c/L</div><div class="hsl">Current diesel</div></div>
</div></div></div>'''

cost_rows = ''
for lpk in [55,45,35,30,25]:
    c = lpk * nat / 100
    cost_rows += f'<tr><td>{lpk} L/100km</td><td class="val">${c:,.2f}</td></tr>'

body = f'''<h2>Sample lane costs</h2>
<p class="intro">Based on national average diesel at {nat}c/L. Use the <a href="/">main dashboard</a> to calculate any route with live prices.</p>
<table><thead><tr><th>Route</th><th class="val">Distance</th><th class="val">Est. cost at 35L/100km</th></tr></thead>
<tr><td>Vancouver &rarr; Toronto</td><td class="val">4,390 km</td><td class="val">${4390*35/100*nat/100:,.0f}</td></tr>
<tr><td>Calgary &rarr; Winnipeg</td><td class="val">1,330 km</td><td class="val">${1330*35/100*nat/100:,.0f}</td></tr>
<tr><td>Toronto &rarr; Montreal</td><td class="val">540 km</td><td class="val">${540*35/100*nat/100:,.0f}</td></tr>
<tr><td>Vancouver &rarr; Seattle</td><td class="val">230 km</td><td class="val">${230*35/100*nat/100:,.0f}</td></tr>
</table>

<h2>Cost by burn rate</h2>
<p class="intro">What different trucks cost per 100km at {nat}c/L.</p>
<table><thead><tr><th>Burn rate</th><th class="val">Cost/100km</th></tr></thead>{cost_rows}</table>

<h2>FAQ</h2>
<div class="faq"><dl>
<dt>How accurate is the calculator?</dt><dd>It uses live diesel and gasoline prices with straight-line driving distances. Actual costs vary with terrain, weather, and traffic. Use it for planning and comparison, not exact fuel-card reconciliation.</dd>
<dt>Can I calculate US lanes?</dt><dd>Yes. The calculator includes 23 cities across Canada and the US. Select any origin and destination for an instant estimate.</dd>
</dl></div>'''

sz = write_page('/fuel-cost-calculator/', 'Trucking Fuel Cost Calculator', 'Calculate fuel costs for any Canadian or US trucking lane. Live diesel prices, 23 cities, per-trip estimates.', 'Calculator', hero, body, '')
print(f"Calculator page: {sz:,} bytes")

# ==============================
# Deploy summary
# ==============================
print(f"\nAll 7 pages built from canonical template at {now}")
