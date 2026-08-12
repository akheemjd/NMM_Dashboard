# NMM — Second Full Dump
Generated: $(date "+%Y-%m-%d %H:%M:%S %Z")

## social_brief.py
NOT PRESENT (find / -name returned nothing)

## requirements.txt
NOT PRESENT

## .gitignore
cloudflared
*.pyc
__pycache__
.DS_Store

## Git Status
Clean — no uncommitted changes

## Git Count-Objects
count: 6683
size: 31.94 MiB
in-pack: 16703
packs: 2
size-pack: 4.52 MiB

---

## TEMPLATES

### templates/_subscribe.html (394 bytes)
```html
<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>
```

### templates/border-wait-times.template.html (6916 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canada–US Border Wait Times for Trucks — Live | Northern Mile</title>
<meta name="description" content="Live commercial border wait times at the major Canada–US crossings, updated every 30 minutes. Ambassador, Blue Water, Peace Bridge, Pacific Highway and more.">
<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical" href="https://dashboard.northernmilemedia.com/border-wait-times/">
<meta property="og:type" content="website"><meta property="og:title" content="Canada–US Truck Border Wait Times — Live | Northern Mile"><meta property="og:description" content="Live commercial wait times at the major Canada–US crossings. Updated every 30 min."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Border Wait Times","item":"https://dashboard.northernmilemedia.com/border-wait-times/"}]},
{"@type":"Dataset","name":"Canada-US Commercial Border Wait Times","description":"Live commercial vehicle wait times at major Canada-US border crossings, updated every 30 minutes.","creator":{"@type":"Organization","name":"Northern Mile Media"},"dateModified":"{{updated_at}}"}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/" class="on">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Border Wait Times</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>Commercial lanes</span><span>Updated {{updated_at}} · refresh 30 min</span></div>

  <section class="cockpit"><div class="gauges">
    <div class="gauge {{border.gauge_class}}"><div class="gl">Busiest now</div><div class="gv">{{border.heavy_count}} <small>Heavy</small></div><div class="gs">{{border.moderate_count}} moderate</div></div>
    <div class="gauge"><div class="gl">Closed</div><div class="gv">{{border.closed_count}}</div><div class="gs">crossings</div></div>
    <div class="gauge"><div class="gl">Longest wait</div><div class="gv">{{border.max_wait}}<small> min</small></div><div class="gs">{{border.max_name}}</div></div>
    <div class="gauge good"><div class="gl">Fastest</div><div class="gv">{{border.min_wait}}<small> min</small></div><div class="gs">{{border.min_name}}</div></div>
  </div></section>

  <!--OPTIONAL:sponsor_border--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_border.name}}</div><div class="l">{{sponsor_border.line}}</div></div><a class="c" href="{{sponsor_border.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_border-->

  <div class="sechead"><h2>All commercial crossings</h2><span class="sub">wait captured at update</span><span class="rule"></span></div>
  <div class="panel"><table class="tbl bx">
  <!--LOOP:crossings--><tr><td>{{name}}<div class="sub">{{sub}} · captured {{captured_at}}</div></td><td class="r"><span class="px">{{wait}}</span></td><td class="r"><span class="pill {{status_class}}">{{status_label}}</span></td></tr><!--/LOOP:crossings-->
  </table></div>
  <p class="note">Wait shown is the commercial-lane time captured at each crossing's last update. Direction: into the US unless noted.</p>

  <div class="sechead"><h2>Common questions</h2><span class="rule"></span></div>
  <div class="faq"><dl>
    <dt>Which crossing is fastest right now?</dt><dd>{{border.min_name}} at {{border.min_wait}} minutes. Times shift through the day — this page refreshes every 30 minutes.</dd>
    <dt>Are these commercial or passenger waits?</dt><dd>Commercial-vehicle lanes. Passenger waits differ and aren't shown here.</dd>
    <dt>How current is the number?</dt><dd>Each crossing carries its own capture time. The overall page updates every 30 minutes.</dd>
  </dl></div>

  <div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/border-wait-times/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Live%20Canada-US%20truck%20border%20wait%20times&url=https://dashboard.northernmilemedia.com/border-wait-times/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/border-wait-times/')">Copy link</button></div>

  <div class="related"><a href="/fuel-prices/">Fuel prices →</a><a href="/road-incidents/">Road incidents →</a><a href="/exchange-rate/">CAD/USD →</a><a href="/cargo-theft/">Cargo theft →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body></html>
```

### templates/cargo-theft.template.html (10656 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Cargo Theft Watch — Recent Incidents | Northern Mile</title>
<meta name="description" content="Recent cargo and trailer theft incidents across Canada, with prevention notes. Reference data from public bulletins, refreshed regularly.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/cargo-theft/">
<meta property="og:type" content="website"><meta property="og:title" content="Canadian Cargo Theft Watch | Northern Mile"><meta property="og:description" content="Recent Canadian cargo theft incidents + prevention notes."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script type="application/ld+json">
{"@context":"https://***@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Cargo Theft","item":"https://dashboard.northernmilemedia.com/cargo-theft/"}]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/" class="on">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Cargo Theft</div>
  <div class="strip"><span>Reference</span><span>Public bulletins · last 12 months</span><span>Updated {{updated_at}}</span></div>

  <!--OPTIONAL:sponsor_theft--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_theft.name}}</div><div class="l">{{sponsor_theft.line}}</div></div><a class="c" href="{{sponsor_theft.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_theft-->

  <div class="sechead"><h2>Cargo theft map</h2><span class="sub">click a pin for details</span><span class="rule"></span></div>
  <div id="theft-map" style="height:400px;border-radius:6px;margin-bottom:20px;"></div>

  <div class="sechead"><h2>Recent cargo theft</h2><span class="sub">reference</span><span class="rule"></span></div>
  <div class="panel" id="theft-list"></div>

  <div class="sechead"><h2>Hotspots</h2><span class="rule"></span></div>
  <div class="panel"><table class="tbl">
  <!--LOOP:hotspots--><tr><td class="prov">{{area}}</td><td class="r mono">{{count}} incidents</td><td class="r mono">{{value}}</td></tr><!--/LOOP:hotspots-->
  </table></div>

  <div class="share" style="margin-top:24px"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/cargo-theft/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Canadian%20cargo%20theft%20watch&url=https://dashboard.northernmilemedia.com/cargo-theft/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/cargo-theft/')">Copy link</button></div>

  <div class="related"><a href="/road-incidents/">Road incidents →</a><a href="/border-wait-times/">Border waits →</a><a href="/industry-news/">Industry news →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Reference data from public bulletins · Informational use only · © 2026 Northern Mile Media</div></div></footer>

<script>window.THEFT_DATA = {{theft_json}};</script>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/app.js?v={{build_version}}"></script>
<script>
(function(){
  var data = window.THEFT_DATA || [];
  var mapEl = document.getElementById('theft-map');
  var listEl = document.getElementById('theft-list');
  if (!data.length || !mapEl) return;

  var map = L.map('theft-map', {scrollWheelZoom: true}).setView([52, -90], 4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OSM'}).addTo(map);
  var markers = [];
  var listHtml = '';

  data.forEach(function(it, i) {
    if (!it.lat || !it.lng) return;
    var popup = '<b>' + it.title + '</b>' +
      '<br>' + it.location + ' &middot; ' + (it.date||'') +
      '<br><span style="color:#E5484D;font-weight:600;">' + it.value + '</span>' +
      (it.business ? '<br><small>Where: ' + it.business + '</small>' : '') +
      (it.method ? '<br><small>How: ' + it.method + '</small>' : '') +
      (it.prevention ? '<br><small style="color:var(--green);">Prevent: ' + it.prevention + '</small>' : '');
    if (it.source_url) {
      popup += '<br><a href="' + it.source_url + '" target="_blank" rel="noopener" style="font-size:0.75rem;">Source →</a>';
    }
    var m = L.circleMarker([it.lat, it.lng], {radius: 10, color: '#E5484D', fillColor: '#E5484D', fillOpacity: 0.85, weight: 2}).addTo(map);
    m.bindPopup(popup);
    markers.push(m);

    listHtml += '<div class="tft theft-row" data-idx="' + markers.length + '" style="cursor:pointer;"' +
      ' data-title="' + (it.title||'').replace(/"/g,'&quot;') + '"' +
      ' data-location="' + (it.location||'').replace(/"/g,'&quot;') + '"' +
      ' data-value="' + (it.value||'') + '"' +
      ' data-date="' + (it.date||'') + '"' +
      ' data-method="' + (it.method||'').replace(/"/g,'&quot;') + '"' +
      ' data-prevention="' + (it.prevention||'').replace(/"/g,'&quot;') + '"' +
      ' data-business="' + (it.business||'').replace(/"/g,'&quot;') + '"' +
      '>' +
      '<div class="h">' + it.title + ' <span class="val">' + it.value + '</span></div>' +
      '<div class="m">' + it.location + '</div></div>';
  });

  listEl.innerHTML = listHtml || '<div class="empty">No recent incidents on monitored corridors</div>';

  // Detail popup panel
  var detailEl = document.createElement('div');
  detailEl.id = 'theft-detail';
  detailEl.style.cssText = 'display:none;position:fixed;top:0;right:0;width:380px;max-width:100vw;height:100vh;background:var(--surface-1);border-left:1px solid var(--border);z-index:9999;overflow-y:auto;padding:24px;font-size:0.875rem;';
  document.body.appendChild(detailEl);

  function showDetail(row) {
    var parts = [];
    parts.push('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">');
    parts.push('<h2 style="margin:0;font-size:1rem;">Incident details</h2>');
    parts.push('<button onclick="document.getElementById(\'theft-detail\').style.display=\'none\'" style="background:none;border:none;color:var(--ink-3);cursor:pointer;font-size:1.25rem;">&times;</button></div>');
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Title</div><div style="font-weight:600;color:var(--ink);">' + (row.getAttribute('data-title')||'') + '</div></div>');
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Value</div><div style="font-size:1.25rem;font-weight:700;color:var(--red);">' + (row.getAttribute('data-value')||'') + '</div></div>');
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Location</div><div>' + (row.getAttribute('data-location')||'') + ' &middot; ' + (row.getAttribute('data-date')||'') + '</div></div>');
    if (row.getAttribute('data-business')) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Where</div><div>' + row.getAttribute('data-business') + '</div></div>');
    if (row.getAttribute('data-method')) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Method</div><div>' + row.getAttribute('data-method') + '</div></div>');
    if (row.getAttribute('data-prevention')) parts.push('<div style="margin-bottom:16px;background:rgba(30,158,102,.08);border-left:2px solid var(--green);padding:12px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--green);margin-bottom:4px;">Prevention</div><div style="color:var(--ink-2);">' + row.getAttribute('data-prevention') + '</div></div>');
    detailEl.innerHTML = parts.join('');
    detailEl.style.display = 'block';
    // Bind close button
    var closeBtn = detailEl.querySelector('.close-detail-btn');
    if (closeBtn) closeBtn.onclick = function() { detailEl.style.display = 'none'; };
  }

  listEl.addEventListener('click', function(e) {
    var row = e.target.closest('.theft-row');
    if (!row) return;
    showDetail(row);
    var idx = parseInt(row.getAttribute('data-idx')) - 1;
    if (markers[idx]) {
      map.setView(markers[idx].getLatLng(), 10);
    }
  });

  setTimeout(function() { map.invalidateSize(); }, 400);
})();
</script>
</body></html>
```

