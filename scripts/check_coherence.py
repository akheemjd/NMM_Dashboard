#!/usr/bin/env python3
"""Coherence guard. Run after the build, before deploy.

Two checks, both fatal:
  1. Every built page has a byte-identical header+nav+footer, ignoring only the
     active-state markers a page legitimately varies (class="on"|is-on, aria-current).
  2. No built page references the retired stylesheet or script.

This is what stops the dashboard drifting back into two visual systems. It is
the same kind of assertion as the source-tree guard and the asset-freshness
check: a wrong state stops the deploy rather than shipping.
"""

import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

RETIRED = ["styles.css", "app.js"]

# The chart library and its script may appear ONLY on these pages. Anywhere else
# means the chart leaked onto a page that should stay lean — same class of drift
# as an old-asset reference, caught the same way.
CHART_ALLOWED = {"/fuel-prices/index.html"}
CHART_MARKERS = ["d3.min.js", "nmdi-chart.js"]


def chrome(html):
    """The header+nav+footer, with per-page and per-build variation normalized out.

    Two things vary legitimately between pages and must not count as drift:

    - the active-page marker (`class="on"`, `aria-current="page"`)
    - the footer's "Updated <timestamp> UTC", which is the BUILD time

    The timestamp was not normalized, so this guard was flaky: a full deploy
    builds every page inside one minute and passed, while any partial rebuild
    left the rebuilt pages on a different minute and reported
    "2 distinct header/nav/footer variants — pages have drifted" for a site
    whose chrome was identical. A guard that fails on build ordering trains
    people to ignore it.
    """
    head = re.search(r'<header class="hd">.*?</nav>', html, re.DOTALL)
    foot = re.search(r'<footer class="ft">.*?</footer>', html, re.DOTALL)
    parts = []
    for m in (head, foot):
        if not m:
            return None
        s = m.group(0)
        s = re.sub(r' class="on"', "", s)
        s = re.sub(r' aria-current="page"', "", s)
        # The country switch marks its active option differently from the nav, and
        # the currency toggle has no active class at all. Both are injected
        # post-build and both legitimately vary per page.
        s = re.sub(r' is-on', "", s)
        s = re.sub(r' aria-current="true"', "", s)
        s = re.sub(r'data-curdefault="(?:CAD|USD)"', 'data-curdefault="X"', s)
        # The nav's Diesel link resolves inside the reader's own tree, so it is
        # /fuel-prices/ on Canadian pages and /us-diesel/ on US pages. Normalised to
        # a token rather than ignored: the rest of the nav is still compared.
        s = re.sub(r'href="(?:/fuel-prices/|/us-diesel/)"', 'href="<tree-diesel>"', s)
        s = re.sub(r'Updated \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC', "Updated <ts> UTC", s)
        parts.append(s)
    return hashlib.md5("".join(parts).encode()).hexdigest()


def main():
    pages = []
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" in files:
            pages.append(os.path.join(dirpath, "index.html"))
        # The 404 is a real page with the same chrome and belongs in the comparison.
        if dirpath == DOCS and "404.html" in files:
            pages.append(os.path.join(dirpath, "404.html"))
    pages.sort()

    if not pages:
        print("GUARD FATAL: no built pages found under docs/")
        return 1

    hashes = {}
    retired_hits = {}
    chart_leaks = {}
    empty_v = {}
    no_chrome = []

    for p in pages:
        rel = os.path.relpath(p, DOCS)
        if rel == ".":
            rel = "/"
        else:
            # Normalize to forward slashes so comparisons against CHART_ALLOWED work on all OSes
            rel = rel.replace("\\", "/")
            rel = f"/{rel}"
        html = open(p, encoding="utf-8").read()

        h = chrome(html)
        if h is None:
            no_chrome.append(rel)
        else:
            hashes.setdefault(h, []).append(rel)

        for asset in RETIRED:
            # Match the retired asset only as an asset reference, not substrings.
            if re.search(r'/assets/' + re.escape(asset) + r'\b', html) or \
               re.search(r'["\'/]' + re.escape(asset) + r'\?', html):
                retired_hits.setdefault(rel, []).append(asset)

        # An empty cache-buster ("?v=") means the version variable was never
        # substituted. That shipped on ~90 city pages because
        # build_city_pages.py read build_version from a file with no such key.
        # It is silent, and it makes a deploy look like it did nothing.
        for m in re.finditer(r'/assets/[A-Za-z0-9._-]+\?v=(?=["\'])', html):
            empty_v.setdefault(rel, []).append(m.group(0))

        # Chart library must appear only on the allowed pages.
        if rel not in CHART_ALLOWED:
            for marker in CHART_MARKERS:
                if marker in html:
                    chart_leaks.setdefault(rel, []).append(marker)

    ok = True

    # Pages with no chrome at all are almost always a stray stub. Report, don't
    # necessarily fail — a redirect stub is legitimate — but surface it.
    if no_chrome:
        print("GUARD NOTE: pages with no header/nav/footer (redirect stubs?):")
        for r in no_chrome:
            print(f"  {r}")

    if len(hashes) > 1:
        ok = False
        print(f"GUARD FATAL: {len(hashes)} distinct header/nav/footer variants — pages have drifted:")
        for h, group in hashes.items():
            print(f"  [{h[:8]}]  {', '.join(group)}")
    else:
        only = next(iter(hashes))
        print(f"GUARD OK: {sum(len(g) for g in hashes.values())} pages share one chrome [{only[:8]}]")

    if retired_hits:
        ok = False
        print("GUARD FATAL: pages still reference retired assets:")
        for rel, assets in retired_hits.items():
            print(f"  {rel}: {', '.join(assets)}")
    else:
        print("GUARD OK: no page references " + " or ".join(RETIRED))

    if chart_leaks:
        ok = False
        print("GUARD FATAL: chart library leaked onto pages that should stay lean:")
        for rel, markers in chart_leaks.items():
            print(f"  {rel}: {', '.join(markers)}")
        print(f"  chart is allowed only on: {', '.join(sorted(CHART_ALLOWED))}")
    else:
        print(f"GUARD OK: chart library confined to {len(CHART_ALLOWED)} allowed pages")

    if empty_v:
        ok = False
        print(f"GUARD FATAL: {len(empty_v)} page(s) ship an empty asset cache-buster:")
        for rel, hits in list(empty_v.items())[:10]:
            print(f"  {rel}: {', '.join(sorted(set(hits)))}")
        if len(empty_v) > 10:
            print(f"  ... and {len(empty_v) - 10} more")
        print("  an empty ?v= means build_version was never substituted, so")
        print("  browsers can serve stale CSS/JS after a deploy.")
    else:
        print(f"GUARD OK: every asset cache-buster carries a version")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
