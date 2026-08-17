#!/usr/bin/env python3
"""Border crossing page builder — programmatic SEO layer.

Renders templates/border-crossing.template.html once per CBSA crossing,
writing docs/border-wait-times/<slug>/index.html. Each page carries a
hand-written context paragraph from content/border/<slug>.md (a missing or
too-thin prose block is a build failure, same as the city pages).
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
CONTENT = os.path.join(ROOT, "content", "border")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402

MIN_PROSE_CHARS = 200  # ~30 words; below this the page is thin


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_json(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def load_prose(slug):
    path = os.path.join(CONTENT, f"{slug}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{slug}: no prose at {path}. Crossing pages are not built from data alone."
        )
    with open(path) as f:
        prose = f.read().strip()
    body = re.sub(r"<!--.*?-->", "", prose, flags=re.DOTALL).strip()
    if len(body) < MIN_PROSE_CHARS:
        raise ValueError(
            f"{slug}: prose body is {len(body)} chars, minimum {MIN_PROSE_CHARS}. "
            f"Too thin to justify the page."
        )
    return prose


def main():
    border = load_json("border.norm.json")
    crossings = border.get("crossings") or []
    if not crossings:
        raise ValueError("border.norm.json has no crossings — refusing to build")

    home = load_json("home.norm.json")
    updated_at = home.get("updated_at", "")
    updated_iso = home.get("updated_iso", "")
    build_version = home.get("build_version", "")

    with open(os.path.join(TMPL, "border-crossing.template.html")) as f:
        template = f.read()

    siblings = [{
        "slug": slugify(c.get("name", "")),
        "name": c.get("name", ""),
        "wait": c.get("wait", ""),
        "status_label": c.get("status_label", ""),
        "status_class": c.get("status_class", ""),
    } for c in crossings]

    seen = {}
    built = 0
    for c in crossings:
        slug = slugify(c.get("name", ""))
        if slug in seen and seen[slug] != c.get("name"):
            raise ValueError(f"crossing slug collision: '{slug}' maps to both "
                             f"{seen[slug]} and {c.get('name')}")
        seen[slug] = c.get("name")

        data = {
            "name": c.get("name", ""),
            "slug": slug,
            "wait": c.get("wait", ""),
            "status_label": c.get("status_label", ""),
            "status_class": c.get("status_class", ""),
            "sub": c.get("sub", ""),
            "prose": load_prose(slug),
            "siblings": [s for s in siblings if s["slug"] != slug],
            "updated_at": updated_at,
            "updated_iso": updated_iso,
            "build_version": build_version,
        }
        html = fill(template, data)
        leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:", "<!--OPTIONAL:") if t in html]
        if leftover:
            raise ValueError(f"{slug}: unresolved template markup remains: {leftover}")

        out_dir = os.path.join(DOCS, "border-wait-times", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(html)
        built += 1

    print(f"Built {built} border crossing pages")


if __name__ == "__main__":
    main()
