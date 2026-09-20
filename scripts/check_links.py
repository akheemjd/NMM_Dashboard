#!/usr/bin/env python3
"""Check the built site's internal link graph.

Two checks, both of which would have caught the bug that left 69 city pages
invisible to Google:

1. BROKEN LINKS — every internal href resolves to a page that exists.
2. ORPHANS — every page is reachable from the homepage by following links.

Check 2 is the important one. A page can be perfectly built, correct, and
still unreachable if nothing links to it, and search engines then never find
it. That is exactly what happened here: /diesel-prices/<province>/ was a 404,
so the 69 city pages beneath it had no inbound link from anywhere.
"""

import os
import re
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")

# Served by something other than a docs/ file, or not a page at all.
IGNORE_PREFIX = ("/assets/", "/favicon", "/apple-touch", "/og-", "/nmdi-chart")


def is_page_link(href):
    return href.startswith("/") and not href.startswith(IGNORE_PREFIX)


def norm(href):
    h = href.split("#")[0].split("?")[0]
    if not h.endswith("/"):
        h += "/"
    return h


def target_exists(path):
    """Resolve a site path to a file under docs/."""
    p = path.split("#")[0].split("?")[0]
    if not p.startswith("/") or p.startswith(IGNORE_PREFIX):
        return True
    full = os.path.join(DOCS, p.lstrip("/"))
    if p.endswith("/") or os.path.isdir(full):
        return os.path.isfile(os.path.join(full, "index.html"))
    return os.path.isfile(full) or os.path.isfile(os.path.join(full, "index.html"))


def to_url(path):
    rel = os.path.relpath(path, DOCS).replace("\\", "/")
    if rel == "index.html":
        return "/"
    return "/" + os.path.dirname(rel) + "/"


def load_pages():
    pages = {}
    for dirpath, _, files in os.walk(DOCS):
        if "index.html" in files:
            p = os.path.join(dirpath, "index.html")
            html = open(p, encoding="utf-8").read()
            links = {norm(h) for h in re.findall(r'href="([^"]+)"', html)
                     if is_page_link(h)}
            pages[to_url(p)] = links
    return pages


def main():
    pages = load_pages()
    if not pages:
        print("LINKCHECK FATAL: no built pages found under docs/")
        return 1

    # 1. Broken links.
    broken = {}
    total = 0
    for page, links in pages.items():
        for href in links:
            total += 1
            if not target_exists(href):
                broken.setdefault(page, []).append(href)

    if broken:
        print(f"LINKCHECK FATAL: {len(broken)} page(s) link to a missing target")
        for rel, hrefs in list(broken.items())[:15]:
            print(f"  {rel}")
            for h in sorted(set(hrefs))[:4]:
                print(f"      -> {h}")
        if len(broken) > 15:
            print(f"  ... and {len(broken) - 15} more")
        return 1
    print(f"LINKCHECK OK: {total} internal links across {len(pages)} pages, all resolve")

    # 2. Orphans — breadth-first from the homepage.
    seen = {"/"}
    q = deque(["/"])
    while q:
        for nxt in pages.get(q.popleft(), ()):
            if nxt in pages and nxt not in seen:
                seen.add(nxt)
                q.append(nxt)

    orphans = sorted(set(pages) - seen)
    if orphans:
        print(f"LINKCHECK FATAL: {len(orphans)} page(s) unreachable from the homepage")
        for o in orphans[:15]:
            print(f"  {o}")
        if len(orphans) > 15:
            print(f"  ... and {len(orphans) - 15} more")
        print("  An unreachable page cannot be crawled or indexed.")
        return 1
    print(f"LINKCHECK OK: all {len(pages)} pages reachable from the homepage")

    return 0


if __name__ == "__main__":
    sys.exit(main())
