#!/usr/bin/env python3
"""Build canonical fuel-prices page from live data. Single source of truth template."""
import json, os, csv
from collections import OrderedDict
from datetime import datetime

DATA = os.path.expanduser("~/northern-mile-dashboard/data")
DOCS = os.path.expanduser("~/northern-mile-dashboard/docs")
f = json.load(open(f"{DATA}/fuel.json"))
now = datetime.utcnow().isoformat()[:16].replace('T',' ')

nat = f.get('diesel_national_avg',171.9)
prov_raw = f.get('provinces',{})
names = {'BC':'British Columbia','AB':'Alberta','SK':'Saskatchewan','MB':'Manitoba','ON':'Ontario','QC':'Quebec','NB':'New Brunswick','NS':'Nova Scotia','PE':'PEI','NL':'Newfoundland'}
provinces = [(c,names[c],prov_raw.get(c,{}).get('diesel',0)) for c in ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']]
prices = {c:p for c,n,p in provinces}
min_p, max_p = min(p[2] for p in provinces), max(p[2] for p in provinces)
spread = max_p - min_p
cheap_c = next(p[0] for p in provinces if p[2]==min_p)
prcy_c = next(p[0] for p in provinces if p[2]==max_p)

# ===== CHART =====
chart_svg = '<div style="color:var(--text-muted);font-size:0.8125rem;padding:32px 0;text-align:center;">Chart building &mdash; data accumulating. Check back as history grows.</div>'
hpath = f"{DATA}/history/fuel_diesel.csv"
if os.path.exists(hpath):
    days = OrderedDict()
    with open(hpath) as fh:
        for row in csv.DictReader(fh):
            d = row['timestamp'][:10]
            if d not in days: days[d] = float(row['national_avg'])
    vals, dates = list(days.values())[-30:], list(days.keys())[-30:]
    if len(vals) >= 7:
        mi, mx = min(vals), max(vals); rng = max(mx-mi, 3)
        W,H, L,R,T,B = 600,140, 48,32,12,24; pw,ph = W-L-R, H-T-B
        s = f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;">'
        for i in range(4):
            y = int(T+ph*i/3)
            s += f'<line x1="{L}" y1="{y}" x2="{W-R}" y2="{y}" stroke="var(--border)" stroke-width="0.5"/>'
        s += f'<line x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}" stroke="var(--border)" stroke-width="1"/>'
        pts = [f'{int(L+pw*i/max(1,len(vals)-1))},{int(T+ph-((v-mi)/rng*ph))}' for i,v in enumerate(vals)]
        s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="var(--amber)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        for i,v in enumerate(vals):
            if i%5==0 or i==len(vals)-1:
                x=int(L+pw*i/max(1,len(vals)-1)); y=int(T+ph-((v-mi)/rng*ph))
                s += f'<circle cx="{x}" cy="{y}" r="3" fill="var(--amber)"/>'
        lx=int(W-R-2); ly=int(T+ph-((vals[-1]-mi)/rng*ph))
        s += f'<text x="{lx}" y="{ly-5}" text-anchor="end" font-size="11" font-weight="600" fill="var(--amber)">${vals[-1]:.2f}</text>'
        for i in [0, len(vals)-1]:
            x=int(L+pw*i/max(1,len(vals)-1))
            s += f'<text x="{x}" y="{H-5}" text-anchor="middle" font-size="7" fill="var(--text-muted)">{dates[i][5:]}</text>'
        s += '</svg>'
        chart_svg = s

# ===== PROVINCE CARDS =====
cards = ''
for code,name,price in provinces:
    diff = round(price - nat, 1)
    is_hi = price == max_p; is_lo = price == min_p
    accent = 'var(--amber)' if is_hi else 'var(--green)' if is_lo else ''
    style = f' style="border-left:3px solid {accent}"' if accent else ''
    diff_cls = 'neg' if diff < 0 else ''
    sign = '+' if diff >= 0 else ''
    cards += f'<div class="mc"{style}><div class="mc-code">{code}</div><div class="mc-name">{name}</div><div class="mc-val">{price}<span>c/L</span></div><div class="mc-delta {diff_cls}">{sign}{diff:.1f}c vs nat</div></div>'

# ===== COST TABLE =====
cost_rows = ''
for lpk in [55,45,38,35,30,25]:
    cost = lpk * nat / 100
    cost_rows += f'<tr><td>{lpk} L/100km</td><td class="val">${cost:,.2f}</td><td class="val">{nat}c &times; {lpk}L</td></tr>'

# ===== ROUTE SAVINGS =====
routes = [('Calgary to Vancouver',970,'AB','BC'),('Regina to Winnipeg',570,'SK','MB'),
          ('Calgary to Saskatoon',620,'AB','SK'),('Halifax to Moncton',260,'NS','NB')]
save_html = ''
for name,km,s,d in routes:
    diff = round(prices[d] - prices[s], 1)
    litres = round(km * 35 / 100)
    save = round(litres * diff / 100)
    if save > 0:
        save_html += f'<div class="sc"><div class="sc-r">{name}<span>{km:,} km</span></div><div class="sc-d">+{diff:.1f}c/L destination &middot; {litres:,}L burn</div><div class="sc-a">Save ${save:,}</div></div>'

fill_400 = round(spread * 4)

# ===== TEMPLATE =====
nav = [(n,p,'active' if p=='/fuel-prices/' else '') for n,p in [
    ('Home','/'),('Fuel','/fuel-prices/'),('FX','/exchange-rate/'),('Border','/border-wait-times/'),
    ('Incidents','/road-incidents/'),('Theft','/cargo-theft/'),('Market','/market-pulse/'),
    ('News','/industry-news/'),('Calc','/fuel-cost-calculator/')]]
nav_html = '\n'.join(f'<a href="{p}" class="{a}">{n}</a>' for n,p,a in nav)

related = [('exchange-rate','CAD to USD'),('border-wait-times','Border wait times'),('road-incidents','Road incidents'),
           ('cargo-theft','Cargo theft'),('market-pulse','Market indicators'),('industry-news','Industry headlines')]
rel_html = '\n'.join(f'<a href="/{p}/">{l} &rarr;</a>' for p,l in related)

html = f'''<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Diesel Prices by Province — Live Updates | Northern Mile</title>
<meta name="description" content="Live diesel prices for every Canadian province. Historical trends, cost calculator, and fuel routing savings. Updated every 30 minutes.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/fuel-prices/">
<meta property="og:title" content="Canadian Diesel Prices — Live | Northern Mile">
<meta property="og:description" content="Diesel across all 10 provinces. National average {nat}c/L. Free.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
<style>
/* DESIGN TOKENS */
:root{{--bg:#15171A;--surface-1:#1E2227;--surface-2:#25282E;--border:#2C3238;--radius-card:8px;--radius-chip:12px;
--text-primary:#E8EAEC;--text-body:#8B939C;--text-muted:#6B7279;
--amber:#F2A900;--green:#1F6B4A;--red:#D93A34}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
*{{font-variant-numeric:tabular-nums}}
body{{background:var(--bg);color:var(--text-body);font-family:'Inter',-apple-system,sans-serif;font-size:.875rem;line-height:1.55;-webkit-font-smoothing:antialiased}}
::-webkit-scrollbar{{width:6px}}::-webkit-scrollbar-track{{background:var(--bg)}}::-webkit-scrollbar-thumb{{background:var(--border);border-radius:3px}}
*{{scrollbar-width:thin;scrollbar-color:var(--border) var(--bg)}}
a{{color:var(--amber);text-decoration:none}}

.header{{background:var(--bg);border-bottom:1px solid var(--border);padding:0 24px;display:flex;align-items:center;justify-content:center;height:56px}}
.header h1{{font-size:.8125rem;font-weight:700;color:var(--text-primary);font-family:'IBM Plex Mono',monospace;letter-spacing:.02em}}
.nav{{background:var(--bg);border-bottom:1px solid var(--border);padding:0 24px;display:flex;justify-content:center;gap:24px;overflow-x:auto;overflow-y:hidden;white-space:nowrap;-webkit-overflow-scrolling:touch}}
.nav a{{color:var(--text-muted);text-decoration:none;font-size:.6875rem;font-weight:600;padding:8px 0;border-bottom:2px solid transparent;flex-shrink:0}}
.nav a:hover,.nav a:focus-visible{{color:var(--text-primary);border-color:var(--text-primary)}}
.nav a.active{{color:var(--amber);border-color:var(--amber)}}
.breadcrumb{{max-width:1200px;margin:0 auto;padding:10px 20px 6px;font-size:.625rem;color:var(--text-muted)}}
.breadcrumb a{{color:var(--text-muted)}}
.updated{{text-align:center;font-size:.75rem;color:var(--text-muted);padding:24px 0 8px;font-family:'IBM Plex Mono',monospace}}
.cta{{text-align:center;margin:32px auto;padding:28px 24px;background:var(--surface-1);border:1px solid var(--amber);border-radius:var(--radius-card);max-width:480px}}
.cta-eyebrow{{color:var(--amber);font-size:.6875rem;text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}}
.cta-body{{color:var(--text-primary);font-size:.9375rem;margin:0 0 6px}}
.cta-sub{{color:var(--text-muted);font-size:.75rem;margin-top:8px}}
.related{{margin:32px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}}
.related a{{display:block;background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px;text-decoration:none;color:var(--text-primary);font-weight:500;font-size:.8125rem;text-align:center}}
.related a:hover{{border-color:var(--amber)}}
.footer{{text-align:center;padding:24px;font-size:.625rem;color:var(--text-muted);border-top:1px solid var(--border);font-family:'IBM Plex Mono',monospace}}
.footer a{{color:var(--text-muted)}}

main{{max-width:1200px;margin:0 auto;padding:12px 20px 48px}}
h2{{font-size:1rem;font-weight:600;color:var(--text-primary);margin:32px 0 12px}}
h2:first-of-type{{margin-top:4px}}
p.intro{{color:var(--text-muted);font-size:.8125rem;margin-bottom:16px}}

.hero{{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:24px 28px;margin-bottom:20px;display:flex;flex-wrap:wrap;gap:24px;align-items:flex-start}}
.hp{{font-size:3.5rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;line-height:1;color:var(--text-primary)}}
.hp span{{font-size:1.125rem;color:var(--text-muted);font-weight:400}}
.hm{{flex:1;min-width:200px}}
.hl{{font-size:.625rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:4px;font-weight:600;font-family:'IBM Plex Mono',monospace}}
.hs{{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}}
.hst{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-chip);padding:12px 16px;min-width:100px}}
.hsv{{font-size:1.125rem;font-weight:600;font-family:'Barlow Condensed',sans-serif}}
.hsl{{font-size:.5625rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;font-family:'IBM Plex Mono',monospace;margin-top:2px}}

.metric-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin-bottom:28px}}
.mc{{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px}}
.mc-code{{font-size:.75rem;font-weight:600;font-family:'IBM Plex Mono',monospace;color:var(--text-muted)}}
.mc-name{{font-size:.6875rem;color:var(--text-muted);margin:2px 0 8px}}
.mc-val{{font-size:1.75rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;color:var(--text-primary);line-height:1.1}}
.mc-val span{{font-size:.6875rem;color:var(--text-muted);font-weight:400}}
.mc-delta{{font-size:.625rem;margin-top:6px;color:var(--amber)}}.mc-delta.neg{{color:var(--green)}}

table{{width:100%;border-collapse:collapse;font-size:.8125rem}}
th{{text-align:left;padding:8px 12px;border-bottom:2px solid var(--border);font-size:.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);font-weight:600;font-family:'IBM Plex Mono',monospace}}
td{{padding:9px 12px;border-bottom:1px solid var(--border)}}td.val{{text-align:right;font-family:'IBM Plex Mono',monospace;color:var(--text-primary)}}

.g2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:28px}}
.cp{{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:20px}}.cp h2:first-child{{margin-top:0}}

.callout-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.sc{{background:var(--surface-2);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px;display:flex;flex-direction:column;justify-content:space-between}}
.sc-r{{font-size:.8125rem;font-weight:500;color:var(--text-primary)}}
.sc-r span{{display:block;font-size:.6875rem;color:var(--text-muted);font-weight:400;margin-top:2px}}
.sc-d{{font-size:.6875rem;color:var(--text-muted);margin-top:4px}}
.sc-a{{font-size:1.375rem;font-weight:600;color:var(--green);font-family:'Barlow Condensed',sans-serif;margin-top:10px}}

.cht{{background:var(--surface-1);border:1px solid var(--border);border-radius:var(--radius-card);padding:20px;margin-bottom:28px}}
.cht-l{{font-size:.625rem;text-transform:uppercase;letter-spacing:.06em;color:var(--text-muted);margin-bottom:12px;font-weight:600;font-family:'IBM Plex Mono',monospace}}

.faq{{margin:32px 0}}.faq dt{{font-weight:600;margin-top:24px;padding-top:16px;border-top:1px solid var(--border);color:var(--amber);font-size:.9375rem}}
.faq dd{{margin:8px 0 0;color:var(--text-body);font-size:.875rem;line-height:1.6}}

@media(max-width:700px){{.hero{{flex-direction:column;padding:20px}}.hp{{font-size:2.5rem}}.metric-grid{{grid-template-columns:repeat(2,1fr)}}.callout-grid{{grid-template-columns:1fr}}.g2{{grid-template-columns:1fr}}.nav{{gap:16px}}}}
</style></head><body>

<div class="header"><a href="/" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><h1>NORTHERN MILE MEDIA</h1></a></div>
<nav class="nav">{nav_html}</nav>
<div class="breadcrumb"><a href="/">Dashboard</a> &rsaquo; Fuel Prices</div>

<main>
  <div class="hero">
    <div><div class="hl">National average &mdash; Diesel</div><div class="hp">{nat}<span>c/L</span></div></div>
    <div class="hm"><div class="hs">
      <div class="hst"><div class="hsv" style="color:var(--green)">{min_p}c</div><div class="hsl">Cheapest &mdash; {cheap_c}</div></div>
      <div class="hst"><div class="hsv" style="color:var(--amber)">{max_p}c</div><div class="hsl">Highest &mdash; {prcy_c}</div></div>
      <div class="hst"><div class="hsv" style="color:var(--amber)">{spread:.1f}c</div><div class="hsl">Spread</div></div>
    </div></div>
  </div>

  <h2>30-day price trend</h2>
  <div class="cht"><div class="cht-l">National average diesel</div><div style="color:var(--text-muted);font-size:0.8125rem;padding:32px 0;text-align:center;">Coming soon {chart_svg}mdash; chart will appear as data accumulates.</div></div>

  <h2>Diesel by province</h2>
  <div class="metric-grid">{cards}</div>

  <div class="g2">
    <div class="cp"><h2>Cost per 100km</h2><p class="intro">At {nat}c/L national average</p>
    <table><thead><tr><th>Burn rate</th><th class="val">Cost/100km</th><th class="val">Formula</th></tr></thead>{cost_rows}</table></div>
    <div class="cp"><h2>Fill-up savings</h2><p class="intro">Fuel in the cheaper province before crossing</p>
    <div class="callout-grid">{save_html}</div></div>
  </div>

  <h2>FAQ</h2>
  <div class="faq"><dl>
    <dt>Why is diesel different across provinces?</dt>
    <dd>Provincial fuel taxes drive most of the gap. BC adds carbon tax and transit levies. Alberta has lower fuel levies and no provincial sales tax. The {cheap_c}&ndash;{prcy_c} spread is {spread:.1f}c/L &mdash; ${fill_400:,} on a 400-litre fill.</dd>
    <dt>Where should I fuel up to save money?</dt>
    <dd>Alberta has the lowest prices. Saskatchewan and Manitoba are next. Fill up before leaving Alberta or Saskatchewan if heading east or west &mdash; prices jump at the provincial borders.</dd>
    <dt>How often do prices update?</dt>
    <dd>Every 30 minutes from public fuel surveys across all ten provinces.</dd>
    <dt>Do these prices include carbon tax?</dt>
    <dd>Yes. All federal and provincial taxes are included in the prices shown.</dd>
  </dl></div>

  <div class="updated">Last updated: {now} &middot; Data refreshes every 30 minutes</div>

  <div class="cta"><div class="cta-eyebrow">Get fuel prices in your inbox</div>
  <div class="cta-body">Fuel, border updates, and market shifts every Wednesday at 6am.</div>
  <div class="cta-sub"><a href="https://northernmilemedia.com">Sign up for the Northern Mile Brief &rarr;</a></div></div>

  <h2 style="text-align:center;">More data</h2>
  <div class="related">{rel_html}</div>
</main>

<div class="footer"><p>Northern Mile Media &middot; For the people who keep Canada moving</p><p style="margin-top:4px;">Data from public sources. Informational use only.</p></div>
</body></html>'''

os.makedirs(f"{DOCS}/fuel-prices", exist_ok=True)
with open(f"{DOCS}/fuel-prices/index.html", 'w') as fh:
    fh.write(html)
print(f"Canonical fuel page: {len(html):,} bytes")
