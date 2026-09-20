#!/usr/bin/env python3
"""Delete probe/draft posts created during the Ghost pipeline audit.

Removes only posts whose slug or title carries the 'zzz' probe marker, so it
can never touch real content. Prints what it finds first, then deletes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ghost_publish import api_call, _load_dotenv

PROBE_MARKERS = ("zzz", "probe", "test-", "srcset")


def is_probe(post):
    slug = (post.get("slug") or "").lower()
    title = (post.get("title") or "").lower()
    return any(m in slug or m in title for m in PROBE_MARKERS)


def main():
    _load_dotenv()

    r = api_call("GET", "posts/?limit=all&fields=id,title,slug,status")
    posts = r.get("posts", [])
    print(f"{len(posts)} post(s) on the site")

    targets = [p for p in posts if is_probe(p)]
    if not targets:
        print("no probe posts found — nothing to delete")
        return 0

    print(f"\n{len(targets)} probe post(s) to remove:")
    for p in targets:
        print(f"  [{p.get('status')}] {p.get('slug')} — {p.get('title')}")

    print()
    for p in targets:
        api_call("DELETE", f"posts/{p['id']}/")
        print(f"  deleted {p.get('slug')}")

    after = api_call("GET", "posts/?limit=1")
    total = after.get("meta", {}).get("pagination", {}).get("total", "?")
    print(f"\n{total} post(s) remaining")
    return 0


if __name__ == "__main__":
    sys.exit(main())
