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
# Provinces whose /diesel-prices/<prov>/ page is written by build_provinces.py from
# content/provinces/<code>.html. build_city_pages still builds the CITY pages beneath
# each province, but it must not also emit a province page: it runs after
# build_provinces.py and its thinner template overwrote all eight of the new ones,
# dropping them back from ~450 words to ~180 with no prose.
DEDICATED_PAGE_PROVINCES = {"ON", "AB", "BC", "SK", "MB", "QC", "NB", "NS", "PE", "NL"}


# Which EIA district answers for a Canadian province. Diesel is priced by district in the
# United States, so a city compares against the district across from it, not against the US
# national figure.
US_DISTRICT_FOR_PROVINCE = {
    "BC": "West Coast (PADD 5)",
    "AB": "Rocky Mountain (PADD 4)",
    "SK": "Rocky Mountain (PADD 4)",
    "MB": "Rocky Mountain (PADD 4)",
    "ON": "Central Atlantic (PADD 1B)",
    "QC": "New England (PADD 1A)",
    "NB": "New England (PADD 1A)",
    "NS": "New England (PADD 1A)",
    "PE": "New England (PADD 1A)",
    "NL": "New England (PADD 1A)",
    "YT": "Rocky Mountain (PADD 4)",
    "NT": "Rocky Mountain (PADD 4)",
    "NU": "Rocky Mountain (PADD 4)",
}


def us_district_for(prov_code):
    """The EIA district block for a province, or None.

    Reads fuel.norm.json, not fuel.json: the EIA block is assembled during normalization, so
    the raw file does not carry it at all. Reading the wrong file found nothing and rendered
    the whole block empty on the province pages once already.
    """
    label = US_DISTRICT_FOR_PROVINCE.get(prov_code)
    if not label:
        return None
    try:
        with open(os.path.join(DATA, "fuel.norm.json")) as f:
            eia = (json.load(f).get("eia") or {})
    except Exception:
        return None
    for d in eia.get("padds_list") or []:
        if d.get("label") != label:
            continue
        cad_gal, usd_gal = d.get("cad_gal"), d.get("usd_gal")
        if not cad_gal or not usd_gal:
            return None
        return {
            "label": label,
            "label_short": label.split(" (")[0],
            "usd_gal": usd_gal,
            "cad_gal": cad_gal,
        }
    return None


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

    home = load_json("home.norm.json")
    updated_at = home.get("updated_at", "")
    updated_iso = home.get("updated_iso", "")
    # build_version lives in the NORMALISED files. Raw fuel.json has no such
    # key, so reading it from fuel silently produced "" and every city page
    # shipped a cache-buster of "?v=". Those ~90 pages could then serve stale
    # CSS from browser cache after a stylesheet change.
    build_version = home.get("build_version") or ""

    with open(os.path.join(TMPL, "city.template.html")) as f:
        template = f.read()

    with open(os.path.join(TMPL, "province-index.template.html")) as f:
        prov_template = f.read()

    # Group by province; keep only cities that map to a real index province.
    by_prov = defaultdict(list)
    for city, price in prices.items():
        code = CITY_PROVINCE_NORM.get(_norm(city))
        if code is None or code not in PROVINCE_NAMES:
            continue
        by_prov[code].append((city, float(price)))

    seen_slugs = {}
    built = []
    hubs = []

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
                # Same slug function used for the directory below, so the link
                # and the page it points at cannot drift apart.
                "city_slug": slugify(_norm(city)),
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
            _us = us_district_for(code)
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
                # The American side. Without this a Canadian city page said nothing at all
                # about the market across the border while the US tree ran 0.2:1 the other way.
                "us": _us,
                "has_us": bool(_us),
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

        # The province hub, for provinces with no hand-written in-depth page.
        #
        # This is the only thing that links a province's survey cities. Without
        # it /diesel-prices/<prov>/ is a 404 and every city beneath it is
        # unreachable by any crawler — which is exactly why 69 city pages sat
        # unindexed. ON and AB keep their editorial page (build_provinces.py
        # writes it), and that page now links its cities too.
        if code not in DEDICATED_PAGE_PROVINCES:
            pv_nat = round(prov_price - national, 1)
            prov_data = {
                "prov_name": prov_name,
                "prov_slug": prov_slug,
                "prov_price": f"{prov_price:.1f}",
                "city_count": n,
                "national": f"{national:.1f}",
                "print_date": print_date,
                "updated_at": updated_at,
                "updated_iso": updated_iso,
                "build_version": build_version,
                "vs_national": (f"+{pv_nat:.1f}" if pv_nat >= 0 else f"{pv_nat:.1f}"),
                "vs_national_abs": f"{abs(pv_nat):.1f}",
                "vs_national_word": "below" if pv_nat < 0 else "above",
                "vs_national_class": "lo" if pv_nat < 0 else "hi",
                "cities": siblings,
            }
            phtml = fill(prov_template, prov_data)
            pleft = [t for t in ("{{", "<!--LOOP:", "<!--IF:") if t in phtml]
            if pleft:
                raise ValueError(
                    f"{prov_slug}: unresolved template markup remains: {pleft}"
                )
            pdir = os.path.join(DOCS, "diesel-prices", prov_slug)
            os.makedirs(pdir, exist_ok=True)
            with open(os.path.join(pdir, "index.html"), "w") as f:
                f.write(phtml)
            hubs.append(prov_slug)

    print(f"Built {len(built)} city pages across {len(by_prov)} provinces")
    print(f"Built {len(hubs)} province hubs: {', '.join(hubs)}")
    for prov_slug, slug in built[:10]:
        print(f"  /diesel-prices/{prov_slug}/{slug}/")
    if len(built) > 10:
        print(f"  ... and {len(built) - 10} more")


if __name__ == "__main__":
    main()