### templates/exchange-rate.template.html (6705 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>USD/CAD Exchange Rate — Live for Truckers | Northern Mile</title>
<meta name="description" content="Live USD to CAD exchange rate from the Bank of Canada, updated every 30 minutes. What a weaker or stronger loonie means for cross-border trucking.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/exchange-rate/">
<meta property="og:type" content="website"><meta property="og:title" content="USD/CAD Exchange Rate — Live | Northern Mile"><meta property="og:description" content="Live USD/CAD from the Bank of Canada, updated every 30 min."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Exchange Rate","item":"https://dashboard.northernmilemedia.com/exchange-rate/"}]},
{"@type":"Dataset","name":"USD/CAD Exchange Rate","description":"Live USD to CAD exchange rate from the Bank of Canada, updated every 30 minutes.","creator":{"@type":"Organization","name":"Northern Mile Media"},"dateModified":"{{updated_at}}"}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/" class="on">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Exchange Rate</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>Bank of Canada</span><span>Updated {{updated_at}} · refresh 30 min</span></div>

  <section class="cluster">
    <div>
      <div class="readlabel"><span class="tick">▸</span> 1 US Dollar equals</div>
      <div class="odo hero-odo" data-value="{{fx.usd_cad}}" data-unit="CAD"></div>
      <div class="trend"><span class="b">{{fx.direction}}</span> {{fx.change}} today</div>
    </div>
    <div class="clus-gauges">
      <div class="g"><div class="gv">{{fx.high_52w}}</div><div class="gl">52-wk high</div></div>
      <div class="g"><div class="gv">{{fx.low_52w}}</div><div class="gl">52-wk low</div></div>
      <div class="g"><div class="gv">{{fx.vs_baseline}}</div><div class="gl">30-day avg</div></div>
    </div>
  </section>

  <!--OPTIONAL:sponsor_fx--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_fx.name}}</div><div class="l">{{sponsor_fx.line}}</div></div><a class="c" href="{{sponsor_fx.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_fx-->

  <div class="sechead"><h2>What it means for you</h2><span class="rule"></span></div>
  <div class="panel">
    <div class="ind"><div class="nm">Cross-border rates<span>Weaker CAD = Canadian carriers more competitive on US-bound freight</span></div><div class="vv">{{fx.direction}}</div></div>
    <div class="ind"><div class="nm">US fuel &amp; parts<span>Weaker CAD raises the cost of fuelling or buying equipment stateside</span></div><div class="vv">{{fx.change}}</div></div>
    <div class="ind"><div class="nm">Fill before you cross<span>Compare US border-state diesel in CAD/L</span></div><a class="vv" href="/fuel-prices/" style="font-size:.75rem;font-family:'IBM Plex Mono',monospace;color:var(--green)">See →</a></div>
  </div>

  <div class="sechead"><h2>Common questions</h2><span class="rule"></span></div>
  <div class="faq"><dl>
    <dt>Where does this rate come from?</dt><dd>The Bank of Canada's published USD/CAD rate, refreshed on the dashboard every 30 minutes.</dd>
    <dt>Why does the exchange rate matter for trucking?</dt><dd>A weaker loonie makes Canadian carriers more competitive on US-bound loads but raises the cost of fuel, parts and equipment bought in the US.</dd>
  </dl></div>

  <div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/exchange-rate/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Live%20USD%2FCAD%20for%20truckers&url=https://dashboard.northernmilemedia.com/exchange-rate/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/exchange-rate/')">Copy link</button></div>

  <div class="related"><a href="/fuel-prices/">Fuel prices →</a><a href="/border-wait-times/">Border waits →</a><a href="/market-pulse/">Market →</a><a href="/fuel-cost-calculator/">Calculator →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body></html>
```

### templates/fuel-cost-calculator.template.html (14021 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Truck Fuel Cost Calculator — Canada | Northern Mile</title>
<meta name="description" content="Trip fuel cost, cost per km, and break-even rate calculator. Pre-loaded with today's Canadian diesel average. Free for owner-operators and dispatchers.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/fuel-cost-calculator/">
<meta property="og:type" content="website"><meta property="og:title" content="Truck Fuel Cost Calculator — Canada | Northern Mile"><meta property="og:description" content="Trip fuel cost, per-km rate and break-even calculator. Free for truckers."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://***@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Fuel Cost Calculator","item":"https://dashboard.northernmilemedia.com/fuel-cost-calculator/"}]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/" class="on">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Fuel Cost Calculator</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>Pre-loaded with NMDI at {{fuel.national_diesel}}c/L</span><span>Updated {{updated_at}}</span></div>

  <!-- 1. Trip Fuel Cost -->
  <div class="sechead"><h2>Trip fuel cost</h2><span class="rule"></span></div>
  <div class="panel" style="padding:20px 22px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
      <div style="flex:1;min-width:120px;"><label class="fl" for="dist">Distance (km)</label><input class="field" id="dist" type="number" value="1000" min="0" oninput="calcAll()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="burn">Burn (L/100km)</label><input class="field" id="burn" type="number" value="38" min="1" oninput="calcAll()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="price">Diesel (c/L)</label><input class="field" id="price" type="number" value="{{fuel.national_diesel}}" min="0" step="0.1" oninput="calcAll()"></div>
    </div>
    <button class="btn" onclick="document.getElementById('price').value='{{fuel.national_diesel}}';calcAll()" style="margin-bottom:12px;">Reset to national avg</button>
    <div class="readout"><div class="rl">Trip fuel cost</div><div class="big" id="trip-cost">—</div><div class="meta" id="trip-detail"></div></div>
  </div>

  <!-- 2. Cost per km -->
  <div class="sechead"><h2>Cost per km</h2><span class="sub">quick rate card</span><span class="rule"></span></div>
  <div class="panel" style="padding:16px 22px">
    <div class="scroll"><table class="tbl">
      <thead><tr><th>Burn rate</th><th class="r">Per km</th><th class="r">Per 100km</th><th class="r">Per 1,000km</th></tr></thead>
      <tbody id="perkm-table"></tbody>
    </table></div>
  </div>

  <!-- 3. Cross-border fuel -->
  <div class="sechead"><h2>Cross-border fuel</h2><span class="sub">USD/gal → CAD c/L</span><span class="rule"></span></div>
  <div class="panel" style="padding:20px 22px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
      <div style="flex:1;min-width:120px;"><label class="fl" for="usd-gal">US diesel (USD/gal)</label><input class="field" id="usd-gal" type="number" value="3.85" step="0.01" oninput="calcUS()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="fx-rate">USD/CAD</label><input class="field" id="fx-rate" type="number" value="{{fx.usd_cad}}" step="0.0001" oninput="calcUS()"></div>
    </div>
    <div class="readout"><div class="rl">Canadian equivalent</div><div class="big" id="us-result">—</div><div class="meta" id="us-detail"></div></div>
  </div>

  <!-- 4. Break-even rate -->
  <div class="sechead"><h2>Break-even rate</h2><span class="sub">minimum you need per km</span><span class="rule"></span></div>
  <div class="panel" style="padding:20px 22px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
      <div style="flex:1;min-width:120px;"><label class="fl" for="be-burn">Burn (L/100km)</label><input class="field" id="be-burn" type="number" value="38" min="1" oninput="calcBE()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="be-diesel">Diesel (c/L)</label><input class="field" id="be-diesel" type="number" value="{{fuel.national_diesel}}" min="0" step="0.1" oninput="calcBE()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="be-fixed">Fixed cost/km (c)</label><input class="field" id="be-fixed" type="number" value="45" min="0" step="1" oninput="calcBE()"></div>
    </div>
    <p style="font-size:0.6875rem;color:var(--ink-3);margin-bottom:12px;">Fixed costs per km: truck payment, insurance, maintenance, plates. Industry average for a Class 8 tractor-trailer is 40–55c/km.</p>
    <div class="readout"><div class="rl">Break-even rate</div><div class="big" id="be-result">—</div><div class="meta" id="be-detail"></div></div>
  </div>

  <!-- 5. Deadhead cost -->
  <div class="sechead"><h2>Deadhead cost</h2><span class="sub">what empty miles cost you</span><span class="rule"></span></div>
  <div class="panel" style="padding:20px 22px">
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;">
      <div style="flex:1;min-width:120px;"><label class="fl" for="dh-km">Deadhead (km)</label><input class="field" id="dh-km" type="number" value="200" min="0" oninput="calcDH()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="dh-burn">Burn (L/100km)</label><input class="field" id="dh-burn" type="number" value="38" min="1" oninput="calcDH()"></div>
      <div style="flex:1;min-width:120px;"><label class="fl" for="dh-diesel">Diesel (c/L)</label><input class="field" id="dh-diesel" type="number" value="{{fuel.national_diesel}}" min="0" step="0.1" oninput="calcDH()"></div>
    </div>
    <div class="readout"><div class="rl">Cost of those empty miles</div><div class="big" id="dh-result">—</div><div class="meta" id="dh-detail"></div></div>
    <div style="margin-top:16px;padding:8px 12px;background:rgba(245,197,24,.08);border-left:2px solid var(--yellow);font-size:0.75rem;color:var(--ink-2);" id="dh-tip"></div>
  </div>


  </div>

  <!-- 5. Rate floor -->
  <div class="sechead"><h2>Rate floor</h2><span class="sub">minimum rate before you move</span><span class="rule"></span></div>
  <div class="panel"><div style="padding:20px 22px">
    <div class="row" style="margin-bottom:12px">
      <div><label class="fl" for="rf-dist">Distance (km)</label><input class="field" id="rf-dist" type="number" value="1380" min="0" oninput="calcRF()"></div>
      <div><label class="fl" for="rf-burn">Burn (L/100km)</label><input class="field" id="rf-burn" type="number" value="38" min="1" oninput="calcRF()"></div>
      <div><label class="fl" for="rf-diesel">Diesel (c/L)</label><input class="field" id="rf-diesel" type="number" value="{{fuel.national_diesel}}" min="0" step="0.1" oninput="calcRF()"></div>
    </div>
    <div class="row" style="margin-bottom:16px">
      <div><label class="fl" for="rf-margin">Target margin (%)</label><input class="field" id="rf-margin" type="number" value="15" min="0" max="50" oninput="calcRF()"></div>
      <div><label class="fl" for="rf-fixed">Fixed cost / trip ($)</label><input class="field" id="rf-fixed" type="number" value="150" min="0" oninput="calcRF()"></div>
    </div>
    <div class="readout"><div class="rl">Minimum rate</div><div class="big" id="rf-result">—</div><div class="meta" id="rf-detail"></div></div>
    <div style="margin-top:16px;padding:12px 16px;background:rgba(30,158,102,.08);border-left:2px solid var(--green);font-size:0.8125rem;color:var(--ink-2);line-height:1.5" id="rf-tip"></div>
  </div></div>

  <div class="sechead"><h2>Common questions</h2><span class="rule"></span></div>
  <div class="faq"><dl>
    <dt>What diesel price does this use?</dt><dd>Pre-loaded with the Northern Mile Diesel Index ({{fuel.national_diesel}}c/L), updated every 30 minutes. Change it to any pump price.</dd>
    <dt>How is the cost worked out?</dt><dd>Litres burned = distance ÷ 100 × burn rate. Cost = litres × price per litre.</dd>
    <dt>How do I use the cross-border calculator?</dt><dd>Enter the US pump price in USD per gallon and the current exchange rate. We convert to Canadian cents per litre so you can compare directly with your home province.</dd>
  </dl></div>

  <div class="related"><a href="/fuel-prices/">Fuel prices →</a><a href="/exchange-rate/">CAD/USD →</a><a href="/border-wait-times/">Border waits →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Estimates only · Informational use · © 2026 Northern Mile Media</div></div></footer>
<script>
// Trip cost
function calcAll(){
  var d=+document.getElementById('dist').value||0, b=+document.getElementById('burn').value||0, p=+document.getElementById('price').value||0;
  var litres=d/100*b, cost=litres*p/100;
  document.getElementById('trip-cost').textContent='$'+cost.toFixed(2);
  document.getElementById('trip-detail').textContent=litres.toFixed(0)+' L × '+p.toFixed(1)+'c/L · '+d+' km at '+b+' L/100km';

  // Per km table
  var rates=[55,45,38,35,30,25], html='';
  rates.forEach(function(r){
    var perkm=(r*p/100).toFixed(1), per100=(r*p/100).toFixed(2), per1k=(r*p*10/100).toFixed(2);
    html+='<tr><td>'+r+' L/100km</td><td class="r mono">'+perkm+'c</td><td class="r mono">$'+per100+'</td><td class="r mono">$'+per1k+'</td></tr>';
  });
  document.getElementById('perkm-table').innerHTML=html;
}

// Cross-border
function calcUS(){
  var us=+document.getElementById('usd-gal').value||0, fx=+document.getElementById('fx-rate').value||0;
  var cadPerL=(us*fx/3.785).toFixed(1);
  document.getElementById('us-result').textContent=cadPerL+'c/L';
  document.getElementById('us-detail').textContent='$'+us.toFixed(2)+'/gal × '+fx.toFixed(4)+' ÷ 3.785 L/gal';
}
calcAll();calcUS();calcBE();calcDH();calcRF();calcRF();

function calcBE(){
  var b=+document.getElementById('be-burn').value||0, d=+document.getElementById('be-diesel').value||0, f=+document.getElementById('be-fixed').value||0;
  var fuelPerKm=b*d/100, total=fuelPerKm+f;
  document.getElementById('be-result').textContent=total.toFixed(1)+'c/km';
  document.getElementById('be-detail').textContent=fuelPerKm.toFixed(1)+'c fuel + '+f+'c fixed · '+b+' L/100km at '+d+'c/L';
}

function calcRF(){
  var km=+document.getElementById('rf-dist').value||0, b=+document.getElementById('rf-burn').value||0, d=+document.getElementById('rf-diesel').value||0, m=+document.getElementById('rf-margin').value||0, f=+document.getElementById('rf-fixed').value||0;
  var litres=km/100*b, fuelCost=litres*d/100;
  var total=fuelCost+f, minRate=total*(1+m/100);
  document.getElementById('rf-result').textContent='$'+minRate.toFixed(0);
  document.getElementById('rf-detail').textContent='Fuel $'+fuelCost.toFixed(0)+' + Fixed $'+f+' = $'+total.toFixed(0)+' + '+m+'% margin';
  var perKm=(minRate/km).toFixed(2);
  document.getElementById('rf-tip').innerHTML='<strong>$'+perKm+'</strong> per km. Below this number, you are losing money on this lane. A broker offers less, you know your floor.';
}
function calcDH(){
  var km=+document.getElementById('dh-km').value||0, b=+document.getElementById('dh-burn').value||0, d=+document.getElementById('dh-diesel').value||0;
  var litres=km/100*b, cost=litres*d/100, perKm=cost/km*100;
  document.getElementById('dh-result').textContent='$'+cost.toFixed(2);
  document.getElementById('dh-detail').textContent=litres.toFixed(0)+' L × '+d+'c/L · '+km+' km at '+b+' L/100km';
  var loads=Math.round(cost/3); // ~$3/km average rate
  document.getElementById('dh-tip').innerHTML='At an average rate of $3.00/km, you need to run roughly <strong>'+loads+' paid km</strong> just to cover these '+km+' deadhead km.';
}
</script>
</body></html>
```

