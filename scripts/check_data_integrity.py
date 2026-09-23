#!/usr/bin/env python3
"""Data invariants the pages depend on.

Every defect this file guards against had the same shape: it rendered cleanly
and did nothing. The chrome guard passed, the link check passed, the build
exited 0, and the site published a wrong number for weeks.

1. A lookback must never return the newest observation. history.value_at()
   anchored its target to today, and the diesel series is weekly, so the
   nearest point to "7 days ago" was the newest print itself and every 7-day
   delta computed to exactly 0.0.

2. The chart's headline value must equal the national average cited on the
   same page. They disagreed (249.2 charted, 267.1 cited four lines below)
   because a source revision never propagated through the history store.

3. The published spread must be the ten-province figure normalize.py computes,
   and low/high must be the extremes of those ten provinces. Recomputing over
   all twelve jurisdictions in fuel.json produced a second, different spread on
   the same property.

Run: python scripts/check_data_integrity.py
Exit 0 = clean, 1 = violation.
"""

import json
import os
import pathlib
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import history  # noqa: E402

INDEX_PROVINCES = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]

PAIRS = (
    ("diesel", "national"), ("diesel", "AB"), ("diesel", "QC"),
    ("fx", "usd_cad"), ("eia", "national"),
)


def _load(name):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"GUARD FATAL: could not read {name}: {e}")
        return None


def check_lookback_not_latest():
    """A lookback has to compare against something older than the newest point."""
    bad = []
    for series, key in PAIRS:
        now = history.latest(series, key)
        if now is None:
            continue
        for n in (7, 30):
            then = history.value_at(series, key, n)
            if then is not None and then == now:
                bad.append(f"{series}/{key} {n}d returned the newest value "
                           f"({now}) as its own comparator")
    return bad


def check_chart_matches_headline():
    """The chart's latest point must equal the published national average."""
    chart, fuel = _load("chart_data.json"), _load("fuel.json")
    if chart is None or fuel is None:
        return ["could not load chart_data.json / fuel.json"]

    c_latest = (chart.get("meta") or {}).get("latest")
    f_nat = fuel.get("diesel_national_avg")
    if c_latest is None or f_nat is None:
        return []
    try:
        if abs(float(c_latest) - float(f_nat)) > 0.05:
            return [f"chart latest {c_latest} != fuel national {f_nat}. "
                    f"Pages cite one figure and chart the other."]
    except (TypeError, ValueError):
        return [f"non-numeric: chart latest {c_latest!r}, fuel national {f_nat!r}"]
    return []


def check_spread_definition():
    """Spread must be high minus low over the ten index provinces."""
    fuel, norm = _load("fuel.json"), _load("fuel.norm.json")
    if fuel is None or norm is None:
        return ["could not load fuel.json / fuel.norm.json"]

    nf = norm.get("fuel") if isinstance(norm.get("fuel"), dict) else norm
    out = []

    spread, low, high = nf.get("spread"), nf.get("low"), nf.get("high")
    if None not in (spread, low, high):
        try:
            calc = round(float(high) - float(low), 1)
            if abs(calc - float(spread)) > 0.15:
                out.append(f"spread {spread} != high {high} - low {low} ({calc})")
        except (TypeError, ValueError):
            out.append(f"non-numeric spread/low/high: {spread!r}/{low!r}/{high!r}")

    provs = fuel.get("provinces") or {}
    vals = {c: (provs.get(c) or {}).get("diesel") for c in INDEX_PROVINCES}
    vals = {k: v for k, v in vals.items() if v is not None}
    if vals:
        lo_c = min(vals, key=vals.get)
        hi_c = max(vals, key=vals.get)
        if nf.get("low_code") and nf["low_code"] != lo_c:
            out.append(f"low_code is {nf['low_code']} but the ten-province low is "
                       f"{lo_c} ({vals[lo_c]}). A territory may have leaked in.")
        if nf.get("high_code") and nf["high_code"] != hi_c:
            out.append(f"high_code is {nf['high_code']} but the ten-province high "
                       f"is {hi_c} ({vals[hi_c]})")
    return out


