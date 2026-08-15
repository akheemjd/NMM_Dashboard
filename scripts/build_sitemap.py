#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt from the pages that actually exist.

Building the sitemap from the live docs/ tree rather than a hardcoded list means
a new page can never be missing from it, and a deleted page can never linger.
Matches the existing format exactly: one <loc> per URL, absolute host, trailing
slash, no lastmod or priority.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
HOST = "https://dashboard.northernmilemedia.com"

# Redirect stubs and non-canonical paths that should not be advertised.
EXCLUDE = {"/methodology/"}  # the stub; the real page is /methodology/nmdi/


def discover():
    urls = []
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" not in files:
            continue
        rel = dirpath.replace(DOCS, "")
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
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"<url><loc>{HOST}{u}</loc></url>")
    lines.append("</urlset>")
    with open(os.path.join(DOCS, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    robots = ("User-agent: *\n"
              "Allow: /\n"
              f"Sitemap: {HOST}/sitemap.xml\n")
    with open(os.path.join(DOCS, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print(f"sitemap.xml — {len(urls)} URLs")
    for u in urls:
        print(f"  {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
