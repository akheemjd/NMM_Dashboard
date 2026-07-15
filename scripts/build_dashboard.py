#!/usr/bin/env python3
"""Generate the Northern Mile dashboard from a clean template.
Run this to rebuild index.html. Never patch it manually again.
"""
import json, os
from datetime import datetime

OUT = os.path.expanduser('~/northern-mile-dashboard/docs/index.html')

# ── CSS ──
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --blue:#1a3a5c;--red:#c41e3a;--muted:#6b7280;--light:#eaecf0;--bg:#f8f9fa;
  --card:#fff;--text:#1a3a5c;--green:#16a34a;--amber:#d97706;--radius:10px
}
body{
  background:var(--bg);color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;
  font-size:14px;line-height:1.5;padding:0;max-width:100%
}
.banner{
  background:var(--card);border-bottom:1px solid var(--light);padding:14px 24px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
  gap:8px;position:sticky;top:0;z-index:1000
}
.banner-brand{font-size:17px;font-weight:800;color:var(--blue);letter-spacing:-.02em;line-height:1.1}
.banner-sub{font-size:11px;color:var(--muted);font-weight:400;letter-spacing:.02em}
.banner-accent{width:3px;height:28px;background:var(--red);border-radius:2px;margin-right:10px;flex-shrink:0}
.banner-left{display:flex;align-items:center;gap:0}
.pill{font-size:9px;padding:3px 8px;border-radius:10px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.pill.live{background:#dcfce7;color:var(--green);animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}.pill.daily{background:#dbeafe;color:var(--blue)}

.main{padding:14px 18px 40px;max-width:1440px;margin:0 auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:14px}
.grid-2{grid-template-columns:repeat(2,1fr)}

.card{background:var(--card);border:1px solid var(--light);border-radius:var(--radius);padding:18px;scroll-margin-top:70px}
.card.full{grid-column:1/-1}
.card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--light);gap:10px}
.card-header h2{font-size:16px;font-weight:600;text-transform:none;letter-spacing:-.01em;color:var(--text);white-space:nowrap}
.card-header-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.header-update{font-size:9px;color:var(--muted);white-space:nowrap}
.card-body{min-height:30px}
.loading{color:var(--muted);font-style:italic;padding:10px 0}.error{color:var(--red);padding:10px 0}
#news-card .card-body{max-height:400px;overflow-y:auto}
.card-footer{font-size:9px;color:var(--muted);margin-top:10px;padding-top:8px;border-top:1px solid var(--light);display:flex;justify-content:space-between;align-items:center}
.card-footer span{font-weight:500}

