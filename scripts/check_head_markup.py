#!/usr/bin/env python3
"""No currency marker may appear inside <head>.

WHY THIS EXISTS

mark(), mark_pairs(), mark_unit() and mark_block_figures() are the four passes that wrap a
money figure in a conversion marker. Only mark() consults SKIP, which is what leaves <head>
alone. The other three were written later and never asked, so they marked a survey sentence in
a meta description:

    content="Diesel prices across 10 Quebec survey cities, 291.4¢/L provincial average,
             <span class="fx" data-c="CAD" data-u="cpl" data-v="30.5">30.5</span>¢ above the
             national index. NRCan weekly survey, print Tue, 29 Sep 2026."

That is the text search engines index and every social card renders. It shipped on 77 pages -
every diesel-prices province and its cities.

THE FIX

fx_layer.outside_head() runs those three passes over everything except the head. This script
checks the result.

WHY A STANDALONE SCRIPT

The same check was first written into check_data_integrity.py and registered there. It returned
an empty list on a deliberately sabotaged page while the identical logic, run inline, found it.
Rather than keep hunting the suite's plumbing, this runs on its own and is gated in deploy.sh
next to check_coherence.py and check_links.py - the shape every guard of this kind already has.

Exit 0 clean, 1 on any page with markup in the head.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")


def main():
    if not os.path.isdir(DOCS):
        print("HEADCHECK SKIP: no docs/")
        return 0

    bad = []
    for root, _dirs, files in os.walk(DOCS):
        if os.sep + "assets" in root:
            continue
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(root, name)
            try:
                head = open(path, encoding="utf-8", errors="replace").read().split("</head>")[0]
            except Exception:
                continue
            where = None
            if re.search(r'content="[^"]*<(?:span|b)\b', head, re.I):
                where = "meta description"
            elif re.search(r"<title>[^<]*<(?:span|b)\b", head, re.I):
                where = "title"
            if where:
                bad.append(f"{os.path.relpath(path, DOCS).replace(os.sep, '/')} ({where})")

    if bad:
        print(f"HEADCHECK FAIL: markup inside <head> on {len(bad)} page(s)")
        for b in bad[:10]:
            print(f"  - {b}")
        return 1

    n = sum(1 for r, _d, fs in os.walk(DOCS) if os.sep + "assets" not in r
            for f in fs if f.endswith(".html"))
    print(f"HEADCHECK OK: no markup in <head> across {n} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
