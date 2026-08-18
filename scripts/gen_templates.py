#!/usr/bin/env python3
"""Generate every dashboard template from one shell.

One header, one nav, one footer, written once. SEO scaffolding — canonical, OG,
JSON-LD, a single h1 — is part of the shell, so no page can ship without it. One
optional module sponsor slot per page, methodology excepted. Change this file,
regenerate, and all eleven pages move together.

Run: python3 scripts/gen_templates.py
"""

import os
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "templates")

GA = "G-NDXR7ERL80"
BASE = "https://dashboard.northernmilemedia.com"
ORG_URL = "https://northernmilemedia.com"
SUB = "https://www.northernmilemedia.com/subscribe/"

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Space+Grotesk:wght@500;600;700&"
         "family=Inter:wght@400;500;600&"
         "family=IBM+Plex+Mono:wght@400;500&display=swap")

# href, label — the one nav, in order. Every page renders this identically.
NAV = [
    ("/", "Home"),
    ("/fuel-prices/", "Diesel"),
    ("/fuel-cost-calculator/", "Calculator"),
    ("/border-wait-times/", "Border"),
    ("/exchange-rate/", "Exchange"),
    ("/road-incidents/", "Incidents"),
    ("/market-pulse/", "Market"),
    ("/industry-news/", "News"),
    ("/methodology/nmdi/", "Methodology"),
    ("/press/", "Press"),
]

ORG_LD = ('{"@type":"Organization","@id":"' + ORG_URL + '/#org","name":"Northern Mile Media",'
          '"url":"' + ORG_URL + '/","description":"Canadian trucking and fuel data publication."}')


def nav_html(active):
    out = []
    for href, lab in NAV:
        is_active = href == active or (href == "/fuel-prices/" and active.startswith("/us-diesel/"))
        on = ' class="on"' if is_active else ""
        cur = ' aria-current="page"' if is_active else ""
        out.append(f'<a href="{href}"{on}{cur}>{lab}</a>')
    return "".join(out)


def country_switch(active):
    def opt(href, label, on):
        cls = 'class="seg-opt is-on"' if on else 'class="seg-opt"'
        cur = ' aria-current="true"' if on else ''
        return f'<a {cls}{cur} href="{href}">{label}</a>'
    return ('<div class="seg" role="group" aria-label="Country">'
            + opt("/fuel-prices/", "Canada", active == "ca")
            + opt("/us-diesel/", "US", active == "us")
            + '</div>')