### templates/fuel-prices.template.html (10219 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Diesel Prices by Province — Live | Northern Mile</title>
<meta name="description" content="Live diesel prices for all ten Canadian provinces, updated every 30 minutes. Tax breakdown, US border-state comparison, IFTA reference and routing savings for truckers.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/fuel-prices/">
<meta property="og:type" content="website"><meta property="og:title" content="Canadian Diesel Prices — Live by Province | Northern Mile"><meta property="og:description" content="Diesel across 10 provinces + US border states. Tax breakdown, IFTA, routing savings."><meta property="og:image" content="https://dashboard.northernmilemedia.com/og-fuel.jpg"><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Fuel Prices","item":"https://dashboard.northernmilemedia.com/fuel-prices/"}]},
{"@type":"Dataset","name":"Canadian Diesel Prices by Province","description":"Live diesel prices for all ten Canadian provinces, updated every 30 minutes.","creator":{"@type":"Organization","name":"Northern Mile Media"},"spatialCoverage":{"@type":"Place","name":"Canada"},"dateModified":"{{updated_at}}"},
{"@type":"FAQPage","mainEntity":[
{"@type":"Question","name":"Why is diesel different across provinces?","acceptedAnswer":{"@type":"Answer","text":"Provincial fuel taxes drive most of the gap. BC adds carbon tax and transit levies; Alberta has lower levies and no provincial sales tax."}},
{"@type":"Question","name":"Where should I fuel up to save money?","acceptedAnswer":{"@type":"Answer","text":"Alberta is cheapest, then Saskatchewan and Manitoba. Crossing into the US, diesel is usually cheaper once converted to Canadian cents per litre."}},
{"@type":"Question","name":"How often do prices update?","acceptedAnswer":{"@type":"Answer","text":"Every 30 minutes from public fuel surveys across all ten provinces and US border states."}}]}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/" class="on">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Fuel Prices</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>NMDI (Northern Mile Diesel Index) · all ten provinces</span><span>Updated {{updated_at}} · NRCan weekly diesel survey · refresh 30 min</span></div>

  <section class="cluster">
    <div>
      <div class="readlabel"><span class="tick">▸</span> NMDI · National</div>
      <div class="odo hero-odo" data-value="{{fuel.national_diesel}}" data-unit="c/L"></div>
      <div class="trend"><span class="b">7-DAY</span> {{fuel.change_7d}} &nbsp; <span class="b">30-DAY</span> {{fuel.change_30d}}</div>
    </div>
    <div class="clus-gauges">
      <div class="g lo"><div class="gv">{{fuel.low}}</div><div class="gl">Cheapest · {{fuel.low_code}}</div></div>
      <div class="g hi"><div class="gv">{{fuel.high}}</div><div class="gl">Highest · {{fuel.high_code}}</div></div>
      <div class="g"><div class="gv">{{fuel.spread}}</div><div class="gl">Spread c/L</div></div>
    </div>
  </section>

  <!--OPTIONAL:sponsor_fuel--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_fuel.name}}</div><div class="l">{{sponsor_fuel.line}}</div></div><a class="c" href="{{sponsor_fuel.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_fuel-->

  <div class="sechead"><h2>NMDI by province</h2><span class="sub">c/L · Δ since last</span><span class="rule"></span></div>
  <div class="scroll"><table class="tbl">
    <thead><tr><th>Prov</th><th>Region</th><th class="r">Price</th><th class="r">Change</th><th class="r">vs Nat</th></tr></thead>
    <!--LOOP:provinces--><tr class="{{rowclass}}"><td class="code">{{code}}</td><td>{{name}}</td><td class="r"><span class="px">{{price}}</span></td><td class="r mono {{change_class}}">{{change}}</td><td class="r mono {{vs_class}}">{{vs_national}}</td></tr><!--/LOOP:provinces-->
  </table></div>
  <p class="note">Arrows show change vs. previous 30-min update. Public fuel surveys, all ten provinces.</p>

  <div class="sechead"><h2>Fill before you cross</h2><span class="sub">US border states · CAD equiv</span><span class="rule"></span></div>
  <p class="intro">US diesel priced per gallon in USD, converted to Canadian cents/litre at {{fx.usd_cad}} so it lines up with the province next door.</p>
  <div class="xb">
  <!--LOOP:border_fuel--><div class="xr"><div class="pair">{{prov_code}} → {{state_code}}</div><div class="cols"><div class="side"><div class="l">{{prov_name}}</div><div class="p">{{prov_price}}</div></div><div class="side"><div class="l">{{state_name}}</div><div class="p">{{state_cad}}</div><div class="g">{{state_usd}}/gal</div></div></div><div class="v">{{verdict}}</div></div><!--/LOOP:border_fuel-->
  </div>
  <p class="note">USD/gal × {{fx.usd_cad}} FX ÷ 3.785 L. State prices refresh 30 min. FX: Bank of Canada.</p>

  

  <div class="sechead"><h2>Fuel tax breakdown</h2><span class="sub">estimated split · c/L</span><span class="rule"></span></div>
  <div class="scroll"><table class="tbl">
    <thead><tr><th>Province</th><th class="r">Base</th><th class="r">Carbon</th><th class="r">Fuel tax</th><th class="r">Sales</th><th class="r">Pump</th></tr></thead>
    <!--LOOP:tax--><tr><td class="code">{{code}}</td><td class="r mono">{{base}}</td><td class="r mono">{{carbon}}</td><td class="r mono">{{fuel_tax}}</td><td class="r mono">{{sales}}</td><td class="r"><span class="px">{{pump}}</span></td></tr><!--/LOOP:tax-->
  </table></div>
  <p class="note">Approximate — exact components wired from public rate tables. Base = wholesale + federal excise.</p>

  <div class="sechead"><h2>IFTA diesel reference</h2><span class="sub">current quarter</span><span class="rule"></span></div>
  <div class="scroll"><table class="tbl">
    <thead><tr><th>Jurisdiction</th><th class="r">Pump c/L</th><th class="r">Tax portion</th><th class="r">Per 100L</th></tr></thead>
    <!--LOOP:ifta--><tr><td class="code">{{code}}</td><td class="r mono">{{pump}}</td><td class="r mono">{{tax_portion}}</td><td class="r mono">{{per_100l}}</td></tr><!--/LOOP:ifta-->
  </table></div>
  <p class="note"><a href="/fuel-cost-calculator/">Open the fuel cost calculator →</a> to estimate quarterly IFTA spend by route.</p>

  <div class="sechead"><h2>Common questions</h2><span class="rule"></span></div>
  <div class="faq"><dl>
    <dt>Why is diesel different across provinces?</dt><dd>Provincial fuel taxes drive most of the gap. BC adds carbon tax and transit levies; Alberta has lower levies and no provincial sales tax. The {{fuel.low_code}}–{{fuel.high_code}} spread is {{fuel.spread}}c/L.</dd>
    <dt>Where should I fuel up to save money?</dt><dd>Alberta is cheapest, then Saskatchewan and Manitoba — fill before leaving them. Crossing the border, US diesel is usually cheaper once converted to Canadian cents/litre. See the border comparison above.</dd>
    <dt>How often do prices update?</dt><dd>Every 30 minutes, from public fuel surveys across all ten provinces and the US border states.</dd>
    <dt>Do these prices include carbon tax?</dt><dd>Yes — all federal and provincial taxes are included in the pump price shown.</dd>
  </dl></div>

  <div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/fuel-prices/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Live%20Canadian%20diesel%20prices%20by%20province&url=https://dashboard.northernmilemedia.com/fuel-prices/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/fuel-prices/')">Copy link</button></div>

  

