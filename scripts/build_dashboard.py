#!/usr/bin/env python3
"""Northern Mile Dashboard — Visual Restructure. 
Phase 1: 12-col grid, new module order, dark palette derived from highway signage.
"""
import json, os
from datetime import datetime

OUT = os.path.expanduser('~/northern-mile-dashboard/docs/index.html')

# ── Design Tokens & CSS ──
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
/* Typography */
.barlow{font-family:'Barlow Condensed',sans-serif;font-weight:600}
body,.inter{font-family:'Inter',-apple-system,sans-serif}
.mono,.timestamp{font-family:'IBM Plex Mono',monospace;font-weight:400}
*{font-variant-numeric:tabular-nums}

/* Banner */
.banner{
  background:var(--asphalt);border-bottom:1px solid var(--line);
  padding:0 24px;display:flex;align-items:center;justify-content:center;
  position:sticky;top:0;z-index:1000;height:64px
}
.banner h1{font-size:0.875rem;font-weight:700;color:var(--salt);font-family:'IBM Plex Mono',monospace;letter-spacing:-.01em}

/* Grid */
.main{max-width:1320px;margin:0 auto;padding:16px 16px 40px}
.grid{display:grid;grid-template-columns:repeat(12,1fr);gap:16px}

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

/* Card chrome */
.eyebrow{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.eyebrow-label{font-size:0.75rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.08em;font-weight:500}
.status-pill{font-size:0.625rem;padding:2px 8px;border-radius:var(--pill-radius);font-weight:600;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap;display:flex;align-items:center;gap:5px}
.status-pill.live{color:var(--gantry);background:rgba(31,107,74,.15)}
.status-pill.live::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--gantry);animation:pulse 2s ease-in-out infinite}
.status-pill.daily{color:var(--gravel);background:rgba(139,147,156,.12)}
.status-pill.reference{color:var(--gravel);background:transparent;border:1px solid var(--line)}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}
@media(prefers-reduced-motion:reduce){.status-pill.live::before{animation:none}}

.card-footer{margin-top:12px;padding-top:8px;border-top:1px solid var(--line);font-size:0.625rem;color:var(--gravel);font-family:'IBM Plex Mono',monospace}

/* Skeleton + fade */
.skeleton{background:var(--line);border-radius:2px;overflow:hidden;position:relative}
.skeleton::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.04),transparent);animation:shimmer 1.5s linear infinite}
@keyframes shimmer{0%{transform:translateX(-100%)}100%{transform:translateX(100%)}}
@media(prefers-reduced-motion:reduce){.skeleton::after{animation:none}}
.fade-in{animation:fadeIn .15s ease-out}
@keyframes fadeIn{0%{opacity:0}100%{opacity:1}}

/* Focus */
*:focus-visible{outline:2px solid var(--amber);outline-offset:2px}

/* Fuel Hero */
.hero-content{display:grid;grid-template-columns:2fr 1fr;gap:24px;align-items:start}
.hero-price{font-size:2.75rem;line-height:1;color:var(--salt)}.hero-price .unit{font-size:1.125rem;color:var(--gravel)}
.hero-delta{display:inline-flex;align-items:center;gap:3px;margin-top:4px;font-size:0.75rem;font-weight:600;padding:2px 8px;border-radius:var(--pill-radius)}
.hero-delta.up{background:rgba(242,169,0,.15);color:var(--amber)}.hero-delta.down{background:rgba(31,107,74,.15);color:var(--gantry)}
.hero-province-list{display:flex;flex-direction:column}.hero-prow{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--line);font-size:0.75rem}.hero-prow:last-child{border-bottom:none}.hero-prow .pcode{font-family:'IBM Plex Mono',monospace;color:var(--gravel)}.hero-prow .pprice{font-family:'IBM Plex Mono',monospace}.pprice.high{color:var(--amber)}.pprice.low{color:var(--gantry)}
.ftoggle{display:flex;background:var(--asphalt);border:1px solid var(--line);border-radius:var(--pill-radius);overflow:hidden}
.ftoggle button{flex:1;background:none;border:none;color:var(--gravel);padding:4px 10px;font-size:0.625rem;font-family:inherit;cursor:pointer;font-weight:600;white-space:nowrap}
.ftoggle button.active{background:var(--salt);color:var(--asphalt)}

