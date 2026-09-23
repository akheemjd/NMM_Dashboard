#!/usr/bin/env python3
"""Generate every dashboard template from one shell.

One header, one nav, one footer, written once. SEO scaffolding — canonical, OG,
JSON-LD, a single h1 — is part of the shell, so no page can ship without it. One
optional module sponsor slot per page, methodology excepted. Change this file,
regenerate, and all eleven pages move together.

Run: python3 scripts/gen_templates.py
"""

import json
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
    ("/freight-barometer/", "Barometer"),
    ("/fuel-prices/", "Diesel"),
    ("/fuel-cost-calculator/", "Calculator"),
    ("/border-wait-times/", "Border"),
    ("/fuel-tax-rates/", "Fuel tax"),
    ("/border-trends/", "Trends"),
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
  <a class="mark" href="/"><img class="logo" src="/assets/logo.png" width="32" height="32" alt=""><b>Northern Mile</b><span>North American trucking data</span></a>
</div></header>

<nav class="nav" aria-label="Sections"><div class="wrap">{nav_html(canon)}</div></nav>

<main class="wrap" id="main">
"""


def foot(extra_script=""):
    flinks = "".join(f'<a href="{h}">{l}</a>' for h, l in NAV if l != "Home")
    # Business and legal links live in a second footer row rather than in the
    # data nav, which should stay about data. Reachability matters: a page
    # nothing links to does not exist, and check_links.py enforces that.
    blinks = "".join(f'<a href="{h}">{l}</a>' for h, l in (
        ("/advertise/", "Advertise"), ("/contact/", "Contact"),
    ))
    year = datetime.date.today().year
    return f"""
</main>

<footer class="ft"><div class="wrap">
  <div class="brand"><a class="name" href="/">Northern Mile Media</a><span class="tag">live North American trucking data</span></div>
  <nav class="flinks" aria-label="Footer">{flinks}</nav>
  <nav class="flinks biz" aria-label="Company">{blinks}</nav>
  <div class="bottom"><span>&copy; {year} Northern Mile Media</span><a href="{SUB}" data-portal="signup">Subscribe free</a><span>Updated {{{{updated_at}}}} UTC</span></div>
</div></footer>