<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body></html>
```

### templates/index.html (10428 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Northern Mile — Live Canadian Trucking Dashboard</title>
<meta name="description" content="Free live dashboard for Canadian trucking. Fuel prices, border crossings, road incidents, cargo theft. No signup.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/">
<meta property="og:title" content="Northern Mile — Live Canadian Trucking Dashboard">
<meta property="og:description" content="Diesel prices, border status, road incidents. No signup. Free forever.">
<meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600&amp;family=IBM+Plex+Mono:wght@400;500&amp;family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
</head><body>

<div class="header"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><img src="/logo.jpg" alt="Northern Mile Media" style="height:32px;width:auto;"><h1>NORTHERN MILE MEDIA</h1></a></div>
<nav class="nav">
  <a href="/" class="active">Home</a>
  <a href="/fuel-prices/">Fuel</a>
  <a href="/exchange-rate/">FX</a>
  <a href="/border-wait-times/">Border</a>
  <a href="/road-incidents/">Incidents</a>
  <a href="/cargo-theft/">Theft</a>
  <a href="/market-pulse/">Market</a>
  <a href="/industry-news/">News</a>
  <a href="/fuel-cost-calculator/">Calc</a>
</nav>
<div class="breadcrumb">Dashboard</div>

<main>
<div class="grd">

  <!-- 1. Fuel Prices — HERO -->
  <div class="mod hero" id="fuel-card">
    <div class="mod-eyebrow"><span class="mod-label">FUEL PRICES</span>
      <div class="ftoggle" id="prices-toggle"><button data-fuel="diesel" class="active">Diesel</button><button data-fuel="gasoline">Gas</button></div>
    </div>
    <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;">
      <div class="fuel-hero">{{fuel_national}}<span class="unit"> c/L</span></div>
      <span style="font-size:0.875rem;font-weight:600;padding:3px 10px;border-radius:12px;background:rgba(242,169,0,.15);color:var(--amber);">{{fuel_delta}}</span>
    </div>
    <div style="margin-top:8px;padding-top:6px;border-top:1px solid var(--border);">
      <div class="fuel-pg">
<!--LOOP:fuel_provinces-->
        <div class="fuel-prow"><span class="pcode">{{code}}</span><span class="pprice {{class}}">{{price}}</span></div>
<!--/LOOP:fuel_provinces-->
      </div>
    </div>
    <div class="mod-footer"><span data-updated="{{fuel_updated}}">Updated {{fuel_updated_display}}</span></div>
  </div>

  <!-- 2. USD/CAD — STANDARD -->
  <div class="mod standard">
    <div class="mod-eyebrow"><span class="mod-label">USD / CAD</span><span class="status-pill live">LIVE</span></div>
    <div style="font-size:2rem;font-weight:600;font-family:'Barlow Condensed';">{{fx_rate}}</div>
    <div style="font-size:0.875rem;font-weight:600;color:var(--{{fx_color}});">{{fx_change}}</div>
    <div class="mod-footer"><span data-updated="{{fx_updated}}">Updated {{fx_updated_display}}</span></div>
  </div>

  <!-- 3. Border Crossings — WIDE -->
  <div class="mod wide">
    <div class="mod-eyebrow"><span class="mod-label">BORDER CROSSINGS</span><span class="status-pill {{border_pill}}">{{border_status}}</span></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;">
<!--LOOP:border_crossings-->
      <div style="background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:10px 12px;">
        <div style="font-size:0.75rem;font-weight:600;">{{name}}</div>
        <div style="font-size:0.6875rem;color:var(--text-muted);">{{route}}</div>
        <div style="font-size:0.875rem;font-weight:700;font-family:'Barlow Condensed';color:var(--{{delay_color}});">{{delay}}</div>
      </div>
<!--/LOOP:border_crossings-->
    </div>
    <div class="mod-footer"><span data-updated="{{border_updated}}">Updated {{border_updated_display}}</span> &middot; CBSA</div>
  </div>

  <!-- 4. Fuel Calculator — STANDARD -->
  <div class="mod standard" id="calc-card">
    <div class="mod-eyebrow"><span class="mod-label">FUEL COST CALCULATOR</span><span class="status-pill live">LIVE</span></div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="display:flex;gap:8px;">
        <select id="calc-from" style="flex:1;background:var(--bg);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:6px 8px;font-size:0.75rem;"></select>
        <select id="calc-to" style="flex:1;background:var(--bg);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:6px 8px;font-size:0.75rem;"></select>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
        <div class="ftoggle" id="fuel-toggle" style="display:flex;background:var(--bg);border:1px solid var(--border);border-radius:12px;overflow:hidden;font-size:0.625rem;">
          <button data-fuel="diesel" class="active" style="border:none;background:none;color:var(--text-muted);padding:4px 8px;cursor:pointer;font-weight:600;">Diesel</button>
          <button data-fuel="gasoline" style="border:none;background:none;color:var(--text-muted);padding:4px 8px;cursor:pointer;font-weight:600;">Gas</button>
        </div>
        <input type="number" id="calc-eff" value="35" min="20" max="60" style="width:60px;background:var(--bg);color:var(--text-primary);border:1px solid var(--border);border-radius:4px;padding:4px 6px;font-size:0.75rem;text-align:center;">
        <span style="font-size:0.625rem;color:var(--text-muted);">L/100km</span>
      </div>
      <div id="calc-result" style="padding:8px;"></div>
    </div>
  </div>

  <!-- 5. Road Incidents — HERO -->
  <div class="mod hero">
    <div class="mod-eyebrow"><span class="mod-label">ROAD INCIDENTS</span><span class="status-pill live">LIVE</span></div>
    <div style="display:flex;gap:0;border-radius:6px;overflow:hidden;">
      <div id="inc-map" style="flex:1;min-height:360px;"></div>
      <div id="inc-list" style="width:280px;max-height:360px;overflow-y:auto;font-size:0.75rem;background:var(--bg);">
<!--IF:incidents_none-->
        <div style="color:var(--green);font-size:0.875rem;padding:20px;text-align:center;">All corridors clear</div>
<!--/IF:incidents_none-->
      </div>
    </div>
    <div class="mod-footer"><span data-updated="{{incidents_updated}}">Updated {{incidents_updated_display}}</span></div>
  </div>

  <!-- 6. Market Pulse — STANDARD -->
  <div class="mod standard">
    <div class="mod-eyebrow"><span class="mod-label">MARKET PULSE</span><span class="status-pill reference">REFERENCE</span></div>
<!--LOOP:market_indicators-->
    <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);font-size:0.75rem;">
      <span style="color:var(--text-muted);">{{label}}</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-weight:600;color:var(--{{color}});">{{value}}</span>
    </div>
<!--/LOOP:market_indicators-->
    <div class="mod-footer"><span data-updated="{{market_updated}}">Updated {{market_updated_display}}</span></div>
  </div>

  <!-- 7. Cargo Theft — HERO -->
  <div class="mod hero">
    <div class="mod-eyebrow"><span class="mod-label">CARGO THEFT WATCH</span><span class="status-pill live">LIVE</span></div>
    <div style="display:flex;gap:0;border-radius:6px;overflow:hidden;">
      <div id="th-map" style="flex:1;min-height:360px;"></div>
      <div id="th-list" style="width:280px;max-height:360px;overflow-y:auto;font-size:0.75rem;background:var(--bg);padding:8px;">
        <div style="font-size:0.625rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.04em;padding:4px 8px;">Recent</div>
<!--LOOP:theft_incidents-->
        <div style="padding:8px 10px;border-bottom:1px solid var(--border);cursor:pointer;">
          <div style="font-size:0.75rem;font-weight:600;">{{title}}</div>
          <div style="font-size:0.6875rem;color:var(--text-muted);">{{location}}</div>
          <div style="font-size:0.75rem;font-weight:700;color:var(--red);">${{value}}</div>
        </div>
<!--/LOOP:theft_incidents-->
        <div style="margin-top:6px;font-size:0.625rem;color:var(--text-muted);text-transform:uppercase;">Hotspots</div>
<!--LOOP:theft_hotspots-->
        <div style="padding:6px 10px;font-size:0.6875rem;">{{city}} — {{note}}</div>
<!--/LOOP:theft_hotspots-->
      </div>
    </div>
    <div class="mod-footer"><span data-updated="{{theft_updated}}">Updated {{theft_updated_display}}</span></div>
  </div>

  <!-- 8. Industry Headlines — WIDE -->
  <div class="mod wide">
    <div class="mod-eyebrow"><span class="mod-label">INDUSTRY HEADLINES</span></div>
<!--LOOP:news_headlines-->
    <div style="padding:8px 0;border-bottom:1px solid var(--border);">
      <a href="{{url}}" target="_blank" rel="noopener" style="font-size:0.8125rem;font-weight:500;">{{title}}</a>
      <span style="font-size:0.625rem;color:var(--text-muted);display:block;">{{source}}</span>
    </div>
<!--/LOOP:news_headlines-->
    <div class="mod-footer"><span data-updated="{{news_updated}}">Updated {{news_updated_display}}</span></div>
  </div>

</div>

<div class="cta"><div class="cta-eyebrow">Get the Northern Mile Brief</div>
<div class="cta-body">Fuel prices, border updates, and market shifts every Wednesday at 6am.</div>
<div class="cta-sub"><a href="https://northernmilemedia.com">Sign up free &rarr;</a></div></div>

</main>

<div class="footer"><p>Northern Mile Media &middot; For the people who keep Canada moving</p><p style="margin-top:4px;">Data from public sources. Informational use only.</p></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>window.INCIDENTS = {{incidents_array}};</script>
<script>window.THEFTS = {{theft_array}};</script>
<script>window.FUEL_DIESEL = {{fuel_diesel_data}};</script>
<script>window.FUEL_GAS = {{fuel_gas_data}};</script>
<script>window.CALC_CITIES = {{calc_cities}};</script>
<script>window.CALC_DISTANCES = {{calc_distances}};</script>
</body></html>
```

### templates/index.template.html (12672 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">
<title>Northern Mile — Live Canadian Trucking Dashboard</title>
<meta name="description" content="One tab for Canadian trucking: live diesel prices, border wait times, road incidents, cargo theft, FX and market data. Updated every 30 minutes. Free, no signup.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/">
<meta property="og:type" content="website"><meta property="og:title" content="Northern Mile — Live Canadian Trucking Dashboard"><meta property="og:description" content="Diesel, border waits, road incidents, FX and market data. One tab. Updated every 30 min. Free."><meta property="og:image" content="https://dashboard.northernmilemedia.com/og.jpg"><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"WebSite","name":"Northern Mile Dashboard","url":"https://dashboard.northernmilemedia.com/","publisher":{"@type":"Organization","name":"Northern Mile Media","url":"https://northernmilemedia.com"}},
{"@type":"Dataset","name":"Canadian Trucking Live Data","description":"Live diesel prices, border wait times, road incidents, FX and market indicators, updated every 30 minutes.","creator":{"@type":"Organization","name":"Northern Mile Media"},"spatialCoverage":{"@type":"Place","name":"Canada"},"dateModified":"{{updated_at}}"}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/" class="on">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>Canadian trucking</span><span>Updated {{updated_at}} · refresh 30 min</span></div>

  <section class="cockpit"><div class="gauges">
    <div class="gauge hero-gauge" data-href="/fuel-prices/" role="link" tabindex="0" aria-label="Fuel prices"><div class="gl">NMDI (Northern Mile Diesel Index) · national</div><div class="odo" data-value="{{fuel.national_diesel}}" data-unit="c/L"></div><div class="gs">{{fuel.change_7d}} / 7d · NRCan weekly survey</div></div>
  </div><div class="sub-gauges">
    <div class="gauge {{border.gauge_class}}" data-href="/border-wait-times/" role="link" tabindex="0" aria-label="Border"><div class="gl">Border</div><div class="gv">{{border.heavy_count}} <small>heavy</small></div><div class="gs">{{border.moderate_count}} moderate · {{border.closed_count}} closed</div></div>
    <div class="gauge" data-href="/exchange-rate/" role="link" tabindex="0" aria-label="Exchange rate"><div class="gl">USD/CAD</div><div class="gv">{{fx.usd_cad}}</div><div class="gs">{{fx.direction}} · {{fx.change}}</div></div>
    <div class="gauge {{incidents.gauge_class}}" data-href="/road-incidents/" role="link" tabindex="0" aria-label="Road incidents"><div class="gl">Collisions</div><div class="gv">{{incidents.active_count}}</div><div class="gs">{{incidents.status_line}}</div></div>
  </div></section>

  <!--OPTIONAL:sponsor_page-->
  <div class="sp"><span class="t">Dashboard presented by</span><div><div class="n">{{sponsor_page.name}}</div><div class="l">{{sponsor_page.line}}</div></div><a class="c" href="{{sponsor_page.url}}">Learn more →</a></div>
  <!--/OPTIONAL:sponsor_page-->

  <div class="sechead"><h2>Road incidents</h2><span class="sub">collisions &amp; closures on freight corridors</span><a class="more" href="/road-incidents/">Open map →</a></div>
  <div class="panel">
    <!--IF:incidents.none--><div class="empty" data-href="/road-incidents/" role="link" tabindex="0"><b>Corridors clear</b>No major closures or collisions on monitored corridors</div><!--/IF:incidents.none-->
    <div class="news">
    <!--LOOP:incidents.incidents--><a href="{{url}}">{{what}}</a><!--/LOOP:incidents.incidents-->
    <a href="/road-incidents/" style="color:var(--ink-3);">View all incidents →</a>
    </div>
  </div>

  <div class="sechead"><h2>Border crossings</h2><span class="sub">commercial wait</span><a class="more" href="/border-wait-times/">All crossings →</a></div>
  <div class="panel"><table class="tbl bx" style="table-layout:fixed;width:100%">
  <colgroup><col style="width:auto"><col style="width:80px"><col style="width:85px"></colgroup>
  <!--LOOP:border_rows--><tr data-href="{{url}}" role="link" tabindex="0" style="height:36px;"><td style="padding:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{{name}}</td><td class="r" style="padding:8px;vertical-align:middle;"><span class="px">{{wait}}</span></td><td class="r" style="padding:8px;vertical-align:middle;"><span class="pill {{status_class}}">{{status_label}}</span></td></tr><!--/LOOP:border_rows-->
  </table></div>
  <!--OPTIONAL:sponsor_border--><div class="sp"><span class="t">Border module by</span><div><div class="n">{{sponsor_border.name}}</div><div class="l">{{sponsor_border.line}}</div></div><a class="c" href="{{sponsor_border.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_border-->

  <div class="sechead"><h2>Fuel &amp; exchange</h2><span class="sub">NMDI · USD/CAD</span><a class="more" href="/fuel-prices/">Full fuel →</a></div>
  <div class="row">
    <div class="panel"><div class="readout"><div class="rl">NMDI (Northern Mile Diesel Index) · national average</div><div class="big">{{fuel.national_diesel}}<small> c/L</small></div><div class="meta">{{fuel.low_code}} {{fuel.low}} low · {{fuel.high_code}} {{fuel.high}} high · spread {{fuel.spread}}c</div></div>
      <table class="tbl">
      <!--LOOP:fuel_top--><tr data-href="/fuel-prices/" role="link" tabindex="0"><td class="code">{{code}}</td><td>{{name}}</td><td class="r"><span class="px">{{price}}</span></td><td class="r mono {{change_class}}">{{change}}</td></tr><!--/LOOP:fuel_top-->
      </table></div>
    <div class="panel"><div class="readout"><div class="rl">USD / CAD</div><div class="big">{{fx.usd_cad}}</div><div class="meta">{{fx.direction}} · {{fx.change}} · Bank of Canada</div></div>
      <div class="ind" data-href="/fuel-prices/" role="link" tabindex="0"><div class="nm">Fill before you cross<span>US border states run cheaper in CAD/L</span></div><div class="vv" style="font-size:.75rem;font-family:'IBM Plex Mono',monospace;color:var(--green)">See →</div></div>
      <div class="ind" data-href="/fuel-prices/" role="link" tabindex="0"><div class="nm">IFTA reference<span>Per-jurisdiction tax portion</span></div><div class="vv" style="font-size:.75rem;font-family:'IBM Plex Mono',monospace;color:var(--green)">See →</div></div></div>
  </div>

  

  <div class="sechead"><h2>Market pulse</h2><span class="sub">freight demand signals</span><a class="more" href="/market-pulse/">Full market →</a></div>
  <div class="panel">
  <!--LOOP:market--><div class="ind" data-href="/market-pulse/" role="link" tabindex="0"><div class="nm">{{name}}<span>{{note}}</span></div><div class="vv {{value_class}}">{{value}}</div></div><!--/LOOP:market-->
  </div>

  <div class="sechead sechead--ref"><h2>Cargo theft</h2><span class="sub">reference · last 12 months</span><a class="more" href="/cargo-theft/">All incidents →</a></div>
  <div class="panel">
  <!--LOOP:theft--><div class="tft" data-href="{{url}}" role="link" tabindex="0"><div class="h">{{title}} <span class="val">{{value}}</span></div><div class="m">{{meta}}</div></div><!--/LOOP:theft-->
    <a href="/cargo-theft/" style="display:block;padding:8px 10px;color:var(--ink-3);font-size:0.75rem;border-top:1px solid var(--border);">More →</a>
  </div>

  <div class="sechead sechead--ref"><h2>Industry news</h2><span class="sub">curated headlines</span><a class="more" href="/industry-news/">All headlines →</a></div>
  <div class="panel"><div class="news">
  <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">{{category}}</span>{{headline}}</a><!--/LOOP:news-->
    <a href="/industry-news/"><span class="src">More</span>All industry headlines →</a>
  </div></div>

  <div class="sechead sechead--ref"><h2>Fuel cost calculator</h2></div>
  <div class="panel"><div class="calc"><div class="txt">Trip fuel cost by distance, burn rate and current diesel — pre-loaded with today's national average.</div><a href="/fuel-cost-calculator/">Open calculator →</a></div></div>

    </div>

  <div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=One%20tab%20for%20Canadian%20trucking&url=https://dashboard.northernmilemedia.com/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/')">Copy link</button></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving · <a href="/methodology/nmdi/" style="color:var(--ink-3)">NMDI methodology</a><div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>