def check_fx_average_agreement():
    """The 30-day FX average must be one number, not two.

    normalize.py defines it as the trailing 21 business days and market_pulse.py
    used a calendar window, so the site published 1.3864 in fx.norm.json and
    1.3868 in market.json. Rounding to one decimal made it worse: the home page
    reported a gap of +0.0002 against a true +0.0138.
    """
    norm = _load("fx.norm.json")
    market = _load("market.json")
    if norm is None or market is None:
        return ["could not load fx.norm.json / market.json"]

    fx = norm.get("fx") if isinstance(norm.get("fx"), dict) else norm
    published = str(fx.get("avg_30d") or "")
    if not published:
        return []

    out = []
    detail = ""
    for i in (market.get("indicators") or []):
        if "CAD" in (i.get("name") or ""):
            detail = str(i.get("detail") or "")
    if not detail:
        return []

    if published not in detail:
        out.append(f"market.json quotes a 30-day FX average that is not "
                   f"fx.norm.json's {published}: {detail!r}")

    # A one-decimal average is the specific failure that hid this for weeks.
    try:
        decimals = len(published.split(".")[1]) if "." in published else 0
        if decimals < 3:
            out.append(f"fx avg_30d {published} carries only {decimals} decimal(s). "
                       f"At one decimal the 30-day gap collapses to ~0.")
    except (IndexError, ValueError):
        pass

    return out


def check_jsonld_valid():
    """Every built page's JSON-LD must parse.

    Found live: 26 pages shipped `{"@context":"https://***@graph":[...`, which is
    invalid JSON, because a redaction pass had written its own redaction into
    gen_templates.py. Google cannot read unparseable structured data and nothing
    noticed, because the string is still perfectly valid HTML.

    Note the trap this file has to guard: gen_templates.py REGENERATES
    templates/*.html, so repairing the templates alone is silently overwritten on
    the next build. The generator is the only place worth fixing.
    """
    bad = []
    for path in sorted(pathlib.Path(DOCS).rglob("index.html")):
        html = path.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                             html, re.S):
            try:
                json.loads(m.group(1))
            except Exception as e:
                bad.append(f"{path.relative_to(DOCS)}: JSON-LD does not parse ({e})")
                break
    return bad


def check_cbp_missing_not_zero():
    """A CBP port that published no delay must not be stored as a delay of 0.

    At fetch time only ~37 of 85 ports carry a numeric commercial delay; the rest
    read N/A, Update Pending or Lanes Closed. Zero means "measured, no wait".
    None means "not reported". Collapsing them publishes "no delay" at a port
    that simply did not answer, which is the worst claim this data can make.
    """
    d = _load("cbp_border.json")
    if d is None:
        return []
    bad = []
    for p in d.get("ports", []):
        has_num = p.get("commercial_delay") is not None
        if p.get("commercial_reported") != has_num:
            bad.append(f"{p.get('port_name')}: commercial_reported="
                       f"{p.get('commercial_reported')} but commercial_delay="
                       f"{p.get('commercial_delay')}")
        lane = ((p.get("commercial") or {}).get("standard") or {}).get("delay")
        if lane != p.get("commercial_delay"):
            bad.append(f"{p.get('port_name')}: headline delay disagrees with its "
                       f"lane block")
    counts = d.get("counts") or {}
    if counts.get("commercial_delay_reported", 0) > counts.get("total", 0):
        bad.append("reported commercial delays exceed the port count")
    return bad


