#!/usr/bin/env python3
"""Correct the 82.5 vs 53.2 spread on a published post.

The article computed the provincial spread from every jurisdiction in
fuel.json, which includes Yukon and the NWT. The dashboard computes it across
the ten index provinces. So the site published two different spreads for the
same week, and the article went further and stated that the Alberta-to-Quebec
difference was 82.5, which is not true under either definition.

The ten-province figure is the site's canon: /fuel-prices/ says "cheapest AB at
243.1, dearest QC at 296.3, spread 53.2".

Usage: python scripts/fix_spread.py <slug> [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import api_call, find_post_by_slug, _load_dotenv  # noqa: E402

# Ordered: longest, most specific first so earlier edits cannot orphan later ones.
REPLACEMENTS = [
    (
        "The 82.5 cent gap between Quebec and the Northwest Territories is the "
        "number that moves your margin.",
        "The 53.2 cent gap between Quebec and Alberta is the number that moves "
        "your margin.",
    ),
    ("The 82.5 cent spread matters more.", "The 53.2 cent spread matters more."),
    (
        "Right now that gap is 82.5 cents. Quebec pays 296.3 at the pump. "
        "Northwest Territories pays 213.8.",
        "Right now that gap is 53.2 cents. Quebec pays 296.3 at the pump. "
        "Alberta pays 243.1.",
    ),
    (
        "The difference between a fill in Alberta and a fill in Quebec is 82.5 "
        "cents a litre",
        "The difference between a fill in Alberta and a fill in Quebec is 53.2 "
        "cents a litre",
    ),
]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    _load_dotenv()
    post = find_post_by_slug(args.slug)
    if not post:
        print(f"not found: {args.slug}")
        return 1

    html = post.get("html") or ""
    if not html:
        # find_post_by_slug does not request the body, so ask for it directly.
        r = api_call(
            "GET",
            f"posts/{post['id']}/?formats=html"
            "&fields=html,custom_excerpt,meta_description,updated_at",
        )
        full = (r.get("posts") or [{}])[0]
        html = full.get("html") or ""
        post.update(full)

    if "82.5" not in html:
        print("no 82.5 in the body — nothing to do")
        return 0

    new = html
    applied = 0
    for old, repl in REPLACEMENTS:
        if old in new:
            new = new.replace(old, repl)
            applied += 1
            print(f"  replaced: {old[:58]}...")

    remaining = new.count("82.5")
    print(f"\napplied {applied}/{len(REPLACEMENTS)} replacements")
    print(f"'82.5' remaining in body: {remaining}")

    if remaining:
        print("ABORT: 82.5 still present. Refusing a partial correction —")
        print("       a half-fixed figure is worse than the original.")
        return 1
    if applied == 0:
        print("ABORT: nothing matched")
        return 1

    payload = {"html": new, "updated_at": post.get("updated_at")}
    for fld in ("custom_excerpt", "meta_description"):
        val = post.get(fld) or ""
        if "82.5" in val:
            for old, repl in REPLACEMENTS:
                val = val.replace(old, repl)
            val = val.replace("82.5", "53.2")
            payload[fld] = val
            print(f"  {fld} updated")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    api_call("PUT", f"posts/{post['id']}/?source=html", {"posts": [payload]})

    chk = api_call(
        "GET",
        f"posts/{post['id']}/?formats=html&fields=html,custom_excerpt,meta_description",
    )
    q = (chk.get("posts") or [{}])[0]
    print(f"\nnow: 82.5 in body = {'82.5' in (q.get('html') or '')}")
    print(f"     53.2 in body = {'53.2' in (q.get('html') or '')}")
    print(f"     excerpt: {(q.get('custom_excerpt') or '')[:90]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
