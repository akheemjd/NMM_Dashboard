#!/usr/bin/env python3
"""City page builder — programmatic SEO layer.

Renders templates/city.template.html once per NRCan survey city, writing
docs/diesel-prices/<province-slug>/<city-slug>/index.html.

Each city page must carry a writer-generated context paragraph
(content/cities/<slug>.md) so the page is not thin. Like the province pages,
a missing or too-short prose block is a build failure, not a warning.
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
CONTENT = os.path.join(ROOT, "content", "cities")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402 — reuse the one template engine
from collect_nrcan_diesel import CITY_PROVINCE  # noqa: E402

MIN_PROSE_CHARS = 400  # ~60 words; below this the page is thin


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_prose(slug):
    path = os.path.join(CONTENT, f"{slug}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{slug}: no prose at {path}. City pages are not built from data alone."
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
    nrcan = json.load(open(os.path.join(DATA, "nrcan_diesel.json")))
    prices = nrcan.get("prices", {})

    pn = json.load(open(os.path.join(DATA, "provinces.norm.json")))
    provinces = pn.get("provinces", {})
    national = float(pn.get("national", 0) or 0)

    tmpl_path = os.path.join(TMPL, "city.template.html")
    with open(tmpl_path) as f:
        template = f.read()

    # Group cities by province, compute vs_prov / vs_national / position.
    by_prov = {}
    for city, price in prices.items():
        code = CITY_PROVINCE.get(city)
        if code is None or code not in provinces:
            continue
        by_prov.setdefault(code, []).append((city, float(price)))

    seen_slugs = {}
    built = []

    for code, cities in sorted(by_prov.items()):
        prov = provinces[code]
        prov_price = float(prov.get("price", 0))
        prov_name = prov.get("name", code)
        prov_slug = prov.get("slug", slugify(prov_name))

        ordered = sorted(cities, key=lambda cv: cv[1])  # cheapest first
        n = len(ordered)
        siblings = []
        for i, (city, price) in enumerate(ordered):
            vs_prov = round(price - prov_price, 1)
            siblings.append({
                "city": city,
                "price": f"{price:.1f}",
                "vs_prov": (f"+{vs_prov:.1f}" if vs_prov >= 0 else f"{vs_prov:.1f}"),
                "vs_class": "lo" if vs_prov < 0 else "hi",
                "pos": i,  # 0 = cheapest
            })

        for sib in siblings:
            city = sib["city"]
            price = float(sib["price"])
            slug = slugify(city)
            if slug in seen_slugs and seen_slugs[slug] != code:
                raise ValueError(
                    f"city slug collision: '{slug}' maps to both "
                    f"{seen_slugs[slug]} and {code} — use a disambiguated filename"
                )
            seen_slugs[slug] = code

            vs_national = round(price - national, 1)
            pos_word = ("cheapest" if sib["pos"] == 0
                        else "dearest" if sib["pos"] == n - 1
                        else f"{sib['pos'] + 1} of {n}")

            data = {
                "name": city,
                "slug": slug,
                "prov_name": prov_name,
                "prov_slug": prov_slug,
                "price": f"{price:.1f}",
                "prov_price": f"{prov_price:.1f}",
                "national": f"{national:.1f}",
                "vs_prov": sib["vs_prov"],
                "vs_national": (f"+{vs_national:.1f}" if vs_national >= 0 else f"{vs_national:.1f}"),
                "vs_national_abs": f"{abs(vs_national):.1f}",
                "vs_national_word": "below" if vs_national < 0 else "above",
                "vs_national_class": "lo" if vs_national < 0 else "hi",
                "position": pos_word,
                "city_count": n,
                "print_date": prov.get("print_date", ""),
                "updated_at": pn.get("updated_at", ""),
                "updated_iso": pn.get("updated_iso", ""),
                "build_version": pn.get("build_version", ""),
                "prose": load_prose(slug),
                "siblings": siblings,
            }

            html = fill(template, data)
            leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:") if t in html]
            if leftover:
                raise ValueError(f"{slug}: unresolved template markup remains: {leftover}")

            out_dir = os.path.join(DOCS, "diesel-prices", prov_slug, slug)
            os.makedirs(out_dir, exist_ok=True)
            with open(os.path.join(out_dir, "index.html"), "w") as f:
                f.write(html)
            built.append((prov_slug, slug))

    print(f"Built {len(built)} city pages")
    for prov_slug, slug in built[:8]:
        print(f"  /diesel-prices/{prov_slug}/{slug}/")
    if len(built) > 8:
        print(f"  ... and {len(built) - 8} more")


if __name__ == "__main__":
    main()
