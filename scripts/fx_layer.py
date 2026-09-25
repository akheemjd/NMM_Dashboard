#!/usr/bin/env python3
"""Post-build: the currency layer.

WHY A POST-BUILD PASS RATHER THAN TEMPLATE EDITS

The site publishes money in two native currencies and never labelled either:

    Canada  271.0¢/L      (CAD, cents per litre)
    US      $6.529/gal    (USD, dollars per gallon)

Measured on the built site: 222 ¢/L figures on 97 pages, 135 $/gal figures on 13
pages, and 703 bare $N.NNNN tax figures on 52 pages. Marking those at their
source would mean editing hundreds of template call sites across eight builders,
including one hand-maintained template that has already drifted three times.

The unit carries the currency for 357 of the 1,061 figures — ¢/L is always CAD
and $/gal is always USD — so the work is a single deterministic pass over the
built HTML instead. One script, every page, and it covers pages the builders do
not own.

WHAT IT EMITS

    <span class="fx" data-c="CAD" data-u="cpl" data-v="271.0">271.0¢/L</span>

data-c  native currency    data-u  unit    data-v  the raw number

assets/fx.js reads those and re-renders in the reader's chosen currency. Default
is CAD, which is what the page already shows, so with JS off the site is
unchanged.

WHERE IT WILL NOT TOUCH

Scripts, styles, comments, JSON-LD and attributes are all skipped. A money figure
inside a <script> is calculator input, not page text, and rewriting it would
corrupt the tool. This is verified by construction (the regex runs on the
text-only segments) and guarded afterwards by check_data_integrity.py.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ROOT, "data")

# Slice the document into text we may edit and text we must not.
#
# The nofx comment pair is the explicit opt-out for a block whose figures must not
# convert: a statutory rate you file at is not a price, and converting it produces
# a number that is not the rate. It MUST come before the generic comment
# alternative — Python's re takes the leftmost-FIRST match, not the longest, so a
# later branch would let <!--.*?--> swallow the opening tag alone and the region
# would not be skipped.
SKIP = re.compile(
    r"(<head\b.*?</head>|<script\b.*?</script>|<style\b.*?</style>|"
    r"<!--nofx-->.*?<!--/nofx-->|<!--.*?-->|<[^>]+>)",
    re.S | re.I,
)

# A figure already marked. Idempotent rebuilds must not double-wrap.
ALREADY = re.compile(r'<span class="fx"', re.I)

# <option> cannot contain a <span> — the browser discards the content, which
# blanked the calculator: 22 of 25 fuel-price options lost their labels and the
# output guard then failed. Options get attributes instead, and fx.js rewrites
# option.text (a plain string) rather than injecting markup.
OPTION = re.compile(r'<option\b([^>]*)>([^<]*)</option>', re.I)
OPT_MONEY = re.compile(r'(\d+(?:\.\d+)?)\s*¢/L|\$(\d+\.\d{3})\s*/?\s*gal|\$(\d+\.\d{4})')
FX_OPEN_TAG = re.compile(r'<span class="fx"[^>]*>', re.I)
# Matches both the value marker (.fx) and the unit marker (.fxu). Unwrapping only
# the value left a nested unit marker that hid the unit from mark_pairs, so the
# value was never re-marked on a rebuild that followed a build.
FX_ANY_OPEN = re.compile(r'<span class="fx[^"]*"[^>]*>', re.I)


# <head> is skipped whole. A <title> is a plain text node containing a real
# price, so the text pass matched it and injected markup into the one place
# search engines read most — 92 pages shipped that way.
# Only the regions that must not be REWRITTEN. Unwrapping a marker inside a
# script would delete the calculator's span literal.
#
# <head> is deliberately NOT here: reset() unwraps markers anywhere, so a bad
# marker injected into a <title> by an earlier build self-heals on the next
# run. It is the marking pass (SKIP, above) that skips <head>, because a title
# is a plain text node holding a real price and would be matched again.
# Regions the layer must not touch. The nofx comment pair is the explicit opt-out:
# a statutory rate you file at is not a price, and converting it produces a number
# that is not the rate. Wrapping a block is clearer than teaching the layer to
# recognise its contents.
SKIP_REGION = re.compile(
    r"(<script\b.*?</script>|<style\b.*?</style>|<!--nofx-->.*?<!--/nofx-->|<!--.*?-->)",
    re.S | re.I,
)


def reset(html):
    """Unwrap every existing marker so a run always starts from clean text.

    Markers nest if the idempotency check ever misses, so unwrapping first makes
    the pass self-healing rather than dependent on that check being perfect.

    Script, style and comment regions are skipped. The calculator builds its
    output from a span literal inside JavaScript, and an earlier version of this
    function deleted that literal — the calculator then produced empty strings
    for every money field, with nothing in the page to show why. mark() had this
    guard; reset() did not.
    """
    if 'class="fx' not in html:
        return html

    parts = SKIP_REGION.split(html)
    for i, seg in enumerate(parts):
        if i % 2 == 1:          # a script / style / comment region
            continue
        if 'class="fx' not in seg:
            continue
        out = []
        depth = 0
        idx = 0
        while idx < len(seg):
            m = FX_ANY_OPEN.match(seg, idx)
            if m:
                depth += 1
                idx = m.end()
                continue
            if depth and seg.startswith("</span>", idx):
                depth -= 1
                idx += len("</span>")
                continue
            out.append(seg[idx])
            idx += 1
        parts[i] = "".join(out)
    return "".join(parts)


# Order matters: test the unit-bearing patterns before the bare-dollar one, or
# "$6.529/gal" is eaten as a plain dollar amount.
PATTERNS = [
    # 271.0¢/L  — always CAD cents per litre
    (re.compile(r"(?<![\w.])(\d{2,3}\.\d)\s*¢/L"), "CAD", "cpl"),
    # $6.529/gal or $6.529 /gal — always USD dollars per gallon
    (re.compile(r"\$(\d+\.\d{3})\s*/?\s*gal\b"), "USD", "gpg"),
    # $1.1734 — four-decimal statutory tax figures. Currency depends on the page.
    (re.compile(r"\$(\d\.\d{4})(?!\d)"), None, "plain4"),
    # $1.97 /L — dollars per litre
    (re.compile(r"\$(\d+\.\d{2,3})\s*/L\b"), None, "lpg"),
]

# Which native currency a bare "$" means on which page. A US state page quotes US
# dollars; everything Canadian quotes Canadian. Mixed pages are resolved by the
# unit-bearing patterns above, which never consult this.
# rel comes from os.path.relpath, so it has NO trailing slash: the US hub is
# "us-diesel", not "us-diesel/". Anchoring on a slash silently matches nothing.
PAGE_CURRENCY = [
    (re.compile(r"^us-diesel(/|$)"), "USD"),
    (re.compile(r"^border-wait-times/all-ports(/|$)"), "USD"),
    (re.compile(r"^fuel-tax-rates(/|$)"), "USD"),   # IFTA US rows; provinces are CA
]

# The currency a page opens in for a first-time reader, as opposed to the source
# currency of the figures on it (PAGE_CURRENCY above). A reader who has already
# chosen keeps their choice — this is only the default.
PAGE_DEFAULT = [
    (re.compile(r"^us$"), "USD"),
    (re.compile(r"^us-diesel(/|$)"), "USD"),
    (re.compile(r"^fuel-tax-rates(/|$)"), "USD"),
    (re.compile(r"^border-wait-times/all-ports(/|$)"), "USD"),
]


def page_default_currency(rel):
    for pat, cur in PAGE_DEFAULT:
        if pat.match(rel):
            return cur
    return "CAD"


def page_currency(rel):
    for pat, cur in PAGE_CURRENCY:
        if pat.match(rel):
            return cur
    return "CAD"


TOGGLE = (
    '<div class="fxtog" role="group" aria-label="Display currency" '
    'data-curdefault="{default}" '
    'title="Figures convert at the live Bank of Canada rate">'
    '<button type="button" data-cur="CAD" aria-pressed="true">CAD</button>'
    '<button type="button" data-cur="USD" aria-pressed="false">USD</button>'
    '</div>'
)

# Injected into the nav on every page by the same pass that marks the figures, so
# there is exactly one place to change it. Authoring it into the templates would
# mean gen_templates.py AND the hand-maintained border-trends template, which has
# already drifted three times this month.
# The toggle lives in the header, not the nav. Same content column, and the
# header's space-between puts it flush right with room to spare.
HD_END = re.compile(r'(</div>\s*</header>)', re.I)
SCRIPT_END = re.compile(r'(<script src="/assets/nm\.js\?v=[^"]*"></script>)', re.I)


NAV_OPEN = re.compile(
    r'(<nav class="nav"[^>]*>\s*<div class="wrap">)', re.I
)
NAV_CLOSE = re.compile(r'(</div>\s*</nav>)', re.I)
NAV_WRAPPED = re.compile(r'<div class="nv">', re.I)


def wrap_navlinks(html):
    """Wrap the nav's inner content in .nv so the toggle gets its own slot.

    Idempotent: a build that runs twice must not nest another .nv.
    """
    if NAV_WRAPPED.search(html):
        return html
    m = NAV_OPEN.search(html)
    if not m:
        return html
    start = m.end()
    c = NAV_CLOSE.search(html, start)
    if not c:
        return html
    return (
        html[:start]
        + '<div class="nv">'
        + html[start:c.start()]
        + "</div>"
        + html[c.start():]
    )


CA_PATH = re.compile(r"^(ca$|ca/|diesel-prices(/|$)|fuel-prices(/|$))")
US_PATH = re.compile(r"^(us$|us/|us-diesel(/|$))")


def country_switch_html(rel):
    """Canada / US switcher, with the active option taken from the page path."""
    ca_on = bool(CA_PATH.match(rel))
    us_on = bool(US_PATH.match(rel))

    def opt(href, label, on):
        cls = "seg-opt is-on" if on else "seg-opt"
        cur = ' aria-current="true"' if on else ""
        return f'<a class="{cls}"{cur} href="{href}">{label}</a>'

    return ('<div class="seg" role="group" aria-label="Country">'
            + opt("/ca/", "Canada", ca_on)
            + opt("/us/", "US", us_on)
            + "</div>")


def add_country_switch(html, rel):
    """Insert the switcher into the header, beside the currency toggle. Idempotent.

    Same placement as the toggle: the header's space-between puts the pair flush
    right with nothing to collide with. The nav scrolls horizontally and a sticky
    child of a scroll container overlaps, which is why neither control lives there.
    """
    if 'aria-label="Country"' in html:
        return html
    if not HD_END.search(html):
        return html
    return HD_END.sub(lambda m: country_switch_html(rel) + m.group(1), html, count=1)


def add_toggle(html, rel=""):
    """Insert the currency toggle into the header and load fx.js. Idempotent.

    rel decides the default currency the page opens in. A stored choice still wins —
    this is only what a first-time reader sees.
    """
    if 'class="fxtog"' in html:
        return html

    toggle = TOGGLE.replace("{default}", page_default_currency(rel))

    if HD_END.search(html):
        html = HD_END.sub(lambda m: toggle + m.group(1), html, count=1)
    else:
        # No header to attach to: still ship the script so marked figures convert.
        pass

    # Load the converter after nm.js. Mirrors that tag's cache-buster rather than
    # inventing one, because check_data_integrity requires every asset to carry a
    # version and a bare /assets/fx.js would fail that guard.
    m = SCRIPT_END.search(html)
    if m:
        ver = re.search(r'\?v=([^"]*)', m.group(1))
        v = ver.group(1) if ver else ""
        html = html.replace(m.group(1),
                            m.group(1) + f'\n<script src="/assets/fx.js?v={v}"></script>',
                            1)
    return html


# A number in a value element immediately followed by a unit element.
#
#     <span class="n">271.0</span><span class="u">¢/L</span>
#     <div class="v down">247.3</div><div class="s">AB · ¢/L</div>
#
# Group 1 = opening tag, 2 = the number, 3 = the closing tag + unit opening tag,
# 4 = the unit text.
PAIR = re.compile(
    r'(<(?:div|span) class="(?:v|n)[^"]*"[^>]*>)([\d.,]+)'
    r'(</(?:div|span)>\s*<(?:div|span) class="(?:s|u)[^"]*"[^>]*>)([^<]*)',
    re.S,
)


# The unit token inside a unit element, so the label follows the value.
UNIT_TOKEN = re.compile(r"(" + chr(0xa2) + "/L|\$/gal)")


def mark_unit(unit_text):
    """Wrap a unit token whose LABEL changes with the currency.

    Only per-gallon labels change, and only by their currency prefix. A ¢/L
    label is correct in both currencies and is returned untouched — marking it
    would flip litres to gallons on toggle, which is what the currency model
    deliberately no longer does.
    """
    usd = "$/gal"
    cad = "C" + usd

    def one(m):
        tok = m.group(1)
        if tok != usd:
            return tok          # ¢/L, or a bare ¢ — the dimension never moves
        return ('<span class="fxu" data-u="' + cad + "|" + usd + '">' + tok + "</span>")

    return UNIT_TOKEN.sub(one, unit_text)
def mark_pairs(html, cur_default):
    """Mark number/unit pairs. Skipped by the later text pass, which sees the
    inserted marker as the preceding tag.

    The unit text decides both unit and currency, and a pair whose unit does not
    name one is left alone: exchange rates and counts live in this shape too.
    """
    def one(m):
        open_v, num, mid, unit = m.group(1), m.group(2), m.group(3), m.group(4)
        if "class=\"fx\"" in open_v:
            return m.group(0)
        if "\u00a2/L" in unit:
            u, c = "cpl", cur_default
        elif "/gal" in unit:
            u, c = "gpg", "USD"
        else:
            return m.group(0)          # a rate or a count, not a price
        # data-bare: the unit is displayed by the sibling element, so the value
        # renders as a plain number while still converting as its source unit.
        inner = (f'<span class="fx" data-c="{c}" data-u="{u}" data-bare="1" '
                 f'data-v="{num}">{num}</span>')
        return open_v + inner + mid + mark_unit(unit)
    return PAIR.sub(one, html)


# Canadian rail rows: class="val", "val up" or "val down". Deliberately NOT
# "val us" — that is the US rail and it is dollars per gallon, matched below.
RAIL_VAL = re.compile(
    r'(<span class="val(?: (?:up|down))?"[^>]*>)(\d+(?:\.\d+)?)(</span>)'
)
RAIL_VAL_US = re.compile(
    r'(<span class="val us"[^>]*>)(\d+(?:\.\d+)?)(</span>)'
)
# Canadian mean marker: "Index 268.5" — cents per litre.
RAIL_MEAN = re.compile(
    r'(<span class="lab">Index\s+)(\d+(?:\.\d+)?)(</span>)'
)
# US mean marker: "US avg 6.529" — dollars per gallon. It looked like the Canadian
# one but the label word differs, so it went unmarked and stayed in USD while the
# rows beneath it converted.
RAIL_MEAN_US = re.compile(
    r'(<span class="lab">US avg\s+)(\d+(?:\.\d+)?)(</span>)'
)
# The rail heading's two endpoints. Both rails use an identical .sp, so the unit is
# read from the caption's own trailing token: the Canadian cap ends ¢/L and the US
# cap ends $/gal. Assuming cpl rendered the US heading as 6.1 and 8.2 while its
# rows showed 8.678 and 11.657.
RAIL_CAP = re.compile(r'<span class="sp">(.*?)</span>', re.S)
CAP_ENDPOINT = re.compile(r'(<b>)(\d+(?:\.\d+)?)(</b>)')
BARE_CENTS = re.compile(r'(?<![\w.])(\d+(?:\.\d+)?)\u00a2(?!/L)')


def mark_block_figures(html, cur_default):
    """Figures whose unit is implied by the block they sit in.

    These carry no unit text and no .v/.s sibling, so neither the text pass nor
    mark_pairs can see them. In the Canadian provinces rail and the ten-year
    series the unit is unambiguous: cents per litre.
    """
    def bare(num):
        return (f'<span class="fx" data-c="{cur_default}" data-u="cpl" '
                f'data-bare="1" data-v="{num}">{num}</span>')

    def bare_us(num):
        # EIA publishes dollars per gallon natively, so the source currency is USD
        # and the unit stays a gallon whichever currency is on display.
        return (f'<span class="fx" data-c="USD" data-u="gpg" '
                f'data-bare="1" data-v="{num}">{num}</span>')

    # US rows first. RAIL_VAL's pattern cannot match "val us", so order does not
    # matter for correctness — but running the narrower rule first keeps that
    # obvious to whoever edits this next.
    html = RAIL_VAL_US.sub(lambda m: m.group(1) + bare_us(m.group(2)) + m.group(3), html)
    html = RAIL_VAL.sub(lambda m: m.group(1) + bare(m.group(2)) + m.group(3), html)
    html = RAIL_MEAN.sub(lambda m: m.group(1) + bare(m.group(2)) + m.group(3), html)
    html = RAIL_MEAN_US.sub(lambda m: m.group(1) + bare_us(m.group(2)) + m.group(3), html)
    # Each rail's heading carries the unit in its own trailing token, so the two
    # endpoints are marked in whichever unit that caption declares.
    def _cap(m):
        inner = m.group(1)
        fn = bare_us if "/gal" in inner else bare
        return '<span class="sp">' + CAP_ENDPOINT.sub(
            lambda e: e.group(1) + fn(e.group(2)) + e.group(3), inner
        ) + "</span>"

    html = RAIL_CAP.sub(_cap, html)
    # A bare cents figure: mark the number, leave the symbol in place. In USD the
    # value converts and the symbol stays — cents per litre, in USD.
    return BARE_CENTS.sub(lambda m: bare(m.group(1)) + "\u00a2", html)


def annotate_options(seg, cur_default):
    """Annotate money-bearing <option> tags so fx.js can rewrite their labels.

    Keeps the prefix ("National average") in data-fxlabel and the native price in
    data-fxv, so the renderer can rebuild the whole label in either currency.
    """
    def one(m):
        attrs, text = m.group(1), m.group(2)
        if "data-fxv" in attrs:
            return m.group(0)
        mm = OPT_MONEY.search(text)
        if not mm:
            return m.group(0)
        if mm.group(1):                      # 271.0 ¢/L
            raw, unit = mm.group(1), "cpl"
        elif mm.group(2):                    # $6.529/gal
            raw, unit = mm.group(2), "gpg"
        else:                                # $0.2600
            raw, unit = mm.group(3), "p4"
        label = re.split(r"\s+[—-]\s+|\s*\(", text, 1)[0].strip()
        return (f'<option{attrs} data-fxc="{cur_default}" data-fxu="{unit}" '
                f'data-fxv="{raw}" data-fxlabel="{label}">{text}</option>')
    return OPTION.sub(one, seg)


def mark(html, rel):
    """Wrap money figures in .fx markers. Returns (html, count)."""
    html = reset(html)
    cur_default = page_currency(rel)
    # Options first, on the whole document: their labels cannot hold markup, so
    # they are annotated with attributes and left as plain text.
    html = annotate_options(html, cur_default)
    html = mark_pairs(html, cur_default)
    html = mark_block_figures(html, cur_default)
    parts = SKIP.split(html)
    out = []
    n = 0

    for idx, seg in enumerate(parts):
        if idx % 2 == 1:          # a captured skip group
            out.append(seg)
            continue
        if not seg:
            continue
        if ALREADY.search(seg):
            out.append(seg)
            continue
        # Idempotency. After a first run the marker tags are their own skip
        # groups, so the inner value ("271.0¢/L") reappears as a clean text
        # segment and would be wrapped again — nesting one level deeper on every
        # deploy, 48 times a day. If the group immediately before this text is a
        # .fx opening tag, this text is already rendered by that marker.
        #
        # Deliberately narrow: an earlier version also skipped anything with an
        # unclosed <span> before it, which silently dropped every figure sitting
        # inside a presentation span — 68 pages lost markers that way. Match the
        # marker, not the shape of surrounding markup. reset() is the backstop
        # for anything this still misses.
        if idx > 0 and FX_OPEN_TAG.match(parts[idx - 1].lstrip()):
            out.append(seg)
            continue
        # <option> labels are handled by annotate_options. A span here is invalid
        # and the browser silently drops it.
        if idx > 0 and parts[idx - 1].lstrip().lower().startswith("<option"):
            out.append(seg)
            continue

        def sub(m, cur, unit):
            raw = m.group(1)
            return (f'<span class="fx" data-c="{cur}" data-u="{unit}" '
                    f'data-v="{raw}">{m.group(0)}</span>')

        for pat, cur, unit in PATTERNS:
            c = cur or cur_default
            if unit == "plain4":
                # A four-decimal dollar figure in text is a statutory fuel tax
                # rate. Keep it distinct from a plain dollar amount so the
                # renderer does not round it to two decimals.
                seg, k = pat.subn(lambda m: sub(m, c, "p4"), seg, count=0)
            elif unit == "lpg":
                seg, k = pat.subn(lambda m: sub(m, c, "lpg"), seg, count=0)
            else:
                seg, k = pat.subn(lambda m: sub(m, c, unit), seg, count=0)
            n += k
        out.append(seg)

    return "".join(out), n


def write_rate():
    """Publish the live rate where the browser can read it."""
    src = os.path.join(DATA, "fx.norm.json")
    raw = json.load(open(src, encoding="utf-8"))
    fx = raw.get("fx") or {}
    rate = fx.get("usd_cad")
    # fx.norm.json calls it obs_date. Checking three keys rather than one so a
    # rename upstream degrades to an empty label instead of killing the build,
    # but the real value must be present or we refuse below.
    as_of = fx.get("obs_date") or fx.get("date") or fx.get("observation_date") or ""
    if not rate or float(rate) <= 0:
        raise SystemExit("fx_layer: no usable usd_cad in fx.norm.json — refusing "
                         "to publish a rate file the toggle would fail on")
    out = {"usd_cad": float(rate), "as_of": str(as_of)[:10],
           "generated": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    os.makedirs(os.path.join(DOCS, "assets"), exist_ok=True)
    with open(os.path.join(DOCS, "assets", "fx.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"  fx.json: USD/CAD {out['usd_cad']} as of {out['as_of']}")
    return out


def main():
    info = write_rate()
    pages = 0
    total = 0
    for dirpath, _dirs, files in os.walk(DOCS):
        for fn in files:
            if fn != "index.html":
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(dirpath, DOCS).replace("\\", "/")
            if rel == ".":
                rel = ""
            html = open(path, encoding="utf-8").read()
            html, n = mark(html, rel)
            html = wrap_navlinks(html)
            html = add_country_switch(html, rel)
            html = add_toggle(html, rel)
            open(path, "w", encoding="utf-8").write(html)
            pages += 1
            total += n
    print(f"  fx markers: {total} figures across {pages} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