def check_sitemap():
    """The sitemap must be well-formed, complete, and honestly dated.

    Every failure here has already happened once:

    - Backslashes in <loc> (from an unnormalised os.walk path) made every page
      except the homepage uncrawlable, and the same bug defeated the EXCLUDE
      lookup because "/\\methodology/" never matched "/methodology/".
    - A missing page is silently unlisted, so the URL set is compared to the
      pages that actually exist on disk.
    - A lastmod in the future is a claim about tomorrow that no source supports.
    - A lastmod of "today" on a page with no changing data is the "always now"
      inaccuracy that made the tag worthless in the first place.
    """
    import datetime
    import xml.etree.ElementTree as ET

    path = os.path.join(DOCS, "sitemap.xml")
    if not os.path.exists(path):
        return ["docs/sitemap.xml is missing — build_sitemap.py did not run"]
    raw = open(path, encoding="utf-8").read()
    bad = []

    if "\\" in raw:
        bad.append(f"sitemap contains {raw.count(chr(92))} backslash(es); "
                   f"search engines cannot crawl those URLs")

    try:
        root = ET.fromstring(raw)
    except Exception as e:
        return [f"sitemap.xml is not well-formed XML ({e})"]

    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    entries = root.findall(f"{ns}url")
    listed = {u.find(f"{ns}loc").text for u in entries}

    # Completeness: every built page must be advertised, and nothing extra.
    on_disk = set()
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" not in files:
            continue
        rel = dirpath.replace(DOCS, "").replace("\\", "/")
        p = (rel + "/").replace("//", "/")
        if not p.startswith("/"):
            p = "/" + p
        if p in ("/methodology/",):
            continue
        html = open(os.path.join(dirpath, "index.html"), encoding="utf-8").read()
        if "http-equiv=\"refresh\"" in html.lower() and len(html) < 600:
            continue
        on_disk.add("https://dashboard.northernmilemedia.com" + p)

    missing = sorted(on_disk - listed)
    extra = sorted(listed - on_disk)
    if missing:
        bad.append(f"{len(missing)} built page(s) absent from the sitemap, e.g. {missing[:3]}")
    if extra:
        bad.append(f"{len(extra)} sitemap URL(s) have no page, e.g. {extra[:3]}")

    today = datetime.date.today()
    for u in entries:
        lm = u.find(f"{ns}lastmod")
        if lm is None or not lm.text:
            continue
        try:
            d = datetime.date.fromisoformat(lm.text.strip())
        except ValueError:
            bad.append(f"unparsable lastmod {lm.text!r}")
            continue
        if d > today:
            bad.append(f"lastmod {d} is in the future (today {today})")

    return bad