def head(title, desc, canon, og_img, ld, og_type="website"):
    ld_block = f'<script type="application/ld+json">\n{ld}\n</script>\n' if ld else ""
    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{BASE}{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Northern Mile Media">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{BASE}{canon}">
<meta property="og:image" content="{BASE}/{og_img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="build" content="{{{{updated_iso}}}}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="/assets/nm.css?v={{{{build_version}}}}">
{ld_block}<script async src="https://www.googletagmanager.com/gtag/js?id={GA}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA}');</script>
<script defer src="https://cdn.jsdelivr.net/ghost/portal@~2.69/umd/portal.min.js" data-i18n="true" data-ghost="https://www.northernmilemedia.com/" data-key="995d6f9b3eeb1574dbebd63ce5" data-api="https://northern-mile-media.ghost.io/ghost/api/content/" data-locale="en" crossorigin="anonymous"></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="hd"><div class="wrap">
  <a class="mark" href="/"><img class="logo" src="/assets/logo.png" width="32" height="32" alt=""><b>Northern Mile</b><span>Canadian trucking data</span></a>
</div></header>

<nav class="nav" aria-label="Sections"><div class="wrap">{nav_html(canon)}</div></nav>

<main class="wrap" id="main">
"""


def foot(extra_script=""):
    flinks = "".join(f'<a href="{h}">{l}</a>' for h, l in NAV if l != "Home")
    year = datetime.date.today().year
    return f"""
</main>

<footer class="ft"><div class="wrap">
  <div class="brand"><a class="name" href="/">Northern Mile Media</a><span class="tag">live Canadian trucking data</span></div>
  <nav class="flinks" aria-label="Footer">{flinks}</nav>
  <div class="bottom"><span>&copy; {year} Northern Mile Media</span><a href="{SUB}" data-portal="signup">Subscribe free</a><span>Updated {{{{updated_at}}}} UTC</span></div>
</div></footer>

<script src="/assets/nm.js?v={{{{build_version}}}}"></script>
{extra_script}</body>
</html>
"""


def sponsor(key):
    """One optional module sponsor. Rendered only when data supplies the block."""
    return (f'\n  <!--OPTIONAL:{key}-->\n'
            f'  <aside class="sp"><span class="t">Presented by</span>'
            f'<span class="n">{{{{{key}.name}}}}</span>'
            f'<span class="l">{{{{{key}.line}}}}</span>'
            f'<a class="c" href="{{{{{key}.url}}}}">Learn more →</a></aside>\n'
            f'  <!--/OPTIONAL:{key}-->\n')


def cite():
    return """
  <div class="cite">
    <div class="cl">Citing this figure</div>
    <q id="citation">Northern Mile Diesel Index: {{fuel.national_diesel}}¢/L national average, ten provinces, NRCan weekly survey print {{fuel.print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/methodology/nmdi/</q>
    <div class="row">
      <button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button>
      <a class="btn" href="/methodology/nmdi/">How it is calculated</a>
    </div>
  </div>
"""


def rail():
    return """
    <div class="rail">
      <div class="cap"><h3>The spread</h3><span class="sp">{{fuel.low_code}} <b>{{fuel.low}}</b> → {{fuel.high_code}} <b>{{fuel.high}}</b> · {{fuel.spread}}¢/L</span></div>
      <div class="mean-wrap"><span class="mean" style="left:{{fuel.national_pct}}%"><span class="lab">Index {{fuel.national_diesel}}</span></span></div>
      <!--LOOP:provinces--><a class="row" href="/fuel-prices/"><span class="code">{{code}}</span><span class="track"><span class="fill" style="width:{{pct}}%"></span><span class="dot" style="left:{{pct}}%"></span></span><span class="val {{change_class}}">{{price}}</span></a><!--/LOOP:provinces-->
    </div>
"""


def _chart_stats():
    """Four-number summary strip. Server-rendered, no JS, shared byte-for-byte
    by the homepage and the fuel page so the numbers always match."""
    return """
      <div class="chart-stats">
        <div class="cstat"><span class="l">Today</span><b>{{chart_latest}}</b><span class="s">{{chart_latest_band}}</span></div>
        <div class="cstat"><span class="l">10y average</span><b>{{chart_avg}}</b><span class="s"></span></div>
        <div class="cstat"><span class="l">10y low</span><b>{{chart_low}}</b><span class="s">{{chart_low_date}}</span></div>
        <div class="cstat"><span class="l">10y high</span><b>{{chart_high}}</b><span class="s">{{chart_high_date}}</span></div>
      </div>"""


def chart_summary():
    """Summary strip only — the homepage carries the ten-year context numbers
    without the interactive chart."""
    return """
    <div class="chart-card">
      <div class="chart-head">
        <h3>National diesel &mdash; where today sits</h3>
      </div>""" + _chart_stats() + """
    </div>"""


def chart_block():
    """Interactive diesel chart. Data embedded as JSON so the figures survive if
    the script fails — the chart enhances the data, it is not the only copy.
    Mounted after the rail on the fuel page only; the coherence guard enforces
    that the D3 loader appears nowhere else."""
    return """
    <div class="chart-card" id="nmdi-chart-card">
      <div class="chart-head">
        <h3>National diesel &mdash; ten-year trend</h3>
        <span class="sub" id="nmdi-readout">{{chart_range_label}}</span>
      </div>""" + _chart_stats() + """
      <div class="story" id="nmdi-story">
        <span class="sl">Zoom to a moment:</span>
        <button data-focus="low" type="button">2020 crash</button>
        <button data-focus="high" type="button">2022 spike</button>
        <button data-focus="today" type="button">Today</button>
      </div>
      <div style="position:relative">
        <svg class="chart-svg" id="nmdi-chart"></svg>
        <div class="tip" id="nmdi-tip"></div>
      </div>
      <div class="hint">How to use it: drag to pan &middot; scroll to zoom &middot; hover for the weekly figure</div>
      <div class="foot-note">Northern Mile Diesel Index, weekly. Source: NRCan.</div>
    </div>
    <script id="nmdi-data" type="application/json">{{chart_data_json}}</script>
"""


# D3 loader + chart init. Included ONLY on pages that call it (home, fuel), via
# the extra_script slot in foot(). Loads D3 from CDN.
CHART_SCRIPT = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>\n'
                '<script src="/assets/nmdi-chart.js?v={{build_version}}"></script>\n')


def subscribe(heading, body):
    return (f'\n  <section class="sub" aria-labelledby="brief">\n'
            f'    <div class="e">The Northern Mile Brief</div>\n'
            f'    <h2 id="brief">{heading}</h2>\n'
            f'    <p>{body}</p>\n'
            f'    <a class="sub-btn" href="{SUB}" data-portal="signup">Subscribe free</a>\n'
            f'    <div class="fine">One email a week. Unsubscribe any time.</div>\n'
            f'  </section>\n')


def write(name, body):
    with open(os.path.join(OUT, f"{name}.template.html"), "w") as f:
        f.write(body)
    print(f"  {name:26} {len(body):6,} bytes")


def crumb(name, slug):
    return ('{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Dashboard","item":"' + BASE + '/"},'
            '{"@type":"ListItem","position":2,"name":"' + name + '","item":"' + BASE + slug + '"}]}')


print("Generating templates")

# ═══ Home ═════════════════════════════════════════════════════════════
home_ld = ('{"@context":"https://schema.org","@graph":[' + ORG_LD + ','
 '{"@type":"WebSite","@id":"' + BASE + '/#site","url":"' + BASE + '/","name":"Northern Mile Dashboard","publisher":{"@id":"' + ORG_URL + '/#org"},"inLanguage":"en-CA"},'
 '{"@type":"Dataset","@id":"' + BASE + '/#nmdi","name":"Northern Mile Diesel Index (NMDI)","alternateName":"NMDI","description":"A national Canadian retail diesel average computed as the unweighted mean of ten provincial averages from the Natural Resources Canada weekly retail survey. Yukon and the Northwest Territories are excluded.","url":"' + BASE + '/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"Canada"},"measurementTechnique":"Unweighted arithmetic mean of provincial means","variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price","unitText":"Canadian cents per litre","value":"{{fuel.national_diesel}}"},"dateModified":"{{updated_iso}}"},'
 '{"@type":"FAQPage","mainEntity":['
 '{"@type":"Question","name":"How is the Northern Mile Diesel Index calculated?","acceptedAnswer":{"@type":"Answer","text":"It is the unweighted arithmetic mean of ten provincial diesel averages. Each provincial figure is itself the unweighted mean of the Natural Resources Canada survey cities in that province. Yukon and the Northwest Territories are surveyed but excluded from the index."}},'
 '{"@type":"Question","name":"How often do Canadian diesel prices change on this dashboard?","acceptedAnswer":{"@type":"Answer","text":"The diesel figure changes weekly, when Natural Resources Canada publishes a new retail survey. The page rebuilds every 30 minutes, but the diesel number holds steady between survey prints."}},'
 '{"@type":"Question","name":"Do these diesel prices include carbon tax?","acceptedAnswer":{"@type":"Answer","text":"Yes. Every price shown is inclusive of federal and provincial fuel taxes, carbon pricing, and sales taxes, as published by Natural Resources Canada."}},'
 '{"@type":"Question","name":"Can I cite the Northern Mile Diesel Index?","acceptedAnswer":{"@type":"Answer","text":"Yes. The dashboard provides a formatted citation with the figure and the survey print date. The full method and a dated revision history of every published correction are on the methodology page."}}]}]}')

write("index",
 head("Canadian Diesel Prices Today — {{fuel.national_diesel}}¢/L National Average | Northern Mile",
      "The Northern Mile Diesel Index: {{fuel.national_diesel}}¢/L across ten Canadian provinces from the NRCan weekly survey, print {{fuel.print_date}}. Live commercial border wait times and the Bank of Canada exchange rate.",
      "/", "og.jpg", home_ld)
 + '''
  <section class="hero">
    <span class="eyebrow">Northern Mile Diesel Index</span>
    <h1>Canadian diesel prices today</h1>
    <div class="figure"><span class="n">{{fuel.national_diesel}}</span><span class="u">¢/L</span><span class="d {{fuel.change_7d_class}}">{{fuel.change_7d}} · 7d</span></div>
    <div class="meta"><span>Ten provinces</span><span>NRCan survey print <b>{{fuel.print_date}}</b></span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
''' + rail() + chart_summary() + cite() + '''
    <div class="stats">
      <a class="stat" href="/fuel-prices/"><div class="l">Cheapest</div><div class="v down">{{fuel.low}}</div><div class="s">{{fuel.low_code}} · ¢/L</div></a>
      <a class="stat" href="/fuel-prices/"><div class="l">Dearest</div><div class="v up">{{fuel.high}}</div><div class="s">{{fuel.high_code}} · ¢/L</div></a>
      <a class="stat" href="/fuel-prices/"><div class="l">Spread</div><div class="v">{{fuel.spread}}</div><div class="s">{{fuel.low_code}} to {{fuel.high_code}}</div></a>
      <a class="stat" href="/exchange-rate/"><div class="l">USD / CAD</div><div class="v">{{fx.usd_cad}}</div><div class="s">{{fx.direction}} {{fx.change}} · BoC</div></a>
      <a class="stat" href="/fuel-prices/"><div class="l">US diesel</div><div class="v">{{eia.us_national_cpl}}</div><div class="s">¢/L · ${{eia.us_national_usd_gal}}/gal</div></a>
      <a class="stat" href="/methodology/nmdi/"><div class="l">North American index</div><div class="v">{{eia.nadi}}</div><div class="s">¢/L · CA + US, equal weight</div></a>
    </div>
  </section>
''' + sponsor("sponsor_page") + '''
  <section class="sec">
    <div class="lead"><h2>On the road</h2><p>What is in front of you right now.</p></div>
    <div class="two">
      <div><h3>Border crossings</h3><div class="rows">
      <!--LOOP:border_rows--><a class="r" href="/border-wait-times/"><span class="k">{{name}}<small>{{status_label}}</small></span><span class="v">{{wait}}</span></a><!--/LOOP:border_rows-->
      </div><p class="note">Each wait carries CBSA's own capture time, not our fetch time. <a href="/border-wait-times/">All crossings</a></p></div>
      <div><h3>Road incidents</h3>
      <!--IF:incidents.none--><div class="empty"><b>Corridors clear</b>No major closures or collisions on the corridors we monitor.</div><!--/IF:incidents.none-->
      <div class="links-list">
      <!--LOOP:incidents.incidents--><a href="{{url}}">{{what}}</a><!--/LOOP:incidents.incidents-->
      </div><p class="note">{{incidents.status_line}} <a href="/road-incidents/">Open map</a></p></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Planning a run</h2><p>What a trip costs, and where the market sits.</p></div>
    <div class="two">
      <div><h3>Exchange and market</h3><div class="rows">
        <a class="r" href="/exchange-rate/"><span class="k">USD / CAD<small>Bank of Canada</small></span><span class="v">{{fx.usd_cad}} {{fx.change}}</span></a>
        <!--LOOP:market--><a class="r" href="/market-pulse/"><span class="k">{{name}}<small>{{note}}</small></span><span class="v {{value_class}}">{{value}}</span></a><!--/LOOP:market-->
      </div></div>
      <div><h3>Industry news</h3><div class="links-list">
        <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">{{category}}</span>{{headline}}</a><!--/LOOP:news-->
      </div><p class="note"><a href="/industry-news/">All headlines</a></p></div>
    </div>
    <p class="note">Diesel prices include all federal and provincial fuel, carbon, and sales taxes. <a href="/fuel-cost-calculator/">Work out what a run costs</a></p>
  </section>
''' + subscribe("One email, Wednesday mornings",
   "What moved in Canadian diesel, at the border, and in freight demand, with every figure dated and linked back to this dashboard. Written for people who move freight, not for people who write about it.")
 + foot())

# ═══ Fuel prices ══════════════════════════════════════════════════════
fuel_ld = ('{"@context":"https://schema.org","@graph":[' + crumb("Diesel prices by province","/fuel-prices/") + ','
 '{"@type":"Dataset","name":"Canadian Diesel Prices by Province","description":"Retail diesel prices for all ten Canadian provinces, from the Natural Resources Canada weekly retail survey.","url":"' + BASE + '/fuel-prices/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"Canada"},"variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price","unitText":"Canadian cents per litre"},"dateModified":"{{updated_iso}}"},'
 '{"@type":"FAQPage","mainEntity":['
 '{"@type":"Question","name":"Why do diesel prices differ between Canadian provinces?","acceptedAnswer":{"@type":"Answer","text":"Provincial fuel tax rates are set independently, carbon pricing differs by jurisdiction, and distance from refining and distribution capacity adds haul cost in northern and island markets. The current spread between the cheapest and dearest province is {{fuel.spread}} cents per litre."}},'
 '{"@type":"Question","name":"Which Canadian province has the cheapest diesel right now?","acceptedAnswer":{"@type":"Answer","text":"In the NRCan survey print dated {{fuel.print_date}}, the lowest provincial average was {{fuel.low_code}} at {{fuel.low}} cents per litre and the highest was {{fuel.high_code}} at {{fuel.high}} cents per litre. These figures change weekly."}}]}]}')

write("fuel-prices",
 head("Diesel Prices by Province in Canada — {{fuel.national_diesel}}¢/L | Northern Mile",
      "Diesel prices for all ten Canadian provinces from the NRCan weekly survey, print {{fuel.print_date}}. National average {{fuel.national_diesel}}¢/L, cheapest {{fuel.low_code}} at {{fuel.low}}, dearest {{fuel.high_code}} at {{fuel.high}}, spread {{fuel.spread}}¢/L.",
      "/fuel-prices/", "og-fuel.jpg", fuel_ld, "article")
 + '''
  <section class="hero">
''' + country_switch("ca") + '''
    <span class="eyebrow">Ten provinces · NRCan weekly survey</span>
    <h1>Diesel prices by province</h1>
    <div class="figure"><span class="n">{{fuel.national_diesel}}</span><span class="u">¢/L national</span><span class="d {{fuel.change_7d_class}}">{{fuel.change_7d}} · 7d</span></div>
    <div class="meta"><span>Survey print <b>{{fuel.print_date}}</b></span><span>30-day <b>{{fuel.change_30d}}</b></span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
''' + rail() + chart_block() + cite() + '''
    <div class="stats">
      <div class="stat"><div class="l">Cheapest</div><div class="v down">{{fuel.low}}</div><div class="s">{{fuel.low_code}} · ¢/L</div></div>
      <div class="stat"><div class="l">Dearest</div><div class="v up">{{fuel.high}}</div><div class="s">{{fuel.high_code}} · ¢/L</div></div>
      <div class="stat"><div class="l">Spread</div><div class="v">{{fuel.spread}}</div><div class="s">{{fuel.low_code}} to {{fuel.high_code}}</div></div>
      <div class="stat"><div class="l">30-day move</div><div class="v">{{fuel.change_30d}}</div><div class="s">¢/L</div></div>
    </div>
  </section>
''' + sponsor("sponsor_fuel") + '''
  <section class="sec">
    <div class="lead"><h2>Every province</h2><p>Price, weekly change, and distance from the national index.</p></div>
    <div class="viz-grid">
      <div class="viz-card">
        <h3 class="viz-title">Price by province</h3>
        <p class="viz-sub">Cents per litre &middot; dashed line is the national average</p>
        {{diesel_spread_svg}}
      </div>
      <div class="viz-card">
        <h3 class="viz-title">This week&rsquo;s moves</h3>
        <p class="viz-sub">Weekly change in cents per litre &middot; red up, green down</p>
        {{diesel_change_svg}}
      </div>
    </div>
    <div class="rows">
    <!--LOOP:provinces--><div class="r"><span class="k">{{name}}<small>{{code}}</small></span><span class="v">{{price}} &nbsp; <span class="{{change_class}}">{{change}}</span> &nbsp; <span class="{{vs_class}}">{{vs_national}}</span></span></div><!--/LOOP:provinces-->
    </div>
    <p class="note">Prices include all federal and provincial fuel, carbon, and sales taxes. Yukon and the Northwest Territories are surveyed but excluded from the index; the reasoning is on the <a href="/methodology/nmdi/">methodology page</a>.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>North American diesel</h2><p>The cross-border index, and the gap Canadian carriers watch.</p></div>
    <div class="stats">
      <div class="stat"><div class="l">North American index</div><div class="v">{{eia.nadi}}</div><div class="s">¢/L · <span class="{{eia.nadi_change_7d_class}}">{{eia.nadi_change_7d}} 7d</span></div></div>
      <div class="stat"><div class="l">US national</div><div class="v">{{eia.us_national_cpl}}</div><div class="s">¢/L · <span class="{{eia.us_change_7d_class}}">{{eia.us_change_7d}} 7d</span> · ${{eia.us_national_usd_gal}}/gal</div></div>
      <div class="stat"><div class="l">Canada vs US</div><div class="v">{{eia.ca_us_gap}}</div><div class="s">¢/L · {{eia.gap_word}}</div></div>
    </div>
    <div class="rows">
    <!--LOOP:eia.padds_list--><div class="r"><span class="k">{{label}}<small>US PADD region</small></span><span class="v">{{cpl}} ¢/L · ${{usd_gal}}/gal</span></div><!--/LOOP:eia.padds_list-->
    </div>
    <p class="note">US figures are the EIA weekly retail diesel survey (ultra-low sulfur, on-highway), converted from USD per gallon at the Bank of Canada rate ({{fx.usd_cad}}). The North American index is the mean of the Canadian NMDI and the US national average — each country counts once. <a href="/methodology/nmdi/">Methodology</a></p>
  </section>

  <section class="sec">
    <div class="lead"><h2>By province, in depth</h2><p>Why each province prices the way it does.</p></div>
    <div class="rows">
      <a class="r" href="/diesel-prices/ontario/"><span class="k">Ontario<small>19 survey cities · widest spread</small></span><span class="v">→</span></a>
      <a class="r" href="/diesel-prices/alberta/"><span class="k">Alberta<small>Consistently the cheapest province</small></span><span class="v">→</span></a>
    </div>
  </section>
''' + subscribe("Diesel, dated and delivered",
   "Where prices moved this week, what the border looked like, and what it means for cost per kilometre. One email on Wednesday mornings, every figure linked back to this page.") + '''
  <section class="sec">
    <div class="lead"><h2>What moves these numbers</h2><p>Three things account for most of the gap between provinces.</p></div>
    <div class="two">
      <div><div class="rows">
        <div class="r"><span class="k">Provincial fuel tax<small>Set independently by each province</small></span><span class="v">Varies</span></div>
        <div class="r"><span class="k">Carbon pricing<small>Included in every price shown</small></span><span class="v">Included</span></div>
        <div class="r"><span class="k">Distance from supply<small>Northern and island markets carry haul cost</small></span><span class="v">Varies</span></div>
      </div></div>
      <div class="reading">
        <p class="note" style="margin-top:0">Diesel moves once a week, when NRCan publishes a new retail survey. Between prints this figure holds steady. It is a retail survey average, not a rack price, and not what a fleet on a fuel card pays.</p>
        <p class="note">The {{fuel.spread}}¢/L gap between {{fuel.low_code}} and {{fuel.high_code}} is a real difference on a 500-litre fill. <a href="/fuel-cost-calculator/">Work out a trip</a></p>
      </div>
    </div>
  </section>
''' + foot(CHART_SCRIPT))

# ═══ Calculator ═══════════════════════════════════════════════════════
calc_ld = ('{"@context":"https://schema.org","@graph":[' + crumb("Fuel cost calculator","/fuel-cost-calculator/") + ','
 '{"@type":"WebApplication","name":"Truck Fuel Cost Calculator","url":"' + BASE + '/fuel-cost-calculator/","applicationCategory":"BusinessApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":"0","priceCurrency":"CAD"},"creator":{"@id":"' + ORG_URL + '/#org"},"description":"Calculates trip diesel cost from distance, fuel consumption, and current Canadian provincial diesel prices."},'
 '{"@type":"FAQPage","mainEntity":['
 '{"@type":"Question","name":"How do you calculate truck fuel cost per kilometre?","acceptedAnswer":{"@type":"Answer","text":"Multiply your fuel consumption in litres per 100 kilometres by the diesel price per litre, then divide by 100. At 35 litres per 100 kilometres and diesel at 2.00 dollars per litre, that is 70 cents per kilometre."}},'
 '{"@type":"Question","name":"What fuel consumption should I use for a loaded tractor-trailer?","acceptedAnswer":{"@type":"Answer","text":"Use your own figure from your own fuel records. Consumption varies widely with load weight, terrain, season, speed, and equipment, so any single assumed number would be wrong for most operators. This calculator does not assume one."}}]}]}')

CALCJS = '''<script>
(function(){"use strict";var $=function(i){return document.getElementById(i);};
var dist=$("dist"),burn=$("burn"),prov=$("prov"),custom=$("custom"),wrap=$("customwrap"),opcost=$("opcost");
function money(v){return "$"+v.toLocaleString("en-CA",{minimumFractionDigits:2,maximumFractionDigits:2});}
function calc(){var isC=prov.value==="custom";wrap.hidden=!isC;
var cents=parseFloat(isC?custom.value:prov.value),d=parseFloat(dist.value),b=parseFloat(burn.value),op=parseFloat(opcost.value)||0;
if(!isFinite(cents)||!isFinite(d)||!isFinite(b)||d<=0||b<=0||cents<=0){["rTotal","rLitres","rPerKm","rPerMi","rPrice","rOpMi","rFloor"].forEach(function(i){$(i).textContent="\\u2014";});return;}
var litres=d/100*b,total=litres*(cents/100),perMi=total/d*1.609344,floor=perMi+op;
$("rLitres").textContent=litres.toLocaleString("en-CA",{maximumFractionDigits:1})+" L";
$("rTotal").textContent=money(total);$("rPerKm").textContent=money(total/d)+" /km";
$("rPerMi").textContent=money(perMi)+" /mi";
$("rOpMi").textContent=money(op)+" /mi";
$("rFloor").textContent=money(floor)+" /mi";
var o=prov.options[prov.selectedIndex];
$("rPrice").textContent=cents.toFixed(1)+"\\u00a2/L \\u00b7 "+(isC?"your price":o.getAttribute("data-name"));}
[dist,burn,prov,custom,opcost].forEach(function(el){el.addEventListener("input",calc);el.addEventListener("change",calc);});
calc();})();
</script>
'''

write("fuel-cost-calculator",
 head("Truck Fuel Cost Calculator (Canada) — Rate Floor + Trip Cost | Northern Mile",
      "Work out your rate floor and trip fuel cost using current Canadian prices. Set fuel consumption and fixed operating cost, pick a province, and see cost per trip, per mile, and the minimum rate you should charge. Prices from the NRCan weekly survey, print {{fuel.print_date}}.",
      "/fuel-cost-calculator/", "og.jpg", calc_ld)
 + '''
  <section class="hero">
    <span class="eyebrow">Prices from NRCan survey print {{fuel.print_date}}</span>
    <h1>Truck fuel cost calculator</h1>
    <p class="stand">What a run costs in diesel, using this week's Canadian prices and your own consumption figure. Change any field and the result updates.</p>
  </section>

  <div class="calc">
    <div>
      <div class="fld"><label for="dist">Distance</label><div class="inp"><input id="dist" type="number" inputmode="decimal" min="0" step="1" value="500"><span class="unit">km</span></div></div>
      <div class="fld"><label for="burn">Fuel consumption</label><div class="inp"><input id="burn" type="number" inputmode="decimal" min="0" step="0.1" value="35"><span class="unit">L/100km</span></div><p class="hint">Use your own number from your own fuel records. We do not assume one for you.</p></div>
      <div class="fld"><label for="prov">Fuel price</label><div class="inp"><select id="prov">
        <option value="{{fuel.national_diesel}}" data-name="National average">National average — {{fuel.national_diesel}}¢/L</option>
        <!--LOOP:provinces--><option value="{{price}}" data-name="{{name}}">{{name}} — {{price}}¢/L</option><!--/LOOP:provinces-->
        <option value="custom" data-name="Custom">Enter my own price</option>
      </select></div></div>
      <div class="fld" id="customwrap" hidden><label for="custom">Your price</label><div class="inp"><input id="custom" type="number" inputmode="decimal" min="0" step="0.1" value="{{fuel.national_diesel}}"><span class="unit">¢/L</span></div><p class="hint">If you run a fuel card, your real cost is usually below the retail survey average. Use the card price.</p></div>
      <div class="fld"><label for="opcost">Fixed operating cost</label><div class="inp"><input id="opcost" type="number" inputmode="decimal" min="0" step="0.01" value="1.85"><span class="unit">$/mi</span></div><p class="hint">Truck payment, insurance, driver pay, maintenance — your all-in cost per mile before fuel. Pull it from your own books.</p></div>
    </div>
    <div class="out">
      <div class="big"><div class="ol">Rate floor</div><div class="ov" id="rFloor">—</div></div>
      <div class="rows">
        <div class="r"><span class="k">Fuel per mile</span><span class="v" id="rPerMi">—</span></div>
        <div class="r"><span class="k">Operating per mile</span><span class="v" id="rOpMi">—</span></div>
        <div class="r"><span class="k">Trip fuel cost</span><span class="v" id="rTotal">—</span></div>
        <div class="r"><span class="k">Litres burned</span><span class="v" id="rLitres">—</span></div>
        <div class="r"><span class="k">Cost per kilometre</span><span class="v" id="rPerKm">—</span></div>
        <div class="r"><span class="k">Price used</span><span class="v" id="rPrice">—</span></div>
      </div>
      <p class="note">Rate floor = fuel per mile + your fixed operating cost per mile. Below this number, the load loses money. Excludes tolls and deadhead. <a href="/fuel-prices/">See prices by province</a></p>
    </div>
  </div>
''' + sponsor("sponsor_calc") + subscribe("Know before you fill",
   "Where diesel moved this week, which crossings backed up, and what it does to cost per kilometre. One email on Wednesday mornings.") + '''
  <section class="sec">
    <div class="lead"><h2>How this is worked out</h2><p>Plain arithmetic, no hidden assumptions.</p></div>
    <div class="two">
      <div><div class="rows">
        <div class="r"><span class="k">Litres burned<small>distance ÷ 100 × consumption</small></span><span class="v">L</span></div>
        <div class="r"><span class="k">Trip cost<small>litres × price per litre</small></span><span class="v">$</span></div>
        <div class="r"><span class="k">Cost per kilometre<small>trip cost ÷ distance</small></span><span class="v">$/km</span></div>
        <div class="r"><span class="k">Rate floor<small>fuel per mile + operating per mile</small></span><span class="v">$/mi</span></div>
      </div></div>
      <div class="reading">
        <p class="note" style="margin-top:0">The prices offered are retail survey averages from NRCan, inclusive of all taxes. They are not rack prices and not what a fleet on a fuel card pays, which is usually lower. If you know your card price, enter it.</p>
        <p class="note">Consumption is the field that changes the answer most, and it is the one we refuse to guess at. Pull the figure from your own records rather than accepting a number off a website.</p>
      </div>
    </div>
  </section>
''' + foot(CALCJS))

# ═══ Border ═══════════════════════════════════════════════════════════
write("border-wait-times",
 head("Canada-US Commercial Border Wait Times | Northern Mile",
      "Live commercial lane wait times at Canada-US border crossings, from the CBSA feed. Each figure carries CBSA's own capture time for that crossing.",
      "/border-wait-times/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Border wait times","/border-wait-times/") + ','
      '{"@type":"Dataset","name":"Canada-US Commercial Border Wait Times","description":"Commercial lane wait times at Canada-United States border crossings, from the Canada Border Services Agency feed.","url":"' + BASE + '/border-wait-times/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">CBSA commercial lanes</span>
    <h1>Border wait times</h1>
    <p class="stand">Commercial lane waits at Canada-US crossings, polled every 30 minutes. Each time shown is CBSA's own capture time for that crossing, not our fetch time, so it reflects how current their data is.</p>
    <div class="meta"><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <div class="rows">
  <!--LOOP:crossings--><a class="r" href="/border-wait-times/{{slug}}/"><span class="k">{{name}}<small>{{sub}}</small></span><span class="v">{{wait}} &nbsp; <span class="{{status_class}}">{{status_label}}</span></span></a><!--/LOOP:crossings-->
  </div>
  <p class="note">Source: Canada Border Services Agency commercial lane feed. Waits change quickly and a figure thirty minutes old may not describe the queue you arrive at.</p>
''' + sponsor("sponsor_border") + subscribe("Border and diesel, weekly",
   "Which crossings backed up, where diesel moved, and what both did to cost per kilometre. One email on Wednesday mornings.") + '''
  <section class="sec">
    <div class="lead"><h2>Reading these numbers</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">These are commercial lane figures, not passenger lanes. A crossing showing a short wait can still be slow for a specific load if secondary inspection is busy, and the feed carries no visibility into that.</p>
      <p class="note">We publish CBSA's capture time rather than our own so you can judge staleness yourself. If a crossing has not reported recently, that shows in the timestamp.</p>
    </div>
  </section>
''' + foot())

# ═══ Exchange ═════════════════════════════════════════════════════════
write("exchange-rate",
 head("USD/CAD Exchange Rate for Carriers — {{fx.usd_cad}} | Northern Mile",
      "The Bank of Canada daily USD/CAD observation at {{fx.usd_cad}}, published for Canadian carriers running cross-border freight and settling fuel in two currencies.",
      "/exchange-rate/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("USD/CAD exchange rate","/exchange-rate/") + ','
      '{"@type":"Dataset","name":"USD/CAD Exchange Rate for Canadian Carriers","description":"The Bank of Canada daily USD/CAD observation, published alongside Canadian diesel prices for carriers running cross-border freight.","url":"' + BASE + '/exchange-rate/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Bank of Canada daily observation</span>
    <h1>USD / CAD</h1>
    <div class="figure"><span class="n">{{fx.usd_cad}}</span><span class="u">CAD per USD</span><span class="d {{fx.direction}}">{{fx.change}}</span></div>
    <div class="meta"><span>Bank of Canada</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
    <div class="cite"><div class="cl">What this is</div><q>The Bank of Canada publishes one USD/CAD observation per business day. It is not a continuous market rate and it is not the rate your bank will give you. It is the reference figure, and it is the one worth quoting.</q></div>
  </section>
''' + sponsor("sponsor_fx") + '''
  <section class="sec">
    <div class="lead"><h2>Where today sits</h2><p>Today against the past 52 weeks.</p></div>
    <div class="viz-card">
      <h3 class="viz-title">52-week range</h3>
      <p class="viz-sub">CAD per US dollar · today is {{fx.range_pct}} of the way from the low to the high</p>
      {{fx_range_gauge_svg}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>The past year</h2><p>Daily observations, with a 30-day moving average.</p></div>
    <div class="viz-grid">
      <div class="viz-card" style="grid-column: 1 / -1">
        <h3 class="viz-title">USD / CAD</h3>
        <p class="viz-sub">Thin line is the daily observation · bold line is the 30-day trend</p>
        {{fx_line_svg}}
      </div>
      <div class="viz-card">
        <h3 class="viz-title">Where the year clustered</h3>
        <p class="viz-sub">Trading days at each rate · green is today&rsquo;s bucket</p>
        {{fx_histogram_svg}}
      </div>
      <div class="viz-card">
        <h3 class="viz-title">Recent moves</h3>
        <p class="viz-sub">Per cent change · green stronger CAD, red weaker</p>
        {{fx_change_bars_svg}}
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>How big a deal</h2><p>Today&rsquo;s move on the noise-to-alert scale.</p></div>
    <div class="viz-card">
      <h3 class="viz-title">Move band</h3>
      <p class="viz-sub">Today&rsquo;s change is {{fx.band_pct}} — a {{fx.band}} move</p>
      {{fx_band_scale_svg}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>What the rate means for your money</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">At {{fx.usd_cad}}, one US dollar buys {{fx.usd_cad}} Canadian dollars.</p>
      <div class="rows">
        <div class="r"><span class="k">US$100</span><span class="v">C${{fx.usd_100}}</span></div>
        <div class="r"><span class="k">US$500</span><span class="v">C${{fx.usd_500}}</span></div>
        <div class="r"><span class="k">US$1,000</span><span class="v">C${{fx.usd_1000}}</span></div>
        <div class="r"><span class="k">C$1,000</span><span class="v">US${{fx.cad_1000}}</span></div>
      </div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Why a diesel dashboard publishes a currency</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">A Canadian carrier running into the United States buys fuel in two currencies and gets paid in one. A cent on the exchange rate moves the cost of a US fill as surely as a cent on the pump price does, and the two rarely move together.</p>
      <p class="note">This page carries the Bank of Canada observation and its date. We publish the observation date rather than the fetch time because they are different things, and conflating them once put a six-week-old rate on this dashboard for thirty days. That correction is documented on the <a href="/methodology/nmdi/">methodology page</a>.</p>
    </div>
  </section>
''' + subscribe("Diesel, the border, and the dollar",
   "The three costs that move a Canadian carrier's week, dated and linked. One email on Wednesday mornings.") + foot())

# ═══ Market ═══════════════════════════════════════════════════════════
write("market-pulse",
 head("Canadian Freight Market Pulse | Northern Mile",
      "Freight demand and cost signals for Canadian carriers, alongside diesel at {{current_diesel}}¢/L and USD/CAD at {{usd_cad}}.",
      "/market-pulse/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Market pulse","/market-pulse/") + ']}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Freight demand signals</span>
    <h1>Market pulse</h1>
    <p class="stand">{{direction_summary}}</p>
    <div class="meta"><span>Diesel <b>{{current_diesel}}</b>¢/L</span><span>USD/CAD <b>{{usd_cad}}</b></span><span>Fuel <b>{{fuel_pct_of_ops}}</b> of operating cost</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <div class="rows">
  <!--LOOP:market--><div class="r"><span class="k">{{name}}<small>{{note}}</small></span><span class="v {{value_class}}">{{value}}</span></div><!--/LOOP:market-->
  </div>
  <p class="note">These indicators mix cost signals and demand signals, which move in opposite directions for a carrier. A rising number is not automatically good news and we do not colour them as though it were.</p>
''' + sponsor("sponsor_market") + subscribe("What moved, and what it cost",
   "Diesel, the border, freight demand, and one argument worth your time. Wednesday mornings.") + foot())

# ═══ News ═════════════════════════════════════════════════════════════
write("industry-news",
 head("Canadian Trucking Industry News | Northern Mile",
      "Headlines we are reading in Canadian trucking and freight, alongside live diesel prices and border wait times.",
      "/industry-news/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Industry news","/industry-news/") + ']}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Headlines we are reading</span>
    <h1>Industry news</h1>
    <p class="stand">Links out to the outlets doing the reporting. We do not rewrite their work, and every headline goes to the original.</p>
    <div class="meta"><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <div class="links-list">
  <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">{{category}}</span>{{headline}}</a><!--/LOOP:news-->
  </div>
  <p class="note">Collected from Canadian trucking and logistics trade feeds. An empty or short list means the feeds were quiet, not that nothing happened.</p>
''' + sponsor("sponsor_news") + subscribe("The week in one email",
   "The numbers that moved and the stories behind them, with every figure dated. Wednesday mornings.") + foot())

print("standard pages done")

# ═══ Road incidents ═══════════════════════════════════════════════════
# The map keeps its inline init and Leaflet CDN, but marker colours, the detail
# panel, and old classes are ported to nm.css tokens. Detail opens INLINE below
# the map, not as a fixed overlay. incidents_json is inserted raw by the build.
INCIDENTS_HEAD = ('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">')

INCIDENTS_MAP = '''
  <section class="hero">
    <span class="eyebrow">Freight corridor closures</span>
    <h1>Road incidents</h1>
    <p class="stand">Closures and major collisions on the freight corridors we monitor. Click a pin or a row for detail.</p>
    <div class="meta"><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>
'''

INCIDENTS_BODY = '''
  <div id="map" class="incmap" hidden></div>
  <div class="panel-list" id="incList" hidden></div>
'''

INCIDENTS_ROADWORK = '''
  <section class="sec">
    <div class="lead"><h2>Scheduled roadwork</h2><p>Planned lane reductions on monitored corridors.</p></div>
    <div id="rwmap" class="incmap" hidden></div>
    <div class="panel-list" id="rwList" hidden></div>
  </section>
'''

INCIDENTS_VIZ = '''
  <section class="sec">
    <div class="lead"><h2>Today on the corridors</h2><p>Where incidents sit, and how much of the disruption is planned versus unplanned.</p></div>
    <div class="viz-grid">
      <div class="viz-card">
        <h3 class="viz-title">Active vs scheduled</h3>
        <p class="viz-sub">Unplanned incidents (amber) vs planned roadwork (blue)</p>
        {{disruption_donut_svg}}
      </div>
      <div class="viz-card">
        <h3 class="viz-title">Incidents by corridor</h3>
        <p class="viz-sub">Busiest highways right now</p>
        {{corridor_svg}}
      </div>
    </div>
  </section>
'''

INCIDENTS_JS = '''<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>window.INCIDENTS = {{incidents_json}}; window.ROADWORK = {{roadwork_json}};</script>
<script>
(function(){
  var data = window.INCIDENTS || [];
  var mapEl = document.getElementById('map');
  var list = document.getElementById('incList');
  if(!mapEl) return;
  mapEl.hidden = false;
  if(list) list.hidden = false;

  var CLOSED = '#B3261E';   // red — closed, matches nm.css --up
  var HEAVY  = '#C8891A';   // amber — heavy, matches nm.css --amber
  var ACTIVE = '#0B5D3B';   // green — moderate/minor, matches nm.css --signal

  var map = L.map('map',{scrollWheelZoom:true}).setView([56.13,-106.35],4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'&copy; OpenStreetMap contributors', maxZoom:19
  }).addTo(map);

  if(!data.length){
    if(list) list.innerHTML = '<div class="empty"><b>Corridors clear</b>No major closures or collisions on monitored corridors.</div>';
    return;
  }

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  // The full detail lives in the marker popup, so clicking a list item and
  // clicking a pin both open the same rich detail on the map itself.
  function popupHtml(it){
    var p = ['<div class="ipop">'];
    p.push('<div class="ipop-h">'+esc(it.road)+(it.direction?' '+esc(it.direction):'')+'</div>');
    if(it.closed) p.push('<div class="ipop-closed">Road closed</div>');
    p.push('<div class="ipop-sev"><span class="pill '+esc(it.severity_class)+'">'+esc(it.severity_label)+'</span></div>');
    p.push('<div class="ipop-what">'+esc(it.what)+'</div>');
    var rows='';
    if(it.event_type) rows+='<div><span>Type</span>'+esc(it.event_type)+'</div>';
    if(it.lanes) rows+='<div><span>Lanes</span>'+esc(it.lanes)+'</div>';
    if(it.clearance) rows+='<div><span>Started</span>'+esc(it.clearance)+'</div>';
    if(it.end_time) rows+='<div><span>Until</span>'+esc(it.end_time)+'</div>';
    if(it.detour) rows+='<div><span>Detour</span>'+esc(it.detour)+'</div>';
    if(rows) p.push('<div class="ipop-rows">'+rows+'</div>');
    if(it.source_url) p.push('<a class="ipop-src" href="'+esc(it.source_url)+'" target="_blank" rel="noopener">View source report →</a>');
    p.push('</div>');
    return p.join('');
  }

  var markers = [];
  data.forEach(function(it){
    var color = it.severity_class === 'closed' ? CLOSED
              : (it.severity_class === 'heavy' ? HEAVY : ACTIVE);
    var m = L.circleMarker([it.lat, it.lng], {radius:8,color:color,fillColor:color,fillOpacity:.85,weight:2}).addTo(map);
    m.bindPopup(popupHtml(it), {maxWidth:280, className:'inc-popup'});
    markers.push(m);

    var row = document.createElement('div');
    row.className = 'inc';
    row.setAttribute('tabindex','0');
    row.setAttribute('role','button');
    var tline = '';
    if(it.clearance || it.end_time){
      tline = '<div class="inc-time">';
      if(it.clearance) tline += '<span class="t-lab">Started</span> ' + esc(it.clearance);
      if(it.end_time) tline += ' · <span class="t-lab">Until</span> ' + esc(it.end_time);
      tline += '</div>';
    }
    row.innerHTML = '<div class="h">'+esc(it.road)+(it.direction?' · '+esc(it.direction):'')+
      ' <span class="pill '+esc(it.severity_class)+'">'+esc(it.severity_label)+'</span></div>'+
      tline+
      '<div class="m">'+esc(it.what)+'</div>';

    function focus(){
      map.flyTo([it.lat, it.lng], 9, {duration:.6});
      map.once('moveend', function(){ m.openPopup(); });
      var prev = list.querySelector('.inc.active');
      if(prev) prev.classList.remove('active');
      row.classList.add('active');
      mapEl.scrollIntoView({behavior:'smooth', block:'nearest'});
    }
    row.addEventListener('click', focus);
    row.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); focus(); } });

    m.on('popupopen', function(){
      var prev = list.querySelector('.inc.active');
      if(prev) prev.classList.remove('active');
      row.classList.add('active');
    });

    if(list) list.appendChild(row);
  });

  var group = L.featureGroup(markers);
  try { map.fitBounds(group.getBounds().pad(0.2)); } catch(e){}
})();

(function(){
  var rw = window.ROADWORK || [];
  var rwMapEl = document.getElementById('rwmap');
  var rwList = document.getElementById('rwList');
  if(!rwMapEl) return;
  if(rwList) rwList.hidden = false;

  var RW_COLOR = '#1C6FE0';   // blue — planned roadwork, matches nm.css --focus

  if(!rw.length){
    if(rwList) rwList.innerHTML = '<div class="empty"><b>No scheduled roadwork</b>No planned lane reductions on monitored corridors.</div>';
    return;
  }

  function esc(s){ return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];}); }

  rwMapEl.hidden = false;
  var rwMap = L.map('rwmap',{scrollWheelZoom:true}).setView([56.13,-106.35],4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'&copy; OpenStreetMap contributors', maxZoom:19
  }).addTo(rwMap);

  var rwMarkers = [];
  rw.forEach(function(it){
    var m = L.circleMarker([it.lat, it.lng], {radius:7,color:RW_COLOR,fillColor:RW_COLOR,fillOpacity:.85,weight:2}).addTo(rwMap);
    var rows = '';
    if(it.when) rows += '<div><span>When</span>'+esc(it.when)+'</div>';
    if(it.lanes) rows += '<div><span>Lanes</span>'+esc(it.lanes)+'</div>';
    m.bindPopup('<div class="ipop"><div class="ipop-h">'+esc(it.road)+'</div><div class="ipop-what">'+esc(it.what)+'</div><div class="ipop-rows">'+rows+'</div></div>', {maxWidth:280, className:'inc-popup'});
    rwMarkers.push(m);

    var row = document.createElement('div');
    row.className = 'rw';
    row.setAttribute('tabindex','0');
    row.setAttribute('role','button');
    row.innerHTML = '<div class="rw-head"><span class="rw-road">'+esc(it.road)+'</span><span class="rw-when">'+esc(it.when)+(it.lanes?' · '+esc(it.lanes):'')+'</span></div><div class="rw-what">'+esc(it.what)+'</div>';

    function focus(){
      rwMap.flyTo([it.lat, it.lng], 9, {duration:.6});
      rwMap.once('moveend', function(){ m.openPopup(); });
      var prev = rwList.querySelector('.rw.active');
      if(prev) prev.classList.remove('active');
      row.classList.add('active');
      rwMapEl.scrollIntoView({behavior:'smooth', block:'nearest'});
    }
    row.addEventListener('click', focus);
    row.addEventListener('keydown', function(e){ if(e.key==='Enter'){ e.preventDefault(); focus(); } });
    m.on('popupopen', function(){
      var prev = rwList.querySelector('.rw.active');
      if(prev) prev.classList.remove('active');
      row.classList.add('active');
    });
    if(rwList) rwList.appendChild(row);
  });

  var group = L.featureGroup(rwMarkers);
  try { rwMap.fitBounds(group.getBounds().pad(0.2)); } catch(e){}
})();
</script>
'''

# Build incidents head with the extra leaflet stylesheet folded in.
_inc_head = head(
    "Canadian Freight Road Incidents & Closures | Northern Mile",
    "Live closures and major collisions on Canadian freight corridors, on an interactive map. Click any incident for detail and the source report.",
    "/road-incidents/", "og.jpg",
    '{"@context":"https://schema.org","@graph":[' + crumb("Road incidents","/road-incidents/") + ']}', "article")
_inc_head = _inc_head.replace('<link rel="stylesheet" href="/assets/nm.css',
    INCIDENTS_HEAD + '\n<link rel="stylesheet" href="/assets/nm.css')

write("road-incidents",
 _inc_head
 + INCIDENTS_MAP
 + INCIDENTS_VIZ
 + INCIDENTS_BODY
 + sponsor("sponsor_incidents")
 + INCIDENTS_ROADWORK
 + subscribe("Corridors and costs",
   "Which corridors closed, where diesel moved, and what it did to the week. One email on Wednesday mornings.")
 + foot(INCIDENTS_JS))

print("incidents done")

# ═══ Methodology ══════════════════════════════════════════════════════
# Prose ported verbatim from the live page. Sponsor slot deliberately omitted:
# this is the page that certifies neutrality.
METHOD_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("NMDI methodology","/methodology/nmdi/") + ','
 '{"@type":"Dataset","@id":"' + BASE + '/#nmdi","name":"Northern Mile Diesel Index (NMDI)","description":"Methodology, population, source, cadence, and revision history for the Northern Mile Diesel Index.","url":"' + BASE + '/methodology/nmdi/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true}]}')

write("methodology",
 head("NMDI Methodology — How the Northern Mile Diesel Index Is Calculated | Northern Mile",
      "Population, method, source, cadence, and the dated revision history of every correction published for the Northern Mile Diesel Index.",
      "/methodology/nmdi/", "og.jpg", METHOD_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">NMDI · Version 1.1 · effective 2026-08-05</span>
    <h1>How the index is calculated</h1>
    <p class="stand">The Northern Mile Diesel Index is a ten-province national diesel average. This page documents exactly how it is built, and every correction ever published against it.</p>
  </section>

  <section class="reading" style="max-width:720px">
    <h2>Population</h2>
    <p class="note" style="margin-top:8px">The NMDI is computed from ten provinces: British Columbia, Alberta, Saskatchewan, Manitoba, Ontario, Quebec, New Brunswick, Nova Scotia, Prince Edward Island, and Newfoundland and Labrador.</p>
    <p class="note">Yukon and the Northwest Territories are collected from the same NRCan survey and displayed on the fuel page. They are excluded from the national index because they carry negligible national freight volume and equal-weighting them distorts the figure. Territorial diesel is supplied off Edmonton and typically prices near Alberta, below the national mean, so the exclusion is the more conservative choice.</p>

    <h2 style="margin-top:32px">Method</h2>
    <p class="note" style="margin-top:8px">Each provincial figure is the unweighted arithmetic mean of NRCan survey city prices within that province. The number of survey cities varies by province. The national index is the unweighted mean of the ten provincial figures. It is not population-weighted or freight-weighted; every province counts equally.</p>
    <p class="note">An unweighted mean of provincial means is simpler to verify and harder to manipulate than a weighting scheme, and it changes only when diesel prices change, not when a weighting assumption changes.</p>

    <h2 style="margin-top:32px">North American Diesel Index</h2>
    <p class="note" style="margin-top:8px">The North American Diesel Index (NADI) combines the Canadian NMDI with the United States national on-highway diesel average. It is the simple arithmetic mean of the two — each country counts once, and the index is not consumption-weighted or freight-weighted.</p>
    <p class="note">The US figure is the U.S. Energy Information Administration weekly retail diesel survey (ultra-low sulfur, on-highway), published in US dollars per gallon. It is converted to Canadian cents per litre at the latest Bank of Canada USD/CAD rate, using 1 US gallon = 3.785411784 litres.</p>
    <p class="note">Equal-country weighting is the deliberate choice: it treats Canada and the United States as two markets rather than scaling by population or consumption, so the index does not collapse into a US price with a Canadian footnote. Canada is higher than the United States in every print since the index began, driven by carbon pricing and provincial fuel taxes.</p>

    <h2 style="margin-top:32px">Source</h2>
    <p class="note" style="margin-top:8px">Natural Resources Canada weekly diesel survey, RSS productID=5, collected by Kalibrate Technologies under contract to NRCan. All figures are inclusive of federal and provincial fuel taxes, carbon taxes, and sales taxes. The federal excise on diesel, normally 4 cents per litre, is suspended nationwide from 20 April to 7 September 2026 per Finance Canada and CBSA Customs Notice 26-11.</p>
    <p class="note">This dashboard contains information licensed under the <a href="https://open.canada.ca/en/open-government-licence-canada" rel="license">Open Government Licence – Canada</a>. Diesel prices originate with Natural Resources Canada.</p>

    <h2 style="margin-top:32px">Cadence</h2>
    <p class="note" style="margin-top:8px">NRCan surveys weekly. The dashboard rebuilds every 30 minutes from the most recent survey, so the diesel figure holds steady between prints and deltas step once a week. The exchange rate reflects the most recent Bank of Canada observation, which is business-daily. Border wait times come from the live CBSA feed, polled every 30 minutes; the timestamp shown is CBSA's capture time for that crossing, not our fetch time, so it reflects how current CBSA's own data is.</p>

    <h2 style="margin-top:32px">Revision history</h2>
    <p class="note" style="margin-top:8px"><b>2026-08-15</b> — Historical backfill. Weekly diesel prints from 2016 through the first live-collection date were reconstructed from Natural Resources Canada's annual city price tables, using the identical ten-province roll-up applied to live data. Prints from the first live-collection date onward come from live weekly collection. Both paths use the same NRCan source and the same method. Where NRCan revised a price after its first print, the reconstructed (revised) value is shown. For the 2026-08-11 print the provincial figures were revised by 0.1–0.9¢/L; the national index was unchanged at 222.2¢/L.</p>
    <p class="note"><b>2026-08-12</b> — Correction. The USD/CAD exchange rate published on this dashboard was incorrect from 2026-07-13, the site's first public deploy, through 2026-08-12. The Bank of Canada API returns observations newest first; the collector read them as oldest first and published the oldest observation as the current rate, with the day-over-day change inverted. At the time the error was found the dashboard displayed 1.4206, an observation dated 2026-06-29, when the correct current observation was 1.3927 dated 2026-08-11. The error affected the exchange rate module only. Diesel prices, the NMDI, and all provincial figures come from a separate source and were not affected. The collector now sorts observations by date, publishes the observation date alongside the rate, and fails loudly rather than falling back to a default when the fetch fails.</p>
    <p class="note"><b>2026-08-05</b> — Index moved from a 12-unit basis (including YT and NT) to a 10-unit basis (excluding territories). The national figure shifted from 224.8 to 228.3¢/L as a function of this methodology change. Values before this date are not directly comparable with later ones.</p>
    <p class="note"><b>2026-07-28</b> — Initial publication. 12-unit basis, unweighted mean of provincial means.</p>

    <h2 style="margin-top:32px">Corrections policy</h2>
    <p class="note" style="margin-top:8px">Errors in the underlying NRCan data are corrected when NRCan publishes a revision. Errors in computation are corrected immediately and logged above. A corrected figure is never retroactively substituted; the new value appears with the correction date and both values are recorded.</p>
    <p class="note" style="margin-top:24px">Questions: <a href="mailto:northernmilemedia@gmail.com">northernmilemedia@gmail.com</a></p>
  </section>
''' + foot())

print("methodology done")

# ═══ Press ═════════════════════════════════════════════════════════════
write("press",
 head("Press & Data — Citable Canadian Trucking Figures | Northern Mile",
      "For journalists: citable Canadian fuel, exchange-rate, and border-wait figures with sources and dates attached. Story angles, how to cite us, and press contact.",
      "/press/", "og.jpg",
      '{"@context":"https://***@graph":[' + crumb("Press & data", "/press/") + ',' +
      '{"@type":"WebPage","name":"Press & Data","description":"Citable Canadian trucking data for journalists, from Northern Mile Media.","url":"' + BASE + '/press/","creator":{"@id":"' + ORG_URL + '/#org"}}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">For journalists</span>
    <h1>Press &amp; data</h1>
    <p class="stand">Every figure we publish carries its source, its date, and a copy-paste citation. Use the numbers. Link the methodology. That is the whole arrangement.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>Story angles</h2><p>Numbers worth a headline, updated weekly.</p></div>
    <div class="rows">
      <div class="r"><span class="k">The Canada–US diesel gap<small>Canada vs the US national average, in cents per litre</small></span><span class="v">{{eia.ca_us_gap}}¢/L · {{eia.gap_word}}</span></div>
      <div class="r"><span class="k">North American Diesel Index<small>the mean of both countries — each counts once</small></span><span class="v">{{eia.nadi}}¢/L</span></div>
      <div class="r"><span class="k">National diesel, weekly move<small>NRCan weekly survey, ten provinces</small></span><span class="v">{{fuel.national_diesel}}¢/L · {{fuel.change_7d}} 7d</span></div>
      <div class="r"><span class="k">USD/CAD<small>Bank of Canada daily observation</small></span><span class="v">{{fx.usd_cad}}</span></div>
      <div class="r"><span class="k">Rate floor<small>fuel + fixed operating cost, per mile</small></span><span class="v"><a href="/fuel-cost-calculator/">Calculator</a></span></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>How to cite us</h2></div>
    <div class="cite">
      <div class="cl">Standard citation</div>
      <q id="citation">Northern Mile Diesel Index: {{fuel.national_diesel}}¢/L national average, ten provinces, NRCan weekly survey print {{fuel.print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/methodology/nmdi/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">Methodology</a></div>
    </div>
    <p class="note">Every figure on the dashboard carries its own citation in the same format. We name the primary source (Natural Resources Canada, Bank of Canada, CBSA, EIA) and the observation date — never an un-dated number.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>Contact</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">For data questions, chart embeds with attribution, or an advance look at the weekly figures:</p>
      <p class="note"><a href="mailto:northernmilemedia@gmail.com">northernmilemedia@gmail.com</a></p>
    </div>
  </section>
''' + subscribe("The weekly numbers, before they're news",
   "Where diesel moved, what the border looked like, and what the dollar did — every Wednesday morning. One email.") + foot())

# ═══ Province page template ═══════════════════════════════════════════
# One template, rendered per province by build_provinces.py. Uses the same shell.
# {{prose}} is the hand-written section; {{cities}} loops the survey cities.
PROV_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{name}} diesel prices","/diesel-prices/{{slug}}/") + ','
 '{"@type":"Dataset","name":"{{name}} Diesel Prices","description":"Retail diesel prices across {{city_count}} {{name}} survey cities, from the NRCan weekly survey.","url":"' + BASE + '/diesel-prices/{{slug}}/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"{{name}}, Canada"},"dateModified":"{{updated_iso}}"}]}')

prov_body = (
 head("{{name}} Diesel Prices — {{price}}¢/L | Northern Mile",
      "Diesel prices across {{city_count}} {{name}} survey cities, {{price}}¢/L provincial average, {{vs_national_abs}}¢ {{vs_national_word}} the national index. NRCan weekly survey, print {{print_date}}.",
      "/diesel-prices/{{slug}}/", "og-fuel.jpg", PROV_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">{{name}} · {{city_count}} survey cities</span>
    <h1>{{name}} diesel prices</h1>
    <div class="figure"><span class="n">{{price}}</span><span class="u">¢/L</span><span class="d {{vs_national_class}}">{{vs_national}} vs national</span></div>
    <div class="meta"><span>NRCan survey print <b>{{print_date}}</b></span><span>National index <b>{{national}}</b>¢/L</span></div>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">{{name}} diesel: {{price}}¢/L provincial average across {{city_count}} survey cities, NRCan weekly survey print {{print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/diesel-prices/{{slug}}/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Why {{name}} prices the way it does</h2></div>
    <div class="reading">
{{prose}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>{{name}} survey cities</h2><p>¢/L · distance from the provincial mean</p></div>
    <div class="rows">
    <!--LOOP:cities--><div class="r"><span class="k">{{city}}</span><span class="v">{{price}} &nbsp; <span class="{{vs_class}}">{{vs_prov}}</span></span></div><!--/LOOP:cities-->
    </div>
    <p class="note">Every price is an NRCan survey observation from the print dated {{print_date}}. The provincial figure is the unweighted mean of these {{city_count}} cities, the same figure that enters the <a href="/methodology/nmdi/">Northern Mile Diesel Index</a>. Prices include all federal and provincial fuel, carbon, and sales taxes.</p>
  </section>
''' + subscribe("{{name}} diesel, every week",
   "Where {{name}} diesel moved, what the border looked like, and what it means for cost per kilometre. One email on Wednesday mornings.")
 + '''
  <p class="note"><a href="/fuel-prices/">← All ten provinces</a></p>
''' + foot())

with open(os.path.join(OUT, "province.template.html"), "w") as f:
    f.write(prov_body)
print(f"  province                   {len(prov_body):6,} bytes")

# One template, rendered per city by build_city_pages.py. Same shell.
# {{prose}} is the writer-generated context section; {{siblings}} loops the
# other survey cities in the same province.
CITY_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{name}} diesel prices", "/diesel-prices/{{prov_slug}}/{{slug}}/") + ','
 '{"@type":"Dataset","name":"{{name}} Diesel Prices","description":"Retail diesel price in {{name}}, {{prov_name}}, from the NRCan weekly survey.","url":"' + BASE + '/diesel-prices/{{prov_slug}}/{{slug}}/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"{{name}}, {{prov_name}}, Canada"},"variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price","unitText":"Canadian cents per litre"},"dateModified":"{{updated_iso}}"}]}')

city_body = (
 head("{{name}} Diesel Price — {{price}}¢/L | Northern Mile",
      "{{name}} diesel is {{price}}¢/L this week, {{vs_national_abs}}¢ {{vs_national_word}} the national index. NRCan weekly survey, print {{print_date}}.",
      "/diesel-prices/{{prov_slug}}/{{slug}}/", "og-fuel.jpg", CITY_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">{{name}} · {{prov_name}}</span>
    <h1>{{name}} diesel prices</h1>
    <div class="figure"><span class="n">{{price}}</span><span class="u">¢/L</span><span class="d {{vs_national_class}}">{{vs_national}} vs national</span></div>
    <div class="meta"><span>NRCan survey print <b>{{print_date}}</b></span><span>{{prov_name}} average <b>{{prov_price}}</b>¢/L</span></div>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">{{name}} diesel: {{price}}¢/L, NRCan weekly survey print {{print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/diesel-prices/{{prov_slug}}/{{slug}}/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Why {{name}} prices the way it does</h2></div>
    <div class="reading">
{{prose}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>{{prov_name}} survey cities</h2><p>¢/L · distance from the provincial mean</p></div>
    <div class="rows">
    <!--LOOP:siblings--><div class="r"><span class="k">{{city}}</span><span class="v">{{price}} &nbsp; <span class="{{vs_class}}">{{vs_prov}}</span></span></div><!--/LOOP:siblings-->
    </div>
    <p class="note">Every price is an NRCan survey observation from the print dated {{print_date}}. The provincial figure is the unweighted mean of its survey cities, the same figure that enters the <a href="/methodology/nmdi/">Northern Mile Diesel Index</a>.</p>
  </section>
''' + subscribe("{{name}} diesel, every week",
   "Where {{name}} and the rest of {{prov_name}} moved, and what it means for cost per kilometre. One email on Wednesday mornings.")
 + '''
  <p class="note"><!--IF:has_province_page--><a href="/diesel-prices/{{prov_slug}}/">← {{prov_name}} overview</a> · <!--/IF:has_province_page--><a href="/fuel-prices/">All ten provinces</a></p>
''' + foot())

with open(os.path.join(OUT, "city.template.html"), "w") as f:
    f.write(city_body)
print(f"  city                      {len(city_body):6,} bytes")

# ═══ US diesel pages ════════════════════════════════════════════════════
# One overview template + one per-PADD template, rendered by build_us_pages.py.
US_LD = ('{"@context":"https://***@graph":[' + crumb("US diesel prices", "/us-diesel/") + ','
 '{"@type":"Dataset","name":"US Retail Diesel Prices","description":"US on-highway diesel, national average plus five PADD regions, from the U.S. Energy Information Administration weekly retail diesel survey, converted to Canadian cents per litre at the latest Bank of Canada rate.","url":"' + BASE + '/us-diesel/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}')

us_body = (
 head("US Diesel Prices — ${{eia.us_national_usd_gal}}/gal | Northern Mile",
      "US on-highway diesel, national average ${{eia.us_national_usd_gal}}/gal ({{eia.us_national_cpl}}¢/L CAD) plus five regional prices. EIA weekly retail diesel survey, converted at the latest Bank of Canada rate.",
      "/us-diesel/", "og.jpg", US_LD, "article")
 + '''
  <section class="hero">
''' + country_switch("us") + '''
    <span class="eyebrow">EIA weekly retail diesel survey · week {{eia.date}}</span>
    <h1>US diesel prices</h1>
    <div class="figure"><span class="n">{{eia.us_national_cpl}}</span><span class="u">¢/L CAD</span><span class="d flat">${{eia.us_national_usd_gal}}/gal</span></div>
    <div class="meta"><span>US national average</span><span>Converted at the latest Bank of Canada rate</span></div>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">US on-highway diesel: ${{eia.us_national_usd_gal}}/gal national average ({{eia.us_national_cpl}}¢/L CAD), EIA weekly retail diesel survey, week ending {{eia.date}}. Northern Mile Media, dashboard.northernmilemedia.com/us-diesel/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Five regions</h2><p>Petroleum Administration for Defense Districts · ¢/L CAD and $/gal</p></div>
    <div class="rows">
    <!--LOOP:padds--><a class="r" href="/us-diesel/{{key}}/"><span class="k">{{label}}</span><span class="v">{{cpl}}¢ &nbsp; <span class="flat">${{usd_gal}}/gal</span></span></a><!--/LOOP:padds-->
    </div>
    <p class="note">Each region is an EIA PADD — Petroleum Administration for Defense District. The price is that region&rsquo;s observation from the EIA weekly retail diesel survey, converted from US dollars per gallon at the latest Bank of Canada USD/CAD rate (1 US gallon = 3.785411784 L).</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>The North American index</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">The North American Diesel Index (NADI) is the mean of the Canadian national average and the US national average — each country counts once, not consumption-weighted. This week the NADI is <b>{{eia.nadi}}¢/L</b>, with Canada {{eia.gap_word}} by <b>{{eia.ca_us_gap}}¢/L</b>.</p>
      <p class="note">Methodology: <a href="/methodology/nmdi/">/methodology/nmdi/</a>. The Canadian half is the NRCan weekly survey (ten provinces); the US half is the EIA national average above.</p>
    </div>
  </section>
''' + subscribe("US and Canadian diesel, every week",
   "Where both sides of the border moved, and what it means for a cross-border carrier's week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-diesel.template.html"), "w") as f:
    f.write(us_body)
print(f"  us-diesel                 {len(us_body):6,} bytes")

# One template, rendered per PADD by build_us_pages.py.
USPADD_LD = ('{"@context":"https://***@graph":[' + crumb("{{label}} diesel prices", "/us-diesel/{{key}}/") + ','
 '{"@type":"Dataset","name":"{{label}} Diesel Prices","description":"US on-highway diesel price in {{label}}, from the EIA weekly retail diesel survey, converted to Canadian cents per litre.","url":"' + BASE + '/us-diesel/{{key}}/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}')

uspadd_body = (
 head("{{label}} Diesel Price — ${{usd_gal}}/gal | Northern Mile",
      "{{label}} diesel is ${{usd_gal}}/gal ({{cpl}}¢/L CAD), {{vs_national_abs}}¢ {{vs_national_word}} the US national average. EIA weekly retail diesel survey, week ending {{date}}.",
      "/us-diesel/{{key}}/", "og.jpg", USPADD_LD, "article")
 + '''
  <section class="hero">
''' + country_switch("us") + '''
    <span class="eyebrow">{{label}} · EIA week {{date}}</span>
    <h1>{{label}} diesel</h1>
    <div class="figure"><span class="n">{{cpl}}</span><span class="u">¢/L CAD</span><span class="d {{vs_national_class}}">{{vs_national}} vs US national</span></div>
    <div class="meta"><span>US national <b>{{national}}</b>¢/L</span><span>Converted at the latest Bank of Canada rate</span></div>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">{{label}} diesel: ${{usd_gal}}/gal ({{cpl}}¢/L CAD), EIA weekly retail diesel survey, week ending {{date}}. Northern Mile Media, dashboard.northernmilemedia.com/us-diesel/{{key}}/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>What {{label}} covers</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">{{states}}</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>The five regions</h2><p>¢/L CAD · $/gal</p></div>
    <div class="rows">
    <!--LOOP:siblings--><a class="r" href="/us-diesel/{{key}}/"><span class="k">{{label}}</span><span class="v">{{cpl}}¢ &nbsp; <span class="flat">${{usd_gal}}/gal</span></span></a><!--/LOOP:siblings-->
    </div>
    <p class="note"><a href="/us-diesel/">← US national and all regions</a></p>
  </section>
''' + subscribe("{{label}} diesel, every week",
   "Where {{label}} and the rest of North America moved, and what it means for a cross-border carrier's week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-padd.template.html"), "w") as f:
    f.write(uspadd_body)
print(f"  us-padd                  {len(uspadd_body):6,} bytes")

# One template, rendered per crossing by build_border_pages.py.
BORDER_LD = ('{"@context":"https://***@graph":[' + crumb("{{name}} border wait", "/border-wait-times/{{slug}}/") + ','
 '{"@type":"Dataset","name":"{{name}} Commercial Border Wait","description":"Commercial lane wait time at {{name}}, from the Canada Border Services Agency feed.","url":"' + BASE + '/border-wait-times/{{slug}}/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}')

border_body = (
 head("{{name}} Border Wait — {{wait}} | Northern Mile",
      "{{name}} commercial lane wait is {{wait}} ({{status_label}}) right now, from the CBSA feed. {{sub}}",
      "/border-wait-times/{{slug}}/", "og.jpg", BORDER_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">CBSA commercial lanes</span>
    <h1>{{name}}</h1>
    <div class="figure"><span class="n">{{wait}}</span><span class="u">wait</span><span class="d {{status_class}}">{{status_label}}</span></div>
    <div class="meta"><span>{{sub}}</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec">
    <div class="lead"><h2>About this crossing</h2></div>
    <div class="reading">
{{prose}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>All crossings</h2><p>commercial lane wait · CBSA</p></div>
    <div class="rows">
    <!--LOOP:siblings--><a class="r" href="/border-wait-times/{{slug}}/"><span class="k">{{name}}</span><span class="v">{{wait}} &nbsp; <span class="{{status_class}}">{{status_label}}</span></span></a><!--/LOOP:siblings-->
    </div>
    <p class="note"><a href="/border-wait-times/">← All border wait times</a></p>
  </section>
''' + subscribe("Border and diesel, weekly",
   "Which crossings backed up, where diesel moved, and what both did to cost per kilometre. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "border-crossing.template.html"), "w") as f:
    f.write(border_body)
print(f"  border-crossing           {len(border_body):6,} bytes")

print("\\nAll templates generated.")