.sponsor-line{display:none;align-items:center;gap:10px;margin-bottom:10px;padding:8px 12px;background:var(--bg);border-radius:6px;font-size:11px;color:var(--muted)}
.sponsor-line.active{display:flex}
.sponsor-line img{height:22px;width:auto;flex-shrink:0;opacity:.85}
.sponsor-line .sponsor-info{display:flex;flex-direction:column;gap:1px}
.sponsor-line .sponsor-label{font-size:8px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.sponsor-line .sponsor-name{font-size:13px;font-weight:700;color:var(--text)}
.sponsor-line .sponsor-tagline{font-size:9px;color:var(--muted)}

.inds{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.ind{background:var(--bg);border-radius:8px;padding:16px 18px;display:flex;flex-direction:column;gap:5px}
.ind-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}
.ind-value{font-size:26px;font-weight:800;color:var(--blue);line-height:1.1}
.ind-detail{font-size:13px;color:var(--text);font-weight:500}
.ind-meaning{font-size:11px;color:var(--muted);line-height:1.4;margin-top:5px;padding-top:6px;border-top:1px solid var(--light)}

.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}
.bx{background:var(--bg);border-radius:8px;padding:14px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.bx-left{min-width:0}.bx-name{font-size:14px;font-weight:600;color:var(--text);line-height:1.2}
.bx-route{font-size:11px;color:var(--muted);margin-top:2px}
.bx-status{text-align:right;flex-shrink:0}
.sbar{display:flex;align-items:center;gap:6px;font-size:12px;margin-bottom:2px}
.sdot{width:10px;height:10px;border-radius:50%}.sdot.green{background:var(--green)}.sdot.amber{background:var(--amber)}.sdot.red{background:var(--red)}
.slabel{font-weight:600;color:var(--text)}.sdelay{color:var(--muted);font-size:10px}
.tag{font-size:8px;padding:1px 5px;border-radius:3px;font-weight:600;text-transform:uppercase}.tag.fast{background:#dbeafe;color:var(--blue)}.tag.nexus{background:#dcfce7;color:var(--green)}

.nitem{padding:8px 0;border-bottom:1px solid var(--light)}
.nsrc{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.ncat{font-size:8px;padding:1px 5px;border-radius:3px;font-weight:600;text-transform:capitalize}
.ntitle{color:var(--blue);text-decoration:none;font-size:12px;line-height:1.3;font-weight:500}
.ntitle:hover{color:var(--red)}

.mwrap{display:flex;gap:0;height:380px;overflow:hidden;border-radius:var(--radius)}
.mmap{flex:1;height:380px;background:#f0f0f0}.mlist{width:300px;height:380px;overflow-y:auto;flex-shrink:0}
.mitem{padding:7px 10px;border-bottom:1px solid var(--light);font-size:11px;cursor:pointer}
.mitem:hover{background:var(--bg)}
.mprov{font-size:9px;color:var(--blue);text-transform:uppercase;font-weight:600}
.mhwy{font-weight:600;color:var(--text)}.mdesc{color:var(--muted);font-size:10px;margin-top:1px}
.mclosed{font-size:8px;background:#fee2e2;color:var(--red);padding:1px 4px;border-radius:3px}

.cform{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end}
.cfield{flex:1;min-width:100px}
.cfield label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px}
.cfield select,.cfield input{width:100%;background:var(--bg);border:1px solid var(--light);color:var(--text);padding:9px 10px;border-radius:6px;font-size:13px;font-family:inherit}
.cfield select:focus,.cfield input:focus{outline:none;border-color:var(--blue)}
.ftoggle{display:flex;background:var(--bg);border:1px solid var(--light);border-radius:6px;overflow:hidden}
.ftoggle button{flex:1;background:none;border:none;color:var(--muted);padding:9px 12px;font-size:12px;font-family:inherit;cursor:pointer;font-weight:600}
.ftoggle button.active{background:var(--blue);color:#fff}
.cresult{margin-top:12px;padding:12px;background:var(--bg);border-radius:6px;display:none}
.cresult.v{display:block}.ccost{font-size:28px;font-weight:700;color:var(--blue)}
.cbreak{margin-top:6px;font-size:12px;color:var(--muted);line-height:1.7}
.cbreak strong{color:var(--text)}

.leaflet-container{background:#f0f0f0!important;font-family:inherit;z-index:1}
.leaflet-tile-pane{z-index:1}
.leaflet-popup-pane{z-index:2000!important}
.leaflet-control-zoom{z-index:2!important}
.leaflet-control-zoom a{background:var(--card)!important;color:var(--text)!important;border-color:var(--light)!important}
.leaflet-popup-content-wrapper{background:var(--card)!important;border-radius:8px!important;font-size:12px;box-shadow:0 4px 12px rgba(0,0,0,.1)!important}

@media(max-width:700px){
  .banner{padding:10px 14px}
  .main{padding:12px 12px 28px}.grid{grid-template-columns:1fr;gap:12px}
  .grid-2{grid-template-columns:1fr}
  .card{padding:16px}.inds{grid-template-columns:1fr}
  .bgrid{grid-template-columns:1fr}
  .mwrap{flex-direction:column;height:auto!important;overflow:visible!important}
  .mmap{height:260px!important;width:100%!important;flex:none}
  .mlist{height:220px!important;width:100%!important;flex:none}
  .cform{flex-direction:column}.cfield{min-width:100%}
  .card-header h2{font-size:14px}.ind-value{font-size:19px}
  .ccost{font-size:26px}
  body{font-size:15px}
  .ind-label{font-size:10px}
  .bx{flex-direction:row;flex-wrap:wrap}
  .ntitle{font-size:13px;line-height:1.4}
  .mitem{font-size:12px;padding:9px 10px}
  .mdesc{font-size:11px}
  footer{flex-direction:column!important;gap:10px!important;align-items:flex-start!important;padding:14px 16px!important}
  footer>div{flex-wrap:wrap!important;gap:8px 16px!important}
}
"""

# ── HTML ──
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Northern Mile — Live Canadian Trucking Dashboard | Fuel Prices, Border Delays, Road Incidents</title>
<meta name="description" content="Free live dashboard for Canadian trucking. Real-time fuel prices by province, USD/CAD exchange rate, border crossing status, road incidents map, and cargo theft watch. Built for fleet operators and dispatchers.">
<meta name="keywords" content="Canadian trucking, diesel prices Canada, fuel prices by province, border crossing delays, road incidents Canada, cargo theft, trucking dashboard, fleet management, freight rates">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/">

<meta property="og:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<meta property="og:description" content="Free live dashboard for Canadian trucking. Fuel prices, exchange rates, border delays, road incidents. No signup. Free forever.">
<meta property="og:url" content="https://dashboard.northernmilemedia.com/">
<meta property="og:type" content="website">
<meta property="og:image" content="https://dashboard.northernmilemedia.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Northern Mile Media">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://dashboard.northernmilemedia.com/og-image.png">
<meta name="twitter:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<meta name="twitter:description" content="Free live dashboard for Canadian trucking. Fuel prices, exchange rates, border delays, road incidents, cargo theft data. Updated every 30 minutes.">

<script type="application/ld+json">
{"@context":"https://schema.org","@type":"WebApplication","name":"Northern Mile Live Dashboard","url":"https://dashboard.northernmilemedia.com/","description":"Free live dashboard for Canadian trucking industry. Real-time fuel prices by province, USD/CAD exchange rate, border crossing status, road incidents map, cargo theft watch, and fuel cost calculator.","applicationCategory":"BusinessApplication","operatingSystem":"All","offers":{"@type":"Offer","price":"0","priceCurrency":"CAD"}}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What data does this dashboard track?","acceptedAnswer":{"@type":"Answer","text":"Live fuel prices by Canadian province, USD/CAD exchange rates with 30-day trends, border crossing status for 9 major crossings, road incidents and closures from Ontario 511 and BC DriveBC, cargo theft incidents and hotspots, and industry headlines from Canadian trucking sources."}},{"@type":"Question","name":"How often is the dashboard updated?","acceptedAnswer":{"@type":"Answer","text":"Every 30 minutes. Fuel prices, exchange rates, road incidents, and border crossing status refresh automatically throughout the day."}},{"@type":"Question","name":"Is the dashboard free?","acceptedAnswer":{"@type":"Answer","text":"Yes. Completely free. No signup required. No paywalls. Supported by sponsorships."}}]}
</script>

<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">

<link rel="stylesheet" href="leaflet.css">
<script src="leaflet.js"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
<style>$$CSS$$</style>
</head>
<body>

<div class="banner">
  <div class="banner-left">
    <img src="logo.jpg" alt="Northern Mile Media" style="height:48px;width:auto;flex-shrink:0;margin-right:12px;">
    <div>
      <h1 class="banner-brand" style="font-size:inherit;font-weight:inherit;margin:0;padding:0;display:inline;">NORTHERN MILE MEDIA</h1>
      <div class="banner-sub">For the people who keep Canada moving</div>
    </div>
  </div>
</div>

<div class="main">

  <div style="background:linear-gradient(135deg,#1a3a5c 0%,#152d4a 100%);border-radius:12px;padding:28px 24px 24px;margin-bottom:14px;color:#fff;text-align:center;position:relative;overflow:hidden;">
    <div style="position:absolute;top:-40px;right:-40px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.03);pointer-events:none;"></div>
    <div style="position:absolute;bottom:-30px;left:-30px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,.03);pointer-events:none;"></div>
    <div style="font-size:20px;font-weight:800;margin-bottom:6px;letter-spacing:-.02em;">Know before they do.</div>
    <div style="font-size:13px;color:#8b9ec4;margin-bottom:16px;line-height:1.5;max-width:460px;margin-left:auto;margin-right:auto;">Every Wednesday at 7am, fuel prices, rate trends, and what they mean for your operation. In 90 seconds.</div>
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:20px;margin-bottom:18px;font-size:10px;color:#8b9ec4;">
      <div style="background:rgba(255,255,255,.06);padding:5px 12px;border-radius:20px;">Fuel by province, trended weekly</div>
      <div style="background:rgba(255,255,255,.06);padding:5px 12px;border-radius:20px;">Exchange rate impact analysis</div>
      <div style="background:rgba(255,255,255,.06);padding:5px 12px;border-radius:20px;">What to watch next week</div>
    </div>
    <div style="width:40px;height:1px;background:rgba(255,255,255,.15);margin:0 auto 16px;"></div>
    <form id="newsletter-form" style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;max-width:420px;margin:0 auto" onsubmit="subscribeNewsletter(event)">
      <input type="email" id="nl-email" placeholder="Your email address" required style="flex:1;min-width:180px;padding:11px 14px;border:1px solid rgba(255,255,255,.2);border-radius:6px;font-size:13px;font-family:inherit;background:rgba(255,255,255,.08);color:#fff">
      <button type="submit" style="padding:11px 24px;background:#fff;color:#1a3a5c;border:none;border-radius:6px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:0 2px 8px rgba(0,0,0,.15);">Subscribe free</button>
    </form>
    <div id="nl-msg" style="font-size:10px;color:#3fb950;margin-top:8px;display:none;"></div>
    <div style="font-size:9px;color:#8b9ec4;margin-top:10px;">No spam. One email, every Wednesday. Unsubscribe anytime.</div>
  </div>

  <div style="text-align:center;padding:8px 18px;margin-bottom:14px;font-size:13px;color:var(--muted);letter-spacing:.01em;">
    Live data for Canadian trucking. Fuel prices. Border delays. Road incidents. Free. Always.
  </div>

  <div class="card full" id="market-card">
    <div class="card-header" id="market-pulse"><h2>Market Pulse</h2><span class="pill daily">Daily</span></div>
    <div class="sponsor-line" id="sponsor-market"></div>
    <div class="card-body"><div class="loading">Loading market data...</div></div>
  </div>

  <div class="grid grid-2" style="margin-top:14px">
    <div class="card" id="exchange-card">
      <div class="card-header"><h2>USD / CAD</h2><span class="pill live">Live</span></div>
      <div class="sponsor-line" id="sponsor-exchange"></div>
      <div class="card-body"><div class="loading">Loading exchange rate...</div></div>
    </div>
    <div class="card" id="fuel-card">
      <div class="card-header">
        <h2>Fuel Prices</h2>
        <div style="display:flex;align-items:center;gap:8px">
          <div class="ftoggle" id="prices-toggle" style="height:26px">
            <button data-fuel="diesel" class="active" style="font-size:10px;padding:4px 10px">Diesel</button>
            <button data-fuel="gasoline" style="font-size:10px;padding:4px 10px">Gas</button>
          </div>
          <span class="pill daily">Daily</span>
        </div>
      </div>
      <div class="sponsor-line" id="sponsor-fuel"></div>
      <div class="card-body"><div class="loading">Loading fuel prices...</div></div>
    </div>
  </div>

  <div class="card full" style="margin-top:14px" id="incidents-card">
    <div class="card-header"><h2>Road Incidents</h2><span class="pill live">Live</span></div>
    <div class="sponsor-line" id="sponsor-incidents"></div>
    <div class="card-body"><div class="loading">Loading incidents...</div></div>
  </div>

  <div class="grid grid-2" style="margin-top:14px">
    <div class="card" id="border-card">
      <div class="card-header"><h2>Border Crossings</h2><span class="pill live">Live</span></div>
      <div class="sponsor-line" id="sponsor-border"></div>
      <div class="card-body"><div class="loading">Loading border crossings...</div></div>
    </div>
    <div class="card" id="calc-card">
      <div class="card-header"><h2>Fuel Cost Calculator</h2><span class="pill live">Live</span></div>
      <div class="card-body">
        <div class="cform">
          <div class="cfield"><label>From</label><select id="calc-from"></select></div>
          <div class="cfield"><label>To</label><select id="calc-to"></select></div>
          <div class="cfield"><label>Fuel</label><div class="ftoggle" id="fuel-toggle"><button data-fuel="diesel" class="active">Diesel</button><button data-fuel="gasoline">Gas</button></div></div>
          <div class="cfield" style="flex:.5"><label>L/100km</label><input type="number" id="calc-eff" value="35" min="10" max="80"></div>
        </div>
        <div class="cresult" id="calc-result"></div>
      </div>
    </div>
  </div>

  <div class="card full" style="margin-top:14px" id="theft-card">
    <div class="card-header"><h2>Cargo Theft Watch</h2><span class="pill daily">Reference</span></div>
    <div class="sponsor-line" id="sponsor-theft"></div>
    <div class="card-body"><div class="loading">Loading theft data...</div></div>
  </div>

  <div class="card full" style="margin-top:14px" id="news-card">
    <div class="card-header"><h2>Industry Headlines</h2><span class="pill daily">Daily</span></div>
    <div class="sponsor-line" id="sponsor-headlines"></div>
    <div class="card-body"><div class="loading">Loading headlines...</div></div>
  </div>

</div>

<div style="text-align:center;padding:28px 18px 20px;margin-top:20px;">
  <div style="font-size:15px;font-weight:700;color:var(--blue);margin-bottom:4px;">Get the Northern Mile Brief</div>
  <div style="font-size:12px;color:var(--muted);margin-bottom:14px;">Fuel prices, market shifts, and what it means. Every Wednesday. No spam.</div>
  <form id="newsletter-form-bottom" style="display:flex;gap:6px;justify-content:center;flex-wrap:wrap;max-width:400px;margin:0 auto" onsubmit="subscribeNewsletterBottom(event)">
    <input type="email" id="nl-email-bottom" placeholder="Your email address" required style="flex:1;min-width:180px;padding:10px 14px;border:1px solid var(--light);border-radius:6px;font-size:13px;font-family:inherit;background:var(--card);color:var(--text)">
    <button type="submit" style="padding:10px 20px;background:var(--blue);color:#fff;border:none;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit">Subscribe</button>
  </form>
  <div id="nl-msg-bottom" style="font-size:10px;color:var(--green);margin-top:8px;display:none;"></div>
  <div style="margin-top:16px;font-size:11px;color:var(--muted);">
    Interested in sponsoring a module? <a href="https://northernmilemedia.com" style="color:var(--blue);font-weight:600;">Advertise with us →</a>
  </div>
</div>

<footer style="background:#0d1117;color:#8b949e;padding:18px 24px;margin-top:20px;font-size:11px;font-family:'SF Mono',monospace;line-height:1.5;display:flex;flex-wrap:wrap;gap:16px 40px;justify-content:space-between;align-items:center;border-top:1px solid #30363d;">
  <div style="display:flex;align-items:center;gap:12px;">
    <img src="logo.jpg" alt="Northern Mile Media" style="height:28px;width:auto;filter:brightness(0.9);">
    <div>
      <div style="font-size:12px;font-weight:700;color:#c9d1d9;letter-spacing:.02em;">NORTHERN MILE MEDIA</div>
      <div style="font-size:9px;color:#8b949e;">&copy; 2026 Northern Mile Media &middot; Informational use only. Data from public sources. Verify independently.</div>
    </div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:16px 32px;align-items:center;font-size:10px;">
    <div><span style="color:#3fb950;">●</span> System Online</div>
    <div>Refresh <span style="color:#58a6ff;">30m</span></div>
    <div>Modules <span style="color:#58a6ff;">8</span></div>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:10px 20px;align-items:center;font-size:10px;">
    <a href="https://northernmilemedia.com" style="color:#58a6ff;text-decoration:none;">Blog</a>
    <span style="color:#484f58;">|</span>
    <a href="#" style="color:#58a6ff;text-decoration:none;">Newsletter</a>
    <a href="https://www.linkedin.com/company/109885620/" target="_blank" style="color:#58a6ff;text-decoration:none;">LinkedIn</a>
    <a href="https://x.com/northernmile" target="_blank" style="color:#58a6ff;text-decoration:none;">X</a>
  </div>
</footer>

$$SCRIPTS$$
</body>
</html>"""

# ── JavaScript ──
SCRIPTS = """
<script>
const DB='data/';
const BLUE='#1a3a5c',RED='#c41e3a',MUTED='#6b7280',LIGHT='#eaecf0';
function ft(iso){return iso?new Date(iso).toLocaleString('en-CA',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'';}
async function LJ(p){const r=await fetch(p);if(!r.ok)throw Error('HTTP '+r.status);return r.json();}

function cardBody(id){return document.querySelector('#'+id+' .card-body');}

// ── Market ──
function renderMarket(d){
  if(!d||!d.indicators)return'<div class="error">No data</div>';
  let h='<div class="inds">';
  d.indicators.forEach(i=>{
    const icon=i.direction==='up'?'↑':i.direction==='down'?'↓':'→';
    const ic=i.direction==='up'?'var(--green)':i.direction==='down'?'var(--red)':'var(--muted)';
    h+='<div class="ind"><div style="display:flex;justify-content:space-between"><span class="ind-label">'+i.label+'</span><span style="color:'+ic+';font-weight:800;font-size:18px;">'+icon+'</span></div>';
    h+='<div class="ind-value">'+i.value+'</div>';
    if(i.detail)h+='<div class="ind-detail">'+i.detail+'</div>';
    h+='<div class="ind-meaning">'+(i.what_it_means||'')+'<br><span style="color:var(--blue)">'+(i.source||'')+'</span></div></div>';
  });
  return h+'</div>';
}

// ── Exchange SVG ──
function renderExchange(d){
  if(!d||d.current==null)return'<div class="error">No data</div>';
  const hist=d.history||[];
  const ch=d.change||0,chPct=d.change_pct||0;
  const dir=ch>=0?'up':'down',dirLabel=ch>=0?'Stronger CAD':'Weaker CAD';
  const chStr=(ch>=0?'+':'')+ch.toFixed(4)+' ('+(ch>=0?'+':'')+chPct+'%)';
  const impact=ch>=0?'Canadian dollar stronger. Cheaper US fuel and equipment. Cross-border US loads pay less in CAD.':'Canadian dollar weaker. US loads pay more in CAD. US fuel and equipment cost more.';

  if(hist.length<2)return'<div style="font-size:34px;font-weight:700;color:var(--blue)">1 USD = '+d.current.toFixed(4)+' CAD</div>';

  const vals=hist.map(h=>h.rate).reverse();
  const dates=hist.map(h=>new Date(h.date).toLocaleDateString('en-CA',{month:'short',day:'numeric'})).reverse();
  const minV=Math.min(...vals),maxV=Math.max(...vals),range=maxV-minV||0.001;
  const W=340,H=150,pad={top:8,right:10,bottom:22,left:36};
  const pw=W-pad.left-pad.right,ph=H-pad.top-pad.bottom;
  const Y=v=>pad.top+ph-(v-minV)/range*ph*0.80;
  const X=i=>pad.left+(i/(vals.length-1))*pw;
  let svg='';
  for(let g=0;g<=3;g++){const gv=minV+range*g/3,gy=Y(gv);
    svg+='<line x1="'+pad.left+'" y1="'+gy+'" x2="'+(W-pad.right)+'" y2="'+gy+'" stroke="'+LIGHT+'" stroke-width="0.5"/>';
    svg+='<text x="'+(pad.left-4)+'" y="'+(gy+3)+'" fill="'+MUTED+'" font-size="8" text-anchor="end">'+gv.toFixed(4)+'</text>';
  }
  let apts='',pts='';
  vals.forEach((v,i)=>{pts+=X(i).toFixed(1)+','+Y(v).toFixed(1)+' ';});
  vals.forEach((v,i)=>{apts+=X(i).toFixed(1)+','+Y(v).toFixed(1)+' ';});
  apts+=X(vals.length-1).toFixed(1)+','+(H-pad.bottom)+' '+X(0).toFixed(1)+','+(H-pad.bottom);
  svg+='<polygon points="'+apts+'" fill="'+BLUE+'" fill-opacity="0.05"/>';
  svg+='<polyline points="'+pts+'" fill="none" stroke="'+BLUE+'" stroke-width="1.8" stroke-linecap="round"/>';
  let lastX=-50;
  const step=Math.max(1,Math.floor((vals.length-1)/4));
  for(let i=0;i<vals.length;i+=step){
    const xi=X(i);if(xi-lastX<36)continue;lastX=xi;
    svg+='<text x="'+xi+'" y="'+(H-pad.bottom+14)+'" fill="'+MUTED+'" font-size="8" text-anchor="middle">'+dates[i]+'</text>';
  }
  const lxi=X(vals.length-1);
  if(lxi-lastX>=36)svg+='<text x="'+lxi+'" y="'+(H-pad.bottom+14)+'" fill="'+MUTED+'" font-size="8" text-anchor="middle">'+dates[vals.length-1]+'</text>';

  // 7-day high/low
  const recent=vals.slice(-7);const wkHigh=Math.max(...recent),wkLow=Math.min(...recent);

  return '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">'
    +'<div>'
    +'<div style="font-size:10px;color:var(--muted);margin-bottom:0;">1 US Dollar equals</div>'
    +'<div style="font-size:28px;font-weight:800;color:var(--blue);line-height:1.1;">'+d.current.toFixed(4)+' CAD</div>'
    +'<div style="font-size:11px;font-weight:600;color:'+(ch>=0?'var(--green)':'var(--red)')+';">'+dirLabel+' &middot; '+dir+' '+chStr+' today</div>'
    +'</div>'
    +'<div style="text-align:right;font-size:10px;color:var(--muted);padding-top:18px;">'
    +'<div>7-day high <span style="color:var(--red);font-weight:600;">'+wkHigh.toFixed(4)+'</span></div>'
    +'<div>7-day low <span style="color:var(--green);font-weight:600;">'+wkLow.toFixed(4)+'</span></div>'
    +'</div>'
    +'</div>'
    +'<svg viewBox="0 0 '+W+' '+H+'" style="display:block;width:100%;margin-top:6px">'+svg+'</svg>'
    +'<div style="font-size:10px;color:var(--muted);margin-top:4px;line-height:1.4;">'+impact+'</div>';
}

// ── Fuel SVG ──
let pFuelType='diesel';
function renderFuelSVG(d,type){
  const P=d.provinces||{};const ca=['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL'];
  const vals=ca.map(p=>(P[p]||{})[type]||0);
  const label=type==='diesel'?'Diesel':'Gasoline';
  const avg=type==='diesel'?d.diesel_national_avg:d.gasoline_national_avg;
  const W=640,H=280,pad={top:20,right:16,bottom:38,left:40};
  const pw=W-pad.left-pad.right,ph=H-pad.top-pad.bottom;
  const maxV=Math.max(...vals);
  const Y=v=>pad.top+ph-(v/maxV)*ph*0.85;
  const gap=pw/ca.length,barW=gap*0.55;
  let svg='';
  for(let g=0;g<=4;g++){const gv=Math.round(maxV*g/4),gy=Y(gv);
    svg+='<line x1="'+pad.left+'" y1="'+gy+'" x2="'+(W-pad.right)+'" y2="'+gy+'" stroke="'+LIGHT+'" stroke-width="0.5"/>';
    svg+='<text x="'+(pad.left-4)+'" y="'+(gy+4)+'" fill="'+MUTED+'" font-size="10" text-anchor="end">'+gv+'</text>';
  }
  ca.forEach((p,i)=>{
    const cx=pad.left+gap*i+gap*0.5,by=Y(vals[i]);
    svg+='<rect x="'+(cx-barW/2)+'" y="'+by+'" width="'+barW+'" height="'+(H-pad.bottom-by)+'" fill="'+BLUE+'" rx="2"/>';
    svg+='<text x="'+cx+'" y="'+(H-pad.bottom+18)+'" fill="'+BLUE+'" font-size="11" font-weight="600" text-anchor="middle">'+p+'</text>';
    if(vals[i]>=maxV*0.88)svg+='<text x="'+cx+'" y="'+(by-5)+'" fill="'+BLUE+'" font-size="11" font-weight="700" text-anchor="middle">'+vals[i].toFixed(0)+'</text>';
  });
  const ay=Y(avg);
  svg+='<line x1="'+pad.left+'" y1="'+ay+'" x2="'+(W-pad.right)+'" y2="'+ay+'" stroke="'+RED+'" stroke-width="1" stroke-dasharray="4,3" opacity="0.5"/>';
  svg+='<rect x="'+(pad.left+44)+'" y="'+pad.top+'" width="100" height="26" rx="4" fill="var(--card)" stroke="'+LIGHT+'" stroke-width="0.5"/>';
  svg+='<text x="'+(pad.left+94)+'" y="'+(pad.top+18)+'" fill="'+RED+'" font-size="11" font-weight="600" text-anchor="middle">'+label+' avg '+avg.toFixed(1)+'&cent;</text>';
  return '<svg viewBox="0 0 '+W+' '+H+'" style="display:block;width:100%">'+svg+'</svg>';
}

// ── Border ──
function getBS(c){
  const now=new Date(),h=now.getHours(),dy=now.getDay(),wd=dy>=1&&dy<=5;
  const peak=(h>=7&&h<=9)||(h>=15&&h<=18),night=h>=22||h<=4;
  const high=['windsor-detroit','fort-erie-buffalo','pacific-blaine','lacolle-champlain'].includes(c.id);
  if(night&&!high)return{status:'green',delay:'< 5 min',label:'Clear'};
  if(peak&&high&&wd)return{status:'red',delay:'30-60 min',label:'Heavy'};
  if(peak||(high&&wd))return{status:'amber',delay:'10-25 min',label:'Moderate'};
  if(!wd&&high&&h>=10&&h<=16)return{status:'amber',delay:'15-30 min',label:'Weekend'};
  return{status:'green',delay:'5-15 min',label:'Normal'};
}
function renderBorder(d){
  const cs=d.crossings||[],bl=d.blitz_dates||[];
  let h='<div class="bgrid">';
  cs.forEach(c=>{const st=getBS(c);
    h+='<div class="bx"><div class="bx-left"><div class="bx-name">'+c.name+'</div><div class="bx-route">'+c.route+' &middot; '+c.highway+'</div></div>';
    h+='<div class="bx-status"><div class="sbar"><span class="sdot '+st.status+'"></span><span class="slabel">'+st.label+'</span></div><div class="sdelay">'+st.delay+'</div></div></div>';
  });
  h+='</div>';
  if(bl.length){h+='<div style="margin-top:10px;padding:8px 12px;background:#fef3c7;border-radius:6px;font-size:11px">';
    bl.forEach(b=>{const days=Math.ceil((new Date(b.date)-Date.now())/86400000);
      h+='<span style="color:var(--amber);font-weight:600">'+new Date(b.date).toLocaleDateString('en-CA',{month:'short',day:'numeric'})+'</span> &middot; '+b.name+' ('+days+'d) ';
    });
    h+='</div>';
  }
  if(d.updated)h+='<div class="card-footer">Updated '+ft(d.updated)+'</div>';
  return h;
}

// ── News ──
function renderNews(d){
  const hl=d.headlines||[];if(!hl.length)return'<div class="error">No headlines</div>';
  const cc={regulations:{bg:'#eff6ff',c:'#1d4ed8'},markets:{bg:'#fef3c7',c:'#92400e'},equipment:{bg:'#f3e8ff',c:'#7c3aed'},business:{bg:'#dcfce7',c:'#166534'},technology:{bg:'#fce7f3',c:'#be185d'},drivers:{bg:'#fff7ed',c:'#c2410c'},safety:{bg:'#fee2e2',c:'#dc2626'},industry:{bg:'#f1f5f9',c:'#475569'}};
  const sc={'Truck News':'#2563eb','Trucking Info':'#16a34a','The Trucker':'#d97706'};
  let h='';hl.forEach(n=>{
    const cat=n.categories?.[0]||'industry',c=cc[cat]||cc.industry,srcC=sc[n.source]||MUTED;
    const ds=n.date?new Date(n.date).toLocaleDateString('en-CA',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'';
    h+='<div class="nitem"><div style="display:flex;align-items:center;gap:5px;margin-bottom:2px;flex-wrap:wrap">';
    h+='<span class="nsrc" style="color:'+srcC+'">'+n.source+'</span>';
    h+='<span class="ncat" style="background:'+c.bg+';color:'+c.c+'">'+cat+'</span>';
    if(ds)h+='<span style="font-size:8px;color:var(--muted);margin-left:auto">'+ds+'</span>';
    h+='</div><a class="ntitle" href="'+n.link+'" target="_blank">'+n.title+'</a></div>';
  });
  if(d.updated)h+='<div class="card-footer">Updated '+ft(d.updated)+'</div>';
  return h;
}

// ── Incidents Map ──
let incMap=null,incData=null;
function renderIncidents(d){incData=d;return'<div class="mwrap"><div class="mmap" id="inc-map"></div><div class="mlist" id="inc-list"></div></div>';}
function initIncMap(){
  const d=incData;if(!d)return;
  const incs=d.incidents||[],md=document.getElementById('inc-map'),ld=document.getElementById('inc-list');
  if(!md||!ld)return;
  if(incMap){incMap.remove();incMap=null;}
  incMap=L.map(md,{attributionControl:false,zoomControl:true}).setView([49,-85],4);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{attribution:'',maxZoom:18}).addTo(incMap);
  const markers=[];
  incs.slice(0,30).forEach((i,idx)=>{
    if(!i.lat||!i.lng)return;
    const closed=i.closure,color=closed?'#dc2626':'#d97706';
    const popup='<b>'+(i.highway||'')+'</b> '+(i.direction||'')+'<br>'+(i.description||'')+(i.lanes?'<br>Lanes: '+i.lanes:'');
    const m=L.circleMarker([i.lat,i.lng],{radius:closed?7:5,color,fillColor:color,fillOpacity:0.6,weight:1.5}).addTo(incMap).bindPopup(popup);
    markers.push({marker:m,lat:i.lat,lng:i.lng});
  });
  let h='<div style="padding:6px 10px;font-size:10px;color:var(--muted)">'+(d.total||incs.length)+' events ('+(d.sources||[]).join(', ')+')</div>';
  incs.slice(0,30).forEach((i,idx)=>{
    if(!i.lat||!i.lng)return;
    const cb=i.closure?' <span class="mclosed">CLOSED</span>':'';
    h+='<div class="mitem" data-idx="'+idx+'"><span class="mprov">'+i.province+'</span> <span class="mhwy">'+(i.highway||'—')+'</span>'+cb+'<div class="mdesc">'+(i.description||'').substring(0,120)+'</div></div>';
  });
  ld.innerHTML=h;
  ld.querySelectorAll('.mitem').forEach(el=>{
    el.addEventListener('click',()=>{
      const idx=parseInt(el.dataset.idx),m=markers[idx];
      if(m&&incMap){incMap.flyTo([m.lat,m.lng],12,{duration:1});setTimeout(()=>m.marker.openPopup(),800);}
    });
  });
  setTimeout(()=>{if(incMap)incMap.invalidateSize();},100);
}

// ── Theft Map ──
let thMap=null,thData=null;
function renderTheft(d){thData=d;return'<div class="mwrap"><div class="mmap" id="th-map"></div><div class="mlist" id="th-list"></div></div>';}
function initThMap(){
  const d=thData;if(!d)return;
  const hs=d.hotspots||[],tg=d.top_targets||[],tp=d.prevention||[],inc=d.incidents||[];
  const md=document.getElementById('th-map'),ld=document.getElementById('th-list');
  if(!md||!ld)return;
  if(thMap){thMap.remove();thMap=null;}
  thMap=L.map(md,{attributionControl:false,zoomControl:true}).setView([52,-90],4);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',{attribution:'',maxZoom:18}).addTo(thMap);
  hs.forEach(h=>{
    const c=h.risk==='high'?'#dc2626':h.risk==='medium'?'#d97706':'#16a34a';
    L.circleMarker([h.lat,h.lng],{radius:h.risk==='high'?18:h.risk==='medium'?13:9,color:c,fillColor:c,fillOpacity:0.15,weight:1.5,dashArray:'4,2'}).addTo(thMap).bindPopup('<b>'+h.city+'</b><br>Risk: '+h.risk.toUpperCase()+'<br>'+h.note);
  });
  const markers=[];
  inc.forEach((i,idx)=>{
    if(!i.lat||!i.lng)return;
    const popup='<b>'+i.title+'</b><br><span style="color:#dc2626;font-weight:600;">'+i.value+'</span><br>'+i.date+' &middot; '+i.location+'<br><b>Method:</b> '+i.method+'<br><b>Prevention:</b> '+i.prevention;
    const m=L.circleMarker([i.lat,i.lng],{radius:7,color:'#dc2626',fillColor:'#dc2626',fillOpacity:0.6,weight:2}).addTo(thMap).bindPopup(popup);
    markers.push({marker:m,lat:i.lat,lng:i.lng});
  });
  let h='<div style="padding:6px 10px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;">Recent Incidents</div>';
  inc.forEach((i,idx)=>{
    const ds=new Date(i.date).toLocaleDateString('en-CA',{month:'short',day:'numeric'});
    h+='<div class="mitem" data-idx="'+idx+'">';
    h+='<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:4px;">';
    h+='<span style="font-size:11px;font-weight:600;color:var(--text);">'+i.title+'</span>';
    h+='<span style="font-size:12px;font-weight:700;color:var(--red);white-space:nowrap;">'+i.value+'</span></div>';
    h+='<div style="font-size:9px;color:var(--muted);margin-top:3px;display:flex;gap:8px;flex-wrap:wrap;">';
    h+='<span>'+ds+'</span><span>'+i.location+'</span><span>'+i.business+'</span></div>';
    h+='<div style="font-size:9px;color:var(--amber);margin-top:2px;font-weight:600;">Method: '+i.method+'</div>';
    h+='<div style="font-size:8px;color:var(--green);margin-top:2px;line-height:1.3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:260px;">Prevention: '+i.prevention+'</div>';
    h+='</div>';
  });
  h+='<div style="margin:8px 10px 0;font-size:9px;color:var(--muted);text-transform:uppercase;">Hotspots</div>';
  hs.forEach((hs,i)=>{
    const c=hs.risk==='high'?'#dc2626':hs.risk==='medium'?'#d97706':'#16a34a';
    h+='<div class="mitem"><div style="display:flex;justify-content:space-between"><span style="font-weight:600;font-size:11px;">'+hs.city+'</span><span style="font-size:8px;padding:1px 5px;border-radius:3px;background:'+c+'18;color:'+c+'">'+hs.risk.toUpperCase()+'</span></div><div style="font-size:9px;color:var(--muted)">'+hs.note+'</div></div>';
  });
  h+='<div style="margin:8px 10px 0;font-size:9px;color:var(--muted);text-transform:uppercase;">Most Targeted</div><div style="display:flex;flex-wrap:wrap;gap:3px;padding:4px 10px 8px">';
  tg.forEach(t=>{h+='<span style="font-size:9px;background:var(--bg);padding:2px 6px;border-radius:3px">'+t+'</span>';});
  h+='</div><div style="margin:0 10px;font-size:9px;color:var(--muted);text-transform:uppercase;">Prevention</div>';
  tp.forEach(t=>{h+='<div style="font-size:9px;padding:3px 10px;border-bottom:1px solid var(--light)">'+t+'</div>';});
  if(d.source)h+='<div style="color:var(--muted);font-size:8px;padding:4px 10px">'+d.source+'</div>';
  ld.innerHTML=h;
  ld.querySelectorAll('.mitem[data-idx]').forEach(el=>{
    el.addEventListener('click',()=>{
      const idx=parseInt(el.dataset.idx),m=markers[idx];
      if(m&&thMap){thMap.flyTo([m.lat,m.lng],10,{duration:1});setTimeout(()=>m.marker.openPopup(),800);}
    });
  });
  setTimeout(()=>{if(thMap)thMap.invalidateSize();},100);
}

// ── Calculator ──
let cDists=null,cCities=[],cFuel=null,cType='diesel';
function initCalc(dd,fd){cDists=dd.distances||{};cCities=dd.cities||[];cFuel=fd;const fe=document.getElementById('calc-from'),te=document.getElementById('calc-to');if(!fe||!te)return;fe.innerHTML=te.innerHTML=cCities.map(c=>'<option value="'+c.code+'">'+c.name+'</option>').join('');fe.value='YYZ';te.value='YUL';fe.addEventListener('change',rCalc);te.addEventListener('change',rCalc);document.getElementById('calc-eff').addEventListener('input',rCalc);document.querySelectorAll('#fuel-toggle button').forEach(b=>{b.addEventListener('click',()=>{document.querySelectorAll('#fuel-toggle button').forEach(x=>x.classList.remove('active'));b.classList.add('active');cType=b.dataset.fuel;rCalc();});});rCalc();}
function gDist(a,b){if(a===b)return 0;return cDists[a+'-'+b]||cDists[b+'-'+a]||null;}
function gPrice(pr,f){const m={BC:'BC',AB:'AB',SK:'SK',MB:'MB',ON:'ON',QC:'QC',NB:'NB',NS:'NS',PE:'PE',NL:'NL','US-WA':'US-WA','US-OR':'US-OR','US-CA':'US-CA','US-TX':'US-TX','US-MN':'US-MN','US-IL':'US-IL','US-MI':'US-MI','US-NY':'US-NY','US-NJ':'US-NJ','US-GA':'US-GA'};const r=cFuel.provinces[m[pr]||'ON'];return r?f==='diesel'?r.diesel:r.gasoline:null;}
function rCalc(){const fc=document.getElementById('calc-from').value,tc=document.getElementById('calc-to').value,eff=parseFloat(document.getElementById('calc-eff').value)||35,re=document.getElementById('calc-result');if(fc===tc){re.classList.remove('v');return;}const d=gDist(fc,tc);if(d===null){re.innerHTML='<div class="ccost">Route unavailable</div>';re.classList.add('v');return;}const f=cCities.find(c=>c.code===fc),t=cCities.find(c=>c.code===tc),p1=gPrice(f?f.province:'ON',cType),p2=gPrice(t?t.province:'ON',cType);if(!p1||!p2){re.innerHTML='<div class="ccost">Price unavailable</div>';re.classList.add('v');return;}const ap=(p1+p2)/2,litres=(d/100)*eff,cost=(litres*ap)/100;re.innerHTML='<div class="ccost">$'+cost.toFixed(2)+'</div><div class="cbreak"><strong>'+(f?f.name:fc)+'</strong> → <strong>'+(t?t.name:tc)+'</strong><br>'+d.toLocaleString()+' km &middot; '+eff+' L/100km &middot; '+litres.toFixed(1)+' L<br>'+(cType==='diesel'?'Diesel':'Gasoline')+': '+ap.toFixed(1)+'&cent;/L avg</div>';re.classList.add('v');}

// ── Newsletter ──
function subscribeNewsletter(e){
  e.preventDefault();
  const email=document.getElementById('nl-email').value.trim();
  const msg=document.getElementById('nl-msg');
  if(!email){msg.textContent='Please enter your email.';msg.style.color='var(--red)';msg.style.display='block';return;}
  const ghostUrl='https://northernmilemedia.com/members/api/send-magic-link/';
  fetch(ghostUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,emailType:'subscribe'})})
    .then(r=>{if(!r.ok)throw new Error('Failed');msg.textContent='Check your email for a confirmation link.';msg.style.color='var(--green)';msg.style.display='block';})
    .catch(()=>{msg.textContent='Check your email to confirm. If it does not arrive, try again in a moment.';msg.style.color='var(--green)';msg.style.display='block';});
  document.getElementById('nl-email').value='';
}
function subscribeNewsletterBottom(e){
  e.preventDefault();
  const email=document.getElementById('nl-email-bottom').value.trim();
  const msg=document.getElementById('nl-msg-bottom');
  if(!email){msg.textContent='Please enter your email.';msg.style.color='var(--red)';msg.style.display='block';return;}
  const ghostUrl='https://northernmilemedia.com/members/api/send-magic-link/';
  fetch(ghostUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:email,emailType:'subscribe'})})
    .then(r=>{if(!r.ok)throw new Error('Failed');msg.textContent='Check your email for a confirmation link.';msg.style.color='var(--green)';msg.style.display='block';})
    .catch(()=>{msg.textContent='Check your email to confirm. If it does not arrive, try again in a moment.';msg.style.color='var(--green)';msg.style.display='block';});
  document.getElementById('nl-email-bottom').value='';
}

// ── Load ──
async function loadAll(){
  const[exchange,market,fuel,news,distances,border,incidents,theft]=await Promise.all([
    LJ(DB+'exchange.json').catch(()=>null),LJ(DB+'market.json').catch(()=>null),LJ(DB+'fuel.json').catch(()=>null),
    LJ(DB+'news.json').catch(()=>null),LJ(DB+'distances.json').catch(()=>null),LJ(DB+'border.json').catch(()=>null),
    LJ(DB+'incidents.json').catch(()=>null),LJ(DB+'theft.json').catch(()=>null),
  ]);
  const panels=[
    {id:'market-card',data:market,render:renderMarket},
    {id:'exchange-card',data:exchange,render:renderExchange},
    {id:'border-card',data:border,render:renderBorder},
    {id:'news-card',data:news,render:renderNews},
    {id:'incidents-card',data:incidents,render:renderIncidents},
    {id:'theft-card',data:theft,render:renderTheft},
  ];
  // Load sponsors
  LJ(DB+'sponsors.json').then(s=>{
    if(!s)return;
    const map={incidents:'sponsor-incidents',exchange:'sponsor-exchange',border:'sponsor-border',fuel:'sponsor-fuel',market:'sponsor-market',theft:'sponsor-theft',headlines:'sponsor-headlines'};
    Object.keys(map).forEach(k=>{
      const v=s[k];if(!v)return;const el=document.getElementById(map[k]);if(!el)return;
      const name=typeof v==='string'?v:v.name||'';
      const tagline=typeof v==='string'?'':v.tagline||'';
      const logo=typeof v==='string'?'':v.logo||'';
      el.innerHTML=''
        +(logo?'<img src="'+logo+'" alt="'+name+' logo">':'')
        +'<div class="sponsor-info">'
        +'<div class="sponsor-label">Presented by</div>'
        +'<div class="sponsor-name">'+name+'</div>'
        +(tagline?'<div class="sponsor-tagline">'+tagline+'</div>':'')
        +'</div>';
      el.classList.add('active');
    });
  }).catch(()=>{});
  // Add update timestamps to headers
  const updateFreq={market:'Daily',theft:'Daily',incidents:'Every 30 min',border:'Every 30 min',exchange:'Every 30 min',fuel:'Every 30 min',news:'Every 30 min'};
  const dataMap={market,fuel,exchange:exchange,border,news,incidents,theft};
  Object.keys(updateFreq).forEach(k=>{
    const d=dataMap[k];if(!d||!d.updated)return;
    const card=document.getElementById(k+'-card');if(!card)return;
    const header=card.querySelector('.card-header');if(!header)return;
    let right=header.querySelector('.card-header-right');
    if(!right){right=document.createElement('div');right.className='card-header-right';
      // Move existing pill into right div
      const pill=header.querySelector('.pill');if(pill)right.appendChild(pill);
      header.appendChild(right);}
    if(!right.querySelector('.header-update')){
      const el=document.createElement('span');el.className='header-update';
      el.textContent='Updated '+ft(d.updated);
      right.appendChild(el);
    }
  });
  panels.forEach(p=>{
    const b=cardBody(p.id);if(!b)return;
    b.innerHTML=p.data?p.render(p.data):'<div class="error">Failed to load</div>';
  });
  if(fuel){
    const fb=cardBody('fuel-card');if(fb)fb.innerHTML=renderFuelSVG(fuel,pFuelType);
  }
  if(distances&&fuel)initCalc(distances,fuel);
  // Fuel toggle
  document.querySelectorAll('#prices-toggle button').forEach(b=>{
    b.addEventListener('click',()=>{
      document.querySelectorAll('#prices-toggle button').forEach(x=>x.classList.remove('active'));
      b.classList.add('active');
      pFuelType=b.dataset.fuel;
      const fb=cardBody('fuel-card');if(fb&&fuel)fb.innerHTML=renderFuelSVG(fuel,pFuelType);
    });
  });
  setTimeout(()=>{initIncMap();initThMap();},400);
}
loadAll();
</script>
"""

# ── Build ──
def build():
    page = HTML.replace('$$CSS$$', CSS.strip())
    page = page.replace('$$SCRIPTS$$', SCRIPTS.strip())
    
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        f.write(page)
    
    # Validate
    div_open = page.count('<div')
    div_close = page.count('</div>')
    script_open = page.count('<script')
    script_close = page.count('</script>')
    
    print(f'Dashboard built: {OUT}')
    print(f'  Size: {len(page):,} bytes')
    print(f'  <div>: {div_open}  </div>: {div_close}')
    print(f'  <script>: {script_open}  </script>: {script_close}')
    
    if div_open != div_close:
        print(f'  WARNING: div mismatch ({div_open} vs {div_close})')
    else:
        print(f'  HTML structure: CLEAN')
    
    return True

if __name__ == '__main__':
    build()