<script src="/assets/nm.js?v={{{{build_version}}}}"></script>
{extra_script}</body>
</html>
"""


def sponsor(key):
    """One optional module sponsor. Rendered only when data supplies the block.

    The eyebrow reads {{label}} from data rather than a hardcoded "Presented by",
    so an unsold slot can say "Sponsor slot" and a sold one "Presented by",
    without a template change.
    """
    return (f'\n  <!--OPTIONAL:{key}-->\n'
            f'  <aside class="sp"><span class="t">{{{{{key}.label}}}}</span>'
            f'<span class="n">{{{{{key}.name}}}}</span>'
            f'<span class="l">{{{{{key}.line}}}}</span>'
            f'<a class="c" href="{{{{{key}.url}}}}">Learn more</a></aside>\n'
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
      <!--LOOP:provinces--><a class="row" href="/diesel-prices/{{slug}}/"><span class="code">{{code}}</span><span class="track"><span class="fill" style="width:{{pct}}%"></span><span class="dot" style="left:{{pct}}%"></span></span><span class="val {{change_class}}">{{price}}</span></a><!--/LOOP:provinces-->
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
    """Two-level trail: Dashboard > name.

    The final crumb carries no 'item'. Google's breadcrumb guidance is that the
    last element is the current page and does not need a URL; all 160 trails on
    the site were emitting one.
    """
    return ('{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Dashboard","item":"' + BASE + '/"},'
            '{"@type":"ListItem","position":2,"name":"' + name + '"}]}')


def crumb3(mid_name, mid_slug, name):
    """Three-level trail: Dashboard > mid > name.

    A city page lives at /diesel-prices/<province>/<city>/, but the trail said
    Dashboard > City and skipped the province — so it described a hierarchy the
    URL does not have.
    """
    return ('{"@type":"BreadcrumbList","itemListElement":['
            '{"@type":"ListItem","position":1,"name":"Dashboard","item":"' + BASE + '/"},'
            '{"@type":"ListItem","position":2,"name":"' + mid_name + '","item":"' + BASE + mid_slug + '"},'
            '{"@type":"ListItem","position":3,"name":"' + name + '"}]}')


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
 head("Diesel Prices in Canada and the US — {{fuel.national_diesel}}¢/L Canada | Northern Mile",
      "The Northern Mile Diesel Index: {{fuel.national_diesel}}¢/L across ten Canadian provinces from the NRCan weekly survey, print {{fuel.print_date}}. Live commercial border wait times and the Bank of Canada exchange rate.",
      "/", "og.jpg", home_ld)
 + '''
  <section class="hero">
    <span class="eyebrow">Free cross-border trucking data · no account</span>
    <h1>Diesel prices in Canada and the US today</h1>
    <div class="figure"><span class="n">{{fuel.national_diesel}}</span><span class="u">¢/L</span><span class="d {{fuel.change_7d_class}}">{{fuel.change_7d}} · 7d</span></div>
    <p class="stand">At 35 L/100km that is <b>{{fuel.fuel_cost_per_km}} per km</b> — the fuel half of your rate floor. <a href="/fuel-cost-calculator/">Work out your lane's full floor</a></p>
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
        <p class="note">The {{fuel.spread}}¢/L gap between {{fuel.low_code}} and {{fuel.high_code}} is <b>${{fuel.spread_dollars_500l}}</b> on a 500-litre fill — fuel where it is cheap on your corridor. <a href="/fuel-cost-calculator/">Work out a trip</a></p>
      </div>
    </div>
  </section>
''' + foot(CHART_SCRIPT))

# ═══ Freight Barometer ═══════════════════════════════════════════════════
write("freight-barometer",
 head("Freight Barometer — This Week's Cross-Border Numbers | Northern Mile",
      "The weekly cross-border snapshot: Canadian diesel {{fuel.national_diesel}}¢/L, the North American index {{eia.nadi}}¢/L, USD/CAD {{fx.usd_cad}}, and the busiest border crossing. Every figure dated and sourced.",
      "/freight-barometer/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Freight barometer","/freight-barometer/") + ']}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Weekly snapshot · NRCan print {{fuel.print_date}}</span>
    <h1>Freight barometer</h1>
    <p class="stand">One screen of the numbers a cross-border carrier tracks every week — diesel, the North American index, the dollar, and the border — each dated and sourced.</p>
    <div class="meta"><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <div class="stats">
    <a class="stat" href="/methodology/nmdi/"><div class="l">Canadian diesel</div><div class="v">{{fuel.national_diesel}}</div><div class="s">¢/L · ten provinces · NRCan print {{fuel.print_date}}</div></a>
    <a class="stat" href="/fuel-prices/"><div class="l">North American index</div><div class="v">{{eia.nadi}}</div><div class="s">¢/L · CA + US, equal weight</div></a>
    <a class="stat" href="/exchange-rate/"><div class="l">USD / CAD</div><div class="v">{{fx.usd_cad}}</div><div class="s">{{fx.direction}} {{fx.change}} · Bank of Canada</div></a>
    <a class="stat" href="/border-wait-times/"><div class="l">Busiest crossing</div><div class="v">{{border.max_wait}}</div><div class="s">{{border.max_name}} · CBSA</div></a>
  </div>

  <section class="sec">
    <div class="lead"><h2>The week in one line</h2></div>
    <p class="stand">{{weekly_read}}</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>Cite this</h2></div>
    <p class="note"><q>Northern Mile freight barometer, {{updated_at}} UTC — Canadian diesel {{fuel.national_diesel}}¢/L, North American index {{eia.nadi}}¢/L, USD/CAD {{fx.usd_cad}}.</q> <a href="/methodology/nmdi/">Methodology</a> · <a href="/fuel-prices/">Prices by province</a></p>
  </section>
''' + sponsor("sponsor_market") + subscribe("The week in one email",
   "Diesel, the border, and one argument worth your time. Wednesday mornings.") + foot())

# ═══ Calculator ═══════════════════════════════════════════════════════
calc_ld = ('{"@context":"https://schema.org","@graph":[' + crumb("Fuel cost calculator","/fuel-cost-calculator/") + ','
 '{"@type":"WebApplication","name":"Truck Fuel Cost Calculator","url":"' + BASE + '/fuel-cost-calculator/","applicationCategory":"BusinessApplication","operatingSystem":"Any","offers":{"@type":"Offer","price":"0","priceCurrency":"CAD"},"creator":{"@id":"' + ORG_URL + '/#org"},"description":"Calculates trip diesel cost from distance, fuel consumption, and current Canadian provincial diesel prices."},'
 '{"@type":"FAQPage","mainEntity":['
 '{"@type":"Question","name":"How do you calculate truck fuel cost per kilometre?","acceptedAnswer":{"@type":"Answer","text":"Multiply your fuel consumption in litres per 100 kilometres by the diesel price per litre, then divide by 100. At 35 litres per 100 kilometres and diesel at 2.00 dollars per litre, that is 70 cents per kilometre."}},'
 '{"@type":"Question","name":"What fuel consumption should I use for a loaded tractor-trailer?","acceptedAnswer":{"@type":"Answer","text":"Use your own figure from your own fuel records. Consumption varies widely with load weight, terrain, season, speed, and equipment, so any single assumed number would be wrong for most operators. This calculator does not assume one."}}]}]}')

CITY_COORDS = {
 "Abbotsford": ("BC", 49.05, -122.33), "Barrie": ("ON", 44.39, -79.69),
 "Bathurst": ("NB", 47.62, -65.65), "Brandon": ("MB", 49.85, -99.96),
 "Brantford": ("ON", 43.14, -80.26), "Calgary": ("AB", 51.04, -114.07),
 "Campbellton": ("NB", 48.01, -66.67), "Charlottetown": ("PE", 46.24, -63.13),
 "Chicoutimi": ("QC", 48.43, -71.07), "Corner Brook": ("NL", 48.95, -57.95),
 "Drummondville": ("QC", 45.88, -72.48), "Edmonton": ("AB", 53.55, -113.49),
 "Edmundston": ("NB", 47.37, -68.33), "Fort St. John": ("BC", 56.25, -120.85),
 "Fredericton": ("NB", 45.96, -66.65), "Gander": ("NL", 48.95, -54.61),
 "Gaspé": ("QC", 48.83, -64.48), "Gatineau": ("QC", 45.48, -75.70),
 "Grand Falls": ("NB", 47.05, -67.74), "Grande Prairie": ("AB", 55.17, -118.80),
 "Guelph": ("ON", 43.54, -80.25), "Halifax": ("NS", 44.65, -63.58),
 "Hamilton": ("ON", 43.26, -79.87), "Kamloops": ("BC", 50.67, -120.34),
 "Kelowna": ("BC", 49.89, -119.50), "Kentville": ("NS", 45.08, -64.50),
 "Kingston": ("ON", 44.23, -76.49), "Kitchener": ("ON", 43.45, -80.49),
 "Labrador City": ("NL", 52.95, -66.91), "Lethbridge": ("AB", 49.69, -112.84),
 "Lloydminster": ("AB", 53.28, -110.01), "London": ("ON", 42.98, -81.24),
 "Miramichi": ("NB", 47.03, -65.47), "Moncton": ("NB", 46.09, -64.77),
 "Montreal": ("QC", 45.50, -73.57), "Moose Jaw": ("SK", 50.39, -105.53),
 "New Glasgow": ("NS", 45.59, -62.64), "North Bay": ("ON", 46.31, -79.46),
 "Oshawa": ("ON", 43.90, -78.87), "Ottawa": ("ON", 45.42, -75.70),
 "Peterborough": ("ON", 44.31, -78.32), "Prince Albert": ("SK", 53.20, -105.75),
 "Prince George": ("BC", 53.92, -122.75), "Quebec City": ("QC", 46.81, -71.21),
 "Red Deer": ("AB", 52.27, -113.81), "Regina": ("SK", 50.45, -104.62),
 "Rimouski": ("QC", 48.45, -68.53), "Saint John": ("NB", 45.27, -66.06),
 "Sarnia": ("ON", 42.97, -82.38), "Saskatoon": ("SK", 52.13, -106.67),
 "Sault Ste. Marie": ("ON", 46.52, -84.35), "Sherbrooke": ("QC", 45.40, -71.89),
 "St. Catharines": ("ON", 43.16, -79.24), "St. John's": ("NL", 47.56, -52.71),
 "Sudbury": ("ON", 46.49, -80.99), "Sussex": ("NB", 45.72, -65.51),
 "Sydney": ("NS", 46.14, -60.19), "Thunder Bay": ("ON", 48.38, -89.25),
 "Timmins": ("ON", 48.48, -81.33), "Toronto": ("ON", 43.65, -79.38),
 "Trois-Rivières": ("QC", 46.34, -72.58), "Truro": ("NS", 45.37, -63.28),
 "Val-d'Or": ("QC", 48.10, -77.78), "Vancouver": ("BC", 49.28, -123.12),
 "Victoria": ("BC", 48.43, -123.37), "Windsor": ("ON", 42.32, -83.04),
 "Winnipeg": ("MB", 49.90, -97.14), "Woodstock": ("NB", 46.15, -67.57),
 "Yarmouth": ("NS", 43.84, -66.12),
 # — US lanes (all keyed "US"; origin routes to the US national price) —
 "Atlanta": ("US", 33.75, -84.39), "Boston": ("US", 42.36, -71.06),
 "Buffalo": ("US", 42.89, -78.88), "Charlotte": ("US", 35.23, -80.84),
 "Chicago": ("US", 41.88, -87.63), "Cincinnati": ("US", 39.10, -84.51),
 "Cleveland": ("US", 41.50, -81.69), "Columbus": ("US", 39.96, -83.00),
 "Dallas": ("US", 32.78, -96.80), "Denver": ("US", 39.74, -104.99),
 "Detroit": ("US", 42.33, -83.05), "Fargo": ("US", 46.88, -96.79),
 "Grand Rapids": ("US", 42.96, -85.66), "Houston": ("US", 29.76, -95.37),
 "Indianapolis": ("US", 39.77, -86.16), "Kansas City": ("US", 39.10, -94.58),
 "Los Angeles": ("US", 34.05, -118.24), "Louisville": ("US", 38.25, -85.76),
 "Memphis": ("US", 35.15, -90.05), "Milwaukee": ("US", 43.04, -87.91),
 "Minneapolis": ("US", 44.98, -93.27), "Nashville": ("US", 36.16, -86.78),
 "New York": ("US", 40.71, -74.01), "Oklahoma City": ("US", 35.47, -97.52),
 "Omaha": ("US", 41.26, -95.93), "Phoenix": ("US", 33.45, -112.07),
 "Pittsburgh": ("US", 40.44, -79.99), "Portland": ("US", 45.52, -122.68),
 "Salt Lake City": ("US", 40.76, -111.89), "Seattle": ("US", 47.61, -122.33),
 "Spokane": ("US", 47.66, -117.43), "St. Louis": ("US", 38.63, -90.20),
 "Toledo": ("US", 41.65, -83.54),
}
_cities_js = json.dumps({n: {"p": p, "la": la, "ln": ln} for n, (p, la, ln) in CITY_COORDS.items()})

# US city → EIA PADD region, for precise fuel pricing.
# City -> the EIA district its STATE is priced in. Derived from the same
# STATE_PADD the state pages use, so the calculator and the state pages
# cannot disagree. Was a hand-written map to top-level PADDs, which put
# Los Angeles in West Coast (277.6 c/L) instead of California (307.1).
US_PADD = {
    "Los Angeles": "california",
    "Buffalo": "central_atlantic",
    "New York": "central_atlantic",
    "Pittsburgh": "central_atlantic",
    "Dallas": "gulf_coast",
    "Houston": "gulf_coast",
    "Atlanta": "lower_atlantic",
    "Charlotte": "lower_atlantic",
    "Chicago": "midwest",
    "Cincinnati": "midwest",
    "Cleveland": "midwest",
    "Columbus": "midwest",
    "Detroit": "midwest",
    "Fargo": "midwest",
    "Grand Rapids": "midwest",
    "Indianapolis": "midwest",
    "Kansas City": "midwest",
    "Louisville": "midwest",
    "Memphis": "midwest",
    "Milwaukee": "midwest",
    "Minneapolis": "midwest",
    "Nashville": "midwest",
    "Oklahoma City": "midwest",
    "Omaha": "midwest",
    "St. Louis": "midwest",
    "Toledo": "midwest",
    "Boston": "new_england",
    "Denver": "rocky_mountain",
    "Salt Lake City": "rocky_mountain",
    "Phoenix": "west_coast_ex_california",
    "Portland": "west_coast_ex_california",
    "Seattle": "west_coast_ex_california",
    "Spokane": "west_coast_ex_california",
}
# City name → airport code, for the precomputed road-distance matrix.
CITY_CODES = {
    "Vancouver": "YVR", "Calgary": "YYC", "Edmonton": "YEG", "Saskatoon": "YXE",
    "Regina": "YQR", "Winnipeg": "YWG", "Toronto": "YYZ", "Ottawa": "YOW",
    "Montreal": "YUL", "Quebec City": "YQB", "Moncton": "YQM", "Halifax": "YHZ",
    "St. John's": "YYT", "Seattle": "SEA", "Portland": "PDX", "Los Angeles": "LAX",
    "Dallas": "DFW", "Minneapolis": "MSP", "Chicago": "ORD", "Detroit": "DTW",
    "Buffalo": "BUF", "New York": "EWR", "Atlanta": "ATL",
}
_padd_js = json.dumps(US_PADD)
_codes_js = json.dumps(CITY_CODES)
with open(os.path.join(HERE, "..", "data", "distances.json")) as _df:
    _dist_js = json.dumps(json.load(_df).get("distances", {}))

CALCJS = '''<script>
(function(){"use strict";var $=function(i){return document.getElementById(i);};
var dist=$("dist"),burn=$("burn"),prov=$("prov"),custom=$("custom"),wrap=$("customwrap"),opcost=$("opcost"),origin=$("origin"),dest=$("dest");
var CITIES=__CITIES__;
var DISTANCES=__DIST__,US_PADD=__PADD__,CODES=__CODES__;
function fill(sel){var g={};Object.keys(CITIES).forEach(function(n){(g[CITIES[n].p]=g[CITIES[n].p]||[]).push(n);});Object.keys(g).sort().forEach(function(p){var og=document.createElement("optgroup");og.label=(p==="US"?"United States":p);g[p].sort().forEach(function(n){var o=document.createElement("option");o.value=n;o.textContent=n;og.appendChild(o);});sel.appendChild(og);});}
function hav(a,b){var R=6371,dLa=(b.la-a.la)*Math.PI/180,dLn=(b.ln-a.ln)*Math.PI/180,la1=a.la*Math.PI/180,la2=b.la*Math.PI/180;var h=Math.sin(dLa/2)*Math.sin(dLa/2)+Math.cos(la1)*Math.cos(la2)*Math.sin(dLn/2)*Math.sin(dLn/2);return 2*R*Math.asin(Math.sqrt(h));}
function lane(){var o=CITIES[origin.value],d=CITIES[dest.value];if(o&&d&&origin.value!==dest.value){var ca=CODES[origin.value],cb=CODES[dest.value],km=(ca&&cb)?(DISTANCES[ca+"-"+cb]||DISTANCES[cb+"-"+ca]||0):0;dist.value=km?km:Math.round(hav(o,d)*1.25);$("distHint").textContent="Auto: "+origin.value+" → "+dest.value+" = "+dist.value+" km";var t=(o.p==="US")?(US_PADD[origin.value]||"US"):o.p;for(var i=0;i<prov.options.length;i++){if(prov.options[i].getAttribute("data-code")===t){prov.value=prov.options[i].value;break;}}}calc();}
function money(v){return "$"+v.toLocaleString("en-CA",{minimumFractionDigits:2,maximumFractionDigits:2});}
// Emit a marked span instead of flat text so the currency toggle can
// re-render these. The calculator computes in CAD natively (every fuel
// option is a CAD cents/litre figure) and fx.js converts for display.
function fxs(v,unit){
  var t=(unit==='cpl')?(v.toFixed(1)+'¢/L'):('$'+v.toFixed(2));
  return '<span class="fx" data-c="CAD" data-u="'+unit+'" data-v="'+v.toFixed(unit==='cpl'?1:2)+'">'+t+'</span>';
}
function calc(){var isC=prov.value==="custom";wrap.hidden=!isC;
var cents=parseFloat(isC?custom.value:prov.value),d=parseFloat(dist.value),b=parseFloat(burn.value),op=parseFloat(opcost.value)||0;
if(!isFinite(cents)||!isFinite(d)||!isFinite(b)||d<=0||b<=0||cents<=0){["rTotal","rLitres","rPerKm","rPerMi","rPrice","rOpMi","rFloor"].forEach(function(i){$(i).textContent="\\u2014";});return;}
var litres=d/100*b,total=litres*(cents/100),perMi=total/d*1.609344,floor=perMi+op;
$("rLitres").textContent=litres.toLocaleString("en-CA",{maximumFractionDigits:1})+" L";
$("rTotal").innerHTML=fxs(total,"plain");
$("rPerKm").innerHTML=fxs(total/d,"plain")+" /km";
$("rPerMi").innerHTML=fxs(perMi,"plain")+" /mi";
$("rOpMi").innerHTML=fxs(op,"plain")+" /mi";
$("rFloor").innerHTML=fxs(floor,"plain")+" /mi";
var o=prov.options[prov.selectedIndex];
$("rPrice").innerHTML=fxs(cents,"cpl")+" · "+(isC?"your price":o.getAttribute("data-name"));
// calc() rebuilds its outputs as native-CAD spans, so ask the currency
// layer to render them. Must live inside calc(): at IIFE top level it ran
// once on load and every later recompute stayed in CAD.
if(window.NMFX&&window.NMFX.ready&&window.NMFX.ready()){try{window.NMFX.render();}catch(e){}}
}
[dist,burn,prov,custom,opcost].forEach(function(el){el.addEventListener("input",calc);el.addEventListener("change",calc);});
// fx.js calls this after the reader switches currency, so the results
// re-render in the new one. Without it the toggle would convert the static
// page and leave the calculator showing stale CAD.
window.NMCalcRefresh=calc;
origin.addEventListener("change",lane);dest.addEventListener("change",lane);dist.addEventListener("input",function(){if(origin.value&&dest.value)$("distHint").textContent="Manual distance — overrides the lane estimate.";});
fill(origin);fill(dest);
try{var sb=localStorage.getItem("nm_burn"),so=localStorage.getItem("nm_opcost");if(sb)burn.value=sb;if(so)opcost.value=so;}catch(e){}
[burn,opcost].forEach(function(el){el.addEventListener("input",function(){try{localStorage.setItem("nm_burn",burn.value);localStorage.setItem("nm_opcost",opcost.value);}catch(e){}});});
calc();})();
</script>
'''.replace("__CITIES__", _cities_js).replace("__DIST__", _dist_js).replace("__PADD__", _padd_js).replace("__CODES__", _codes_js)

write("fuel-cost-calculator",
 head("Truck Fuel Cost Calculator — Rate Floor + Trip Cost | Northern Mile",
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
      <div class="fld"><label for="origin">Lane</label><div class="lane"><div class="inp"><select id="origin"><option value="">From — pick a city</option></select></div><div class="inp"><select id="dest"><option value="">To — pick a city</option></select></div></div><p class="hint">Pick a Canadian or US lane and the distance and fuel price fill in automatically — real road distance where we have it, an estimate otherwise. US lanes use their EIA region price (excludes Canadian carbon tax).</p></div>
      <div class="fld"><label for="dist">Distance</label><div class="inp"><input id="dist" type="number" inputmode="decimal" min="0" step="1" value="500"><span class="unit">km</span></div><p class="hint" id="distHint">Pick a lane above and this fills in automatically — or type the distance you know.</p></div>
      <div class="fld"><label for="burn">Fuel consumption</label><div class="inp"><input id="burn" type="number" inputmode="decimal" min="0" step="0.1" value="35"><span class="unit">L/100km</span></div><p class="hint">Use your own number from your own fuel records. We do not assume one for you.</p></div>
      <div class="fld"><label for="prov">Fuel price</label><div class="inp"><select id="prov">
        <option value="{{fuel.national_diesel}}" data-name="National average">National average — {{fuel.national_diesel}}¢/L</option>
        <!--LOOP:provinces--><option value="{{price}}" data-name="{{name}}" data-code="{{code}}">{{name}} — {{price}}¢/L</option><!--/LOOP:provinces-->
        <option value="{{eia.us_national_cpl}}" data-name="US national average" data-code="US">US national average — {{eia.us_national_cpl}}¢/L</option>
        <!--LOOP:eia.padds_list--><option value="{{cpl}}" data-name="{{label}}" data-code="{{key}}">{{label}} — {{cpl}}¢/L</option><!--/LOOP:eia.padds_list-->
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
    <p class="stand">Busiest right now: <b>{{border.max_name}}</b> at <b>{{border.max_wait}}</b> — wait is idle time, and the faster crossing is usually the cheaper crossing. Polled every 30 minutes from CBSA's own capture times.</p>
    <div class="meta"><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <div class="rows">
  <!--LOOP:crossings--><a class="r" href="/border-wait-times/{{slug}}/"><span class="k">{{name}}<small>{{sub}}</small></span><span class="v">{{wait}} &nbsp; <span class="{{status_class}}">{{status_label}}</span></span></a><!--/LOOP:crossings-->
  </div>
  <p class="note">Source: Canada Border Services Agency commercial lane feed. Waits change quickly and a figure thirty minutes old may not describe the queue you arrive at.</p>
  <p class="note">Looking for the US-bound direction, or the Mexican border? We publish every port the US Customs and Border Protection feed carries — <a href="/border-wait-times/all-ports/">all 85 land border crossings</a>, including the commercial and FAST lanes.</p>
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
      "The Bank of Canada daily USD/CAD observation at {{fx.usd_cad}}, published for carriers running cross-border freight and settling fuel in two currencies.",
      "/exchange-rate/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("USD/CAD exchange rate","/exchange-rate/") + ','
      '{"@type":"Dataset","name":"USD/CAD Exchange Rate for Cross-Border Carriers","description":"The Bank of Canada daily USD/CAD observation, published alongside diesel prices on both sides of the border for carriers running cross-border freight.","url":"' + BASE + '/exchange-rate/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Bank of Canada daily observation</span>
    <h1>USD / CAD</h1>
    <div class="figure"><span class="n">{{fx.usd_cad}}</span><span class="u">CAD per USD</span><span class="d {{fx.direction}}">{{fx.change}}</span></div>
    <div class="meta"><span>Bank of Canada</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
    <div class="cite"><div class="cl">What this is</div><q>The Bank of Canada publishes one USD/CAD observation per business day. It is not a continuous market rate and it is not the rate your bank will give you. It is the reference figure, and it is the one worth quoting.</q></div>
    <p class="stand">A rising rate means a weaker loonie — US freight pays more in CAD, but US parts and equipment cost more. A falling rate is the reverse. <a href="/fuel-cost-calculator/">Work out what a lane costs</a></p>
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
 head("Freight Market Pulse | Northern Mile",
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

  <section class="sec">
    <div class="lead"><h2>The week in one line</h2></div>
    <p class="stand">{{weekly_read}}</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>What's ahead</h2></div>
    <p class="note">The federal diesel excise (4¢/L, suspended since 20 April) returns on <b>8 September 2026</b> — expect the national average to step up that week. Diesel prices update every Tuesday when NRCan publishes a new survey print.</p>
  </section>

  <div class="rows">
  <!--LOOP:market--><div class="r"><span class="k">{{name}}<small>{{what_it_means}} · {{source}}</small></span><span class="v {{value_class}}">{{value}}</span></div><!--/LOOP:market-->
  </div>
  <p class="note">These indicators mix cost signals and demand signals, which move in opposite directions for a carrier. A rising number is not automatically good news and we do not colour them as though it were. <a href="/methodology/nmdi/">How the numbers are sourced</a></p>
''' + sponsor("sponsor_market") + subscribe("What moved, and what it cost",
   "Diesel, the border, freight demand, and one argument worth your time. Wednesday mornings.") + foot())

# ═══ News ═════════════════════════════════════════════════════════════
write("industry-news",
 head("Trucking Industry News, Canada and the US | Northern Mile",
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
  <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">{{category}}</span>{{headline}}<small class="why">{{why}} · via {{source}}</small></a><!--/LOOP:news-->
  </div>
  <p class="note">Each headline links to the outlet that reported it — we do not rewrite their work. The "why it matters" line is our read on what it means for a Canadian carrier. An empty or short list means the feeds were quiet, not that nothing happened.</p>
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
    "Road Incidents & Closures, Canada and the US | Northern Mile",
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
    <p class="note">Yukon and the Northwest Territories are collected from the same NRCan survey and reported in the weekly brief, but they are not published as separate locations on the fuel page. They are excluded from the national index because they carry negligible national freight volume and equal-weighting them distorts the figure. Territorial diesel is supplied off Edmonton and typically lands near Alberta's price, below the national mean, so the exclusion is the more conservative choice.</p>

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
 head("Press & Data — Citable North American Trucking Figures | Northern Mile",
      "For journalists: citable Canadian fuel, exchange-rate, and border-wait figures with sources and dates attached. Story angles, how to cite us, and press contact.",
      "/press/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Press & data", "/press/") + ',' +
      '{"@type":"WebPage","name":"Press & Data","description":"Citable North American trucking data for journalists, from Northern Mile Media.","url":"' + BASE + '/press/","creator":{"@id":"' + ORG_URL + '/#org"}}]}', "article")
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
    <div class="lead"><h2>What drives {{name}} prices</h2></div>
    <div class="reading">
{{prose}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>{{name}} survey cities</h2><p>¢/L · distance from the provincial mean</p></div>
    <div class="rows">
    <!--LOOP:cities--><a class="r" href="/diesel-prices/{{slug}}/{{city_slug}}/"><span class="k">{{city}}</span><span class="v">{{price}} &nbsp; <span class="{{vs_class}}">{{vs_prov}}</span></span></a><!--/LOOP:cities-->
    </div>
    <p class="note">Every price is an NRCan survey observation from the print dated {{print_date}}. The provincial figure is the unweighted mean of these {{city_count}} cities, the same figure that enters the <a href="/methodology/nmdi/">Northern Mile Diesel Index</a>. Prices include all federal and provincial fuel, carbon, and sales taxes.</p>
  </section>
''' + subscribe("{{name}} diesel, every week",
   "Where {{name}} diesel moved, what the border looked like, and what it means for cost per kilometre. One email on Wednesday mornings.")
 + '''
  <p class="note"><a href="/fuel-prices/">← All ten provinces</a></p>
''' + foot())

write("advertise",
 head("Advertise — Reach North American Carriers | Northern Mile",
      "Sponsor the pages Canadian carriers check before they buy fuel. Founding rates for the first sponsors, with no audience number we cannot stand behind.",
      "/advertise/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Advertise", "/advertise/") + ',' +
      '{"@type":"WebPage","name":"Advertise","description":"Sponsorship and founding rates for Northern Mile Media.","url":"' + BASE + '/advertise/","creator":{"@id":"' + ORG_URL + '/#org"}}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">For sponsors</span>
    <h1>Advertise</h1>
    <p class="stand">Northern Mile reaches Canadian carriers, owner-operators and fleet managers at the moment they check fuel, border and currency data. The list is new and small. That is what a founding rate is for.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>Where you appear</h2><p>Four placements, sold separately. None of them are programmatic, and none of them follow a reader around the internet.</p></div>
    <div class="rows">
      <div class="r"><span class="k">The Northern Mile Brief<small>one email a week, every Wednesday, to the full list</small></span><span class="v">Weekly</span></div>
      <div class="r"><span class="k">Diesel pages<small>the page carriers open before they fill, plus every city and province page</small></span><span class="v">Placement</span></div>
      <div class="r"><span class="k">Tool pages<small>the fuel cost calculator and the rate floor, used to price an actual run</small></span><span class="v">Placement</span></div>
      <div class="r"><span class="k">Data pages<small>border wait times, exchange rate, market pulse, incidents</small></span><span class="v">Placement</span></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>What we will and will not say</h2></div>
    <div class="reading">
      <p>The Brief goes to a small number of inboxes today. We are not going to quote you a reach number we cannot stand behind, because the reason you would buy this is that our numbers are true. The same applies to ours.</p>
      <p>What we can tell you is exactly what you are buying: the placement, the page, the issue, and the date. Every figure on this site carries its source and its print date, and so does every invoice.</p>
      <p>We do not run popups, interstitials, auto-play video or retargeting. A sponsorship is one quiet block on a page a carrier chose to open.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Founding terms</h2><p>For the first sponsors, while the list is being built.</p></div>
    <div class="rows">
      <div class="r"><span class="k">Rate<small>agreed in writing before the first placement runs</small></span><span class="v">Fixed</span></div>
      <div class="r"><span class="k">Lock<small>the founding rate holds for twelve months, including while the list grows</small></span><span class="v">12 months</span></div>
      <div class="r"><span class="k">Position<small>your name on the page, labelled as a sponsor, never disguised as editorial</small></span><span class="v">Labelled</span></div>
      <div class="r"><span class="k">Reporting<small>sends, opens and clicks for any email placement, sent after each issue</small></span><span class="v">Per issue</span></div>
      <div class="r"><span class="k">Notice<small>cancel before the next issue and you are not billed for it</small></span><span class="v">One issue</span></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Who this suits</h2></div>
    <div class="reading">
      <p>Fuel cards, factoring, insurance, ELD and compliance software, load boards, and truck stop operators. Anything a Canadian carrier buys with the money it just saved on diesel.</p>
      <p>If you sell to carriers and you want to be the name they saw first, get in while the rate reflects that the list is young.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Talk to us</h2></div>
    <div class="reading">
      <p>Email <a href="mailto:northernmilemedia@gmail.com?subject=Sponsorship">northernmilemedia@gmail.com</a> with what you sell and which placement you are considering. You will get a reply from a person, and a rate you can hold us to.</p>
    </div>
  </section>
''' + foot())

write("contact",
 head("Contact | Northern Mile",
      "How to reach Northern Mile Media for sponsorship, data questions, corrections and press.",
      "/contact/", "og.jpg",
      '{"@context":"https://schema.org","@graph":[' + crumb("Contact", "/contact/") + ',' +
      '{"@type":"WebPage","name":"Contact","description":"Contact Northern Mile Media.","url":"' + BASE + '/contact/","creator":{"@id":"' + ORG_URL + '/#org"}}]}', "article")
 + '''
  <section class="hero">
    <span class="eyebrow">Contact</span>
    <h1>Get in touch</h1>
    <p class="stand">One address, read by a person. Say what you need and you will get an answer.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>Who to write to</h2></div>
    <div class="rows">
      <div class="r"><span class="k">Sponsorship<small>placements, founding rates, campaign dates</small></span><span class="v"><a href="mailto:northernmilemedia@gmail.com?subject=Sponsorship">Email</a></span></div>
      <div class="r"><span class="k">Corrections<small>if a figure is wrong, tell us. We correct at the next issue and say what changed</small></span><span class="v"><a href="mailto:northernmilemedia@gmail.com?subject=Correction">Email</a></span></div>
      <div class="r"><span class="k">Press and citable data<small>sources, dates, and a copy-paste citation for any figure</small></span><span class="v"><a href="/press/">/press/</a></span></div>
      <div class="r"><span class="k">How the numbers are built<small>every source, every method, every revision</small></span><span class="v"><a href="/methodology/nmdi/">/methodology/nmdi/</a></span></div>
    </div>
  </section>

  <section class="sec">
    <div class="reading">
      <p>Northern Mile Media is an independent Canadian publication. It is not owned by, funded by, or affiliated with any carrier, broker, fuel retailer or industry association. Nobody pays for a number on this site.</p>
    </div>
  </section>
''' + foot())

with open(os.path.join(OUT, "province.template.html"), "w") as f:
    f.write(prov_body)
print(f"  province                   {len(prov_body):6,} bytes")

# One template, rendered per city by build_city_pages.py. Same shell.
# {{prose}} is the writer-generated context section; {{siblings}} loops the
# other survey cities in the same province.
CITY_LD = ('{"@context":"https://schema.org","@graph":[' + crumb3("{{prov_name}} diesel prices", "/diesel-prices/{{prov_slug}}/", "{{name}} diesel prices") + ','
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
    <p class="stand">{{name}} runs <b>{{vs_national_abs}}¢ {{vs_national_word}}</b> the national index — a real difference on a 500-litre fill. <a href="/fuel-cost-calculator/">Work out a trip</a></p>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">{{name}} diesel: {{price}}¢/L, NRCan weekly survey print {{print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/diesel-prices/{{prov_slug}}/{{slug}}/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>What drives {{name}} prices</h2></div>
    <div class="reading">
{{prose}}
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>{{prov_name}} survey cities</h2><p>¢/L · distance from the provincial mean</p></div>
    <div class="rows">
    <!--LOOP:siblings--><a class="r" href="/diesel-prices/{{prov_slug}}/{{city_slug}}/"><span class="k">{{city}}</span><span class="v">{{price}} &nbsp; <span class="{{vs_class}}">{{vs_prov}}</span></span></a><!--/LOOP:siblings-->
    </div>
    <p class="note">Every price is an NRCan survey observation from the print dated {{print_date}}. The provincial figure is the unweighted mean of its survey cities, the same figure that enters the <a href="/methodology/nmdi/">Northern Mile Diesel Index</a>.</p>
  </section>
''' + subscribe("{{name}} diesel, every week",
   "Where {{name}} and the rest of {{prov_name}} moved, and what it means for cost per kilometre. One email on Wednesday mornings.")
 + '''
  <p class="note"><a href="/diesel-prices/{{prov_slug}}/">← {{prov_name}} overview</a> · <a href="/fuel-prices/">All ten provinces</a></p>
''' + foot())

with open(os.path.join(OUT, "city.template.html"), "w") as f:
    f.write(city_body)
print(f"  city                      {len(city_body):6,} bytes")

# One template, rendered per province by build_city_pages.py.
#
# Every one of the ten provinces needs this page, not just the two with
# editorial prose. It is the ONLY hub that links a province's survey cities.
# Before it existed, /diesel-prices/quebec/ was a 404 and its cities had no
# inbound link from anywhere on the site, so nothing could crawl to them.
PROVINCE_INDEX_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{prov_name}} diesel prices", "/diesel-prices/{{prov_slug}}/") + ','
 '{"@type":"Dataset","name":"{{prov_name}} Diesel Prices","description":"Retail diesel prices across {{city_count}} {{prov_name}} survey cities, from the Natural Resources Canada weekly retail survey.","url":"' + BASE + '/diesel-prices/{{prov_slug}}/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"{{prov_name}}, Canada"},"variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price","unitText":"Canadian cents per litre"},"dateModified":"{{updated_iso}}"}]}')

province_index_body = (
 head("{{prov_name}} Diesel Prices — {{prov_price}}¢/L | Northern Mile",
      "Diesel prices across {{city_count}} {{prov_name}} survey cities, {{prov_price}}¢/L provincial average, {{vs_national_abs}}¢ {{vs_national_word}} the national index. NRCan weekly survey, print {{print_date}}.",
      "/diesel-prices/{{prov_slug}}/", "og-fuel.jpg", PROVINCE_INDEX_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">{{prov_name}} · {{city_count}} survey cities</span>
    <h1>{{prov_name}} diesel prices</h1>
    <div class="figure"><span class="n">{{prov_price}}</span><span class="u">¢/L</span><span class="d {{vs_national_class}}">{{vs_national}} vs national</span></div>
    <div class="meta"><span>NRCan survey print <b>{{print_date}}</b></span><span>National index <b>{{national}}</b>¢/L</span></div>
    <p class="stand">The {{prov_name}} average is the unweighted mean of its {{city_count}} survey cities. <a href="/fuel-cost-calculator/">Work out a trip</a></p>
    <div class="cite">
      <div class="cl">Citing this figure</div>
      <q id="citation">{{prov_name}} diesel: {{prov_price}}¢/L provincial average across {{city_count}} survey cities, NRCan weekly survey print {{print_date}}. Northern Mile Media, dashboard.northernmilemedia.com/diesel-prices/{{prov_slug}}/</q>
      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation"><span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">How it is calculated</a></div>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Every {{prov_name}} survey city</h2><p>¢/L · distance from the provincial mean</p></div>
    <div class="rows">
    <!--LOOP:cities--><a class="r" href="/diesel-prices/{{prov_slug}}/{{city_slug}}/"><span class="k">{{city}}</span><span class="v">{{price}} &nbsp; <span class="{{vs_class}}">{{vs_prov}}</span></span></a><!--/LOOP:cities-->
    </div>
    <p class="note">Every price is an NRCan survey observation from the print dated {{print_date}}. This page rebuilds every 30 minutes, but the survey figure holds until the next weekly print.</p>
  </section>
''' + subscribe("{{prov_name}} diesel, every week",
   "Where {{prov_name}} and the rest of Canada moved, and what it means for cost per kilometre. One email on Wednesday mornings.")
 + '''
  <p class="note"><a href="/fuel-prices/">← All ten provinces</a> · <a href="/methodology/nmdi/">Methodology</a></p>
''' + foot())

with open(os.path.join(OUT, "province-index.template.html"), "w") as f:
    f.write(province_index_body)
print(f"  province-index            {len(province_index_body):6,} bytes")

# ═══ US diesel pages ════════════════════════════════════════════════════
# One overview template + one per-PADD template, rendered by build_us_pages.py.
US_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("US diesel prices", "/us-diesel/") + ','
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
    <div class="lead"><h2>Ten districts</h2><p>Every EIA diesel district · ¢/L CAD and $/gal</p></div>
    <div class="rows">
    <!--LOOP:padds--><a class="r" href="/us-diesel/district/{{key_url}}/"><span class="k">{{label}}</span><span class="v">{{cpl}}¢ &nbsp; <span class="flat">${{usd_gal}}/gal</span></span></a><!--/LOOP:padds-->
    </div>
    <p class="note">Each region is an EIA PADD — Petroleum Administration for Defense District. The price is that region&rsquo;s observation from the EIA weekly retail diesel survey, converted from US dollars per gallon at the latest Bank of Canada USD/CAD rate (1 US gallon = 3.785411784 L).</p>
    <p class="note">Each district is an EIA pricing region. The price is that district&rsquo;s observation from the EIA weekly retail diesel survey, converted from US dollars per gallon at the latest Bank of Canada USD/CAD rate (1 US gallon = 3.785411784 L).</p>
    <p class="note">EIA does not price diesel by state, so there is no state-level figure to show. The <a href="/us-diesel/states/">state pages</a> give each state&rsquo;s fuel tax and name the district its diesel figure comes from.</p>
  </section>

  <section class="sec">
    <div class="lead"><h2>The North American index</h2></div>
    <div class="reading">
      <p class="note" style="margin-top:0">The North American Diesel Index (NADI) is the mean of the Canadian national average and the US national average — each country counts once, not consumption-weighted. This week the NADI is <b>{{eia.nadi}}¢/L</b>, with {{eia.gap_word}} by <b>{{eia.ca_us_gap}}¢/L</b>.</p>
      <p class="note">Methodology: <a href="/methodology/nmdi/">/methodology/nmdi/</a>. The Canadian half is the NRCan weekly survey (ten provinces); the US half is the EIA national average above.</p>
    </div>
  </section>
''' + subscribe("US and Canadian diesel, every week",
   "Where both sides of the border moved, and what it means for a cross-border carrier's week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-diesel.template.html"), "w") as f:
    f.write(us_body)
print(f"  us-diesel                 {len(us_body):6,} bytes")

# One template, rendered per PADD by build_us_pages.py.
USPADD_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{label}} diesel prices", "/us-diesel/{{key}}/") + ','
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
    <section class="sec">
      <div class="lead"><h2>States in {{label}}</h2><p>Each state's own fuel tax and IFTA rate</p></div>
      <div class="rows">
      <!--LOOP:state_links--><a class="r" href="/us-diesel/{{slug}}/"><span class="k">{{name}}</span><span class="v">{{abbr}}</span></a><!--/LOOP:state_links-->
      </div>
    </section>

    <div class="lead"><h2>The other districts</h2><p>¢/L CAD · $/gal</p></div>
    <div class="rows">
    <!--LOOP:siblings--><a class="r" href="/us-diesel/district/{{key_url}}/"><span class="k">{{label}}</span><span class="v">{{cpl}}¢ &nbsp; <span class="flat">${{usd_gal}}/gal</span></span></a><!--/LOOP:siblings-->
    </div>
    <p class="note"><a href="/us-diesel/">← US national and all regions</a></p>
  </section>
''' + subscribe("{{label}} diesel, every week",
   "Where {{label}} and the rest of North America moved, and what it means for a cross-border carrier's week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-padd.template.html"), "w") as f:
    f.write(uspadd_body)
print(f"  us-padd                  {len(uspadd_body):6,} bytes")

# One template, rendered per crossing by build_border_pages.py.
BORDER_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{name}} border wait", "/border-wait-times/{{slug}}/") + ','
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

# ═══ CBP port reference ══════════════════════════════════════════════════════
# Every port CBP publishes, both borders, all three lane classes. This is the
# page that closes the 9-crossings gap: CBSA covers 9 Canada-bound crossings,
# CBP covers 85 in the US-bound direction and nobody presents the full set.
#
# The template carries TWO loop blocks because a port with no published delay
# must render differently from a port that measured zero. {{reported}} drives an
# IF block so "not reported" is visible rather than an implied zero.
CBP_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("All border crossings", "/border-wait-times/all-ports/") + ','
 '{"@type":"Dataset","name":"North American Land Border Ports","description":"Every US land border port published by U.S. Customs and Border Protection, with commercial, passenger and pedestrian lane waits. 85 ports across the Canadian and Mexican borders.","url":"' + BASE + '/border-wait-times/all-ports/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}')

cbp_ports_body = (
 head("All Border Crossings — 85 US Land Ports | Northern Mile",
      "Every land border port U.S. Customs and Border Protection publishes, with commercial truck, passenger and pedestrian lane waits. Both the Canadian and Mexican borders, refreshed from the CBP feed.",
      "/border-wait-times/all-ports/", "og.jpg", CBP_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">CBP · all lanes · US-bound</span>
    <h1>Every land border crossing</h1>
    <div class="figure"><span class="n">{{port_count}}</span><span class="u">ports</span></div>
    <div class="meta"><span>{{ca_count}} on the Canadian border · {{mx_count}} on the Mexican border</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec">
    <div class="lead"><h2>How to read this</h2></div>
    <div class="reading">
      <p>These are <b>US-bound</b> waits. The Canada-bound direction is a separate feed published by the Canada Border Services Agency, and it is on the <a href="/border-wait-times/">crossing pages</a>. A carrier crossing south checks here; a carrier coming home checks there.</p>
      <p>Only {{reported_count}} of {{port_count}} ports had published a commercial truck delay when this page was last built. <b>A port with no published figure is shown as not reported, never as zero.</b> Zero means the agency measured no wait. Not reported means the agency did not say, and those are not the same thing to a driver deciding whether to roll now or wait an hour.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Canadian border</h2><p>US-bound · CBP commercial lanes</p></div>
    <div class="rows">
    <!--LOOP:ca_ports--><div class="r"><span class="k">{{port_name}}{{crossing_suffix}}<small>{{jurisdiction}}</small></span><span class="v">{{commercial_display}}</span></div><!--/LOOP:ca_ports-->
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Mexican border</h2><p>US-bound · CBP commercial lanes</p></div>
    <div class="rows">
    <!--LOOP:mx_ports--><div class="r"><span class="k">{{port_name}}{{crossing_suffix}}<small>{{jurisdiction}}</small></span><span class="v">{{commercial_display}}</span></div><!--/LOOP:mx_ports-->
    </div>
    <p class="note">Mexico publishes no southbound figures, so only the US-bound direction exists for these ports.</p>
  </section>
''' + subscribe("Border and diesel, weekly",
   "Which crossings backed up, where diesel moved, and what both did to cost per kilometre. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "cbp-ports.template.html"), "w") as f:
    f.write(cbp_ports_body)
print(f"  cbp-ports                 {len(cbp_ports_body):6,} bytes")

# ═══ IFTA fuel tax rates ═════════════════════════════════════════════════════
# Compliance reference. IFTA, Inc. publishes the authoritative quarterly rate
# for every jurisdiction in one file, and this is the only all-jurisdiction
# compliance dataset that exists in a single place. Everything else in this
# space is fragmented across 50+ government portals.
#
# Two rate schedules are published because they genuinely differ: the U.S. row
# applies to US-licensed carriers and the Can row to Canadian-licensed carriers.
# Showing one number would be wrong for roughly a third of the jurisdictions.
IFTA_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("IFTA fuel tax rates", "/fuel-tax-rates/") + ','
 '{"@type":"Dataset","name":"IFTA Fuel Tax Rates by Jurisdiction","description":"Official quarterly IFTA fuel tax rates for all 10 Canadian provinces and 48 US states, for US-licensed and Canadian-licensed carriers separately.","url":"' + BASE + '/fuel-tax-rates/","creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,"dateModified":"{{updated_iso}}"}]}')

ifta_body = (
 head("IFTA Fuel Tax Rates — All 58 Jurisdictions | Northern Mile",
      "Official IFTA fuel tax rates for every Canadian province and US state, both carrier rate schedules, for the current quarter. Free, cited, and updated when IFTA publishes.",
      "/fuel-tax-rates/", "og.jpg", IFTA_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">IFTA · {{quarter}} · official matrix</span>
    <h1>IFTA fuel tax rates</h1>
    <div class="figure"><span class="n">{{jurisdiction_count}}</span><span class="u">jurisdictions</span></div>
    <div class="meta"><span>{{ca_count}} provinces · {{us_count}} states</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Two rates, and why</h2></div>
    <div class="reading">
      <p>IFTA publishes a rate for <b>US-licensed</b> carriers and a separate rate for <b>Canadian-licensed</b> carriers wherever the two differ. They are columns here, not one averaged number, because a carrier filing with one licence should not be reading the other licence's rate.</p>
      <p>Rates are set quarterly by IFTA, Inc. from each jurisdiction's own fuel tax statute, and shown in the unit that statute uses: cents per litre in Canada, and per gallon in the US. Three states also levy a separate surcharge on certain fuel types, which is shown beside the base rate rather than silently added to it.</p>
      <p class="note">This is the published tax rate. It is not tax advice, and it is not your filing. Your return depends on litres purchased and distance travelled in each jurisdiction.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Canadian provinces</h2><p>per litre · {{quarter}}</p></div>
    <div class="rows">
    <!--LOOP:ca_jur--><div class="r"><span class="k">{{name}}<small>{{surcharge_note}}</small></span><span class="v">{{rates_display}}</span></div><!--/LOOP:ca_jur-->
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>US states</h2><p>per gallon · {{quarter}}</p></div>
    <div class="rows">
    <!--LOOP:us_jur--><div class="r"><span class="k">{{name}}<small>{{surcharge_note}}</small></span><span class="v">{{rates_display}}</span></div><!--/LOOP:us_jur-->
    </div>
    <p class="note">US rates are levied per gallon and Canadian rates per litre; both are shown in the unit the jurisdiction actually uses rather than converted, so the figure matches the statute.</p>
  </section>
''' + subscribe("Border and diesel, weekly",
   "Which crossings backed up, where diesel moved, and what both did to cost per kilometre. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "ifta-rates.template.html"), "w") as f:
    f.write(ifta_body)
print(f"  ifta-rates                {len(ifta_body):6,} bytes")

# ═══ US state pages ═══════════════════════════════════════════════════════════
#
# The honest version of what the incumbents fake. EIA does not publish diesel by
# state, so most US "state diesel price" pages quietly serve a district figure
# under a state URL and mention the fact in a footnote. This page shows what IS
# state-level (the fuel taxes) AS state-level, and shows the diesel figure as a
# district figure with the reason stated in the body. The attribution is the
# product: it is the one thing a competitor cannot copy without giving up the
# number of "state" pages they advertise.
US_STATE_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("{{state_name}}", "{{path_url}}") + ','
 '{"@type":"WebPage","name":"{{state_name}} diesel prices and fuel tax",'
 '"url":"{{canonical}}","isAccessibleForFree":true,'
 '"creator":{"@id":"' + ORG_URL + '/#org"},'
 '"dateModified":"{{updated_iso}}"}]}')

us_state_body = (
 head("{{state_name}} Diesel Prices and Fuel Tax | Northern Mile",
      "{{description}}",
      "{{path_url}}", "og.jpg", US_STATE_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">United States · {{abbr}}</span>
    <h1>{{state_name}} diesel prices and fuel tax</h1>
    <div class="figure"><span class="n">{{district_price_short}}</span><span class="u">{{district_unit}}</span></div>
    <div class="meta"><span>{{district_label}} district · week ending {{diesel_week}}</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Fuel tax in {{state_name}}</h2><p>The part of this page that is genuinely about {{state_name}}</p></div>
    <div class="stats">
      <div class="stat"><div class="l">State excise, diesel</div><div class="v">{{state_excise}}</div><div class="s">per gallon, statutory</div></div>
      <div class="stat"><div class="l">Other state fees</div><div class="v">{{state_other}}</div><div class="s">{{state_other_note}}</div></div>
      <div class="stat"><div class="l">Federal</div><div class="v">{{federal_excise}}</div><div class="s">per gallon, all states</div></div>
      <div class="stat"><div class="l">All in</div><div class="v">{{all_in}}</div><div class="s">state total plus federal</div></div>
    </div>
    <div class="reading">
      <p>The four numbers add up. State excise {{state_excise}} plus other state fees {{state_other}} gives a state total of <b>{{state_total}}</b>. Add the federal {{federal_excise}} and the all-in figure is <b>{{all_in}}</b> a gallon.</p>
      <p class="note">Every figure is rounded to four decimal places of a dollar before it is shown, and the totals are the sum of the rounded figures rather than of the unrounded ones. On three states those two differ by one ten-thousandth of a dollar. We print the sum that matches the numbers you can see, because a page that shows its arithmetic should have arithmetic that checks out.</p>
      <p>{{ifta_sentence}}</p>
      <p>{{tax_note}}</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Why there is no {{state_name}} diesel price here</h2></div>
    <div class="reading">
      <p>The Energy Information Administration publishes a weekly on-highway diesel price on a <b>district</b> basis, not a state basis. There are ten districts in the whole country and {{state_name}} is not one of them.</p>
      <p>{{state_name}} sits in the <b>{{district_label}}</b> district. The figure at the top of this page is that district's weekly price. It is not a {{state_name}} price, and we are not going to label it as one.</p>
      <p>Plenty of sites will show you a {{state_name}} diesel price. What they are showing you is the same district number they show for every neighbouring state, because the state-level number does not exist to show. If a site claims a per-state diesel price, ask it which survey it came from.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>What is state-level in {{state_name}}</h2></div>
    <div class="rows">
      <div class="r"><span class="k">Fuel tax rate<small>levied by {{abbr}}, published by IFTA</small></span><span class="v">{{ifta_display}}</span></div>
      <div class="r"><span class="k">Statutory excise<small>levied by {{abbr}}, published by EIA</small></span><span class="v">{{state_excise_display}}</span></div>
      <div class="r"><span class="k">Diesel price<small>published by district, not by state</small></span><span class="v">{{district_label}}</span></div>
    </div>
  </section>
  <!--IF:has_border-->
  <section class="sec">
    <div class="lead"><h2>Border crossings in {{state_name}}</h2><p>{{border_count}} ports · CBP commercial lanes</p></div>
    <div class="reading">
      <p>{{border_intro}}</p>
    </div>
    <div class="rows">
      <!--LOOP:borderrows--><div class="r"><span class="k">{{label}}</span><span class="v">{{delay}}</span></div><!--/LOOP:borderrows-->
    </div>
    <p class="note">A port with no published figure is shown as not reported. Zero means the agency measured no commercial delay. Not reported means the agency did not say.</p>
  </section>
  <!--/IF:has_border-->

  <section class="sec">
    <div class="lead"><h2>Where to go next</h2></div>
    <div class="rows">
      <a class="r" href="/us-diesel/"><span class="k">US diesel by district<small>All ten EIA districts in one table</small></span><span class="v">all 10</span></a>
      <a class="r" href="/fuel-tax-rates/"><span class="k">IFTA fuel tax rates<small>Every province and state</small></span><span class="v">58</span></a>
      <a class="r" href="/border-wait-times/all-ports/"><span class="k">Border crossings<small>Both borders, all lanes</small></span><span class="v">85</span></a>
      <a class="r" href="/fuel-prices/"><span class="k">Canadian diesel prices<small>By province and city</small></span><span class="v">by province</span></a>
      <a class="r" href="/methodology/nmdi/"><span class="k">Methodology<small>Sources and how the index is built</small></span><span class="v">sources</span></a>
    </div>
  </section>
''' + subscribe("Diesel, border and tax, weekly",
   "What fuel, the border and the dollar did to cost per mile this week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-state.template.html"), "w") as f:
    f.write(us_state_body)
print(f"  us-state                  {len(us_state_body):6,} bytes")

# ═══ US state index ═══════════════════════════════════════════════════════════
# Without this the 51 state pages are orphans: nothing links to them, and
# check_links.py fails the build on an unreachable page. The hub is also where
# the district/state distinction gets stated once, plainly, before the reader
# clicks into a state.
US_STATES_LD = ('{"@context":"https://schema.org","@graph":[' + crumb("US states", "/us-diesel/states/") + ','
 '{"@type":"CollectionPage","name":"US state diesel and fuel tax",'
 '"url":"' + BASE + '/us-diesel/states/","isAccessibleForFree":true,'
 '"creator":{"@id":"' + ORG_URL + '/#org"}}]}')

us_states_body = (
 head("US State Diesel Prices and Fuel Tax — All 51 | Northern Mile",
      "Every US state with the fuel tax it actually levies and the diesel district it sits in. EIA prices diesel by district, not by state, and each page says which district applies.",
      "/us-diesel/states/", "og.jpg", US_STATES_LD, "article")
 + '''
  <section class="hero">
    <span class="eyebrow">United States · 50 states and DC</span>
    <h1>Diesel and fuel tax by state</h1>
    <div class="figure"><span class="n">{{state_count}}</span><span class="u">states</span></div>
    <div class="meta"><span>{{district_count}} districts cover the 50 states · week ending {{diesel_week}}</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec">
    <div class="lead"><h2>Read this before the table</h2></div>
    <div class="reading">
      <p>The Energy Information Administration publishes a weekly on-highway diesel price for <b>ten districts</b>, not for fifty states. There is no state-level diesel price to publish, for any state, from any source.</p>
      <p>So every US site with a "state diesel price" page is serving you a district number under a state heading. Some say so in a footnote. Most do not say so at all.</p>
      <p>This table gives you the two things that genuinely are per-state, the fuel tax a state levies and the tax a carrier files under IFTA, and names the district each state's diesel figure comes from. A state page shows the same district number a neighbouring state's page shows, and tells you that is what it is doing.</p>
    </div>
  </section>

  <section class="sec">
    <div class="lead"><h2>All 51</h2><p>Rates per gallon. Diesel is the district figure.</p></div>
    <div class="rows">
      <!--LOOP:states--><a class="r" href="{{url}}"><span class="k">{{name}}<small>{{district}} district · IFTA {{ifta}}</small></span><span class="v">{{all_in}}<small>all in</small></span></a><!--/LOOP:states-->
    </div>
    <p class="note">All-in is state excise plus other state fees plus the {{federal}} federal rate. IFTA is the rate a US-licensed carrier files for that state.</p>
  </section>
''' + subscribe("Diesel, border and tax, weekly",
   "What fuel, the border and the dollar did to cost per mile this week. One email on Wednesday mornings.") + foot())

with open(os.path.join(OUT, "us-states.template.html"), "w") as f:
    f.write(us_states_body)
print(f"  us-states                 {len(us_states_body):6,} bytes")

print("\\nAll templates generated.")
