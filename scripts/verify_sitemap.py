#!/usr/bin/env python3
"""Verify docs/sitemap.xml is valid and free of filesystem-path artifacts.

A Windows separator leaked into every URL but the homepage, which would have
left the whole dashboard unlisted by search engines. This is the regression
check for that.
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HOST = "https://dashboard.northernmilemedia.com"
BACKSLASH = chr(92)


def main():
    path = Path(__file__).resolve().parent.parent / "docs" / "sitemap.xml"
    if not path.exists():
        print(f"missing: {path}")
        return 2

    text = path.read_text(encoding="utf-8")

    try:
        ET.fromstring(text)
        print("XML: valid")
    except ET.ParseError as e:
        print(f"XML: INVALID -- {e}")
        return 1

    locs = re.findall(r"<loc>([^<]+)</loc>", text)
    bad = [u for u in locs if BACKSLASH in u]

    print(f"URLs: {len(locs)}")
    print(f"containing a backslash: {len(bad)}")

    for u in bad[:5]:
        print(f"  BAD {u}")

    if bad:
        return 1

    for u in locs[:5]:
        print(f"  {u.replace(HOST, '')}")
    print("  ...")
    for u in locs[-3:]:
        print(f"  {u.replace(HOST, '')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