/* Border cards */
.bgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
.bx{background:var(--asphalt);border:1px solid var(--line);border-radius:4px;padding:12px;display:flex;justify-content:space-between;align-items:center;gap:8px}
.bx-left{min-width:0}.bx-name{font-size:0.75rem;font-weight:600;color:var(--salt)}.bx-route{font-size:0.625rem;color:var(--gravel);margin-top:2px}
.bx-status{text-align:right}.sbar{display:flex;align-items:center;gap:5px;font-size:0.75rem}.sdot{width:8px;height:8px;border-radius:50%}.sdot.green{background:var(--gantry)}.sdot.amber{background:var(--amber)}.sdot.red{background:var(--flare)}.slabel{font-weight:600;color:var(--salt)}.sdelay{color:var(--gravel);font-size:0.625rem}

/* Incidents map */
.mwrap{display:flex;gap:0;height:100%;border-radius:var(--radius);overflow:hidden}
.mmap{flex:1;min-height:360px;background:#1a1d21}.mlist{width:280px;overflow-y:auto;flex-shrink:0;font-size:0.75rem}
.mitem{padding:8px 10px;border-bottom:1px solid var(--line);cursor:pointer}
.mitem:hover{background:rgba(255,255,255,.03)}
.mhwy{font-weight:600;color:var(--salt)}.mdesc{color:var(--gravel);font-size:0.625rem;margin-top:2px}
.leaflet-container{background:#1a1d21!important;font-family:inherit;z-index:1}
.leaflet-popup-content-wrapper{background:var(--slab)!important;color:var(--salt)!important;border-radius:8px!important}

/* Headlines */
.nitem{padding:8px 0;border-bottom:1px solid var(--line)}.nitem:last-child{border-bottom:none}
.nsrc{font-size:0.625rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em}
.ntitle{color:var(--salt);text-decoration:none;font-size:0.75rem;line-height:1.4;font-weight:500}
.ntitle:hover{text-decoration:underline}

/* Calculator */
.cform{display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end}
.cfield{flex:1;min-width:100px}
.cfield label{font-size:0.625rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px}
.cfield select,.cfield input{width:100%;background:var(--asphalt);border:1px solid var(--line);color:var(--salt);padding:8px 10px;border-radius:4px;font-size:0.75rem;font-family:inherit}
.cfield select:focus,.cfield input:focus{outline:none;border-color:var(--amber)}
.ftoggle button.active{background:var(--salt);color:var(--asphalt)}
.cresult{margin-top:12px;padding:12px;background:var(--asphalt);border-radius:4px;display:none}.cresult.v{display:block}.ccost{font-size:1.75rem;font-weight:600;font-family:'Barlow Condensed',sans-serif;color:var(--salt)}.cbreak{margin-top:6px;font-size:0.75rem;color:var(--gravel);line-height:1.6}

/* Theft */
.theft-item{padding:10px 0;border-bottom:1px solid var(--line);font-size:0.75rem}
.theft-item:last-child{border-bottom:none}.theft-method{color:var(--flare);font-weight:600;font-size:0.625rem;text-transform:uppercase;letter-spacing:.04em}.theft-prevention{color:var(--gravel);font-size:0.625rem;margin-top:3px}

@media(max-width:900px){
  .hero-content{grid-template-columns:1fr;gap:12px}
  .mwrap{flex-direction:column;height:auto!important}.mmap{min-height:260px!important}.mlist{width:100%!important;max-height:200px}
  .cform{flex-direction:column}.cfield{min-width:100%}
}
"""

# ── HTML Template ──
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Northern Mile — Live Canadian Trucking Dashboard</title>
<meta name="description" content="Free live dashboard for Canadian trucking. Fuel prices, border crossings, road incidents. No signup.">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/">
<meta property="og:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<meta property="og:description" content="Diesel prices, border status, road incidents. No signup. Free forever.">
<meta property="og:url" content="https://dashboard.northernmilemedia.com/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Northern Mile Media">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<link rel="icon" type="image/png" sizes="32x32" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&family=IBM+Plex+Mono:wght@400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="leaflet.css">
<script src="leaflet.js"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
<style>$$CSS$$</style>
</head>
<body>

<div class="banner">
  <h1>NORTHERN MILE MEDIA</h1>
</div>

<div class="main">

  <div style="text-align:center;padding:8px 18px;margin-bottom:16px;font-size:0.875rem;color:var(--gravel);">
    Live data for Canadian trucking. Fuel prices. Border delays. Road incidents. Free. Always.
  </div>

  <div class="grid">

    <!-- 1. Fuel Prices — HERO -->
    <div class="module hero" id="fuel-card">
      <div class="eyebrow">
        <span class="eyebrow-label">Fuel Prices</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <div class="ftoggle" id="prices-toggle"><button data-fuel="diesel" class="active">Diesel</button><button data-fuel="gasoline">Gas</button></div>
          <span class="status-pill daily">Daily</span>
        </div>
      </div>
      <div class="sponsor-line" id="sponsor-fuel"></div>
      <div class="card-body"><div class="skeleton" style="height:140px;"></div></div>
    </div>

    <!-- 2. Border Crossings — WIDE -->
    <div class="module wide" id="border-card">
      <div class="eyebrow"><span class="eyebrow-label">Border Crossings</span><span class="status-pill live">Live</span></div>
      <div class="sponsor-line" id="sponsor-border"></div>
      <div class="card-body"><div class="skeleton" style="height:200px;"></div></div>
    </div>

    <!-- 3. USD/CAD — COMPACT -->
    <div class="module compact" id="exchange-card">
      <div class="eyebrow"><span class="eyebrow-label">USD / CAD</span><span class="status-pill live">Live</span></div>
      <div class="sponsor-line" id="sponsor-exchange"></div>
      <div class="card-body"><div class="skeleton" style="height:100px;"></div></div>
    </div>

    <!-- 4. Road Incidents — TALL -->
    <div class="module tall" id="incidents-card">
      <div class="eyebrow"><span class="eyebrow-label">Road Incidents</span><span class="status-pill live">Live</span></div>
      <div class="sponsor-line" id="sponsor-incidents"></div>
      <div class="card-body"><div class="skeleton" style="height:360px;"></div></div>
    </div>

    <!-- 5. Fuel Cost Calculator — STANDARD -->
    <div class="module standard" id="calc-card">
      <div class="eyebrow"><span class="eyebrow-label">Fuel Calculator</span><span class="status-pill live">Live</span></div>
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

    <!-- 6. Market Pulse — STANDARD -->
    <div class="module standard" id="market-card">
      <div class="eyebrow"><span class="eyebrow-label">Market Pulse</span><span class="status-pill daily">Daily</span></div>
      <div class="sponsor-line" id="sponsor-market"></div>
      <div class="card-body"><div class="skeleton" style="height:120px;"></div></div>
    </div>

    <!-- 7. Industry Headlines — WIDE -->
    <div class="module wide" id="news-card">
      <div class="eyebrow"><span class="eyebrow-label">Industry Headlines</span><span class="status-pill daily">Daily</span></div>
      <div class="sponsor-line" id="sponsor-headlines"></div>
      <div class="card-body" style="max-height:320px;overflow-y:auto;"><div class="skeleton" style="height:200px;"></div></div>
    </div>

    <!-- 8. Cargo Theft — STANDARD -->
    <div class="module standard" id="theft-card">
      <div class="eyebrow"><span class="eyebrow-label">Cargo Theft</span><span class="status-pill reference">Reference</span></div>
      <div class="sponsor-line" id="sponsor-theft"></div>
      <div class="card-body" style="max-height:300px;overflow-y:auto;"><div class="skeleton" style="height:120px;"></div></div>
    </div>

  </div>

</div>

<div style="text-align:center;min-height:220px;margin-top:32px;padding:24px;background:var(--slab);border:1px solid var(--line);border-radius:var(--radius);">
  <div style="font-size:0.875rem;font-weight:600;color:var(--salt);margin-bottom:4px;">Get the Northern Mile Brief</div>
  <div style="font-size:0.75rem;color:var(--gravel);margin-bottom:16px;">Fuel prices, market shifts, and what it means. Every Wednesday.</div>
  <script src="https://cdn.jsdelivr.net/ghost/signup-form@~0.3/umd/signup-form.min.js" data-background-color="#1E2227" data-text-color="#E8EAEC" data-button-color="#E8EAEC" data-button-text-color="#15171A" data-title="" data-description="" data-site="https://www.northernmilemedia.com/" data-locale="en" async></script>
</div>

<footer style="padding:16px 24px;text-align:center;font-size:0.625rem;color:var(--gravel);border-top:1px solid var(--line);font-family:'IBM Plex Mono',monospace;">
  &copy; 2026 Northern Mile Media &middot; Data from public sources &middot; Informational use only
</footer>

$$SCRIPTS$$
</body>
</html>"""

# ── JavaScript ──
SCRIPTS = r"""
<script>
const DB='data/';

function ft(iso){return iso?new Date(iso).toLocaleString('en-CA',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'';}
async function LJ(p){const r=await fetch(p);if(!r.ok)throw Error('HTTP '+r.status);return r.json();}

function cardBody(id){return document.querySelector('#'+id+' .card-body');}

function relTime(iso){
  if(!iso)return'';
  const diff=Math.floor((Date.now()-new Date(iso))/1000);
  if(diff<60)return'Just now';
  if(diff<3600)return Math.floor(diff/60)+'m ago';
  if(diff<86400)return Math.floor(diff/3600)+'h ago';
  return Math.floor(diff/86400)+'d ago';
}

// Update relative timestamps every 60s
function stampFooter(cardId,updated){var f=document.querySelector('#'+cardId+' .ts-foot');if(f)f.textContent='Updated '+relTime(updated);}
setInterval(function(){
  document.querySelectorAll('[data-updated]').forEach(function(el){var t=el.getAttribute('data-updated');el.textContent='Updated '+relTime(t);});
},60000);

// ── Market ──
function renderMarket(d){
  if(!d||!d.indicators)return'<div class="error" style="color:var(--flare);padding:8px 0;font-size:0.75rem;">Market data unavailable</div>';
  let h='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;">';
  d.indicators.forEach(function(i){
    var icon=i.direction==='up'?'↑':i.direction==='down'?'↓':'→';
    var ic=i.direction==='up'?'var(--gantry)':i.direction==='down'?'var(--flare)':'var(--gravel)';
    h+='<div style="background:var(--asphalt);border-radius:4px;padding:12px;">';
    h+='<div style="display:flex;justify-content:space-between;"><span style="font-size:0.625rem;color:var(--gravel);text-transform:uppercase;letter-spacing:.04em;">'+i.label+'</span><span style="color:'+ic+';font-weight:600;font-size:0.875rem;">'+icon+'</span></div>';
    h+='<div style="font-size:1.125rem;font-weight:600;color:var(--salt);margin:2px 0;">'+i.value+'</div>';
    if(i.detail)h+='<div style="font-size:0.75rem;color:var(--salt);">'+i.detail+'</div>';
    h+='<div style="font-size:0.625rem;color:var(--gravel);margin-top:6px;padding-top:6px;border-top:1px solid var(--line);">'+(i.what_it_means||'')+'</div>';
    h+='</div>';
  });
  return h+'</div>';
}

// ── Exchange ──
function renderExchange(d){
  if(!d||d.current==null)return'<div style="color:var(--gravel);font-size:0.75rem;">Exchange data unavailable</div>';
  var ch=d.change||0,chPct=d.change_pct||0;
  var dir=ch>=0?'up':'down',dirLabel=ch>=0?'Stronger CAD':'Weaker CAD';
  var chStr=(ch>=0?'+':'')+ch.toFixed(4)+' ('+(ch>=0?'+':'')+chPct+'%)';
  var impact=ch>=0?'Cheaper US fuel/equipment. US loads pay less CAD.':'US loads pay more CAD. US fuel costs more.';
  return '<div><div style="font-size:0.625rem;color:var(--gravel);margin-bottom:2px;">1 US Dollar equals</div>'+
    '<div style="font-size:1.75rem;font-weight:600;color:var(--salt);" class="barlow">'+d.current.toFixed(4)+' CAD</div>'+
    '<div style="font-size:0.75rem;font-weight:600;color:'+(ch>=0?'var(--gantry)':'var(--flare)')+';margin-top:2px;">'+dir+' '+chStr+'</div>'+
    '<div style="font-size:0.625rem;color:var(--gravel);margin-top:8px;line-height:1.4;">'+impact+'</div></div>';
}

// ── Fuel Hero ──
var pFuelType='diesel';
function renderFuelHero(d,type){
  var P=d.provinces||{};
  var ca=['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL'];
  var label=type==='diesel'?'Diesel':'Gasoline';
  var avg=type==='diesel'?d.diesel_national_avg:d.gasoline_national_avg;
  var unit=type==='diesel'?'¢/L':'¢/L';
  var prevAvg=type==='diesel'?d.prev_diesel_avg||avg:avg-0.5;
  var delta=avg-prevAvg,up=delta>0;
  var arr=up?'↑':'↓';
  
  var vals=ca.map(function(p){return(P[p]||{})[type]||0;});
  var minV=Math.min.apply(null,vals),maxV=Math.max.apply(null,vals);
  var idxMin=vals.indexOf(minV),idxMax=vals.indexOf(maxV);
  
  var rows='';
  ca.forEach(function(p,i){
    var v=vals[i];
    var cls=v===maxV?' high':v===minV?' low':'';
    rows+='<div class="hero-prow"><span class="pcode">'+p+'</span><span class="pprice'+cls+'">'+v.toFixed(1)+'</span></div>';
  });
  
  return '<div class="hero-content">'+
    '<div>'+
      '<div class="hero-price">'+avg.toFixed(1)+'<span class="unit"> '+unit+'</span></div>'+
      '<div class="hero-delta '+(up?'up':'down')+'">'+arr+' '+(delta>=0?'+':'')+delta.toFixed(1)+'</div>'+
      '<div style="font-size:0.625rem;color:var(--gravel);margin-top:6px;">National average — '+label+'</div>'+
    '</div>'+
    '<div class="hero-province-list">'+rows+'</div>'+
    '</div>';
}

// ── Border ──
function getBS(c){
  var now=new Date(),h=now.getHours(),dy=now.getDay(),wd=dy>=1&&dy<=5;
  var peak=(h>=7&&h<=9)||(h>=15&&h<=18),night=h>=22||h<=4;
  var high=['windsor-detroit','fort-erie-buffalo','pacific-blaine','lacolle-champlain'].indexOf(c.id)>=0;
  if(night&&!high)return{status:'green',delay:'< 5 min',label:'Clear'};
  if(peak&&high&&wd)return{status:'red',delay:'30-60 min',label:'Heavy'};
  if(peak||(high&&wd))return{status:'amber',delay:'10-25 min',label:'Moderate'};
  if(!wd&&high&&h>=10&&h<=16)return{status:'amber',delay:'15-30 min',label:'Weekend'};
  return{status:'green',delay:'5-15 min',label:'Normal'};
}
function renderBorder(d){
  var cs=d.crossings||[],bl=d.blitz_dates||[];
  var h='<div class="bgrid">';
  cs.forEach(function(c){var st=getBS(c);
    h+='<div class="bx"><div class="bx-left"><div class="bx-name">'+c.name+'</div><div class="bx-route">'+c.route+' &middot; '+c.highway+'</div></div>';
    h+='<div class="bx-status"><div class="sbar"><span class="sdot '+st.status+'"></span><span class="slabel">'+st.label+'</span></div><div class="sdelay">'+st.delay+'</div></div></div>';
  });
  h+='</div>';
  if(bl.length){h+='<div style="margin-top:8px;padding:8px 12px;background:rgba(242,169,0,.08);border-radius:4px;font-size:0.625rem;color:var(--amber);">';
    bl.forEach(function(b){var days=Math.ceil((new Date(b.date)-Date.now())/86400000);
      h+='<span style="font-weight:600;">'+new Date(b.date).toLocaleDateString('en-CA',{month:'short',day:'numeric'})+'</span> &middot; '+b.name+' ('+days+'d) ';
    });
    h+='</div>';}
  return h;
}

// ── News ──
function renderNews(d){
  var hl=d.headlines||[];if(!hl.length)return'<div style="color:var(--gravel);font-size:0.75rem;">No headlines</div>';
  var cc={regulations:{bg:'rgba(37,99,235,.1)',c:'#60a5fa'},markets:{bg:'rgba(242,169,0,.1)',c:'#fbbf24'},equipment:{bg:'rgba(124,58,237,.1)',c:'#a78bfa'},business:{bg:'rgba(31,107,74,.1)',c:'#4ade80'},technology:{bg:'rgba(190,24,93,.1)',c:'#f472b6'},drivers:{bg:'rgba(194,65,12,.1)',c:'#fb923c'},safety:{bg:'rgba(220,38,38,.1)',c:'#f87171'},industry:{bg:'rgba(71,85,105,.1)',c:'#94a3b8'}};
  var sc={'Truck News':'#60a5fa','Trucking Info':'#4ade80','The Trucker':'#fbbf24'};
  var h='';hl.forEach(function(n){
    var cat=n.categories?.[0]||'industry',c=cc[cat]||cc.industry,srcC=sc[n.source]||'var(--gravel)';
    var ds=n.date?new Date(n.date).toLocaleDateString('en-CA',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}):'';
    h+='<div class="nitem"><div style="display:flex;align-items:center;gap:5px;margin-bottom:3px;flex-wrap:wrap">';
    h+='<span class="nsrc" style="color:'+srcC+';">'+n.source+'</span>';
    h+='<span style="font-size:0.5rem;padding:1px 5px;border-radius:3px;font-weight:600;text-transform:capitalize;background:'+c.bg+';color:'+c.c+';">'+cat+'</span>';
    if(ds)h+='<span style="font-size:0.5rem;color:var(--gravel);margin-left:auto">'+ds+'</span>';
    h+='</div><a class="ntitle" href="'+n.link+'" target="_blank">'+n.title+'</a></div>';
  });
  return h;
}

// ── Incidents Map ──
var incMap=null,incData=null;
function renderIncidents(d){incData=d;return'<div class="mwrap"><div class="mmap" id="inc-map"></div><div class="mlist" id="inc-list"></div></div>';}

// ── Theft ──
function renderTheft(d){
  var incs=d.incidents||[];if(!incs.length)return'<div style="color:var(--gravel);font-size:0.75rem;">No recent theft data</div>';
  var h='';incs.forEach(function(t){
    h+='<div class="theft-item"><div class="theft-method">'+t.method+'</div><div style="color:var(--salt);font-size:0.75rem;margin:2px 0;">'+t.description+'</div><div class="theft-prevention">Prevention: '+t.prevention+'</div></div>';
  });
  return h;
}

// ── Load All ──
(async function(){
  var allData=await Promise.all([LJ(DB+'exchange.json').catch(function(){return null;}),LJ(DB+'market.json').catch(function(){return null;}),LJ(DB+'fuel.json').catch(function(){return null;}),LJ(DB+'news.json').catch(function(){return null;}),LJ(DB+'distances.json').catch(function(){return null;}),LJ(DB+'border.json').catch(function(){return null;}),LJ(DB+'incidents.json').catch(function(){return null;}),LJ(DB+'theft.json').catch(function(){return null;})]);
  var ex=allData[0],mk=allData[1],fl=allData[2],nw=allData[3],di=allData[4],bo=allData[5],inc=allData[6],th=allData[7];
  var modules=[
    {id:'market-card',data:mk,render:renderMarket,updated:mk&&mk.updated},
    {id:'exchange-card',data:ex,render:renderExchange,updated:ex&&ex.updated},
    {id:'fuel-card',data:fl,render:function(d){return renderFuelHero(d,pFuelType);},updated:fl&&fl.updated},
    {id:'border-card',data:bo,render:renderBorder,updated:bo&&bo.updated},
    {id:'incidents-card',data:inc,render:renderIncidents,updated:inc&&inc.updated},
    {id:'news-card',data:nw,render:renderNews,updated:nw&&nw.updated},
    {id:'theft-card',data:th,render:renderTheft,updated:th&&th.updated},
  ];
  
  modules.forEach(function(m){
    var el=document.querySelector('#'+m.id+' .card-body');
    if(!el)return;
    try{
      var html=m.render(m.data);
      el.innerHTML=html;
      el.classList.add('fade-in');
      if(m.updated){
        var ft='<div class="card-footer"><span class="ts-foot" data-updated="'+m.updated+'">Updated '+relTime(m.updated)+'</span></div>';
        var parent=document.getElementById(m.id);
        if(parent&&parent.querySelector('.card-footer'))parent.querySelector('.card-footer').innerHTML='<span class="ts-foot" data-updated="'+m.updated+'">Updated '+relTime(m.updated)+'</span>';
        else{var div=document.createElement('div');div.className='card-footer';div.innerHTML='<span class="ts-foot" data-updated="'+m.updated+'">Updated '+relTime(m.updated)+'</span>';el.parentNode.appendChild(div);}
      }
    }catch(e){
      el.innerHTML='<div style="color:var(--gravel);font-size:0.75rem;">'+m.id.replace('-card','').replace('fuel','Fuel')+' unavailable. Last update unknown.</div>';
    }
  });
  
  // Incidents map init
  setTimeout(function(){
    if(!incData||incData.length===0)return;
    var mc=document.getElementById('inc-map');if(!mc)return;
    incMap=L.map('inc-map').setView([50,-85],4);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'&copy; <a href="https://carto.com/">CARTO</a>'}).addTo(incMap);
    L.Icon.Default.prototype.options.imagePath='https://unpkg.com/leaflet@1.9.4/dist/images/';
    var markers=[],list=document.getElementById('inc-list'),lh='';
    incData.forEach(function(inc,i){
      if(inc.lat&&inc.lon){
        var m=L.marker([inc.lat,inc.lon]).addTo(incMap).bindPopup('<strong>'+inc.highway+'</strong><br>'+inc.state+'<br>'+inc.type+' &middot; '+inc.severity+'<br>'+inc.delay+'<br>'+inc.detour);
        markers.push(m);
        lh+='<div class="mitem" onclick="incMap.setView(['+inc.lat+','+inc.lon+'],10);" style="cursor:pointer"><div class="mhwy">'+inc.highway+' &middot; '+inc.state+'</div><div class="mdesc">'+inc.type+' &middot; '+inc.severity+' &middot; '+inc.delay+'</div></div>';
      }
    });
    if(!lh)lh='<div style="padding:10px;color:var(--gravel);font-size:0.75rem;">No active incidents.</div>';
    list.innerHTML=lh;
    incMap.invalidateSize();
  },300);
  
  // Sponsors
  LJ(DB+'sponsors.json').then(function(s){
    if(s&&s.modules)Object.keys(s.modules).forEach(function(k){
      var sp=s.modules[k],el=document.getElementById('sponsor-'+k);
      if(!el||!sp.logo)return;
      el.className='sponsor-line active';
      el.innerHTML='<img src="'+sp.logo+'" alt="'+sp.name+'"><div class="sponsor-info"><span class="sponsor-label">Presented by</span><span class="sponsor-name">'+sp.name+'</span></div>';
    });
  }).catch(function(){});
  
  // Fuel toggle
  var pt=document.getElementById('prices-toggle');
  if(pt)pt.addEventListener('click',function(e){
    if(e.target.tagName!=='BUTTON')return;
    document.querySelectorAll('#prices-toggle button').forEach(function(b){b.classList.remove('active');});
    e.target.classList.add('active');
    pFuelType=e.target.dataset.fuel;
    if(fl)cardBody('fuel-card').innerHTML=renderFuelHero(fl,pFuelType);
  });
  
  // Calculator
  var calcDistances={},calcFuel={};
  LJ(DB+'distances.json').then(function(d){
    calcDistances=d.distances||{};
    var cities=d.cities||[];
    ['calc-from','calc-to'].forEach(function(id){
      var sel=document.getElementById(id);
      cities.forEach(function(c){var o=document.createElement('option');o.value=c.code;o.textContent=c.name;sel.appendChild(o);});
    });
  }).catch(function(){});
  LJ(DB+'fuel.json').then(function(d){calcFuel=d;}).catch(function(){});
  
  // Calc toggle
  var calcFuelType='diesel';
  document.getElementById('fuel-toggle').addEventListener('click',function(e){
    if(e.target.tagName!=='BUTTON')return;
    document.querySelectorAll('#fuel-toggle button').forEach(function(b){b.classList.remove('active');});
    e.target.classList.add('active');
    calcFuelType=e.target.dataset.fuel;
  });
  
  document.getElementById('calc-eff').addEventListener('input',function(){runCalc();});
  document.getElementById('calc-from').addEventListener('change',function(){runCalc();});
  document.getElementById('calc-to').addEventListener('change',function(){runCalc();});
  
  function runCalc(){
    var from=document.getElementById('calc-from').value;
    var to=document.getElementById('calc-to').value;
    var eff=parseFloat(document.getElementById('calc-eff').value)||35;
    var res=document.getElementById('calc-result');
    if(!from||!to||from===to){res.className='cresult';return;}
    var dist=calcDistances[from+'-'+to]||calcDistances[to+'-'+from];
    if(!dist){res.innerHTML='<div style="color:var(--gravel);font-size:0.75rem;">Route not available.</div>';res.className='cresult v';return;}
    var famt=calcFuel&&calcFuel.provinces?calcFuel.provinces[from.split('-')[0]]:null;
    var rate=famt?famt[calcFuelType]:0;
    if(!rate)rate=calcFuelType==='diesel'?calcFuel.diesel_national_avg:calcFuel.gasoline_national_avg;
    if(!rate)rate=171.9;
    var liters=dist*eff/100,total=liters*rate/100;
    res.innerHTML='<div class="ccost">$'+total.toFixed(2)+'</div><div class="cbreak">'+dist.toLocaleString()+' km &middot; '+eff+' L/100km &middot; '+rate.toFixed(1)+'&cent;/L '+calcFuelType+'</div>';
    res.className='cresult v';
  }
  
})();
</script>
"""

# ── BUILD ──
def build():
    html = HTML.replace('$$CSS$$', CSS).replace('$$SCRIPTS$$', SCRIPTS)
    with open(OUT, 'w') as f:
        f.write(html)
    print(f"Dashboard built: {OUT}")
    print(f"  Size: {len(html):,} bytes")

if __name__ == '__main__':
    build()
