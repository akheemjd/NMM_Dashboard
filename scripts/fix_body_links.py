#!/usr/bin/env python3
"""Repoint dashboard links in Ghost post bodies at the right domain.

The writer produced bodies linking to www.northernmilemedia.com/fuel-prices/
and similar. Those paths exist on the DASHBOARD host, not the blog host, so
every one of them 404s. Nothing caught it: check_links.py walks docs/ (the
static dashboard build) and the blog pipeline never inspects a body's links.

Usage:
  python scripts/fix_body_links.py <slug> [--dry-run]
  python scripts/fix_body_links.py --all [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import api_call, _load_dotenv  # noqa: E402

BLOG_HOST = "https://www.northernmilemedia.com"
DASH_HOST = "https://dashboard.northernmilemedia.com"

# Dashboard-only paths. A link to one of these on the blog host is always
# a mistake, because the blog serves none of them.
DASH_PATHS = (
    "fuel-prices", "border-wait-times", "freight-barometer", "border-trends",
    "fuel-cost-calculator", "exchange-rate", "road-incidents", "market-pulse",
    "industry-news", "diesel-prices", "us-diesel", "methodology", "press",
)


def bad_links(html):
    out = []
    for host in (BLOG_HOST, "https://northernmilemedia.com"):
        for p in DASH_PATHS:
            for sep in ("/", "/#"):
                needle = f"{host}/{p}{sep}"
                if needle in html:
                    out.append(f"{host}/{p}/")
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true", help="Every published post")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if not args.slug and not args.all:
        ap.error("pass a slug or --all")

    _load_dotenv()

    if args.all:
        r = api_call("GET", "posts/?limit=all&filter=status:published"
                            "&fields=id,slug,title,updated_at")
        posts = [{"slug": p["slug"], "id": p["id"], "title": p.get("title"),
                  "updated_at": p.get("updated_at")} for p in r.get("posts", [])]
    else:
        r = api_call("GET", f"posts/slug/{args.slug}/?fields=id,slug,title,updated_at")
        posts = r.get("posts") or []

    fixed = 0
    for p in posts:
        rr = api_call("GET", f"posts/{p['id']}/?formats=html&fields=html,updated_at")
        full = (rr.get("posts") or [{}])[0]
        html = full.get("html") or ""
        bad = bad_links(html)
        if not bad:
            continue

        new = html
        for host in (BLOG_HOST, "https://northernmilemedia.com"):
            for path in DASH_PATHS:
                new = new.replace(f"{host}/{path}/", f"{DASH_HOST}/{path}/")
                new = re.sub(rf"{re.escape(host)}/{path}\b", f"{DASH_HOST}/{path}/", new)

        print(f"{p['slug']}")
        for b in bad:
            print(f"    was: {b}")
        print(f"    ->  {DASH_HOST}/...")

        if args.dry_run:
            continue

        api_call("PUT", f"posts/{p['id']}/?source=html", {
            "posts": [{"html": new, "updated_at": full.get("updated_at")}]
        })
        chk = api_call("GET", f"posts/{p['id']}/?formats=html&fields=html")
        stored = ((chk.get("posts") or [{}])[0]).get("html") or ""
        left = bad_links(stored)
        if left:
            print(f"    STILL BAD: {left}")
            return 1
        print("    verified clean")
        fixed += 1

    if args.dry_run:
        print(f"\ndry run — {len(posts)} post(s) scanned")
    else:
        print(f"\n{fixed} post(s) repaired")
    return 0


if __name__ == "__main__":
    sys.exit(main())