<script>
(function(){
  var cities = {{calc_cities}};
  var distances = {{calc_distances}};
  var diesel = {{fuel.national_diesel}};
  var fromEl = document.getElementById('home-from');
  var toEl = document.getElementById('home-to');
  var effEl = document.getElementById('home-eff');
  var resultEl = document.getElementById('home-calc-result');
  var detailEl = document.getElementById('home-calc-detail');
  if (!fromEl || !toEl) return;

  cities.forEach(function(c){var o=document.createElement('option');o.value=c.code;o.textContent=c.name;fromEl.appendChild(o.cloneNode(true));toEl.appendChild(o);});
  fromEl.value='YVR';toEl.value='YYZ';

  function calc(){
    var from=fromEl.value,to=toEl.value,eff=parseFloat(effEl.value)||35;
    var dist=distances[from+'-'+to]||distances[to+'-'+from];
    if(!dist||from===to){resultEl.innerHTML='<div style="font-size:0.75rem;color:var(--ink-3);">Trip cost</div><div style="font-size:2rem;font-weight:600;color:var(--ink);">—</div>';detailEl.textContent='';return;}
    var litres=dist*eff/100,cost=litres*diesel/100;
    resultEl.innerHTML='<div style="font-size:0.75rem;color:var(--ink-3);">Trip cost</div><div style="font-size:2rem;font-weight:600;color:var(--ink);">$'+cost.toFixed(0)+'</div>';
    detailEl.textContent=dist.toLocaleString()+' km · '+eff+' L/100km · '+diesel+'c/L';
  }
  fromEl.addEventListener('change',calc);toEl.addEventListener('change',calc);effEl.addEventListener('input',calc);
  calc();
})();
</script>
</body></html>
```

### templates/industry-news.template.html (4594 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Trucking Industry News — Curated Headlines | Northern Mile</title>
<meta name="description" content="Curated Canadian and North American trucking headlines: freight markets, equipment, regulations and fuel. Refreshed through the day.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/industry-news/">
<meta property="og:type" content="website"><meta property="og:title" content="Trucking Industry News — Curated | Northern Mile"><meta property="og:description" content="Curated Canadian trucking headlines, refreshed daily."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Industry News","item":"https://dashboard.northernmilemedia.com/industry-news/"}]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/" class="on">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Industry News</div>
  <div class="strip"><span><span class="dot"></span><b>Daily</b></span><span>Curated headlines</span><span>Updated {{updated_at}}</span></div>

  <!--OPTIONAL:sponsor_news--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_news.name}}</div><div class="l">{{sponsor_news.line}}</div></div><a class="c" href="{{sponsor_news.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_news-->

  <div class="sechead"><h2>Headlines</h2><span class="sub">links open at the source</span><span class="rule"></span></div>
  <div class="panel"><div class="news">
  <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">{{category}}</span>{{headline}}</a><!--/LOOP:news-->
  </div></div>

  <div class="share" style="margin-top:24px"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/industry-news/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Canadian%20trucking%20headlines&url=https://dashboard.northernmilemedia.com/industry-news/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/industry-news/')">Copy link</button></div>

  

<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Headlines link to their original publishers · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body></html>
```

### templates/market-pulse.template.html (6867 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Freight Market Pulse — Live Indicators | Northern Mile</title>
<meta name="description" content="Freight demand signals: GDP, diesel cost, cross-province spreads, and CAD impact on trucking. Live market pulse.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/market-pulse/">
<meta property="og:type" content="website"><meta property="og:title" content="Canadian Freight Market Pulse | Northern Mile"><meta property="og:description" content="Freight demand signals: GDP, diesel, spreads, FX."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://***@graph":[{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Market Pulse","item":"https://dashboard.northernmilemedia.com/market-pulse/"}]}]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/" class="on">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Market Pulse</div>
  <div class="strip"><span><span class="dot"></span><b>Daily</b></span><span>Freight demand signals</span><span>{{direction_summary}}</span><span>Updated {{updated_at}}</span></div>

  <!--OPTIONAL:sponsor_market--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_market.name}}</div><div class="l">{{sponsor_market.line}}</div></div><a class="c" href="{{sponsor_market.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_market-->

  <div class="sechead"><h2>Indicators</h2><span class="rule"></span></div>
  <div class="panel">
  <!--LOOP:market--><div class="ind"><div class="nm">{{name}}<span>{{note}}</span></div><div class="vv {{value_class}}">{{value}}</div></div><!--/LOOP:market-->
  </div>

  <div class="sechead"><h2>How to read these</h2><span class="rule"></span></div>
  <div class="panel" style="color:var(--ink-2);font-size:0.875rem;line-height:1.6;">
    <p>Five indicators, one question each: <strong style="color:var(--ink);">is freight getting stronger or weaker?</strong></p>
    <p style="margin-top:12px;"><strong style="color:var(--green)">Green</strong> = signal is moving in your favour (more loads, lower costs). <strong style="color:var(--red)">Red</strong> = signal is moving against you (higher diesel, weaker demand). <strong style="color:var(--yellow)">Yellow</strong> = watch closely.</p>
    <p style="margin-top:12px;">Fuel costs sit at {{fuel_pct_of_ops}} of operating costs. At {{current_diesel}}c/L diesel and {{usd_cad}} USD/CAD, margin pressure on Canadian carriers is real. These indicators don't predict rates — they show the cost and demand floor that rates are built on.</p>
  </div>

  <div class="sechead"><h2>FAQ</h2><span class="rule"></span></div>
  <div class="faq"><dl>
    <dt>Why watch GDP for trucking?</dt><dd>Freight volume tracks economic output. Rising GDP means more loads moving; a contraction signals softening demand. The correlation isn't perfect — construction, retail, and manufacturing matter more than overall GDP — but it's the broadest signal available.</dd>
    <dt>What does "fuel cost per 1,000 km" tell me?</dt><dd>What it costs in diesel to move a loaded tractor-trailer 1,000 kilometres at current pump prices. It assumes 35 L/100km — a typical highway burn rate. Use this number directly in a rate quote.</dd>
    <dt>Why track BC-AB spread separately?</dt><dd>The 19.6c gap between BC and Alberta diesel creates a routing decision on every cross-Rockies lane. Fill in Alberta, run through BC. That spread pays for itself on a single long-haul tank.</dd>
    <dt>How does USD/CAD affect trucking?</dt><dd>A weaker loonie makes Canadian exports cheaper for US buyers — southbound freight demand rises. But oil (priced in USD) costs more in CAD, pushing diesel up. Cross-border carriers feel both sides.</dd>
  </dl></div>

  <div class="share"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/market-pulse/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Canadian%20freight%20market%20pulse&url=https://dashboard.northernmilemedia.com/market-pulse/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/market-pulse/')">Copy link</button></div>

  <div class="related"><a href="/fuel-prices/">Fuel prices →</a><a href="/exchange-rate/">CAD/USD →</a><a href="/industry-news/">Industry news →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Data from public sources · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body></html>
