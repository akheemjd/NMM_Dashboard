"""The nav, in a module both the template generator and the post-build pass can use.

WHY THIS EXISTS

templates/border-trends.template.html is hand-maintained and carries its own copy of
the nav. When the nav was rebuilt it kept the old thirteen-link version, and the
coherence guard reported it as the single page with different chrome.

Chrome authored per template drifts. That is already recorded for the currency toggle
and the country switch, which is why both are injected post-build. The nav belongs in
the same category: it is chrome, it appears on every page, and no template should be
able to author its own version of it.

So the nav now lives here, gen_templates imports it to build the markup, and fx_layer
REPLACES whatever nav a page arrives with. A hand-maintained template that ships a
stale nav gets corrected on the way out instead of drifting until a guard notices.
"""
import re

# Five groups instead of thirteen peer links: the grouping is the information. Nothing
# about a flat list of thirteen says that Barometer, Market, Exchange and News are one
# subject, or that Diesel, Fuel tax and Calculator are another.
#
# Each group link carries data-tree="diesel" so the post-build pass can point it into
# the reader's own tree. The strip's "Canada by province" link must not be rewritten on
# a US page, which is why that rewrite is keyed on the attribute and not on the href.
NAV_GROUPS = [
    ("Diesel", "/fuel-prices/", "diesel", [
        ("/fuel-prices/", "Canada by province", "Ten provinces, NRCan weekly survey"),
        ("/us-diesel/", "US by district", "Ten EIA districts, dollars per gallon"),
        ("/us-diesel/states/", "US by state", "Fuel tax and district diesel"),
    ]),
    ("Border", "/border-wait-times/", "", [
        ("/border-wait-times/", "Wait times", "Nine crossings, CBSA capture times"),
        ("/border-wait-times/all-ports/", "All 85 ports", "CBP commercial lanes"),
        ("/border-trends/", "Trends", "Where waits have moved"),
    ]),
    ("Cost", "/fuel-cost-calculator/", "", [
        ("/fuel-cost-calculator/", "Trip calculator", "Lane cost and rate floor"),
        ("/fuel-tax-rates/", "Fuel tax", "IFTA rates, both schedules"),
    ]),
    ("Market", "/freight-barometer/", "", [
        ("/freight-barometer/", "Freight barometer", "Demand direction"),
        ("/market-pulse/", "Market pulse", "GDP, spreads, congestion"),
        ("/exchange-rate/", "Exchange rate", "USD/CAD, Bank of Canada"),
        ("/road-incidents/", "Road incidents", "Closures and collisions"),
        ("/industry-news/", "Industry news", "Headlines, sourced"),
    ]),
    ("About", "/methodology/nmdi/", "", [
        ("/methodology/nmdi/", "Methodology", "Every source and revision"),
        ("/press/", "Press", "Citable data and citations"),
        ("/contact/", "Contact", "Corrections and sponsorship"),
    ]),
]


def nav_group_for(canon):
    """Which group a page belongs to. Longest matching href wins.

    Order matters: /us-diesel/states/ and /us-diesel/ are both children of Diesel, so a
    short prefix must not shadow a longer one.
    """
    # The country homepages are the diesel entry points. / is the choice and belongs to
    # no section, which is why the chooser shows no strip.
    if canon in ("/ca/", "/us/"):
        return "Diesel"
    best, span = "", -1
    for name, href, _tree, kids in NAV_GROUPS:
        for khref, _lab, _desc in kids:
            if (canon == khref or canon.startswith(khref)) and len(khref) > span:
                best, span = name, len(khref)
    return best


def nav_groups_html(canon):
    """The five group links, with the current page's group marked."""
    here = nav_group_for(canon)
    out = []
    for name, href, tree, _kids in NAV_GROUPS:
        on = ' class="ng on"' if name == here else ' class="ng"'
        cur = ' aria-current="true"' if name == here else ""
        dt = f' data-tree="{tree}"' if tree else ""
        out.append(f'<a href="{href}"{on}{cur}{dt}>{name}'
                   f'<span class="chev" aria-hidden="true"></span></a>')
    return "".join(out)


