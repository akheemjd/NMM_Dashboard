#!/usr/bin/env python3
"""City page builder — programmatic SEO layer.

Renders templates/city.template.html once per NRCan survey city that maps to
one of the ten index provinces, writing
docs/diesel-prices/<province-slug>/<city-slug>/index.html.

Province metadata is derived from the ten-province maps (PROVINCE_NAMES /
SLUGS) and the NRCan sidecar, NOT from provinces.norm.json — which is
deliberately limited to the provinces that carry a dedicated in-depth page
(ON, AB). City pages span all ten provinces regardless.

Each city page must carry a writer-generated context paragraph
(content/cities/<slug>.md). A missing or too-short prose block is a build
failure, not a warning.
"""
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")
CONTENT = os.path.join(ROOT, "content", "cities")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402 — reuse the one template engine
from collect_nrcan_diesel import CITY_PROVINCE, CITY_PROVINCE_NORM, _norm  # noqa: E402
from normalize_provinces import PROVINCE_NAMES, SLUGS  # noqa: E402

MIN_PROSE_CHARS = 400  # ~60 words; below this the page is thin

# Only these provinces have a dedicated in-depth page to link back to.
DEDICATED_PAGE_PROVINCES = {"AB", "ON"}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_json(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


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
    nrcan = load_json("nrcan_diesel.json")
    prices = nrcan.get("prices", {})

    fuel = load_json("fuel.json")
    national = float(fuel.get("diesel_national_avg", 0) or 0)
    print_date = fuel.get("print_date", "")
    build_version = fuel.get("build_version", "")

    home = load_json("home.norm.json")
    updated_at = home.get("updated_at", "")
    updated_iso = home.get("updated_iso", "")

    with open(os.path.join(TMPL, "city.template.html")) as f:
        template = f.read()

    # Group by province; keep only cities that map to a real index province.
    by_prov = defaultdict(list)
    for city, price in prices.items():
        code = CITY_PROVINCE_NORM.get(_norm(city))
        if code is None or code not in PROVINCE_NAMES:
            continue
        by_prov[code].append((city, float(price)))

    seen_slugs = {}
    built = []

    for code in sorted(by_prov):
        cities = sorted(by_prov[code], key=lambda cv: cv[1])  # cheapest first
        prov_price = round(sum(p for _, p in cities) / len(cities), 1)
        prov_name = PROVINCE_NAMES[code]
        prov_slug = SLUGS[code]
        has_prov_page = code in DEDICATED_PAGE_PROVINCES
        n = len(cities)

        siblings = []
        for city, price in cities:
            vs_prov = round(price - prov_price, 1)
            siblings.append({
                "city": city,
                "price": f"{price:.1f}",
                "vs_prov": (f"+{vs_prov:.1f}" if vs_prov >= 0 else f"{vs_prov:.1f}"),
                "vs_class": "lo" if vs_prov < 0 else "hi",
            })

        for sib in siblings:
            city = sib["city"]
            slug = slugify(_norm(city))
            if slug in seen_slugs and seen_slugs[slug] != code:
                raise ValueError(
                    f"city slug collision: '{slug}' maps to both "
                    f"{seen_slugs[slug]} and {code}"
                )
            seen_slugs[slug] = code

            vs_national = round(float(sib["price"]) - national, 1)
            data = {
                "name": city,
                "slug": slug,
                "prov_name": prov_name,
                "prov_slug": prov_slug,
                "has_province_page": has_prov_page,
                "price": sib["price"],
                "prov_price": f"{prov_price:.1f}",
                "national": f"{national:.1f}",
                "vs_prov": sib["vs_prov"],
                "vs_national": (f"+{vs_national:.1f}" if vs_national >= 0 else f"{vs_national:.1f}"),
                "vs_national_abs": f"{abs(vs_national):.1f}",
                "vs_national_word": "below" if vs_national < 0 else "above",
                "vs_national_class": "lo" if vs_national < 0 else "hi",
                "city_count": n,
                "print_date": print_date,
                "updated_at": updated_at,
                "updated_iso": updated_iso,
                "build_version": build_version,
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

    print(f"Built {len(built)} city pages across {len(by_prov)} provinces")
    for prov_slug, slug in built[:10]:
        print(f"  /diesel-prices/{prov_slug}/{slug}/")
    if len(built) > 10:
        print(f"  ... and {len(built) - 10} more")


if __name__ == "__main__":
    main()
