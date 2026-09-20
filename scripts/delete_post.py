#!/usr/bin/env python3
"""Delete a Ghost post by slug.

Refuses to delete anything that is not a draft unless --force is given, so a
published post cannot be removed by accident.

Usage:  python scripts/delete_post.py <slug> [--force]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import api_call, find_post_by_slug, _load_dotenv  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--force", action="store_true",
                    help="Allow deleting a published post")
    args = ap.parse_args(argv)

    _load_dotenv()
    p = find_post_by_slug(args.slug)
    if not p:
        print(f"not found: {args.slug}")
        return 1

    if p.get("status") == "published" and not args.force:
        print(f"REFUSING: '{args.slug}' is published. Pass --force if you mean it.")
        return 1

    api_call("DELETE", f"posts/{p['id']}/")
    print(f"deleted [{p.get('status')}] {args.slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
