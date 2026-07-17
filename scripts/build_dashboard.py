#!/usr/bin/env python3
"""Northern Mile Dashboard — v2.1 Operating Brief.
Usage: python3 build_dashboard.py [staging|production]
  staging  → docs/v2/, BASE_PATH=/v2/, noindex, no GA, no sponsor chrome
  production → docs/, normal meta, GA, sponsor chrome. Fails if noindex present.
"""
import json, os, sys, csv
from datetime import datetime

MODE = sys.argv[1] if len(sys.argv) > 1 else 'production'
if MODE not in ('staging', 'production'):
    print("Usage: python3 build_dashboard.py [staging|production]")
    sys.exit(1)

STAGING = MODE == 'staging'
BASE = os.path.expanduser('~/northern-mile-dashboard')
DATA_DIR = os.path.join(BASE, 'data')

if STAGING:
    OUT_DIR = os.path.join(BASE, 'docs', 'v2')
    BASE_PATH = '/v2/'
else:
    OUT_DIR = os.path.join(BASE, 'docs')
    BASE_PATH = '/'

os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, 'index.html')

def load(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

# === Load all data at build time ===
market = load('market.json')
fuel = load('fuel.json')
exchange = load('exchange.json')
border_data = load('border.json')
incidents_data = load('incidents.json')
news_data = load('news.json')
theft_data = load('theft.json')
distances = load('distances.json')
sponsors = load('sponsors.json')
killswitch = load('killswitch.json')
health = load('health.json')

# === History archive append ===
def archive_append(filename, headers, row):
    """Append one row to data/history/filename. Creates if new."""
    history_dir = os.path.join(DATA_DIR, 'history')
    os.makedirs(history_dir, exist_ok=True)
    path = os.path.join(history_dir, filename)
    exists = os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(headers)
        w.writerow(row)

now_iso = datetime.utcnow().isoformat()

# Archive fuel
if fuel.get('diesel_national_avg'):
    archive_append('fuel_diesel.csv', ['timestamp', 'national_avg', 'bc', 'ab', 'sk', 'mb', 'on', 'qc', 'nb', 'ns', 'pe', 'nl'],
        [now_iso, fuel['diesel_national_avg'], 
         fuel.get('provinces',{}).get('BC',{}).get('diesel',''),
         fuel.get('provinces',{}).get('AB',{}).get('diesel',''),
         fuel.get('provinces',{}).get('SK',{}).get('diesel',''),
         fuel.get('provinces',{}).get('MB',{}).get('diesel',''),
         fuel.get('provinces',{}).get('ON',{}).get('diesel',''),
         fuel.get('provinces',{}).get('QC',{}).get('diesel',''),
         fuel.get('provinces',{}).get('NB',{}).get('diesel',''),
         fuel.get('provinces',{}).get('NS',{}).get('diesel',''),
         fuel.get('provinces',{}).get('PE',{}).get('diesel',''),
         fuel.get('provinces',{}).get('NL',{}).get('diesel','')])
    archive_append('fuel_gas.csv', ['timestamp', 'national_avg', 'bc', 'ab', 'sk', 'mb', 'on', 'qc', 'nb', 'ns', 'pe', 'nl'],
        [now_iso, fuel.get('gasoline_national_avg',''),
         fuel.get('provinces',{}).get('BC',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('AB',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('SK',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('MB',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('ON',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('QC',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('NB',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('NS',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('PE',{}).get('gasoline',''),
         fuel.get('provinces',{}).get('NL',{}).get('gasoline','')])

# Archive FX
if exchange.get('current'):
    archive_append('usdcad.csv', ['timestamp', 'rate', 'change', 'change_pct'],
        [now_iso, exchange['current'], exchange.get('change',''), exchange.get('change_pct','')])

# Archive market pulse
if market.get('indicators'):
    archive_append('market_pulse.csv', ['timestamp', 'gdp', 'freight_yoy', 'diesel_vs_baseline', 'bc_ab_spread'],
        [now_iso] + [i.get('value','') for i in market.get('indicators',[])][:4])

# === Kill switch check ===
if killswitch.get('publish') == False:
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Paused</title></head>
    <body style="background:{'#1E2227' if STAGING else '#15171A'};color:#E8EAEC;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
    <div style="text-align:center"><h1 style="font-size:1.5rem;margin-bottom:8px;">Dashboard Paused</h1>
    <p style="color:#8B939C;">Scheduled maintenance. Back shortly.</p></div></body></html>"""
    with open(OUT, 'w') as f:
        f.write(html)
    print(f"Kill switch active. Paused page built: {OUT}")
    sys.exit(0)

# === Staleness guard ===
now = datetime.utcnow()
max_age_minutes = 90  # 90 min = missed 2 collections
stale_modules = []
for name, key in [('fuel', 'fuel.json'), ('exchange', 'exchange.json'), ('border', 'border.json'),
                   ('incidents', 'incidents.json'), ('news', 'news.json'), ('market', 'market.json'),
                   ('theft', 'theft.json')]:
    d = load(key)
    if d.get('updated'):
        try:
            updated = datetime.fromisoformat(d['updated'])
            age = (now - updated).total_seconds() / 60
            if age > max_age_minutes:
                stale_modules.append(f"{name} ({int(age)}m old)")
        except:
            pass

# === Production guard: fail if noindex present ===
if not STAGING:
    # Check for noindex in the HTML we're about to write
    if BASE_PATH != '/' or '/v2/' in OUT:
        print("ERROR: Production build must output to docs/ with BASE_PATH=/")
        print(f"  Got: OUT={OUT}, BASE_PATH={BASE_PATH}")
        sys.exit(1)

# ======================
# SERVER-RENDERED VALUES
# ======================

# Fuel hero values
fuel_diesel_avg = fuel.get('diesel_national_avg', '—')
fuel_gas_avg = fuel.get('gasoline_national_avg', '—')
fuel_prev_diesel = fuel.get('prev_diesel_avg', fuel_diesel_avg)
fuel_delta = fuel_diesel_avg - fuel_prev_diesel if isinstance(fuel_diesel_avg, (int,float)) and isinstance(fuel_prev_diesel, (int,float)) else 0
fuel_delta_up = fuel_delta > 0
fuel_delta_str = f"{'+' if fuel_delta>=0 else ''}{fuel_delta:.1f}" if isinstance(fuel_delta, (int,float)) else '—'

# Province list (server-rendered)
fuel_province_rows = ''
ca = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']
pdata = fuel.get('provinces', {})
vals = [pdata.get(p,{}).get('diesel', 0) for p in ca]
min_v, max_v = min(vals) if vals else 0, max(vals) if vals else 0
for i, p in enumerate(ca):
    v = vals[i]
    cls = ' high' if v == max_v else ' low' if v == min_v else ''
    fuel_province_rows += f'<div class="hero-prow"><span class="pcode">{p}</span><span class="pprice{cls}">{v:.1f}</span></div>\n'

# Exchange values
ex_rate = exchange.get('current', '—')
ex_change = exchange.get('change', 0) or 0
ex_is_zero = abs(ex_change) < 0.0001
if ex_is_zero:
    ex_arrow_html = '<span style="color:var(--gravel);">—</span>'
    ex_dir_class = ''
    ex_dir_text = 'Unchanged'
else:
    ex_up = ex_change >= 0
    ex_arrow_html = '<span style="color:var(--' + ('gantry' if ex_up else 'flare') + ');">' + ('↑' if ex_up else '↓') + '</span>'
    ex_dir_class = ' up' if ex_up else ' down'
    ex_dir_text = 'Stronger CAD' if ex_up else 'Weaker CAD'

# Market indicators
market_cards = ''
if market.get('indicators'):
    for i in market.get('indicators', []):
        up = i.get('direction') == 'up'
        icon = '↑' if up else '↓'
        ic = 'var(--gantry)' if up else 'var(--flare)'
        market_cards += f'''<div style="background:var(--asphalt);border-radius:4px;padding:12px;">
<div style="display:flex;justify-content:space-between;"><span style="font-size:0.625rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.04em;">{i['label']}</span><span style="color:{ic};font-weight:600;font-size:0.875rem;">{icon}</span></div>
<div style="font-size:1.125rem;font-weight:600;color:var(--salt);margin:2px 0;">{i['value']}</div>
{'<div style="font-size:0.75rem;color:var(--salt);">' + i.get('detail','') + '</div>' if i.get('detail') else ''}
<div style="font-size:0.625rem;color:var(--gravel);margin-top:6px;padding-top:6px;border-top:1px solid var(--line);">{i.get('what_it_means','')}</div>
</div>'''

# Headlines (strict newest-first, all gravel category pills)
headlines_html = ''
hl = news_data.get('headlines', [])
if hl:
    # Sort by date descending (newest first)
    hl.sort(key=lambda x: x.get('date',''), reverse=True)
    for n in hl:
        cat = n.get('categories', ['industry'])[0] if n.get('categories') else 'industry'
        ds = ''
        if n.get('date'):
            try:
                ds = datetime.fromisoformat(n['date']).strftime('%b %d, %H:%M')
            except:
                pass
        headlines_html += f'''<div class="nitem"><div style="display:flex;align-items:center;gap:5px;margin-bottom:3px;flex-wrap:wrap">
<span class="nsrc" style="color:var(--gravel);">{n.get('source','')}</span>
<span style="font-size:0.5rem;padding:1px 5px;border-radius:3px;font-weight:600;text-transform:capitalize;background:rgba(139,147,156,.12);color:var(--gravel);border:1px solid var(--line);">{cat}</span>
{'<span style="font-size:0.5rem;color:var(--gravel);margin-left:auto">' + ds + '</span>' if ds else ''}
</div><a class="ntitle" href="{n.get('link','#')}" target="_blank">{n.get('title','')}</a></div>\n'''

# Cargo theft
theft_html = ''
if theft_data.get('incidents'):
    for t in theft_data['incidents']:
        ds = ''
        try:
            ds = datetime.fromisoformat(t['date']).strftime('%b %d')
        except:
            pass
        theft_html += f'''<div class="theft-item"><div class="theft-method">{t.get('method','')}</div><div style="color:var(--salt);font-size:0.75rem;margin:2px 0;">{t.get('title','')} &middot; <span style="color:var(--flare);font-weight:600;">{t.get('value','')}</span></div><div style="font-size:0.625rem;color:var(--gravel);">{ds} &middot; {t.get('location','')}</div><div class="theft-prevention">Prevention: {t.get('prevention','')}</div></div>\n'''

# Border crossings
border_crossings_html = ''
now = datetime.now()
for c in border_data.get('crossings', []):
    h = now.hour; dy = now.weekday(); wd = dy < 5
    peak = (7 <= h <= 9) or (15 <= h <= 18)
    high = c.get('id','') in ['windsor-detroit','fort-erie-buffalo','pacific-blaine','lacolle-champlain']
    if h >= 22 or h <= 4: st, delay, label = 'green', '< 5 min', 'Clear'
    elif peak and high and wd: st, delay, label = 'red', '30-60 min', 'Heavy'
    elif peak or (high and wd): st, delay, label = 'amber', '10-25 min', 'Moderate'
    elif not wd and high and 10 <= h <= 16: st, delay, label = 'amber', '15-30 min', 'Weekend'
    else: st, delay, label = 'green', '5-15 min', 'Normal'
    border_crossings_html += f'''<div class="bx"><div class="bx-left"><div class="bx-name">{c.get('name','')}</div><div class="bx-route">{c.get('route','')} &middot; {c.get('highway','')}</div></div><div class="bx-status"><div class="sbar"><span class="sdot {st}"></span><span class="slabel">{label}</span></div><div class="sdelay">{delay}</div></div></div>\n'''

# Staleness warning
staleness_warning = ''
if stale_modules:
    staleness_warning = '<div style="background:rgba(242,169,0,.08);border:1px solid var(--amber);border-radius:6px;padding:8px 12px;margin-bottom:16px;font-size:0.75rem;color:var(--amber);">⚠ Stale data: ' + ', '.join(stale_modules) + '. Last known values shown.</div>'

# Sponsor chrome (sponsors.json)
sponsor_html = ''
if not STAGING and sponsors.get('modules'):
    for mod_id, sp in sponsors['modules'].items():
        if sp.get('name') and sp.get('logo'):
            sponsor_html += f'''<div class="sponsor-line active" id="sponsor-{mod_id}"><img src="{sp['logo']}" alt="{sp['name']}"><span>Sponsored by {sp['name']}</span></div>'''

# ======================
# CSS
# ======================
CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --asphalt:#15171A;--slab:#1E2227;--line:#2C3238;--salt:#E8EAEC;
  --gravel:#8B939C;--gantry:#1F6B4A;--amber:#F2A900;--flare:#D93A34;
  --radius:6px;--pill-radius:3px
}
body{
  background:var(--asphalt);color:var(--salt);
  font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:0.875rem;line-height:1.5;padding:0;max-width:100%;
  -webkit-font-smoothing:antialiased
}
.barlow{font-family:'Barlow Condensed',sans-serif;font-weight:600}
.mono,.timestamp{font-family:'IBM Plex Mono',monospace;font-weight:400}
*{font-variant-numeric:tabular-nums}
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:var(--asphalt)}
::-webkit-scrollbar-thumb{background:var(--line);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--gravel)}
*{scrollbar-width:thin;scrollbar-color:var(--line) var(--asphalt)}

.banner{
  background:var(--asphalt);border-bottom:1px solid var(--line);
  padding:0 24px;display:flex;align-items:center;justify-content:center;
  position:sticky;top:0;z-index:1000;height:64px
}
.banner h1{font-size:0.875rem;font-weight:700;color:var(--salt);font-family:'IBM Plex Mono',monospace;letter-spacing:-.01em}

.main{max-width:1320px;margin:0 auto;padding:12px 16px 32px}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:10px}

.module{background:var(--slab);border:1px solid var(--line);border-radius:var(--radius);padding:16px;position:relative}
.module.hero{grid-column:span 12}
.module.wide{grid-column:span 8}
.module.tall{grid-column:span 8;grid-row:span 2}
.module.standard{grid-column:span 4}
.module.compact{grid-column:span 4}

@media(max-width:900px){
  .module{grid-column:span 12!important;grid-row:auto!important}
  .banner{padding:0 12px;height:56px}
  .main{padding:12px 12px 32px}
}

.eyebrow{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.eyebrow-label{font-size:0.75rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.08em;font-weight:500}
.status-pill{font-size:0.625rem;padding:2px 8px;border-radius:var(--pill-radius);font-weight:600;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;display:flex;align-items:center;gap:5px}
.status-pill.live{color:var(--gantry);background:rgba(31,107,74,.15)}
.status-pill.live::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--gantry);animation:pulse 2s ease-in-out infinite}
.status-pill.daily{color:var(--gravel);background:rgba(139,147,156,.12)}
.status-pill.reference{color:var(--gravel);background:transparent;border:1px solid var(--line)}
.status-pill.typical{color:var(--amber);background:rgba(242,169,0,.12)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
@media(prefers-reduced-motion:reduce){.status-pill.live::before{animation:none}}

.card-footer{margin-top:8px;padding-top:6px;border-top:1px solid var(--line);font-size:0.625rem;color:var(--gravel);font-family:'IBM Plex Mono',monospace}

.skeleton{background:var(--line);border-radius:2px;overflow:hidden;position:relative}
.skeleton::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.04),transparent);animation:shimmer 1.5s linear infinite}
@keyframes shimmer{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
@media(prefers-reduced-motion:reduce){.skeleton::after{animation:none}}

*:focus-visible{outline:2px solid var(--amber);outline-offset:2px}

/* Fuel Hero */
.hero-content{display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:start}
.hero-price{font-size:2.75rem;line-height:1;color:var(--salt)}.hero-price .unit{font-size:1.125rem;color:var(--gravel)}
.hero-delta{display:inline-flex;align-items:center;gap:3px;margin-top:4px;font-size:0.75rem;font-weight:600;padding:2px 8px;border-radius:var(--pill-radius)}
.hero-delta.up{background:rgba(242,169,0,.15);color:var(--amber)}.hero-delta.down{background:rgba(31,107,74,.15);color:var(--gantry)}
.hero-province-list{display:grid;grid-template-columns:repeat(5,1fr);border:1px solid var(--line);border-radius:4px;overflow:hidden}.hero-prow{display:flex;justify-content:space-between;align-items:baseline;padding:6px 12px;font-size:0.875rem;gap:12px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);background:var(--asphalt)}.hero-prow:nth-child(5n){border-right:none}.hero-prow:nth-child(n+6){border-bottom:none}.hero-prow .pcode{font-family:'IBM Plex Mono',monospace;color:var(--gravel);font-weight:500}.hero-prow .pprice{font-family:'IBM Plex Mono',monospace;font-weight:600}.pprice.high{color:var(--amber)}.pprice.low{color:var(--gantry)}
.ftoggle{display:flex;background:var(--asphalt);border:1px solid var(--line);border-radius:var(--pill-radius);overflow:hidden}
.ftoggle button{flex:1;background:none;border:none;color:var(--gravel);padding:4px 10px;font-size:0.625rem;font-family:inherit;cursor:pointer;font-weight:600;white-space:nowrap}
.ftoggle button.active{background:var(--salt);color:var(--asphalt)}

.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.bx{background:var(--asphalt);border:1px solid var(--line);border-radius:4px;padding:12px;display:flex;justify-content:space-between;align-items:center;gap:8px}
.bx-left{min-width:0}.bx-name{font-size:0.75rem;font-weight:600;color:var(--salt)}.bx-route{font-size:0.625rem;color:var(--gravel);margin-top:2px}
.bx-status{text-align:right}.sbar{display:flex;align-items:center;gap:5px;font-size:0.75rem}.sdot{width:8px;height:8px;border-radius:50%}.sdot.green{background:var(--gantry)}.sdot.amber{background:var(--amber)}.sdot.red{background:var(--flare)}.slabel{font-weight:600;color:var(--salt)}.sdelay{color:var(--gravel);font-size:0.625rem}

.mwrap{display:flex;gap:0;height:420px;border-radius:var(--radius);overflow:hidden}
.mmap{flex:1;min-width:0;height:420px;background:#1a1d21}.mlist{width:280px;max-width:45%;overflow-y:auto;flex-shrink:0;font-size:0.75rem}
.mitem{padding:8px 10px;border-bottom:1px solid var(--line);cursor:pointer}
.mitem:hover{background:rgba(255,255,255,.03)}
.mhwy{font-weight:600;color:var(--salt)}.mdesc{color:var(--gravel);font-size:0.625rem;margin-top:2px}
.leaflet-container{background:#1a1d21!important;font-family:inherit;z-index:1}
.leaflet-popup-content-wrapper{background:var(--slab)!important;color:var(--salt)!important;border-radius:8px!important}

.nitem{padding:8px 0;border-bottom:1px solid var(--line)}.nitem:last-child{border-bottom:none}
.nsrc{font-size:0.625rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.ntitle{color:var(--salt);text-decoration:none;font-size:0.75rem;line-height:1.4;font-weight:500}
.ntitle:hover{text-decoration:underline}

.cform{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end}
.cfield{flex:1;min-width:100px}
.cfield label{font-size:0.625rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px}
.cfield select,.cfield input{width:100%;background:var(--asphalt);border:1px solid var(--line);color:var(--salt);padding:8px 10px;border-radius:4px;font-size:0.75rem;font-family:inherit}
.cfield select:focus,.cfield input:focus{outline:none;border-color:var(--amber)}
.cresult{margin-top:12px;padding:12px;background:var(--asphalt);border-radius:4px;display:none}.cresult.v{display:block}.ccost{font-size:1.75rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;color:var(--salt)}.cbreak{margin-top:6px;font-size:0.75rem;color:var(--gravel);line-height:1.6}

.theft-item{padding:10px 0;border-bottom:1px solid var(--line);font-size:0.75rem}
.theft-item:last-child{border-bottom:none}.theft-method{color:var(--flare);font-weight:600;font-size:0.625rem;text-transform:uppercase;letter-spacing:.04em}.theft-prevention{color:var(--gravel);font-size:0.625rem;margin-top:3px}

.sponsor-line{display:none;align-items:center;gap:8px;margin-bottom:10px;padding:6px 10px;background:rgba(31,107,74,.08);border-radius:4px;font-size:0.625rem;color:var(--gantry)}
.sponsor-line.active{display:flex}
.sponsor-line img{height:20px;width:auto}

.module:hover .share-btn,.module:focus-within 
.share-btn:hover{background:var(--asphalt);color:var(--salt);border-color:var(--gravel)}

100%{opacity:1;transform:translateX(-50%) translateY(0)}}
100%{opacity:0}}
.sponsor-disclosure{font-size:0.5rem;color:var(--gravel);margin-top:8px;text-align:center}

@media(max-width:900px){
  .hero-content{grid-template-columns:1fr;gap:12px}
  .mwrap{flex-direction:column;height:auto!important}.mmap{width:100%!important;min-height:260px!important}.mlist{width:100%!important;max-width:100%!important;max-height:200px}
  .cform{flex-direction:column}.cfield{min-width:100%}
}
"""

# ======================
# HTML
# ======================
noindex_meta = '<meta name="robots" content="noindex">' if STAGING else ''
ga_script = '' if STAGING else '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>'''
staging_badge = '<div style="position:fixed;bottom:8px;right:8px;background:var(--amber);color:var(--asphalt);padding:4px 8px;border-radius:4px;font-size:0.625rem;font-weight:600;z-index:9999;">STAGING</div>' if STAGING else ''

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
{noindex_meta}
<title>Northern Mile — Live Canadian Trucking Dashboard</title>
<meta name="description" content="Free live dashboard for Canadian trucking. Fuel prices, border crossings, road incidents. No signup.">
<link rel="canonical" href="https://dashboard.northernmilemedia.com{'' if not STAGING else '/v2/'}">
<meta property="og:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<meta property="og:description" content="Diesel prices, border status, road incidents. No signup. Free forever.">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="{BASE_PATH}favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&family=IBM+Plex+Mono:wght@400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{BASE_PATH}leaflet.css">
<script src="{BASE_PATH}leaflet.js"></script>
{ga_script}
<style>{CSS}</style>
</head>
<body>
{staging_badge}

<div class="banner">
  <a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;">
    <img src="{BASE_PATH}logo.jpg" alt="Northern Mile Media" style="height:32px;width:auto;">
    <h1>NORTHERN MILE MEDIA</h1>
  </a>
</div>

<div class="main">
  {staleness_warning}

  <div style="text-align:center;padding:8px 18px;margin-bottom:16px;font-size:0.875rem;color:var(--gravel);">
    Live data for Canadian trucking. Fuel prices. Border delays. Road incidents. Free. Always.
  </div>

  <div class="grid">

<!-- 1. Fuel Prices — HERO (server-rendered) -->
    <div class="module wide" id="fuel-card">
      <div class="eyebrow">
        <span class="eyebrow-label">Fuel Prices</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <div class="ftoggle" id="prices-toggle"><button data-fuel="diesel" class="active">Diesel</button><button data-fuel="gasoline">Gas</button></div>
          <span class="status-pill daily">Daily</span>
        </div>
      </div>
      <div style="display:flex;align-items:baseline;gap:12px;">
        <span class="hero-price" style="margin:0;font-size:3.5rem;">{fuel_diesel_avg}<span class="unit" style="font-size:1.25rem;"> ¢/L</span></span>
        <span class="hero-delta {'up' if fuel_delta_up else 'down'}" style="font-size:1rem;padding:3px 10px;">{'↑' if fuel_delta_up else '↓'} {fuel_delta_str}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:2px 10px;align-items:center;margin-top:8px;padding-top:6px;border-top:1px solid var(--line);">
        <div class="hero-province-list">{fuel_province_rows}</div>
      </div>
      
      
      <div class="card-footer"><span class="ts-foot" data-updated="{fuel.get('updated','')}">Updated {fuel.get('updated','')[:16] if fuel.get('updated') else '—'}</span></div>
    </div>

    <!-- 2. USD / CAD — COMPACT (server-rendered) -->
    <div class="module compact" id="exchange-card">
      <div class="eyebrow"><span class="eyebrow-label">USD / CAD</span><span class="status-pill live">Live</span></div>
      <div>
        <div style="font-size:0.625rem;color:var(--gravel);margin-bottom:2px;">1 US Dollar equals</div>
        <div style="font-size:1.75rem;font-weight:600;color:var(--salt);" class="barlow">{ex_rate} CAD</div>
        <div style="font-size:0.75rem;font-weight:600;margin-top:2px;color:var(--{'gantry' if ex_up else 'flare' if not ex_is_zero else 'gravel'});">{ex_arrow_html} {ex_dir_text}{'' if ex_is_zero else ' · ' + ('+' if ex_up else '') + f'{ex_change:.4f}'}</div>
        <div style="font-size:0.625rem;color:var(--gravel);margin-top:8px;line-height:1.4;">Bank of Canada closing rate</div>
      </div>
      <div class="card-footer"><span class="ts-foot" data-updated="{exchange.get('updated','')}">Updated {exchange.get('updated','')[:16] if exchange.get('updated') else '—'}</span></div>
    </div>

    <!-- 3. Border Crossings — WIDE (server-rendered) -->
    <div class="module wide" id="border-card">
      <div class="eyebrow"><span class="eyebrow-label">Border Crossings</span><span class="status-pill typical" title="Estimated from historical traffic patterns. Real-time CBSA data coming soon.">Typical</span></div>
      <div class="bgrid">{border_crossings_html}</div>
      <div style="font-size:0.625rem;color:var(--gravel);margin-top:8px;">Estimated from historical patterns. Real-time data coming.</div>
      <div class="card-footer"><span class="ts-foot" data-updated="{border_data.get('updated','')}">Updated {border_data.get('updated','')[:16] if border_data.get('updated') else '—'}</span></div>
    </div>

    <!-- 4. Fuel Cost Calculator — STANDARD (JS) -->
    <div class="module standard" id="calc-card">
      <div class="eyebrow"><span class="eyebrow-label">Fuel Calculator</span><span class="status-pill live">Live</span></div>
      <div class="cform">
        <div class="cfield"><label>From</label><select id="calc-from"></select></div>
        <div class="cfield"><label>To</label><select id="calc-to"></select></div>
        <div class="cfield"><label>Fuel</label><div class="ftoggle" id="fuel-toggle"><button data-fuel="diesel" class="active">Diesel</button><button data-fuel="gasoline">Gas</button></div></div>
        <div class="cfield" style="flex:.5"><label>L/100km</label><input type="number" id="calc-eff" value="35" min="10" max="80"></div>
      </div>
      <div class="cresult" id="calc-result"></div>
    </div>

    <!-- 5. Road Incidents — TALL (JS map only) -->
    <div class="module hero" id="incidents-card">
      <div class="eyebrow"><span class="eyebrow-label">Road Incidents</span><span class="status-pill live">Live</span></div>
      <div class="mwrap"><div class="mmap" id="inc-map"></div><div class="mlist" id="inc-list"></div></div>
      <div class="card-footer"><span class="ts-foot" data-updated="{incidents_data.get('updated','')}">Updated {incidents_data.get('updated','')[:16] if incidents_data.get('updated') else '—'}</span></div>
    </div>

    <!-- 6. Cargo Theft — STANDARD (server-rendered + JS map) -->
    <div class="module hero" id="theft-card">
      <div class="eyebrow"><span class="eyebrow-label">Cargo Theft</span><span class="status-pill reference">Reference</span></div>
      <div class="mwrap"><div class="mmap" id="th-map"></div><div class="mlist" id="th-list"><div style="padding:8px 10px;font-size:0.625rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.04em;">Recent</div>{theft_html.replace('class="theft-item"','class="mitem"')}<div style="margin:6px 10px 0;font-size:0.625rem;color:var(--gravel);text-transform:uppercase;">Hotspots</div></div></div>
      <div class="card-footer"><span class="ts-foot" data-updated="{theft_data.get('updated','')}">Updated {theft_data.get('updated','')[:16] if theft_data.get('updated') else '—'}</span></div>
    </div>

    <!-- 7. Market Pulse — STANDARD (server-rendered) -->
    <div class="module wide" id="market-card">
      <div class="eyebrow"><span class="eyebrow-label">Market Pulse</span><span class="status-pill daily">Daily</span></div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;">{market_cards}</div>
      
      <div class="card-footer"><span class="ts-foot" data-updated="{market.get('updated','')}">Updated {market.get('updated','')[:16] if market.get('updated') else '—'}</span></div>
    </div>

    <!-- 8. Industry Headlines — WIDE (server-rendered) -->
    <div class="module standard" id="news-card">
      <div class="eyebrow"><span class="eyebrow-label">Industry Headlines</span><span class="status-pill daily">Daily</span></div>
      <div style="max-height:320px;overflow-y:auto;">{headlines_html}</div>
      <div class="card-footer"><span class="ts-foot" data-updated="{news_data.get('updated','')}">Updated {news_data.get('updated','')[:16] if news_data.get('updated') else '—'}</span></div>
    </div>

</div>

</div>

<div style="text-align:center;max-width:480px;margin:32px auto 0;padding:24px;background:var(--slab);border:1px solid var(--line);border-radius:var(--radius);">
  <div style="font-size:0.875rem;font-weight:600;color:var(--salt);margin-bottom:4px;">Get the Northern Mile Brief</div>
  <div style="font-size:0.75rem;color:var(--gravel);margin-bottom:16px;">Fuel prices, market shifts, and what it means. Every Wednesday.</div>
  <script src="https://cdn.jsdelivr.net/ghost/signup-form@~0.3/umd/signup-form.min.js" data-background-color="#1E2227" data-text-color="#E8EAEC" data-button-color="#E8EAEC" data-button-text-color="#15171A" data-title="" data-description="" data-site="https://www.northernmilemedia.com/" data-locale="en" async></script>
</div>

<footer style="padding:16px 24px;text-align:center;font-size:0.625rem;color:var(--gravel);border-top:1px solid var(--line);font-family:'IBM Plex Mono',monospace;">
  <div class="sponsor-disclosure">Sponsors never influence the data.</div>
  &copy; 2026 Northern Mile Media &middot; Data from public sources &middot; Informational use only
</footer>

<script>
// === Relative time ticker ===
function relTime(iso){{
  if(!iso)return'';
  var diff=Math.floor((Date.now()-new Date(iso))/1000);
  if(diff<60)return'Just now';
  if(diff<3600)return Math.floor(diff/60)+'m ago';
  if(diff<86400)return Math.floor(diff/3600)+'h ago';
  return Math.floor(diff/86400)+'d ago';
}}
setInterval(function(){{
  document.querySelectorAll('.ts-foot').forEach(function(el){{
    var t=el.getAttribute('data-updated');
    if(t)el.textContent='Updated '+relTime(t);
  }});
}},60000);

// === Fuel toggle (client-side re-render) ===
var fuelData={json.dumps(fuel)};
document.getElementById('prices-toggle').addEventListener('click',function(e){{
  if(e.target.tagName!=='BUTTON')return;
  document.querySelectorAll('#prices-toggle button').forEach(function(b){{b.classList.remove('active');}});
  e.target.classList.add('active');
  var type=e.target.dataset.fuel;
  var avg=type==='diesel'?fuelData.diesel_national_avg:fuelData.gasoline_national_avg;
  var prev=type==='diesel'?(fuelData.prev_diesel_avg||avg):avg-1;
  var delta=avg-prev,up=delta>0;
  var ca=['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL'];
  var P=fuelData.provinces||{{}};
  var vals=ca.map(function(p){{return(P[p]||{{}})[type]||0;}});
  var maxV=Math.max.apply(null,vals),minV=Math.min.apply(null,vals);
  var rows='';
  ca.forEach(function(p,i){{
    var v=vals[i],cls=v===maxV?' high':v===minV?' low':'';
    rows+='<div class=\"hero-prow\"><span class=\"pcode\">'+p+'</span><span class=\"pprice'+cls+'\">'+v.toFixed(1)+'</span></div>';
  }});
  document.querySelector('#fuel-card .hero-price').innerHTML=avg+'<span class=\"unit\"> &cent;/L</span>';
  document.querySelector('#fuel-card .hero-delta').className='hero-delta '+(up?'up':'down');
  document.querySelector('#fuel-card .hero-delta').textContent=(up?'↑ ':'↓ ')+(delta>=0?'+':'')+delta.toFixed(1);
  document.querySelector('#fuel-card .hero-province-list').innerHTML=rows;
}});

// === Calculator ===
var calcDistances={json.dumps(distances.get('distances',{}))};
var calcCitiesData={json.dumps(distances.get('cities',[]))};
var calcCitiesData={json.dumps(distances.get('cities',[]))};
var calcFuel={json.dumps(fuel)};
var calcFuelType='diesel';
document.getElementById('fuel-toggle').addEventListener('click',function(e){{
  if(e.target.tagName!=='BUTTON')return;
  document.querySelectorAll('#fuel-toggle button').forEach(function(b){{b.classList.remove('active');}});
  e.target.classList.add('active');
  calcFuelType=e.target.dataset.fuel;
  runCalc();
}});
// Populate dropdowns
calcCitiesData.forEach(function(c){{
  var o1=document.createElement('option');o1.value=c.code;o1.textContent=c.name;
  var o2=document.createElement('option');o2.value=c.code;o2.textContent=c.name;
  document.getElementById('calc-from').appendChild(o1);
  document.getElementById('calc-to').appendChild(o2);
}});
document.getElementById('calc-from').value='YVR';
document.getElementById('calc-to').value='YYZ';
setTimeout(runCalc,200);

// Populate dropdowns
calcCitiesData.forEach(function(c){{
  var o1=document.createElement('option');o1.value=c.code;o1.textContent=c.name;
  var o2=document.createElement('option');o2.value=c.code;o2.textContent=c.name;
  document.getElementById('calc-from').appendChild(o1);
  document.getElementById('calc-to').appendChild(o2);
}});
document.getElementById('calc-from').value='YVR';
document.getElementById('calc-to').value='YYZ';
setTimeout(runCalc,200);

document.getElementById('calc-eff').addEventListener('input',runCalc);
document.getElementById('calc-from').addEventListener('change',runCalc);
document.getElementById('calc-to').addEventListener('change',runCalc);

function runCalc(){{
  var from=document.getElementById('calc-from').value;
  var to=document.getElementById('calc-to').value;
  var eff=parseFloat(document.getElementById('calc-eff').value)||35;
  var res=document.getElementById('calc-result');
  if(!from||!to||from===to){{res.className='cresult';return;}}
  var dist=calcDistances[from+'-'+to]||calcDistances[to+'-'+from];
  if(!dist){{res.innerHTML='<div style=\"color:var(--gravel);font-size:0.75rem;\">Route not available.</div>';res.className='cresult v';return;}}
  var rate=calcFuelType==='diesel'?calcFuel.diesel_national_avg:calcFuel.gasoline_national_avg;
  if(!rate)rate=calcFuelType==='diesel'?171.9:168.7;
  var liters=dist*eff/100,total=liters*rate/100;
  res.innerHTML='<div class=\"ccost\">$'+total.toFixed(2)+'</div><div class=\"cbreak\">'+dist.toLocaleString()+' km &middot; '+eff+' L/100km &middot; '+rate.toFixed(1)+'&cent;/L '+calcFuelType+'</div>';
  res.className='cresult v';
}}

// === Maps (Leaflet) ===
var incData={json.dumps(incidents_data)};
var thData={json.dumps(theft_data)};

setTimeout(function(){{
  // Road Incidents Map
  var incList=incData.incidents||(Array.isArray(incData)?incData:[]);
  var mc=document.getElementById('inc-map');
  if(mc&&incList.length){{
    var incMap=L.map('inc-map',{{zoomControl:false,attributionControl:false}});
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'&copy; OSM'}}).addTo(incMap);
    L.Icon.Default.prototype.options.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
    var bounds=[],list=document.getElementById('inc-list'),h='',markers=[];
    incList.forEach(function(inc,i){{
      var lat=inc.lat||inc.latitude,lon=inc.lon||inc.longitude||inc.lng;
      if(!lat||!lon)return;
      var hwy=inc.highway||inc.road||'',prov=inc.province||inc.state||'';
      var desc=inc.description||inc.desc||'';
      var m=L.marker([lat,lon]).addTo(incMap).bindPopup('<strong>'+hwy+'</strong><br>'+prov+'<br>'+desc);
      markers.push(m);
      bounds.push([lat,lon]);
      h+='<div class=\"mitem\" data-idx=\"\+i+\\" style=\"cursor:pointer\" onclick=\"void(0)\" data-lat=\"\+lat+\\" data-lon=\"\+lon+\\"(['+lat+','+lon+'],12);\" style=\"cursor:pointer\"><div class=\"mhwy\">'+hwy+' &middot; '+prov+'</div><div class=\"mdesc\">'+desc.substring(0,80)+'</div></div>';
    }});
    list.innerHTML=h||'<div style=\"padding:10px;color:var(--gravel);font-size:0.75rem;\">No active incidents.</div>';
    if(bounds.length)incMap.fitBounds(bounds,{{padding:[30,30]}});else incMap.setView([50,-85],4);
    // Click handlers (need map in scope)
    document.querySelectorAll('#inc-list .mitem').forEach(function(el,i){{el.onclick=function(){{incMap.setView(bounds[i],12);markers[i].openPopup();}};}});
  }}

  // Cargo Theft Map
  var thInc=thData.incidents||[];
  var thHs=thData.hotspots||[];
  var md2=document.getElementById('th-map');
  if(md2&&(thInc.length||thHs.length)){{
    var thMap=L.map('th-map',{{zoomControl:false,attributionControl:false}}).setView([52,-90],4);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:''}}).addTo(thMap);
    var bounds2=[];
    thHs.forEach(function(h){{
      var c=h.risk==='high'?'#D93A34':h.risk==='medium'?'#F2A900':'#1F6B4A';
      L.circleMarker([h.lat,h.lng],{{radius:h.risk==='high'?16:h.risk==='medium'?12:8,color:c,fillColor:c,fillOpacity:.12,weight:1.5,dashArray:'4,2'}}).addTo(thMap).bindPopup('<b>'+h.city+'</b><br>Risk: '+h.risk.toUpperCase()+'<br>'+h.note);
      bounds2.push([h.lat,h.lng]);
    }});
    var thMarkers=[];
    thInc.forEach(function(i){{
      if(!i.lat||!i.lng)return;
      var m=L.circleMarker([i.lat,i.lng],{{radius:7,color:'#D93A34',fillColor:'#D93A34',fillOpacity:.5,weight:2}}).addTo(thMap).bindPopup('<b>'+i.title+'</b><br><span style="color:#D93A34;font-weight:600;">'+i.value+'</span><br>'+i.date+' &middot; '+i.location+'<br><b>Method:</b> '+i.method+'<br><b>Prevention:</b> '+i.prevention);
      thMarkers.push(m);
      bounds2.push([i.lat,i.lng]);
    }});
    if(bounds2.length)thMap.fitBounds(bounds2,{{padding:[20,20]}});
    // Click handlers: only incident items (exclude header rows)
    document.querySelectorAll('#th-list .mitem').forEach(function(el,i){{
      el.addEventListener('click',function(){{
        var m=thMarkers[i];
        if(m){{thMap.setView(m.getLatLng(),12);m.openPopup();}}
      }});
    }});
    setTimeout(function(){{thMap.invalidateSize();}},200);
  }}
}},400);


</script>""" + """
<script>
</script>""" + """
</body>
</html>"""

# === Production guard ===
if not STAGING and ('noindex' in html.split('<meta name="robots"')[1][:30] if 'noindex' in html else False):
    print("ERROR: Production build contains noindex. Aborting.")
    sys.exit(1)

# Remove stale debug JSON print
html = html.split("{json.dumps({'stale_modules':")[0] + '\n</body>\n</html>'




with open(OUT, 'w') as f:
    f.write(html)

print(f"[{MODE.upper()}] Dashboard built: {OUT}")
print(f"  Size: {len(html):,} bytes")
if stale_modules:
    print(f"  ⚠ Stale: {', '.join(stale_modules)}")