def nav_strips_html(canon):
    """Every group's children, one strip visible.

    All five are emitted so every link is in the DOM for a crawler, and so the current
    group still shows with JS off. Only the current one lacks the hidden attribute.
    """
    here = nav_group_for(canon)
    out = []
    for name, _href, _tree, kids in NAV_GROUPS:
        on = name == here
        hidden = "" if on else " hidden"
        cls = "strip on" if on else "strip"
        links = "".join(f'<a href="{h}">{l}</a>' for h, l, _d in kids)
        out.append(f'<div class="{cls}" data-group="{name}"{hidden}>'
                   f'<div class="wrap">{links}'
                   f'<span class="hint">{name}</span></div></div>')
    return "".join(out)


def nav_drawer_html(canon):
    """The mobile drawer: the same groups as a list. Hidden until the button.

    Emitted on every page including the chooser, where the header carries no controls
    but a reader still needs to reach the sections.
    """
    here = nav_group_for(canon)
    out = ['<div class="drawer" id="drawer" hidden><div class="wrap">']
    for name, href, tree, kids in NAV_GROUPS:
        out.append(f'<div class="dgrp"><b>{name}</b>')
        for h, l, _d in kids:
            cls = "dg on" if h == canon else "dg"
            dt = f' data-tree="{tree}"' if (tree and h == href) else ""
            out.append(f'<a class="{cls}" href="{h}"{dt}>{l}</a>')
        out.append("</div>")
    out.append('<div class="dgrp"><b>More</b>'
               '<a class="dg" href="/advertise/">Advertise</a>'
               '<a class="dg" href="/contact/">Contact</a></div>')
    out.append("</div></div>")
    return "".join(out)


# Explicit boundaries. The drawer contains nested divs, so a non-greedy
# `.*?</div></div>` stops inside it rather than at its end — which made replace_nav
# leave a partial drawer behind and append a new one on every pass.
NAV_START = "<!--navstart-->"
NAV_END = "<!--navend-->"


def nav_block(canon):
    """The whole nav: group row, strips, drawer, between two boundary markers."""
    return (NAV_START
            + '<nav class="nav" aria-label="Sections"><div class="wrap">'
            + nav_groups_html(canon)
            + '</div></nav>'
            + nav_strips_html(canon)
            + nav_drawer_html(canon)
            + NAV_END)


NAV_ANY = re.compile(r'<nav class="nav".*?</nav>', re.S)


def canon_of(rel):
    """A docs-relative path as the canonical form the group matcher expects."""
    return "/" if rel == "" else "/" + rel.strip("/") + "/"


def replace_nav(html, rel):
    """Swap whatever nav the page arrived with for the generated one.

    Two cases:

      * a page that already carries a generated nav, boundaries and all — the marked
        block comes out and the same block goes back in, so a second run changes nothing
      * a page from a hand-maintained template, which carries a nav but no strips, no
        drawer and no boundaries — just the nav element is replaced

    This exists because templates/border-trends.template.html authors its own chrome.
    A template should not be able to publish a nav of its own, so whatever it ships gets
    corrected on the way out.
    """
    canon = canon_of(rel)
    if NAV_START in html:
        # Replace the marked block in one step. Removing it first and then searching for
        # a nav to substitute removed the very thing it was looking for: the block
        # contains the nav, so the search found nothing and the nav disappeared.
        return re.sub(re.escape(NAV_START) + r".*?" + re.escape(NAV_END),
                      lambda m: nav_block(canon), html, flags=re.S, count=1)
    if not NAV_ANY.search(html):
        return html
    return NAV_ANY.sub(lambda m: nav_block(canon), html, count=1)
