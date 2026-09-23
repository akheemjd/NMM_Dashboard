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
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402

# PADD coverage — the states each district contains (standard EIA definitions).
# Which states sit in which district is data, not prose. It was a hardcoded map
# with five entries; when the collector was extended to all ten districts the
# five new ones fell through to an empty string and shipped pages of ~1,150
# characters with no state list at all. Deriving it means a district added
# upstream cannot produce an empty page.
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "the District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}


def _slug(k):
    """District keys use underscores; URLs use hyphens, like the state pages."""
    return (k or "").replace("_", "-")


def district_states_sentence(key, label, district_states):
    """'Midwest (PADD 2) spans Illinois, Indiana, ... and Wisconsin.'

    Reads DISTRICT_STATES (what the district covers), not state_padd (which
    district a state is priced in). Using the assignment map made the West Coast
    page list six states and omit California, on a page whose own label says
    PADD 5 — and PADD 5 includes California.
    """
    codes = sorted((district_states or {}).get(key, []))
    names = [STATE_NAMES.get(c, c) for c in codes]
    if not names:
        return ""
    if len(names) == 1:
        # "California spans California" reads badly.
        return f"{label} covers {names[0]} alone."
    return f"{label} spans " + ", ".join(names[:-1]) + f" and {names[-1]}."




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

    # Overview — national figure + every district.
    overview = fill(us_tmpl, {
        "eia": eia,
        "padds": [dict(p, key_url=_slug(p["key"])) for p in padds],
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
    _district_states = load_json("eia_diesel.json").get("district_states") or {}
    # The templates link districts under /us-diesel/district/<slug>/, so every
    # item in a LOOP needs key_url — the overview's padds list included. Missing
    # it is a hard failure in fill(), which is the point.
    siblings = [{"key": p["key"], "key_url": _slug(p["key"]), "label": p["label"],
                 "cpl": p["cpl"], "usd_gal": p["usd_gal"]}
                for p in padds]

    built = 0
    for p in padds:
        cpl = float(p["cpl"])
        vs = round(cpl - national_cpl, 1)
        data = {
            "key": p["key"],
            # Districts live under /us-diesel/district/ so they can never collide
            # with a state page. 'california' was both the EIA district key and
            # the California state slug, and because build_us_states.py runs after
            # this builder it silently overwrote the district page every build.
            # Hyphens match the state pages; the old keys used underscores.
            "key_url": _slug(p["key"]),
            "label": p["label"],
            "cpl": p["cpl"],
            "usd_gal": p["usd_gal"],
            "date": eia.get("date", ""),
            "national": f"{national_cpl:.1f}",
            "vs_national": (f"+{vs:.1f}" if vs >= 0 else f"{vs:.1f}"),
            "vs_national_abs": f"{abs(vs):.1f}",
            "vs_national_word": "above" if vs >= 0 else "below",
            "vs_national_class": "lo" if vs < 0 else "hi",
            "states": district_states_sentence(p["key"], p["label"], _district_states),
            "siblings": [s for s in siblings if s["key"] != p["key"]],
            "updated_at": updated_at,
            "updated_iso": updated_iso,
            "build_version": build_version,
        }
        html = fill(padd_tmpl, data)
        _check(html, p["key"])
        # Under district/ so a district key can never collide with a state slug.
        out_dir = os.path.join(DOCS, "us-diesel", "district", _slug(p["key"]))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(html)
        built += 1

    # Remove the pre-move district directories. They are no longer linked, and a
    # page nothing points at is what check_links.py fails the build for — but do
    # NOT touch a path that is now a state page. '/us-diesel/california/' must
    # survive as the California STATE page; the district moved to district/.
    state_slugs = {
        re.sub(r"[^a-z0-9]+", "-", (s.get("name") or "").lower().replace("&", " and ")).strip("-")
        for s in (load_json("us_fuel_tax.json").get("states") or [])
        if s.get("name")
    }
    old_root = os.path.join(DOCS, "us-diesel")
    for p in padds:
        stale = os.path.join(old_root, p["key"])
        if os.path.isdir(stale) and p["key"] not in state_slugs:
            import shutil
            shutil.rmtree(stale)
            print(f"  removed stale district path /us-diesel/{p['key']}/")

    print(f"Built US diesel overview + {built} PADD pages")


if __name__ == "__main__":
    main()