```

### templates/methodology.template.html (7294 bytes)
```html
<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>NMDI Methodology — Northern Mile</title>
<meta name="description" content="How the Northern Mile Diesel Index is calculated — population, method, source, cadence, and revision history.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/methodology/nmdi/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
</head>
<body>
<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="strip"><span><span class="dot"></span>Methodology</span><span>Northern Mile Diesel Index (NMDI)</span></div>

  <section style="max-width:720px;margin:32px 0 48px">
    <h1 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.75rem;margin:0 0 8px;color:var(--ink)">NMDI — Northern Mile Diesel Index</h1>
    <p style="color:var(--ink-3);font-size:0.875rem;margin:0 0 32px">Version 1.1 · Effective 2026-08-05</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Population</h2>
    <p>The NMDI is computed from ten provinces: British Columbia, Alberta, Saskatchewan, Manitoba, Ontario, Quebec, New Brunswick, Nova Scotia, Prince Edward Island, and Newfoundland and Labrador.</p>
    <p>Yukon and the Northwest Territories are collected from the same NRCan survey and displayed on the fuel page. They are excluded from the national index and the spread because they carry negligible national freight volume and equal-weighting them distorts both figures.</p>
    <p>This is a volume-relevance exclusion, not a price-outlier exclusion. Territorial diesel is supplied off Edmonton and typically prices near Alberta — below the national mean. Including them would pull the index down, not up, which makes the exclusion the more conservative choice.</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Method</h2>
    <p>Each provincial figure is the unweighted arithmetic mean of NRCan survey city prices within that province. The number of survey cities varies by province — Alberta has six, Ontario has nineteen, Prince Edward Island has one.</p>
    <p>The national index is the unweighted mean of the ten provincial figures. It is <em>not</em> a population-weighted or freight-volume-weighted average. This means the national figure treats every province equally regardless of its share of national diesel consumption.</p>
    <p>The rationale: a province-weighting or volume-weighting scheme introduces its own assumptions about which data series to weight by and how frequently to update the weights. An unweighted mean of provincial means is simpler to verify and harder to manipulate, and it changes only when diesel prices change, not when weighting methodology changes.</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Source</h2>
    <p>Natural Resources Canada weekly diesel survey, RSS productID=5. The survey covers 72 retail locations across all provinces and territories. Data is published weekly, collected by Kalibrate Technologies under contract to NRCan.</p>
    <p>All figures are published inclusive of federal and provincial fuel taxes, carbon taxes, and sales taxes. The federal excise tax on diesel (normally 4 cents per litre) is suspended from April 20 through September 7, 2026 per Finance Canada and CBSA Customs Notice 26-11.</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Cadence</h2>
    <p>NRCan surveys weekly. The dashboard rebuilds every 30 minutes from the most recent survey data, so the diesel figure holds steady between surveys. Deltas step once per week when a new print lands — they do not drift daily. The border wait times, road incidents, and exchange rate modules are genuinely live; diesel is not.</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Revision history</h2>
    <p><strong>2026-08-05</strong> — Index moved from a 12-unit basis (including YT and NT) to a 10-unit basis (excluding territories). The national figure shifted from 224.8 to 228.3¢/L as a function of this methodology change. Historical values and percentiles computed before this date are not directly comparable with post-change values.</p>
    <p><strong>2026-07-28</strong> — Initial publication. 12-unit basis, unweighted mean of provincial means.</p>

    <h2 style="font-family:'Saira Condensed',sans-serif;font-weight:600;font-size:1.25rem;color:var(--ink);margin:32px 0 12px">Corrections policy</h2>
    <p>Errors in the underlying NRCan data are corrected when NRCan publishes a revision. Errors in computation are corrected immediately and logged in the revision history above. A corrected figure is never retroactively substituted — the new value appears with the correction date and both values are recorded.</p>
    <p style="margin-top:32px;color:var(--ink-3);font-size:0.875rem">Questions: <a href="mailto:northernmilemedia@gmail.com" style="color:var(--green)">northernmilemedia@gmail.com</a></p>
  </section>

<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>
  </div>
</main>







<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<br><a href="/methodology/nmdi/" style="color:var(--ink-3)">NMDI methodology</a><div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>
<script src="/assets/app.js?v={{build_version}}"></script>
</body>
</html>
```

### templates/road-incidents.template.html (12197 bytes)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Road Incidents &amp; Closures for Trucks — Live Map | Northern Mile</title>
<meta name="description" content="Live map of major road closures and collisions on Canadian freight corridors, updated every 30 minutes. Click any incident for road, severity, clearance and detour.">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://dashboard.northernmilemedia.com/road-incidents/">
<meta property="og:type" content="website"><meta property="og:title" content="Canadian Road Incidents — Live Map | Northern Mile"><meta property="og:description" content="Live closures and collisions on Canadian freight corridors. Updated every 30 min."><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{updated_at}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link rel="stylesheet" href="/assets/styles.css?v={{build_version}}">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Road Incidents","item":"https://dashboard.northernmilemedia.com/road-incidents/"}]}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/" class="on">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Road Incidents</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>Closures + collisions · freight corridors</span><span>Updated {{updated_at}} · refresh 30 min</span></div>

  <div class="sechead"><h2>Incident map</h2><span class="sub">click a pin or row for detail</span><span class="rule"></span></div>
  <div id="map"></div>

  <!--OPTIONAL:sponsor_incidents--><div class="sp"><span class="t">Presented by</span><div><div class="n">{{sponsor_incidents.name}}</div><div class="l">{{sponsor_incidents.line}}</div></div><a class="c" href="{{sponsor_incidents.url}}">Learn more →</a></div><!--/OPTIONAL:sponsor_incidents-->

  <div class="sechead"><h2>Active incidents</h2><span class="rule"></span></div>
  <div class="panel" id="incList" style="max-height:500px;overflow-y:auto;"></div>

    <div class="sechead"><h2>Scheduled work</h2><span class="sub">coming closures &amp; construction</span><span class="rule"></span></div>
  <div class="panel" style="max-height:500px;overflow-y:auto;"><table class="tbl">
    <thead><tr><th>Highway</th><th>Work</th><th class="r">When</th><th class="r">Lanes</th></tr></thead>
    <!--LOOP:coming_roadwork--><tr class="inc-row" data-road="{{road}}" data-what="{{what}}" data-clearance="{{when}}" data-lanes="{{lanes}}" data-severity="Roadwork" data-severity-class="mod" data-direction="" data-event="Scheduled roadwork" data-closed="" data-end-time="" style="cursor:pointer;" onclick="showIncDetail(this);"><td class="code">{{road}}</td><td>{{what}}</td><td class="r">{{when}}</td><td class="r mono">{{lanes}}</td></tr><!--/LOOP:coming_roadwork-->
  </table></div>

  <div class="share" style="margin-top:24px"><a href="https://www.facebook.com/sharer/sharer.php?u=https://dashboard.northernmilemedia.com/road-incidents/" target="_blank" rel="noopener">Facebook</a><a href="https://twitter.com/intent/tweet?text=Live%20Canadian%20road%20closures%20for%20trucks&url=https://dashboard.northernmilemedia.com/road-incidents/" target="_blank" rel="noopener">Share on X</a><button type="button" onclick="copyLink(this,'https://dashboard.northernmilemedia.com/road-incidents/')">Copy link</button></div>

  <div class="related"><a href="/border-wait-times/">Border waits →</a><a href="/fuel-prices/">Fuel prices →</a><a href="/cargo-theft/">Cargo theft →</a></div>

</main>

<!-- subscribe partial — Ghost Portal GET form, works cross-origin -->


<!-- subscribe partial — link to Ghost Portal, cross-origin safe -->
<div class="cta">
  <div class="e">The Northern Mile Brief</div>
  <div class="b">Fuel, border and market shifts. Every Wednesday, 6am.</div>
  <a class="sub-btn" href="https://northernmilemedia.com/subscribe/">Subscribe</a>
  <div class="s" style="margin-top:8px">Free. One email a week. Unsubscribe anytime.</div>
</div>

<footer class="ft"><div class="wrap">Northern Mile Media · For the people who keep Canada moving<div class="note">Data from public sources · Sponsors never influence the data · Informational use only · © 2026 Northern Mile Media</div></div></footer>

<!-- HERMES: write the incident array below. Each item:
     {road,direction,severity,severity_label,severity_class,what,clearance,detour,source_url,lat,lng}
     Leave [] for no incidents; the map + list show a clean "corridors clear" state. -->
<script>window.INCIDENTS = {{incidents_json}};</script>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="/assets/app.js?v={{build_version}}"></script>
<script>
(function(){
  var data = window.INCIDENTS || [];
  var map = L.map('map',{scrollWheelZoom:true}).setView([56.13,-106.35],4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'&copy; OpenStreetMap &copy; CARTO', subdomains:'abcd', maxZoom:19
  }).addTo(map);
  var list = document.getElementById('incList');
  if(!data.length){
    list.innerHTML = '<div class="empty"><b>Corridors clear</b>No major closures or collisions on monitored corridors · checked {{updated_at}}</div>';
    return;
  }
  var markers = [];
  data.forEach(function(it, idx){
    var color = it.severity_class === 'closed' ? '#E5484D' : '#F5C518';
    var m = L.circleMarker([it.lat, it.lng], {radius:8,color:color,fillColor:color,fillOpacity:.85,weight:2}).addTo(map);
    m.bindPopup(
      '<b>'+it.road+' '+it.direction+'</b>'+
      '<br>'+it.what+
      (it.event_type?'<br><small>'+it.event_type+'</small>':'')+
      (it.lanes?'<br><small>Lanes: '+it.lanes+'</small>':'')+
      (it.closed?'<br><span style="color:#E5484D;font-weight:600;">CLOSED</span>':'')+
      (it.clearance?'<br><small>Started: '+it.clearance+'</small>':'')+
      (it.end_time?'<br><small>Until: '+it.end_time+'</small>':'')+
      (it.source_url?'<br><a href="'+it.source_url+'" target="_blank" rel="noopener">Source →</a>':'')
    );
    markers.push(m);
    var row = document.createElement('div');
    row.className = 'inc';
    row.setAttribute('tabindex','0');
    row.setAttribute('role','button');
    row.setAttribute('data-road', it.road||'');
    row.setAttribute('data-direction', it.direction||'');
    row.setAttribute('data-what', it.what||'');
    row.setAttribute('data-severity', it.severity_label||'');
    row.setAttribute('data-severity-class', it.severity_class||'');
    row.setAttribute('data-event', it.event_type||'');
    row.setAttribute('data-lanes', it.lanes||'');
    row.setAttribute('data-closed', it.closed||'');
    row.setAttribute('data-clearance', it.clearance||'');
    row.setAttribute('data-end-time', it.end_time||'');
    row.setAttribute('data-lat', it.lat||'');
    row.setAttribute('data-lng', it.lng||'');
    row.innerHTML = '<div class="h">'+it.road+' · '+it.direction+' <span class="pill '+it.severity_class+'" style="float:right">'+it.severity_label+'</span></div><div class="m">'+it.what+(it.clearance?' · clears '+it.clearance:'')+'</div>';
    row.addEventListener('click', function(){ showIncDetail(row); map.flyTo([it.lat, it.lng], 10, {duration:.6}); });
    row.addEventListener('keydown', function(e){ if(e.key==='Enter') showIncDetail(row); });
    list.appendChild(row);
  });
  var group = L.featureGroup(markers);
  map.fitBounds(group.getBounds().pad(0.2));

  // Detail panel
  var incDetail = document.createElement('div');
  incDetail.id = 'inc-detail';
  incDetail.style.cssText = 'display:none;position:fixed;top:0;right:0;width:380px;max-width:100vw;height:100vh;background:var(--surface-1);border-left:1px solid var(--border);z-index:9999;overflow-y:auto;padding:24px;font-size:0.875rem;';
  document.body.appendChild(incDetail);

  window.showIncDetail = function(row) {
    var closed = row.getAttribute('data-closed');
    var parts = [];
    parts.push('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;"><h2 style="margin:0;font-size:1rem;">Incident details</h2><button class="inc-close-btn" style="background:none;border:none;color:var(--ink-3);cursor:pointer;font-size:1.25rem;">&times;</button></div>');
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Highway</div><div style="font-weight:600;color:var(--ink);font-size:1rem;">'+row.getAttribute('data-road')+' '+row.getAttribute('data-direction')+'</div></div>');
    if (closed) parts.push('<div style="margin-bottom:16px;background:rgba(229,72,77,.12);border-left:2px solid var(--red);padding:12px;"><div style="font-size:0.75rem;font-weight:700;color:var(--red);">ROAD CLOSED</div></div>');
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Description</div><div style="color:var(--ink-2);">'+row.getAttribute('data-what')+'</div></div>');
    var sev = '<span class="pill '+row.getAttribute('data-severity-class')+'">'+row.getAttribute('data-severity')+'</span>';
    parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Severity</div><div>'+sev+'</div></div>');
    var eventType = row.getAttribute('data-event');
    if (eventType) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Type</div><div>'+eventType+'</div></div>');
    var lanes = row.getAttribute('data-lanes');
    if (lanes) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Lanes</div><div>'+lanes+'</div></div>');
    var clearance = row.getAttribute('data-clearance');
    if (clearance) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Started</div><div>'+clearance+'</div></div>');
    var endTime = row.getAttribute('data-end-time');
    if (endTime) parts.push('<div style="margin-bottom:16px;"><div style="font-size:0.625rem;text-transform:uppercase;color:var(--ink-3);margin-bottom:4px;">Until</div><div>'+endTime+'</div></div>');
    incDetail.innerHTML = parts.join('');
    incDetail.style.display = 'block';
    var closeBtn = incDetail.querySelector('.inc-close-btn');
    if (closeBtn) closeBtn.onclick = function() { incDetail.style.display = 'none'; };
  };
})();
</script>
</body></html>
```

