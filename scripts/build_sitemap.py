#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt from the pages that actually exist.

WHY LASTMOD IS BACK (2026-09-23)
--------------------------------
The original decision was to omit lastmod entirely, on the grounds that the
content changes every 30 minutes so any lastmod would always read "now". That
reasoning conflated two different dates:

  * the BUILD time, stamped in every page footer, which changes every run
  * the DATA time, when the figures on the page last actually moved

A lastmod that always reads "now" is worse than none: Google documents that it
ignores a lastmod it finds consistently inaccurate, so the tag buys nothing and
costs bytes. The DATA date is accurate, verifiable, and meaningful — the NRCan
diesel page genuinely last changed when NRCan printed, which is weekly, not every
30 minutes.

So each page carries the observation date of the source that feeds it:

  fuel pages      -> NRCan print_date        (weekly)
  US diesel       -> EIA survey date         (weekly)
  border          -> capture date            (hourly feed)
  fuel tax        -> IFTA fetch date         (quarterly)
  exchange        -> Bank of Canada obs date (business daily)

A page whose dates cannot be resolved gets NO lastmod rather than a guessed one.
An absent tag is honest; an invented date is not.
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "data")
HOST = "https://dashboard.northernmilemedia.com"

# Redirect stubs and non-canonical paths that should not be advertised.
EXCLUDE = {"/methodology/"}  # the stub; the real page is /methodology/nmdi/


def _load(name):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _weekday_date(s):
    """'Tue, 15 Sep 2026' -> '2026-09-15'."""
    from datetime import datetime
    if not s:
        return None
    try:
        return datetime.strptime(s, "%a, %d %b %Y").strftime("%Y-%m-%d")
    except Exception:
        return None


def iso_head(v, n=10):
    return (str(v) or "")[:n] or None


def build_dates():
    """Map page-path prefix -> the date that page's data last changed.

    Longest prefix wins, so /us-diesel/ overrides / for the US pages.
    """
    fuel = _load("fuel.json")
    eia = _load("eia_diesel.json")
    cbp = _load("cbp_border.json")
    ifta = _load("ifta.json")
    fx = _load("exchange.json")
    news = _load("news.json")
    incidents = _load("incidents.json")

    fuel_d = _weekday_date(fuel.get("print_date")) or iso_head(fuel.get("updated"))
    eia_d = iso_head(eia.get("date"))
    cbp_d = iso_head(cbp.get("fetched_date"))
    ifta_d = iso_head(ifta.get("fetched_date"))
    fx_d = iso_head(fx.get("observation_date"))
    news_d = iso_head(news.get("updated"))
    inc_d = iso_head(incidents.get("updated"))

    # The homepage carries figures from several sources, so it changes whenever
    # the most volatile of them does. Border is the fastest-moving.
    newest = max([d for d in (fuel_d, eia_d, cbp_d, fx_d) if d] or [None]) if any(
        (fuel_d, eia_d, cbp_d, fx_d)) else None

    return [
        ("/us-diesel/", eia_d),
        ("/diesel-prices/", fuel_d),
        ("/fuel-prices/", fuel_d),
        ("/fuel-cost-calculator/", fuel_d),
        ("/fuel-tax-rates/", ifta_d),
        ("/border-wait-times/", cbp_d),
        ("/border-trends/", cbp_d),
        ("/exchange-rate/", fx_d),
        ("/industry-news/", news_d),
        ("/road-incidents/", inc_d),
        ("/market-pulse/", fx_d),
        ("/freight-barometer/", fuel_d),
        ("/", newest),
    ]


def lastmod_for(path, table):
    """Longest-prefix match, and ONLY the homepage gets the catch-all.

    Giving the "/" fallback to every unmatched page put today's date on
    /advertise/, /contact/ and /press/ — static pages that did not change at all.
    That is the same "always now" inaccuracy this file exists to avoid, so an
    unmatched page gets no lastmod instead of a borrowed one.
    """
    for prefix, date in table:
        if prefix != "/" and path.startswith(prefix) and date:
            return date
    if path == "/":
        for prefix, date in table:
            if prefix == "/":
                return date
    return None


def discover():
    urls = []
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" not in files:
            continue
        # Normalise Windows separators. os.walk yields "C:\...\docs\border-trends",
        # so stripping DOCS left "\border-trends" and the sitemap advertised URLs
        # containing backslashes. Search engines cannot crawl those, which left
        # every page except the homepage effectively unlisted. The same bug also
        # defeated the EXCLUDE lookup below, since "/\methodology/" never matched
        # "/methodology/".
        rel = dirpath.replace(DOCS, "").replace("\\", "/")
        path = (rel + "/").replace("//", "/")
        if not path.startswith("/"):
            path = "/" + path
        if path in EXCLUDE:
            continue
        # Skip a stub: an index.html that is only a meta-refresh redirect.
        html = open(os.path.join(dirpath, "index.html"), encoding="utf-8").read()
        if "http-equiv=\"refresh\"" in html.lower() and len(html) < 600:
            continue
        urls.append(path)
    urls.sort(key=lambda u: (u != "/", u))
    return urls


def main():
    urls = discover()
    table = build_dates()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    dated = 0
    for u in urls:
        lm = lastmod_for(u, table)
        if lm:
            dated += 1
            lines.append(f"<url><loc>{HOST}{u}</loc><lastmod>{lm}</lastmod></url>")
        else:
            lines.append(f"<url><loc>{HOST}{u}</loc></url>")
    lines.append("</urlset>")
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    robots = ("User-agent: *\n"
              "Allow: /\n"
              f"Sitemap: {HOST}/sitemap.xml\n")
    with open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"sitemap.xml — {len(urls)} URLs, {dated} with a data-derived lastmod")
    return 0


if __name__ == "__main__":
    sys.exit(main())