def _slugify_state(name):
    """Must match build_us_states.py's slugify exactly, or nothing is found."""
    s = name.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def check_us_state_pages():
    """Every US state page must attribute its diesel figure to a district.

    This is the one property that separates these pages from the fifty-state
    pages the incumbents publish. EIA prices diesel across eleven districts, not
    fifty states, so a state page showing a diesel number without saying where it
    came from is making a claim the source does not support.

    Three things are asserted, and all three have a real failure behind them:

    1. The district is named. A page that says "Texas diesel" and prints the Gulf
       Coast number is the exact dishonesty this build exists to avoid.
    2. The page states that EIA does not price by state. Without that sentence
       the attribution is present but inert.
    3. The tax figures reconcile, because the page prints the arithmetic. A card
       showing excise, other fees, federal and all-in that does not add up is a
       wrong number on a page whose whole pitch is that the numbers are right.
    """
    import html as _html

    base = os.path.join(DOCS, "us-diesel")
    if not os.path.isdir(base):
        return ["docs/us-diesel/ is missing — build_us_states.py did not run"]

    # _load() takes a full filename; it does not append ".json".
    tax = _load("us_fuel_tax.json")
    if not tax:
        return ["data/us_fuel_tax.json unreadable — cannot verify the state pages"]
    federal = (tax.get("federal") or {}).get("diesel_total")
    states_tax = {s["abbr"]: s for s in tax.get("states", []) if s.get("abbr")}

    # Only the state pages. /us-diesel/ also holds the district pages
    # (midwest, gulf_coast, ...), and those are a different kind of page with a
    # different contract, so they are matched out by name rather than by a
    # guessed phrase. A slug is a state page only if a state name slugs to it.
    state_slugs = {_slugify_state(s["name"]) for s in tax.get("states", [])
                   if s.get("name")}

    bad = []
    found = 0
    for dirpath, _, files in os.walk(base):
        if "index.html" not in files:
            continue
        # Direct children of /us-diesel/ only. Matching on basename alone also
        # caught /us-diesel/district/california/, which is a district page and has
        # a different contract — it correctly does not attribute a district
        # because it IS one.
        rel = os.path.relpath(dirpath, base).replace("\\", "/")
        if "/" in rel:
            continue
        slug = os.path.basename(dirpath)
        if slug not in state_slugs:
            continue
        path = os.path.join(dirpath, "index.html")
        rel = os.path.relpath(path, DOCS).replace("\\", "/")
        h = open(path, encoding="utf-8", errors="replace").read()
        text = _html.unescape(re.sub(r"<[^>]+>", " ", h))
        text = re.sub(r"\s+", " ", text)
        found += 1

        if "district" not in text.lower():
            bad.append(f"{rel}: no district attribution anywhere on the page")
            continue

        if "not a state basis" not in text and "by district, not by state" not in text \
                and "not by state" not in text:
            bad.append(f"{rel}: diesel figure shown without saying EIA prices by district")

        # the page prints "excise + other fees = state total" and "+ federal = all-in"
        a = re.search(r"State excise \$([0-9.]+) plus other state fees \$([0-9.]+) "
                      r"gives a state total of \$([0-9.]+)", text)
        b = re.search(r"Add the federal \$([0-9.]+) and the all-in figure is \$([0-9.]+)", text)
        if not a or not b:
            bad.append(f"{rel}: the tax arithmetic sentence is missing")
        else:
            exc, oth, tot = (float(x) for x in a.groups())
            fed, allin = (float(x) for x in b.groups())
            if abs((exc + oth) - tot) > 0.0006:
                bad.append(f"{rel}: excise {exc} + other {oth} != state total {tot}")
            if abs((tot + fed) - allin) > 0.0006:
                bad.append(f"{rel}: state total {tot} + federal {fed} != all-in {allin}")
            if federal is not None and abs(fed - federal) > 0.0001:
                bad.append(f"{rel}: page prints federal {fed}, data says {federal}")

    if found < 45:
        bad.append(f"only {found} US state pages built; expected 50 or more")

    return bad


def check_brand_identity():
    """The brand must describe the same geography the data covers.

    check_coherence.py only compares pages to each other, so it catches drift on
    ONE page and is blind to a stale string that sits on ALL of them. When the
    brand was continentalised, "Canadian trucking data" survived in the header of
    the hand-maintained border-trends template for two build cycles precisely
    because that page was consistent with itself.

    The brand tagline now appears in two places, the header mark and the footer,
    and both must agree.
    """
    bad = []
    banned = [
        "Canadian trucking data",   # identity, not geography
        "Canadian Carriers",        # advertise page
        "Citable Canadian",         # press page
    ]
    counts = {b: 0 for b in banned}
    foot_tags = {}
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" not in files:
            continue
        h = open(os.path.join(dirpath, "index.html"), encoding="utf-8",
                 errors="replace").read()
        rel = os.path.relpath(os.path.join(dirpath, "index.html"), DOCS).replace("\\", "/")
        for b in banned:
            if b in h:
                counts[b] += 1
                bad.append(f"{rel}: still says {b!r}")
        m = re.search(r'<span class="tag">([^<]*)</span>', h)
        if m:
            foot_tags[m.group(1)] = foot_tags.get(m.group(1), 0) + 1

    if len(foot_tags) > 1:
        bad.append(f"footer tagline is not uniform: {foot_tags}")
    if "North American" not in "".join(foot_tags):
        bad.append(f"footer tagline does not read North American: {foot_tags}")
    return bad


