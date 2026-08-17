#!/usr/bin/env python3
"""US diesel page builder — programmatic SEO layer.

Renders templates/us-diesel.template.html once (national overview) and
templates/us-padd.template.html once per EIA PADD region, writing
docs/us-diesel/index.html and docs/us-diesel/<padd-key>/index.html.

All figures come from fuel.norm.json's `eia` block (built by normalize.py),
which already carries the CAD ¢/L conversion and the NADI.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402

# PADD coverage — the states each district contains (standard EIA definitions).
PADD_STATES = {
    "east_coast": "East Coast (PADD 1) spans New England and the Central Atlantic — Maine, New Hampshire, Vermont, Massachusetts, Rhode Island, Connecticut, New York, New Jersey, Pennsylvania, Delaware, Maryland, and the District of Columbia.",
    "midwest": "Midwest (PADD 2) spans the industrial middle of the country — Ohio, Indiana, Illinois, Michigan, Wisconsin, Minnesota, Iowa, Missouri, North Dakota, South Dakota, Nebraska, Kansas, Kentucky, Tennessee, and Oklahoma.",
    "gulf_coast": "Gulf Coast (PADD 3) spans Texas, New Mexico, Arkansas, Louisiana, Mississippi, and Alabama — the refining heart of the country.",
    "rocky_mountain": "Rocky Mountain (PADD 4) spans Montana, Wyoming, Idaho, Utah, and Colorado.",
    "west_coast": "West Coast (PADD 5) spans Washington, Oregon, California, Nevada, and Arizona.",
}


def load_json(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def _check(html, name):
    leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:", "<!--OPTIONAL:") if t in html]
    if leftover:
        raise ValueError(f"{name}: unresolved template markup remains: {leftover}")


def main():
    fuel = load_json("fuel.norm.json")
    eia = fuel.get("eia", {})
    padds = eia.get("padds_list") or []
    if not padds:
        raise ValueError("eia.padds_list empty — refusing to build US pages")

    updated_at = fuel.get("updated_at", "")
    updated_iso = fuel.get("updated_iso", "")
    build_version = fuel.get("build_version", "")

    with open(os.path.join(TMPL, "us-diesel.template.html")) as f:
        us_tmpl = f.read()
    with open(os.path.join(TMPL, "us-padd.template.html")) as f:
        padd_tmpl = f.read()

    # Overview — national figure + the five regions.
    overview = fill(us_tmpl, {
        "eia": eia,
        "padds": padds,
        "updated_at": updated_at,
        "updated_iso": updated_iso,
        "build_version": build_version,
    })
    _check(overview, "us-diesel")
    os.makedirs(os.path.join(DOCS, "us-diesel"), exist_ok=True)
    with open(os.path.join(DOCS, "us-diesel", "index.html"), "w") as f:
        f.write(overview)

    # Per-PADD pages.
    national_cpl = float(eia.get("us_national_cpl", 0) or 0)
    siblings = [{"key": p["key"], "label": p["label"], "cpl": p["cpl"], "usd_gal": p["usd_gal"]}
                for p in padds]

    built = 0
    for p in padds:
        cpl = float(p["cpl"])
        vs = round(cpl - national_cpl, 1)
        data = {
            "key": p["key"],
            "label": p["label"],
            "cpl": p["cpl"],
            "usd_gal": p["usd_gal"],
            "date": eia.get("date", ""),
            "national": f"{national_cpl:.1f}",
            "vs_national": (f"+{vs:.1f}" if vs >= 0 else f"{vs:.1f}"),
            "vs_national_abs": f"{abs(vs):.1f}",
            "vs_national_word": "above" if vs >= 0 else "below",
            "vs_national_class": "lo" if vs < 0 else "hi",
            "states": PADD_STATES.get(p["key"], ""),
            "siblings": [s for s in siblings if s["key"] != p["key"]],
            "updated_at": updated_at,
            "updated_iso": updated_iso,
            "build_version": build_version,
        }
        html = fill(padd_tmpl, data)
        _check(html, p["key"])
        out_dir = os.path.join(DOCS, "us-diesel", p["key"])
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(html)
        built += 1

    print(f"Built US diesel overview + {built} PADD pages")


if __name__ == "__main__":
    main()