## EXTRA SCRIPTS

### scripts/build_seo_pages.py (26187 bytes)
```python
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

<div class="header"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><img src="/logo.jpg" alt="Northern Mile Media" style="height:32px;width:auto;"><h1>NORTHERN MILE MEDIA</h1></a></div>
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
<div class="hst"><div class="hsv">{mk.get('fuel_cost_per_1000km','—')}</div><div class="hsl">Fuel cost per 1,000 km</div></div>
<div class="hst"><div class="hsv">{mk.get('bc_ab_spread','—')}</div><div class="hsl">BC-AB spread</div></div>
</div></div></div>'''

market_indicators = [
    ('GDP Growth', mk.get('gdp','—'), 'Monthly', 'Canadian economic output. Strong GDP means more freight to move.'),
    ('Freight Trend', mk.get('freight_trend','—'), 'Year-over-year', 'Direction of freight volumes. Up means more loads. Down means softer demand.'),
    ('Fuel cost per 1,000 km', mk.get('fuel_cost_per_1000km','—'), 'Current', 'Per-1,000km fuel cost at current diesel prices. Used directly in rate quotes.'),
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

sz = write_page('/market-pulse/', 'Canadian Trucking Market Indicators', 'Canadian trucking market indicators: GDP growth, freight trends, fuel cost per 1,000 km, BC-AB fuel spread. Free.', 'Market', hero, body, '')
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
```

### scripts/build_fuel_page.py (14630 bytes)
```python
#!/usr/bin/env python3
"""Build canonical fuel-prices page from live data. Single source of truth template."""
import json, os
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

<div class="header"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;text-decoration:none;color:inherit;"><img src="/logo.jpg" alt="Northern Mile Media" style="height:32px;width:auto;"><h1>NORTHERN MILE MEDIA</h1></a></div>
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
  <div class="cht"><div class="cht-l">National average diesel</div><div style="color:var(--text-muted);font-size:0.8125rem;padding:32px 0;text-align:center;">Coming soon mdash; chart will appear as data accumulates.</div></div>

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
```

### scripts/chart_builder.py (8134 bytes)
```python
#!/usr/bin/env python3
"""Northern Mile branded chart generator.
Colors: Bold North palette.
Usage: from chart_builder import build_blog_charts; build_blog_charts()
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import json, os
from datetime import datetime

DATA = os.path.expanduser('~/northern-mile-dashboard/data')
OUT = os.path.expanduser('~/northern-mile-dashboard/web')

# Brand palette: Northern Road
PRIMARY = '#1a3a5c'     # Highway Blue
SECONDARY = '#c41e3a'   # Maple Red
MUTED = '#6b7280'       # Pavement Grey
GREEN = '#16a34a'       # Positive
AMBER = '#d97706'       # Caution
BG = '#f8f9fa'          # Snow White

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'axes.grid': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'text.color': SECONDARY,
    'axes.labelcolor': MUTED,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
})

def load_data(name):
    with open(os.path.join(DATA, f'{name}.json')) as f:
        return json.load(f)

def chart_fuel_prices():
    """Fuel prices by province — diesel vs gasoline."""
    fuel = load_data('fuel')
    ca = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']
    diesel = [fuel['provinces'][p]['diesel'] for p in ca]
    gasoline = [fuel['provinces'][p]['gasoline'] for p in ca]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = range(len(ca))
    w = 0.34

    # Bars with spacing
    bars1 = ax.bar([i - w/2 for i in x], diesel, w, color=PRIMARY, label='Diesel', edgecolor='white', linewidth=1)
    bars2 = ax.bar([i + w/2 for i in x], gasoline, w, color=SECONDARY, label='Gasoline', edgecolor='white', linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels(ca, fontsize=11, fontweight='600', color=PRIMARY)
    ax.set_ylabel('Cents per litre', fontsize=10, color=MUTED)

    # Legend top right
    ax.legend(frameon=False, fontsize=11, loc='upper right', handlelength=1, handleheight=1)

    # National averages in annotation box
    natl_d = fuel['diesel_national_avg']
    natl_g = fuel['gasoline_national_avg']
    ax.axhline(y=natl_d, color=PRIMARY, linestyle='--', linewidth=1, alpha=0.35)
    ax.axhline(y=natl_g, color=SECONDARY, linestyle='--', linewidth=1, alpha=0.35)

    ax.text(0.98, 0.95, f'Diesel avg  {natl_d}¢\nGas avg  {natl_g}¢',
            transform=ax.transAxes, fontsize=9, color=PRIMARY, ha='right', va='top',
            fontweight='600', linespacing=1.6,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e2e5e9', linewidth=0.5))

    # Value on highest bar only
    max_val = max(diesel + gasoline)
    max_idx = (diesel + gasoline).index(max_val)
    bar_list = list(bars1) + list(bars2)
    bar = bar_list[max_idx]
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f'{max_val:.0f}¢', ha='center', fontsize=10, fontweight='700', color=PRIMARY)

    ax.set_ylim(0, max(diesel + gasoline) * 1.15)
    ax.set_xlim(-0.6, len(ca) - 0.4)
    plt.tight_layout(pad=2)
    plt.savefig(os.path.join(OUT, 'chart-fuel-prices.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-fuel-prices.png'

def chart_exchange():
    """USD/CAD 30-day trend."""
    fx = load_data('exchange')
    history = fx.get('history', [])
    if not history: return None

    dates = [h['date'] for h in history]
    rates = [h['rate'] for h in history]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dates, rates, color=PRIMARY, linewidth=2, solid_capstyle='round')
    ax.fill_between(dates, rates, min(rates)-0.002, alpha=0.08, color=PRIMARY)
    
    # Key dates
    ax.set_ylabel('USD / CAD', fontsize=10)
    step = max(1, len(dates)//5)
    tick_idx = list(range(0, len(dates), step))
    if tick_idx[-1] != len(dates)-1:
        tick_idx.append(len(dates)-1)
    ax.set_xticks([dates[i] for i in tick_idx])
    ax.set_xticklabels([dates[i] for i in tick_idx], fontsize=8)
    
    # Min/max annotations
    min_val, max_val = min(rates), max(rates)
    min_idx = rates.index(min_val)
    max_idx = rates.index(max_val)
    ax.annotate(f'Low {min_val:.4f}', xy=(dates[min_idx], min_val),
                xytext=(dates[min_idx], min_val-0.003), fontsize=8, color=MUTED, ha='center')
    ax.annotate(f'High {max_val:.4f}', xy=(dates[max_idx], max_val),
                xytext=(dates[max_idx], max_val+0.003), fontsize=8, color=MUTED, ha='center')
    
    # Current value
    ax.annotate(f'{rates[-1]:.4f}', xy=(0.98, 0.92), xycoords='axes fraction',
                fontsize=16, fontweight='bold', color=PRIMARY, ha='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e2e5e9', linewidth=0.5))
    
    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(OUT, 'chart-exchange.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-exchange.png'

def chart_cost_breakdown():
    """Operating cost pie chart."""
    fig, ax = plt.subplots(figsize=(6.5, 5))
    labels = ['Fuel', 'Labour', 'Equipment\n& Maintenance', 'Insurance', 'Other']
    sizes = [30, 35, 15, 10, 10]
    colors = [PRIMARY, SECONDARY, AMBER, MUTED, '#cbd5e1']
    explode = (0.03, 0, 0, 0, 0)
    
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', startangle=90, pctdistance=0.72,
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
        textprops={'fontsize': 10, 'fontweight': '600'}
    )
    for t in autotexts: t.set_fontsize(11); t.set_fontweight('700'); t.set_color('white')
    # Fuel label in secondary since it's on red
    autotexts[0].set_color(SECONDARY)
    
    ax.set_title('Where Your Operating Dollar Goes', fontsize=13, fontweight='700', pad=18, color=SECONDARY)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'chart-cost-breakdown.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-cost-breakdown.png'

def chart_diesel_spread():
    """Diesel price spread across provinces."""
    fuel = load_data('fuel')
    prods = ['BC','AB','ON','QC','MB','SK','NB','NS','PE','NL']
    values = [fuel['provinces'][p]['diesel'] for p in prods]
    
    # Sort by value descending
    pairs = sorted(zip(values, prods), reverse=True)
    values, prods = zip(*pairs)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [PRIMARY if v == max(values) else SECONDARY if v <= sorted(values)[1] else '#cbd5e1' for v in values]
    
    bars = ax.barh(prods, values, color=colors, height=0.6)
    ax.set_xlabel('Cents per litre', fontsize=10)
    
    # Value labels
    for bar, val in zip(bars, values):
        ax.text(val + 1.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}¢',
                va='center', fontsize=11, fontweight='700', color=SECONDARY)
    
    # Spread callout
    spread = max(values) - min(values)
    ax.annotate(f'{spread:.1f}¢\nspread', xy=(0.98, 0.94), xycoords='axes fraction',
                fontsize=10, fontweight='700', color=PRIMARY, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e2e5e9'))
    
    ax.set_xlim(0, max(values) * 1.12)
    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(OUT, 'chart-diesel-spread.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-diesel-spread.png'

def build_all():
    """Generate all blog charts."""
    results = []
    for fn in [chart_fuel_prices, chart_exchange, chart_cost_breakdown, chart_diesel_spread]:
        name = fn.__name__
        try:
            f = fn()
            if f:
                results.append(f)
                print(f'  {name} → {f}')
        except Exception as e:
            print(f'  {name} failed: {e}')
    print(f'\n{len(results)} charts saved to {OUT}/')
    return results

if __name__ == '__main__':
    print(f'Northern Mile Charts — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    build_all()
```

## gh run list --limit 20
```
completed	success	Auto-update 2026-08-11 21:13	Deploy to GitHub Pages	master	push	31552914515	19s	2026-08-12T01:13:48Z
completed	success	Auto-update 2026-08-11 20:43	Deploy to GitHub Pages	master	push	31551202085	20s	2026-08-12T00:43:36Z
completed	success	Auto-update 2026-08-11 20:13	Deploy to GitHub Pages	master	push	31549418486	21s	2026-08-12T00:13:14Z
completed	success	Auto-update 2026-08-11 19:41	Deploy to GitHub Pages	master	push	31547470158	23s	2026-08-11T23:42:02Z
completed	success	Auto-update 2026-08-11 19:11	Deploy to GitHub Pages	master	push	31545524874	22s	2026-08-11T23:11:51Z
completed	success	Auto-update 2026-08-11 18:41	Deploy to GitHub Pages	master	push	31543493163	19s	2026-08-11T22:41:42Z
completed	success	Auto-update 2026-08-11 18:10	Deploy to GitHub Pages	master	push	31541261737	17s	2026-08-11T22:10:33Z
completed	success	Auto-update 2026-08-11 17:39	Deploy to GitHub Pages	master	push	31538895068	21s	2026-08-11T21:39:23Z
completed	success	Auto-update 2026-08-11 17:08	Deploy to GitHub Pages	master	push	31536437997	22s	2026-08-11T21:08:16Z
completed	success	Auto-update 2026-08-11 16:37	Deploy to GitHub Pages	master	push	31533851162	22s	2026-08-11T20:37:10Z
completed	success	Auto-update 2026-08-11 16:05	Deploy to GitHub Pages	master	push	31531199137	20s	2026-08-11T20:05:56Z
completed	success	Auto-update 2026-08-11 15:34	Deploy to GitHub Pages	master	push	31528563080	28s	2026-08-11T19:34:47Z
completed	success	Auto-update 2026-08-11 15:03	Deploy to GitHub Pages	master	push	31525931011	16s	2026-08-11T19:03:38Z
completed	success	Auto-update 2026-08-11 14:32	Deploy to GitHub Pages	master	push	31523246317	19s	2026-08-11T18:32:28Z
completed	success	Auto-update 2026-08-11 14:01	Deploy to GitHub Pages	master	push	31520554422	32s	2026-08-11T18:01:20Z
completed	success	Auto-update 2026-08-11 13:30	Deploy to GitHub Pages	master	push	31517891958	21s	2026-08-11T17:30:15Z
completed	success	Auto-update 2026-08-11 12:58	Deploy to GitHub Pages	master	push	31515238793	16s	2026-08-11T16:59:03Z
completed	success	Auto-update 2026-08-11 12:28	Deploy to GitHub Pages	master	push	31512541111	31s	2026-08-11T16:28:05Z
completed	success	Auto-update 2026-08-11 11:56	Deploy to GitHub Pages	master	push	31509795794	25s	2026-08-11T15:56:59Z
completed	success	Auto-update 2026-08-11 11:25	Deploy to GitHub Pages	master	push	31506952001	39s	2026-08-11T15:25:37Z
```