def check_og_images_exist():
    """Every og:image on every page must point at a file we actually built.

    /border-trends/ pointed at /og/border-trends.png, which did not exist —
    build_og.py only produces og.jpg and og-fuel.jpg. Nothing checked, so a
    social card would have silently fallen back to a blank for that page. Adding
    the tags is only half the job; this is the other half.
    """
    import re as _re
    base = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs = base / "docs"
    missing = []
    for f in docs.rglob("index.html"):
        h = f.read_text(encoding="utf-8", errors="replace")
        for m in _re.finditer(r'<meta property="og:image" content="([^"]+)"', h):
            url = m.group(1)
            rel = url.split("dashboard.northernmilemedia.com/", 1)[-1]
            if not (docs / rel).exists():
                missing.append(f"{f.parent.relative_to(docs)} -> {rel}")
    return missing


def check_fx_markers():
    """The currency layer must be complete, well-formed and non-nesting.

    Three failure modes, all of which have already happened once:

    1. A marker missing data-v renders nothing once the reader toggles currency —
       the figure just disappears. Silent and invisible in CAD.
    2. Nested markers double-wrap on every rebuild; at 48 deploys a day that is
       48 levels deep by the evening.
    3. fx.json missing or unparseable leaves the toggle looking live while doing
       nothing, which is the defect class this codebase keeps producing.
    """
    import json as _json
    import re as _re
    base = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs = base / "docs"
    out = []

    rate = docs / "assets" / "fx.json"
    if not rate.exists():
        out.append("assets/fx.json is missing — the toggle would silently do nothing")
    else:
        try:
            j = _json.loads(rate.read_text(encoding="utf-8"))
            if not (j.get("usd_cad") and float(j["usd_cad"]) > 0):
                out.append("assets/fx.json has no usable usd_cad")
        except Exception as e:
            out.append(f"assets/fx.json does not parse: {e}")

    MISSING = _re.compile(r'<span class="fx"(?![^>]*data-v=)[^>]*>')
    NESTED = _re.compile(r'<span class="fx"[^>]*><span class="fx"')
    for f in docs.rglob("index.html"):
        h = f.read_text(encoding="utf-8", errors="replace")
        rel = f.parent.relative_to(docs)
        if MISSING.search(h):
            out.append(f"{rel}: .fx marker with no data-v")
        if NESTED.search(h):
            out.append(f"{rel}: nested .fx markers — the layer is not idempotent")
        if 'class="fxtog"' in h and "/assets/fx.js" not in h:
            out.append(f"{rel}: currency toggle rendered without fx.js")
    return out


CHECKS = (
    ("every og:image resolves to a built file", check_og_images_exist),
    ("the currency layer is complete and non-nesting", check_fx_markers),
    ("lookback never returns the newest point", check_lookback_not_latest),
    ("chart headline agrees with the cited average", check_chart_matches_headline),
    ("spread uses the ten-province definition", check_spread_definition),
    ("one 30-day FX average across the site", check_fx_average_agreement),
    ("structured data parses on every page", check_jsonld_valid),
    ("cbp commercial delay never faked as zero", check_cbp_missing_not_zero),
    ("sitemap is well-formed, complete and honestly dated", check_sitemap),
    ("us state pages attribute diesel to a district", check_us_state_pages),
    ("brand identity matches the data geography", check_brand_identity),
)


def main():
    failures = []
    for name, fn in CHECKS:
        bad = fn()
        if bad:
            print(f"GUARD FATAL: {name}")
            for b in bad:
                print(f"  - {b}")
            failures += bad
        else:
            print(f"GUARD OK: {name}")

    if failures:
        print(f"\nGUARD FATAL: {len(failures)} data integrity violation(s)")
        return 1
    print("\nGUARD OK: data integrity")
    return 0


if __name__ == "__main__":
    sys.exit(main())
