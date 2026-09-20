#!/usr/bin/env python3
"""Refresh an already-published brief, and correct a future published_at.

Two separate things, both on posts that are already live.

1. BODY — regenerate the brief with real links to the week's articles and
   write the result back. The published brief had a "Read this week's posts"
   section containing no links, which made it read as a thin duplicate of the
   article it was supposed to be pointing at. Updating the body does NOT
   re-send the email; only publishing does.

2. DATE — a post can carry a published_at in the future and still be live,
   which puts a post dated "tomorrow" at the top of the blog. This corrects it
   to when the post actually went live.

Usage:
  python scripts/refresh_brief.py <slug> [--body] [--date] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import (  # noqa: E402
    api_call, markdown_to_html, find_post_by_slug, _load_dotenv,
)
from weekly_brief import build_brief  # noqa: E402
from send_weekly_brief import recent_posts  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--body", action="store_true", help="Regenerate the body")
    ap.add_argument("--date", action="store_true",
                    help="Set published_at to the real publish time")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if not args.body and not args.date:
        ap.error("pass --body and/or --date")

    _load_dotenv()
    post = find_post_by_slug(args.slug)
    if not post:
        print(f"not found: {args.slug}")
        return 1

    pid = post["id"]
    print(f"post:      {post.get('title')}")
    print(f"published: {post.get('published_at')}")

    payload = {"updated_at": post.get("updated_at")}

    if args.body:
        title, subtitle, md = build_brief(recent_posts=recent_posts())
        if title != post.get("title"):
            print(f"WARNING: regenerated title differs ({title!r})")
            print("         writing the existing title back, not the new one")
            title = post.get("title")
        html = markdown_to_html(md)
        links = html.count("<a href=")
        print(f"body:      {len(html)} chars, {links} links")
        if links < 2:
            print("ABORT: regenerated body has too few links, refusing to write")
            return 1
        payload["html"] = html
        payload["custom_excerpt"] = subtitle
        payload["meta_description"] = subtitle

    if args.date:
        created = post.get("created_at")
        print(f"date:      moving published_at {post.get('published_at')} -> {created}")
        payload["published_at"] = created

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    r = api_call("PUT", f"posts/{pid}/?source=html", {"posts": [payload]})
    p = (r.get("posts") or [{}])[0]

    chk = api_call("GET", f"posts/{pid}/?formats=html&fields=html,published_at,feature_image,email_only")
    q = (chk.get("posts") or [{}])[0]
    stored = q.get("html") or ""
    print(f"\nnow: published_at={q.get('published_at')}")
    print(f"     body={len(stored)} chars  links={stored.count('<a href=')}")
    print(f"     feature_image={'set' if q.get('feature_image') else 'MISSING'}"
          f"  email_only={q.get('email_only')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
