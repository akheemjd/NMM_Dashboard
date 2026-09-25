"""Generate the /ca/ and /us/ homepage templates.

A separate generator rather than more code inside gen_templates.py. Injecting a
large template literal into that file meant nesting triple-quoted strings inside a
triple-quoted string, and every apostrophe and escaped quote in transit broke
something. A new file has no existing content to collide with.

Runs AFTER gen_templates.py, so it can import that module and reuse its block
functions — rail(), chart_summary(), sponsor(), subscribe(), foot(), head(),
country_switch(). The shared blocks are the same functions the old homepage used, so
the three pages cannot drift apart in structure.

Depends on gen_templates.write() having already placed the shared templates.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_templates as G  # noqa: E402  (import runs its generation, by design)

rail = G.rail
chart_summary = G.chart_summary
sponsor = G.sponsor
subscribe = G.subscribe
foot = G.foot
head = G.head
country_switch = G.country_switch
write = G.write
BASE = G.BASE
ORG_LD = G.ORG_LD
ORG_URL = G.ORG_URL

AP = chr(39)   # literal apostrophe, so no escape has to survive anything


def shared_tail():
    """Border, market, news — byte-identical on both country homepages."""
    return (
        '\n  <section class="sec">\n'
        '    <div class="lead"><h2>On the road</h2><p>What is in front of you right now.</p></div>\n'
        '    <div class="two">\n'
        '      <div><h3>Border crossings</h3><div class="rows">\n'
        '      <!--LOOP:border_rows--><a class="r" href="/border-wait-times/"><span class="k">{{name}}'
        '<small>{{status_label}}</small></span><span class="v">{{wait}}</span></a><!--/LOOP:border_rows-->\n'
        '      </div><p class="note">Each wait carries CBSA' + AP + 's own capture time, not our fetch time. '
        '<a href="/border-wait-times/">All crossings</a></p></div>\n'
        '      <div><h3>Road incidents</h3>\n'
        '      <!--IF:incidents.none--><div class="empty"><b>Corridors clear</b>No major closures or '
        'collisions on the corridors we monitor.</div><!--/IF:incidents.none-->\n'
        '      <div class="links-list">\n'
        '      <!--LOOP:incidents.incidents--><a href="{{url}}">{{what}}</a><!--/LOOP:incidents.incidents-->\n'
        '      </div><p class="note">{{incidents.status_line}} <a href="/road-incidents/">Open map</a></p></div>\n'
        '    </div>\n'
        '  </section>\n'
        '\n'
        '  <section class="sec">\n'
        '    <div class="lead"><h2>Planning a run</h2><p>What a trip costs, and where the market sits.</p></div>\n'
        '    <div class="two">\n'
        '      <div><h3>Exchange and market</h3><div class="rows">\n'
        '        <a class="r" href="/exchange-rate/"><span class="k">USD / CAD<small>Bank of Canada</small>'
        '</span><span class="v">{{fx.usd_cad}} {{fx.change}}</span></a>\n'
        '        <!--LOOP:market--><a class="r" href="/market-pulse/"><span class="k">{{name}}'
        '<small>{{note}}</small></span><span class="v {{value_class}}">{{value}}</span></a><!--/LOOP:market-->\n'
        '      </div></div>\n'
        '      <div><h3>Industry news</h3><div class="links-list">\n'
        '        <!--LOOP:news--><a href="{{url}}" target="_blank" rel="noopener"><span class="src">'
        '{{category}}</span>{{headline}}</a><!--/LOOP:news-->\n'
        '      </div><p class="note"><a href="/industry-news/">All headlines</a></p></div>\n'
        '    </div>\n'
        '    <p class="note">Diesel prices include all federal and provincial fuel, carbon, and sales taxes. '
        '<a href="/fuel-cost-calculator/">Work out what a run costs</a></p>\n'
        '  </section>\n'
    )


# ══════════════════════════════════════════════════════════════ /ca/ ══
ca_ld = (
    '{"@context":"https://schema.org","@graph":[' + ORG_LD + ','
    '{"@type":"WebSite","@id":"' + BASE + '/ca/#site","url":"' + BASE + '/ca/",'
    '"name":"Northern Mile Canada","publisher":{"@id":"' + ORG_URL + '/#org"},"inLanguage":"en-CA"},'
    '{"@type":"Dataset","name":"Canadian Diesel Prices",'
    '"description":"Retail diesel prices for ten Canadian provinces, from the Natural Resources Canada '
    'weekly retail survey.","url":"' + BASE + '/ca/","creator":{"@id":"' + ORG_URL + '/#org"},'
    '"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"Canada"},'
    '"variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price",'
    '"unitText":"Canadian cents per litre","value":"{{fuel.national_diesel}}"},'
    '"dateModified":"{{updated_iso}}"}]}'
)

write(
    "ca-home",
    head(
        "Canadian Diesel Prices — {{fuel.national_diesel}}¢/L national | Northern Mile",
        "Canadian diesel from the NRCan weekly survey, print {{fuel.print_date}}. National average "
        "{{fuel.national_diesel}}¢/L across ten provinces, cheapest {{fuel.low_code}} at {{fuel.low}}, "
        "dearest {{fuel.high_code}} at {{fuel.high}}. Live border waits and the Bank of Canada rate.",
        "/ca/", "og-fuel.jpg", ca_ld,
    )
    + '\n  <section class="hero">\n'
    + ""
    + '    <span class="eyebrow">Canada · NRCan weekly survey</span>\n'
    '    <h1>Canadian diesel prices today</h1>\n'
    '    <div class="figure"><span class="n">{{fuel.national_diesel}}</span><span class="u">¢/L</span>'
    '<span class="d {{fuel.change_7d_class}}">{{fuel.change_7d}} · 7d</span></div>\n'
    '    <div class="meta"><span>Ten provinces</span><span>NRCan print <b>{{fuel.print_date}}</b></span>'
    '<span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>\n'
    '    <p class="stand">Cross-border, for context: <b>{{eia.ca_us_gap}}¢/L</b> · {{eia.gap_word}} than '
    'the US average of <b>${{eia.us_national_usd_gal}}/gal</b>. <a href="/us/">US site</a></p>\n'
    '    <div class="cite">\n'
    '      <div class="cl">Citing this figure</div>\n'
    '      <q id="citation">Northern Mile Canadian Diesel Index: {{fuel.national_diesel}}¢/L across ten '
    'Canadian provinces, NRCan weekly survey print {{fuel.print_date}}. Northern Mile Media, '
    'dashboard.northernmilemedia.com/ca/</q>\n'
    '      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation">'
    '<span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">'
    'How it is calculated</a></div>\n'
    '    </div>\n'
    '  </section>\n'
    + rail("ca")
    + chart_summary()
    + '\n  <section class="sec">\n    <div class="stats">\n'
    '      <a class="stat" href="/fuel-prices/"><div class="l">Cheapest</div><div class="v down">'
    '{{fuel.low}}</div><div class="s">{{fuel.low_code}} · ¢/L</div></a>\n'
    '      <a class="stat" href="/fuel-prices/"><div class="l">Dearest</div><div class="v up">'
    '{{fuel.high}}</div><div class="s">{{fuel.high_code}} · ¢/L</div></a>\n'
    '      <a class="stat" href="/fuel-prices/"><div class="l">Spread</div><div class="v">'
    '{{fuel.spread}}</div><div class="s">{{fuel.low_code}} to {{fuel.high_code}} spread · ¢/L</div></a>\n'
    '      <a class="stat" href="/fuel-tax-rates/"><div class="l">Fuel tax</div><div class="v">58</div>'
    '<div class="s">IFTA jurisdictions · CAD/L</div></a>\n'
    '      <a class="stat" href="/exchange-rate/"><div class="l">USD / CAD</div><div class="v">'
    '{{fx.usd_cad}}</div><div class="s">{{fx.direction}} {{fx.change}} · BoC</div></a>\n'
    '      <a class="stat" href="/us/"><div class="l">US diesel</div><div class="v">'
    '{{eia.us_national_usd_gal}}</div><div class="s">$/gal · ten districts</div></a>\n'
    '    </div>\n  </section>\n'
    + sponsor("sponsor_page")
    + shared_tail()
    + subscribe(
        "Canadian diesel, every Wednesday",
        "What moved in Canadian diesel, at the border, and in freight demand, with every figure dated "
        "and linked back to this dashboard. Written for people who move freight, not for people who "
        "write about it.",
    )
    + foot()
)

# ══════════════════════════════════════════════════════════════ /us/ ══
us_ld = (
    '{"@context":"https://schema.org","@graph":[' + ORG_LD + ','
    '{"@type":"WebSite","@id":"' + BASE + '/us/#site","url":"' + BASE + '/us/",'
    '"name":"Northern Mile US","publisher":{"@id":"' + ORG_URL + '/#org"},"inLanguage":"en-US"},'
    '{"@type":"Dataset","name":"US On-Highway Diesel Prices",'
    '"description":"US on-highway diesel price by EIA district and nationally, from the EIA weekly '
    'retail diesel survey.","url":"' + BASE + '/us/","creator":{"@id":"' + ORG_URL + '/#org"},'
    '"isAccessibleForFree":true,"spatialCoverage":{"@type":"Place","name":"United States"},'
    '"variableMeasured":{"@type":"PropertyValue","name":"Retail diesel price",'
    '"unitText":"US dollars per gallon","value":"{{eia.us_national_usd_gal}}"},'
    '"dateModified":"{{updated_iso}}"}]}'
)

write(
    "us-home",
    head(
        "US Diesel Prices — ${{eia.us_national_usd_gal}}/gal national | Northern Mile",
        "US on-highway diesel from the EIA weekly retail diesel survey, week ending {{eia.date}}. "
        "National average ${{eia.us_national_usd_gal}}/gal across ten districts, cheapest "
        "{{us_low_code}} at ${{us_low}}/gal, dearest {{us_high_code}} at ${{us_high}}/gal.",
        "/us/", "og.jpg", us_ld,
    )
    + '\n  <section class="hero">\n'
    + ""
    + '    <span class="eyebrow">United States · EIA weekly retail diesel survey</span>\n'
    '    <h1>US diesel prices today</h1>\n'
    '    <div class="figure"><span class="n">{{eia.us_national_usd_gal}}</span><span class="u">$/gal</span>'
    '<span class="d {{eia.us_change_7d_class}}">{{eia.us_change_7d}} · 7d</span></div>\n'
    '    <div class="meta"><span>Ten EIA districts</span><span>EIA week <b>{{eia.date}}</b></span>'
    '<span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>\n'
    '    <p class="stand">Cross-border, for context: <b>{{eia.ca_us_gap}}¢/L</b> · {{eia.gap_word}} than '
    'the Canadian average of <b>{{fuel.national_diesel}}¢/L</b>. <a href="/ca/">Canadian site</a></p>\n'
    '    <div class="cite">\n'
    '      <div class="cl">Citing this figure</div>\n'
    '      <q id="citation">US on-highway diesel: ${{eia.us_national_usd_gal}}/gal national average, EIA '
    'weekly retail diesel survey, week ending {{eia.date}}. Northern Mile Media, '
    'dashboard.northernmilemedia.com/us/</q>\n'
    '      <div class="row"><button class="btn btn--brand" type="button" data-copy="citation">'
    '<span class="cp">Copy citation</span></button><a class="btn" href="/methodology/nmdi/">'
    'How it is calculated</a></div>\n'
    '    </div>\n'
    '  </section>\n'
    + rail("us")
    + '\n  <section class="sec">\n'
    '    <div class="lead"><h2>Where today sits</h2></div>\n'
    '    <div class="reading">\n'
    '      <p class="note" style="margin-top:0">EIA publishes a current weekly price and a district '
    'breakdown, not a price history, so there is no ten-year series for the US. The <a href="/ca/">'
    'Canadian site</a> carries one because NRCan publishes one.</p>\n'
    '    </div>\n'
    '  </section>\n'
    '\n  <section class="sec">\n    <div class="stats">\n'
    '      <a class="stat" href="/us-diesel/"><div class="l">Cheapest</div><div class="v down">'
    '{{us_low}}</div><div class="s">{{us_low_code}} · $/gal</div></a>\n'
    '      <a class="stat" href="/us-diesel/"><div class="l">Dearest</div><div class="v up">'
    '{{us_high}}</div><div class="s">{{us_high_code}} · $/gal</div></a>\n'
    '      <a class="stat" href="/us-diesel/"><div class="l">Spread</div><div class="v">'
    '{{us_spread}}</div><div class="s">{{us_low_code}} to {{us_high_code}} spread · $/gal</div></a>\n'
    '      <a class="stat" href="/us-diesel/states/"><div class="l">State fuel tax</div>'
    '<div class="v">51</div><div class="s">states and DC · $/gal</div></a>\n'
    '      <a class="stat" href="/exchange-rate/"><div class="l">USD / CAD</div><div class="v">'
    '{{fx.usd_cad}}</div><div class="s">{{fx.direction}} {{fx.change}} · BoC</div></a>\n'
    '      <a class="stat" href="/ca/"><div class="l">Canadian diesel</div><div class="v">'
    '{{fuel.national_diesel}}</div><div class="s">¢/L · ten provinces</div></a>\n'
    '    </div>\n  </section>\n'
    + sponsor("sponsor_page")
    + shared_tail()
    + subscribe(
        "US and Canadian diesel, every Wednesday",
        "Where both sides of the border moved, and what it means for a cross-border carrier" + AP
        + "s week. One email on Wednesday mornings.",
    )
    + foot()
)

# ══════════════════════════════════════════════════════ / (the chooser) ══
chooser_ld = (
    '{"@context":"https://schema.org","@graph":[' + ORG_LD + ','
    '{"@type":"WebSite","@id":"' + BASE + '/#site","url":"' + BASE + '/",'
    '"name":"Northern Mile","publisher":{"@id":"' + ORG_URL + '/#org"},"inLanguage":"en-CA"},'
    '{"@type":"Dataset","name":"North American Diesel Prices",'
    '"description":"Canadian and US retail diesel prices from the Natural Resources Canada weekly '
    'survey and the EIA weekly retail diesel survey.","url":"' + BASE + '/",'
    '"creator":{"@id":"' + ORG_URL + '/#org"},"isAccessibleForFree":true,'
    '"spatialCoverage":{"@type":"Place","name":"Canada and the United States"},'
    '"dateModified":"{{updated_iso}}"}]}'
)

write(
    "index",
    head(
        "Diesel Prices in Canada and the US — pick your side | Northern Mile",
        "Canadian diesel {{fuel.national_diesel}}¢/L across ten provinces, US diesel "
        "${{eia.us_national_usd_gal}}/gal across ten districts. Canada is {{eia.ca_us_gap}}¢/L "
        "{{eia.gap_word}}. Pick your side of the border, or read the cross-border figures first.",
        "/", "og.jpg", chooser_ld,
    )
    + '''
  <section class="hero">
    <span class="eyebrow">Free cross-border trucking data · no account</span>
    <h1>Which side of the border do you run?</h1>
    <div class="pick">
      <a class="pickcard" href="/ca/">
        <span class="pflag">Canada</span>
        <span class="pval">{{fuel.national_diesel}}<em>¢/L</em></span>
        <span class="pmeta">Ten provinces · NRCan weekly survey · print {{fuel.print_date}}</span>
        <span class="pgo">Canadian site →</span>
      </a>
      <a class="pickcard" href="/us/">
        <span class="pflag">United States</span>
        <span class="pval">{{eia.us_national_usd_gal}}<em>$/gal</em></span>
        <span class="pmeta">Ten EIA districts · week ending {{eia.date}}</span>
        <span class="pgo">US site →</span>
      </a>
    </div>
    <p class="stand">Both trees are free and need no account. The <a href="#crossborder">cross-border
    figures</a> below are the same in either one.</p>
    <div class="meta"><span>Ten provinces · ten districts</span><span>Rebuilt <b>{{updated_at}}</b> UTC</span></div>
  </section>

  <section class="sec" id="crossborder">
    <div class="lead"><h2>Cross-border</h2><p>The two things only a both-sides reading can tell you.</p></div>
    <div class="stats">
      <a class="stat" href="/methodology/nmdi/"><div class="l">Canada vs US</div>
        <div class="v">{{eia.ca_us_gap}}<span class="u2">¢/L</span></div>
        <div class="s">{{eia.gap_word}} · Canadian ¢/L, compared on one axis</div></a>
      <a class="stat" href="/methodology/nmdi/"><div class="l">North American index</div>
        <div class="v">{{eia.nadi}}<span class="u2">¢/L</span></div>
        <div class="s">CA + US, equal weight</div></a>
      <a class="stat" href="/exchange-rate/"><div class="l">USD / CAD</div><div class="v">{{fx.usd_cad}}</div>
        <div class="s">{{fx.direction}} {{fx.change}} · Bank of Canada</div></a>
      <a class="stat" href="/border-wait-times/"><div class="l">Border crossings</div>
        <div class="v">85<span class="u2">ports</span></div>
        <div class="s">CBP and CBSA commercial waits</div></a>
      <a class="stat" href="/fuel-tax-rates/"><div class="l">Fuel tax</div><div class="v">58<span class="u2">jurisdictions</span></div>
        <div class="s">IFTA rates, both carrier schedules</div></a>
      <a class="stat" href="/fuel-cost-calculator/"><div class="l">Trip cost</div><div class="v">→</div>
        <div class="s">Work out a lane and a rate floor</div></a>
    </div>
  </section>
'''
    + shared_tail()
    + subscribe(
        "One email, Wednesday mornings",
        "Both sides of the border in one email, with every figure dated and linked back to this "
        "dashboard. Written for people who move freight, not for people who write about it.",
    )
    + foot()
)

print("  ca-home, us-home and the chooser at / written")
