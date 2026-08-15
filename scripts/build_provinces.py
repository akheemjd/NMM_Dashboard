#!/usr/bin/env python3
"""Province page builder.

Renders templates/province.template.html once per province in
data/provinces.norm.json, writing docs/diesel-prices/<slug>/index.html.

The prose for each province is hand-written and lives in
content/provinces/<code>.html. The build refuses to run if that file is
missing, is trivially short, or still carries the TODO marker. Ten pages of
generated numbers with boilerplate around them is the thin-content pattern
search engines demote; the prose is the reason these pages exist, so an
unwritten one is a build failure, not a warning.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")
CONTENT = os.path.join(ROOT, "content", "provinces")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402  — reuse the one template engine

TODO_MARKER = "TODO-WRITE-THIS"
MIN_PROSE_CHARS = 1200  # roughly 200 words; below this the page is thin


def load_prose(code):
    path = os.path.join(CONTENT, f"{code.lower()}.html")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{code}: no prose at {path}. Province pages are not built from data alone."
        )
    with open(path) as f:
        prose = f.read().strip()

    # Guidance lives in HTML comments. It is not content, so it counts toward
    # neither the marker check nor the length floor.
    body = re.sub(r"<!--.*?-->", "", prose, flags=re.DOTALL).strip()

    if TODO_MARKER in body:
        raise ValueError(f"{code}: prose still contains {TODO_MARKER} — not ready to publish")
    if len(body) < MIN_PROSE_CHARS:
        raise ValueError(
            f"{code}: prose body is {len(body)} chars, minimum {MIN_PROSE_CHARS}. "
            f"Too thin to justify the page."
        )
    return prose


def main():
    norm_path = os.path.join(DATA, "provinces.norm.json")
    if not os.path.exists(norm_path):
        raise FileNotFoundError(f"{norm_path} missing — run normalize_provinces.py first")

    with open(norm_path) as f:
        payload = json.load(f)

    tmpl_path = os.path.join(TMPL, "province.template.html")
    with open(tmpl_path) as f:
        template = f.read()

    provinces = payload.get("provinces") or {}
    if not provinces:
        raise ValueError("provinces.norm.json has no provinces")

    built = []
    for code, block in provinces.items():
        data = dict(block)
        data["prose"] = load_prose(code)

        html = fill(template, data)

        leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:") if t in html]
        if leftover:
            raise ValueError(f"{code}: unresolved template markup remains: {leftover}")

        out_dir = os.path.join(DOCS, "diesel-prices", block["slug"])
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w") as f:
            f.write(html)
        built.append((code, block["slug"], len(html)))

    print(f"Built {len(built)} province pages")
    for code, slug, size in built:
        print(f"  /diesel-prices/{slug}/  ({size:,} bytes)")


if __name__ == "__main__":
    main()