## gh workflow list --all
```
Deploy to GitHub Pages	active	328831050
Deploy to GitHub Pages	disabled_manually	328740196
pages-build-deployment	active	312637494
```

## crontab -l
```
```

## systemctl list-timers --all (head 30)
```
NEXT                            LEFT LAST                               PASSED UNIT                         ACTIVATES
Tue 2026-08-11 21:50:00 EDT     6min Tue 2026-08-11 21:40:01 EDT  3min 34s ago sysstat-collect.timer        sysstat-collect.service
Tue 2026-08-11 22:34:04 EDT    50min Tue 2026-08-11 21:33:06 EDT     10min ago anacron.timer                anacron.service
Tue 2026-08-11 22:57:09 EDT 1h 13min Tue 2026-08-11 21:42:06 EDT  1min 30s ago fwupd-refresh.timer          fwupd-refresh.service
Wed 2026-08-12 00:00:00 EDT 2h 16min Tue 2026-08-11 00:00:06 EDT       21h ago dpkg-db-backup.timer         dpkg-db-backup.service
Wed 2026-08-12 00:00:00 EDT 2h 16min Tue 2026-08-11 00:00:06 EDT       21h ago sysstat-rotate.timer         sysstat-rotate.service
Wed 2026-08-12 00:07:00 EDT 2h 23min Tue 2026-08-11 00:07:06 EDT       21h ago sysstat-summary.timer        sysstat-summary.service
Wed 2026-08-12 00:44:04 EDT  3h 0min Tue 2026-08-11 00:03:06 EDT       21h ago logrotate.timer              logrotate.service
Wed 2026-08-12 06:02:54 EDT       8h Tue 2026-08-11 06:51:43 EDT       14h ago apt-daily-upgrade.timer      apt-daily-upgrade.service
Wed 2026-08-12 06:24:34 EDT       8h Tue 2026-08-11 07:06:58 EDT       14h ago man-db.timer                 man-db.service
Wed 2026-08-12 08:03:22 EDT      10h Tue 2026-08-11 18:23:06 EDT  3h 20min ago apt-daily.timer              apt-daily.service
Wed 2026-08-12 11:49:05 EDT      14h Tue 2026-08-11 20:40:01 EDT   1h 3min ago motd-news.timer              motd-news.service
Wed 2026-08-12 20:08:21 EDT      22h Tue 2026-08-11 20:08:21 EDT  1h 35min ago systemd-tmpfiles-clean.timer systemd-tmpfiles-clean.service
Sun 2026-08-16 03:10:58 EDT   4 days Sun 2026-08-09 03:11:06 EDT    2 days ago e2scrub_all.timer            e2scrub_all.service
Mon 2026-08-17 00:41:05 EDT   5 days Mon 2026-08-10 00:38:32 EDT 1 day 21h ago fstrim.timer                 fstrim.service
-                                  - -                                       - apport-autoreport.timer      apport-autoreport.service
-                                  - -                                       - ua-timer.timer               ua-timer.service

16 timers listed.
```

## data/history/series.csv (92 lines)
```
date,series,key,value
2026-08-05,diesel,AB,200.3000
2026-08-06,diesel,AB,200.9000
2026-08-07,diesel,AB,200.7000
2026-08-08,diesel,AB,200.7000
2026-08-09,diesel,AB,200.7000
...
2026-08-07,diesel,national,222.9000
2026-08-08,diesel,national,222.9000
2026-08-09,diesel,national,222.9000
2026-08-10,diesel,national,222.2000
2026-08-11,diesel,national,222.2000
```

## data/history/border.csv (19 lines)
```
date,crossing_id,delay_minutes,observation_time
2026-08-10,coutts-sweetgrass,0,20:15 MDT
2026-08-10,emerson-pembina,0,22:15 CDT
2026-08-10,fort-erie-buffalo,3,23:20 EDT
2026-08-10,lacolle-champlain,0,20:12 EDT
2026-08-10,lansdowne-alexandria,0,22:15 EDT
...
2026-08-11,lansdowne-alexandria,0,20:15 EDT
2026-08-11,pacific-blaine,5,18:00 PDT
2026-08-11,queenston-lewiston,5,21:00 EDT
2026-08-11,sarnia-port-huron,0,19:15 EDT
2026-08-11,windsor-detroit,0,20:15 EDT
```

## data/health.json
```json
{
  "sources": {
    "fuel": {
      "last_success": "2026-08-12T01:13:45.070680+00:00",
      "last_attempt": "2026-08-12T01:13:45.070702+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "exchange": {
      "last_success": "2026-08-12T01:13:45.071531+00:00",
      "last_attempt": "2026-08-12T01:13:45.071540+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "border": {
      "last_success": "2026-08-12T01:13:45.072265+00:00",
      "last_attempt": "2026-08-12T01:13:45.072274+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "incidents": {
      "last_success": "2026-08-12T01:13:45.073242+00:00",
      "last_attempt": "2026-08-12T01:13:45.073251+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "market": {
      "last_success": "2026-08-12T01:13:45.073874+00:00",
      "last_attempt": "2026-08-12T01:13:45.073882+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "news": {
      "last_success": "2026-08-12T01:13:45.074548+00:00",
      "last_attempt": "2026-08-12T01:13:45.074556+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    },
    "theft": {
      "last_success": "2026-08-12T01:13:45.075293+00:00",
      "last_attempt": "2026-08-12T01:13:45.075302+00:00",
      "consecutive_failures": 0,
      "status": "ok"
    }
  },
  "updated": "2026-08-12T01:13:45.075307+00:00"
}```

## data/alerts.json
```
NOT PRESENT
```

## docs/ listing
```
total 384
drwxrwxr-x 13 hermes hermes   4096 Aug  7 08:17 .
drwxrwxr-x 14 hermes hermes   4096 Aug 11 21:43 ..
-rw-rw-r--  1 hermes hermes      0 Jul 19 20:59 .nojekyll
-rw-rw-r--  1 hermes hermes     32 Aug  6 13:30 CNAME
-rw-------  1 hermes hermes   2055 Jul 24 20:08 app.js
drwxrwxr-x  2 hermes hermes   4096 Jul 20 22:31 assets
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 border-wait-times
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 cargo-theft
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 exchange-rate
-rw-rw-r--  1 hermes hermes  55334 Jul 14 00:16 favicon.ico
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 fuel-cost-calculator
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 fuel-prices
-rw-rw-r--  1 hermes hermes  22690 Aug 11 21:13 index.html
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 industry-news
-rw-rw-r--  1 hermes hermes  14806 Jul 20 22:22 leaflet.css
-rw-rw-r--  1 hermes hermes 147552 Jul 20 22:22 leaflet.js
-rw-rw-r--  1 hermes hermes  53084 Aug  6 15:55 logo.jpg
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 market-pulse
drwxrwxr-x  3 hermes hermes   4096 Aug  7 08:17 methodology
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 road-incidents
-rw-rw-r--  1 hermes hermes     84 Aug  7 08:17 robots.txt
-rw-rw-r--  1 hermes hermes    876 Aug  7 08:17 sitemap.xml
-rw-rw-r--  1 hermes hermes  17611 Aug  5 20:43 styles.css
drwxrwxr-x  2 hermes hermes   4096 Aug  6 14:20 v2
```

## docs/fuel-prices/index.html (first 40 lines)
```html
<!DOCTYPE html><html lang="en-CA"><head><meta charset="UTF-8"><meta name="google-site-verification" content="xdt2nZry-WK9v9FSFfb5Fi2VKCfrRfA4HJhKuIQJ9s8" />
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Canadian Diesel Prices by Province — Live | Northern Mile</title>
<meta name="description" content="Live diesel prices for all ten Canadian provinces, updated every 30 minutes. Tax breakdown, US border-state comparison, IFTA reference and routing savings for truckers.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="https://dashboard.northernmilemedia.com/fuel-prices/">
<meta property="og:type" content="website"><meta property="og:title" content="Canadian Diesel Prices — Live by Province | Northern Mile"><meta property="og:description" content="Diesel across 10 provinces + US border states. Tax breakdown, IFTA, routing savings."><meta property="og:image" content="https://dashboard.northernmilemedia.com/og-fuel.jpg"><meta name="twitter:card" content="summary_large_image">
<meta name="build" content="20:15 EDT">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Saira+Condensed:wght@500;600;700&family=Saira:wght@500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css?v=">
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Dashboard","item":"https://dashboard.northernmilemedia.com/"},{"@type":"ListItem","position":2,"name":"Fuel Prices","item":"https://dashboard.northernmilemedia.com/fuel-prices/"}]},
{"@type":"Dataset","name":"Canadian Diesel Prices by Province","description":"Live diesel prices for all ten Canadian provinces, updated every 30 minutes.","creator":{"@type":"Organization","name":"Northern Mile Media"},"spatialCoverage":{"@type":"Place","name":"Canada"},"dateModified":"20:15 EDT"},
{"@type":"FAQPage","mainEntity":[
{"@type":"Question","name":"Why is diesel different across provinces?","acceptedAnswer":{"@type":"Answer","text":"Provincial fuel taxes drive most of the gap. BC adds carbon tax and transit levies; Alberta has lower levies and no provincial sales tax."}},
{"@type":"Question","name":"Where should I fuel up to save money?","acceptedAnswer":{"@type":"Answer","text":"Alberta is cheapest, then Saskatchewan and Manitoba. Crossing into the US, diesel is usually cheaper once converted to Canadian cents per litre."}},
{"@type":"Question","name":"How often do prices update?","acceptedAnswer":{"@type":"Answer","text":"Every 30 minutes from public fuel surveys across all ten provinces and US border states."}}]}
]}
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NDXR7ERL80"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NDXR7ERL80');</script>
</head><body>

<header class="hd"><div class="wrap"><a href="https://northernmilemedia.com" style="display:flex;align-items:center;gap:10px;color:inherit"><img src="/logo.jpg" alt="Northern Mile Media"><b>Northern Mile</b></a></div></header>
<nav class="nav"><div class="wrap"><a href="/">Home</a><a href="/fuel-prices/" class="on">Fuel</a><a href="/exchange-rate/">FX</a><a href="/border-wait-times/">Border</a><a href="/road-incidents/">Incidents</a><a href="/cargo-theft/">Theft</a><a href="/market-pulse/">Market</a><a href="/industry-news/">News</a><a href="/fuel-cost-calculator/">Calc</a></div></nav>

<main class="wrap">
  <div class="breadcrumb"><a href="/">Dashboard</a> › Fuel Prices</div>
  <div class="strip"><span><span class="dot"></span><b>Live</b></span><span>NMDI (Northern Mile Diesel Index) · all ten provinces</span><span>Updated 20:15 EDT · NRCan weekly diesel survey · refresh 30 min</span></div>

  <section class="cluster">
    <div>
      <div class="readlabel"><span class="tick">▸</span> NMDI · National</div>
      <div class="odo hero-odo" data-value="222.2" data-unit="c/L"></div>
      <div class="trend"><span class="b">7-DAY</span> — &nbsp; <span class="b">30-DAY</span> </div>
    </div>
    <div class="clus-gauges">
      <div class="g lo"><div class="gv">200.4</div><div class="gl">Cheapest · AB</div></div>
```

## og-image references
```
No references found
```
