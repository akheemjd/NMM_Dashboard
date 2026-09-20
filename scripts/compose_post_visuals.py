#!/usr/bin/env python3
"""Compose the visual package for a blog post.

Given a topic, this reads the dashboard feeds, decides which chart types suit
the data that actually exists, renders a hero card plus 2-4 figures, uploads
everything to Ghost, and writes a manifest the publishing step uses to
substitute {{figure:name}} placeholders in the draft.

The point is that visuals are a REQUIREMENT, not a nice-to-have: the publish
step refuses to ship a post whose figures did not render.

Usage:
    python scripts/compose_post_visuals.py --topic-id market-diesel-national-week \
        --headline "Canada's national diesel average this week" \
        --keyword "canada diesel price" --eyebrow "Market Pulse"

    python scripts/compose_post_visuals.py --list-templates
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import blog_visuals as bv

DATA = ROOT / "data"
VISUAL_DIR = ROOT / "visuals"


# ── Data loading ───────────────────────────────────────────────

def load_json(name):
    p = DATA / name
    if not p.exists():
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


PROVINCE_NAMES = {
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba",
    "NB": "New Brunswick", "NL": "Newfoundland", "NS": "Nova Scotia",
    "NT": "Northwest Territories", "NU": "Nunavut", "ON": "Ontario",
    "PE": "Prince Edward Island", "QC": "Quebec", "SK": "Saskatchewan",
    "YT": "Yukon",
}

# Short forms for axis labels. Charts have limited width, and Canadian
# truckers read postal abbreviations instantly. "Prince Edward Island" and
# "Northwest Territories" in particular blow out the label gutter.
PROVINCE_SHORT = {
    "AB": "Alberta", "BC": "BC", "MB": "Manitoba", "NB": "New Brunswick",
    "NL": "Newfoundland", "NS": "Nova Scotia", "NT": "NWT", "NU": "Nunavut",
    "ON": "Ontario", "PE": "PEI", "QC": "Quebec", "SK": "Saskatchewan",
    "YT": "Yukon",
}

INDEX_PROVINCES = ["AB", "BC", "MB", "NB", "NL", "NS", "ON", "PE", "QC", "SK"]


def province_prices(fuel, short=True):
    """[(display_name, price)] for every province that has a price."""
    names = PROVINCE_SHORT if short else PROVINCE_NAMES
    out = []
    for code, info in (fuel.get("provinces") or {}).items():
        if isinstance(info, dict) and info.get("diesel") is not None:
            out.append((names.get(code, code), float(info["diesel"])))
    return out


def national_average(fuel):
    """Unweighted mean of the 10 freight-relevant provinces."""
    vals = [float(v["diesel"]) for c, v in (fuel.get("provinces") or {}).items()
            if c in INDEX_PROVINCES and isinstance(v, dict) and v.get("diesel") is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


# ── Figure recipes ─────────────────────────────────────────────
# Each returns (name, figure, caption) or None. The composer runs the ones
# whose data is present and keeps whatever renders.

def fig_provincial_ranked(fuel):
    rows = province_prices(fuel)
    if len(rows) < 4:
        return None
    rows.sort(key=lambda r: -r[1])
    nat = national_average(fuel)
    date = fuel.get("print_date", "")
    f = bv.ranked_bars(
        [r[0] for r in rows], [r[1] for r in rows],
        title="Diesel by province",
        subtitle=f"Cents per litre, NRCan print {date}" if date else "Cents per litre",
        source="Natural Resources Canada weekly diesel survey",
        unit="c", average=nat,
    )
    if not f:
        return None
    return ("provincial-spread", f,
            "Provincial diesel prices against the national index, per the NRCan weekly survey.")


def fig_diesel_trend(fuel):
    hist = fuel.get("history") or fuel.get("series") or []
    pts = []
    for h in hist:
        d = h.get("date") or h.get("print_date") or h.get("d")
        v = h.get("national") or h.get("value") or h.get("v")
        if d and v is not None:
            try:
                pts.append((d[:10], float(v)))
            except (TypeError, ValueError):
                continue
    if len(pts) < 5:
        return None
    pts.sort(key=lambda p: p[0])
    f = bv.trend_line(
        [p[0] for p in pts], [p[1] for p in pts],
        title="National diesel average",
        subtitle="Cents per litre, historical series",
        source="Natural Resources Canada weekly diesel survey",
        unit="c",
    )
    if not f:
        return None
    return ("diesel-trend", f,
            "The national diesel average over the available series.")


def fig_fx_bars(exchange):
    hist = (exchange.get("history") or [])[-14:]
    pts = [(h.get("date", "")[:10], h.get("rate")) for h in hist if h.get("rate")]
    if len(pts) < 5:
        return None
    f = bv.trend_line(
        [p[0] for p in pts], [float(p[1]) for p in pts],
        title="CAD/USD",
        subtitle="Bank of Canada noon rate, last 14 observations",
        source="Bank of Canada Valet API",
        unit="",
        decimals=4,   # an FX rate at 1 decimal reads 1.4 for 1.4002
    )
    if not f:
        return None
    return ("fx-trend", f, "The Canadian dollar against the US dollar, recent observations.")


def fig_border_ranked(border):
    crossings = [c for c in (border.get("crossings") or []) if c.get("commercial")]
    rows = [(c.get("name", c.get("id", "?")), c.get("delay_minutes"))
            for c in crossings if c.get("delay_minutes") is not None]
    if len(rows) < 4:
        return None
    f = bv.ranked_bars(
        [r[0] for r in rows], [float(r[1]) for r in rows],
        title="Commercial border delays",
        subtitle="Current wait, minutes",
        source="CBSA border wait times",
        unit=" min",
    )
    if not f:
        return None
    return ("border-rank", f, "Current commercial wait times at CBSA-reported crossings.")


def fig_border_distribution(border_trends):
    """Delay distribution for the busiest crossing, from the history store."""
    crossings = border_trends.get("crossings") or {}
    if not crossings:
        return None
    # Pick the crossing with the most observations
    best = None
    for cid, stats in crossings.items():
        obs = stats.get("observations") or 0
        if best is None or obs > best[1]:
            best = (cid, obs)
    if not best or best[1] < 20:
        return None
    return None  # needs raw samples, not summary stats


def fig_us_canada(fuel, eia):
    """Grouped comparison of Canadian vs US diesel, converted to one unit."""
    if not eia or not fuel:
        return None
    return None  # needs a reliable unit conversion from the brief; skip by default


RECIPES = [
    ("provincial", fig_provincial_ranked),
    ("diesel_trend", fig_diesel_trend),
    ("fx", fig_fx_bars),
    ("border", fig_border_ranked),
]


# ── Composer ───────────────────────────────────────────────────

def compose(topic_id, headline, keyword=None, eyebrow=None,
            stat_value=None, stat_label=None, source=None, upload=True,
            max_figures=3):
    """Render the hero plus supporting figures and (optionally) upload them.

    Returns a manifest dict describing every asset produced.
    """
    fuel = load_json("fuel.json")
    exchange = load_json("exchange.json")
    border = load_json("border.json")
    border_trends = load_json("border_trends.json")
    eia = load_json("eia_diesel.json")

    outdir = VISUAL_DIR / topic_id
    outdir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "topic_id": topic_id,
        "headline": headline,
        "keyword": keyword,
        "generated": datetime.now(timezone.utc).isoformat(),
        "hero": None,
        "figures": [],
        "placeholders_expected": [],
    }

    # ── Hero (always) ──
    if not stat_value:
        nat = national_average(fuel)
        if nat:
            stat_value = f"{nat}c"
            stat_label = stat_label or "national diesel average"
            source = source or "Natural Resources Canada weekly diesel survey"

    hero_img = bv.hero_card(
        headline=headline,
        eyebrow=eyebrow,
        stat_value=stat_value,
        stat_label=stat_label,
        source=source,
    )
    hero_path = bv.save_hero(hero_img, f"{topic_id}-hero", outdir)
    hero_url = None
    if upload:
        from ghost_publish import upload_image
        r = upload_image(hero_path)
        hero_url = r.get("url") if r.get("success") else None
    manifest["hero"] = {
        "local": str(hero_path),
        "url": hero_url,
        "stat": stat_value,
        "stat_label": stat_label,
    }

    # ── Supporting figures ──
    sources = {
        "provincial": lambda: fig_provincial_ranked(fuel),
        "diesel_trend": lambda: fig_diesel_trend(fuel),
        "fx": lambda: fig_fx_bars(exchange),
        "border": lambda: fig_border_ranked(border),
    }

    for name, fn in sources.items():
        if len(manifest["figures"]) >= max_figures:
            break
        try:
            got = fn()
        except Exception as e:
            print(f"  figure '{name}' failed: {e}")
            continue
        if not got:
            continue
        fig_name, fig, caption = got
        path = bv.save(fig, fig_name, outdir)

        url = None
        if upload:
            from ghost_publish import upload_image
            r = upload_image(path)
            url = r.get("url") if r.get("success") else None

        manifest["figures"].append({
            "name": fig_name,
            "local": str(path),
            "url": url,
            "caption": caption,
        })
        manifest["placeholders_expected"].append(f"{{{{figure:{fig_name}}}}}")

    mpath = outdir / "manifest.json"
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    manifest["_manifest_path"] = str(mpath)
    return manifest


def substitute_placeholders(markdown, manifest):
    """Replace {{figure:name}} placeholders with real markdown images.

    Unknown placeholders are stripped rather than shipped literally, and the
    function reports what it removed so the caller can decide whether that is
    acceptable.
    """
    import re
    figures = {f["name"]: f for f in manifest.get("figures", [])}
    missing = []

    def _repl(m):
        name = m.group(1).strip()
        fig = figures.get(name)
        if not fig or not fig.get("url"):
            missing.append(name)
            return ""
        caption = fig.get("caption", "")
        alt = caption or name.replace("-", " ")
        out = f"![{alt}]({fig['url']})"
        if caption:
            out += f"\n*{caption}*"
        return out

    cleaned = re.sub(r"\{\{figure:([a-zA-Z0-9_-]+)\}\}", _repl, markdown)
    return cleaned, missing


def main():
    ap = argparse.ArgumentParser(description="Compose blog visuals for a post")
    ap.add_argument("--topic-id", required=False)
    ap.add_argument("--headline", required=False)
    ap.add_argument("--keyword")
    ap.add_argument("--eyebrow")
    ap.add_argument("--stat-value")
    ap.add_argument("--stat-label")
    ap.add_argument("--source")
    ap.add_argument("--no-upload", action="store_true",
                    help="Render locally without uploading to Ghost")
    ap.add_argument("--max-figures", type=int, default=3)
    args = ap.parse_args()

    if not args.topic_id or not args.headline:
        ap.error("--topic-id and --headline are required")

    print(f"=== Composing visuals for {args.topic_id} ===")
    m = compose(
        args.topic_id, args.headline,
        keyword=args.keyword, eyebrow=args.eyebrow,
        stat_value=args.stat_value, stat_label=args.stat_label,
        source=args.source,
        upload=not args.no_upload,
        max_figures=args.max_figures,
    )

    hero = m["hero"]
    print(f"  hero:    {'uploaded' if hero.get('url') else 'LOCAL ONLY'}")
    if hero.get("url"):
        print(f"           {hero['url']}")
    for f in m["figures"]:
        state = "uploaded" if f.get("url") else "LOCAL ONLY"
        print(f"  figure:  {f['name']:20} {state}")
        if f.get("url"):
            print(f"           {f['url']}")

    if not m["figures"]:
        print("  WARNING: no supporting figures rendered — check the data feeds")

    print(f"\n  manifest: {m['_manifest_path']}")
    print(f"  placeholders to use in the draft: "
          f"{', '.join(m['placeholders_expected']) or '(none)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
