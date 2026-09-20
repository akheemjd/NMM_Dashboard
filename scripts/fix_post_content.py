#!/usr/bin/env python3
"""Fix two content defects in already-published blog posts.

1. The IFTA post states the penalty rule correctly ("the greater of 50 dollars
   or 10 percent of the net tax you owe") and then reports a 50 dollar penalty
   on 2,300 dollars of net tax, where 10 percent is 230 dollars. The post
   contradicts itself four paragraphs apart. The rule as stated is the actual
   IFTA rule, so the reported figure is the error.

   NOTE: that figure appears inside an anecdote attributed to a named third
   party, so this is a judgement call. The alternative reading is that the
   minimum genuinely applied and the anecdote is right. Verify with the source
   if it matters. What is not defensible is publishing both numbers.

2. The CRA post ends with a markdown-style link that was never given a URL:
   "[our post on incorporating vs. sole proprietorship for a Canadian owner-op]"
   and that post does not exist. Dead bracket in one of the three best posts.

Usage: python scripts/fix_post_content.py [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import api_call, _load_dotenv  # noqa: E402

IFTA = "ifta-filing-deadlines-for-canadian-carriers-in-2026-and-the-mistakes-that-trigger-audits"
CRA = "cra-psb-owner-operator-audit-canada"

REPLACEMENTS = {
    IFTA: [
        ("plus a 50 dollar penalty and 180 dollars in interest",
         "plus a 230 dollar penalty and 180 dollars in interest"),
    ],
    CRA: [
        (r"\s*\[our post on incorporating vs\. sole proprietorship for a Canadian owner-op\]",
         " our post on incorporating versus sole proprietorship, when it goes up"),
    ],
}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    _load_dotenv()
    rc = 0

    for slug, pairs in REPLACEMENTS.items():
        r = api_call("GET", f"posts/slug/{slug}/?formats=html&fields=id,html,updated_at")
        post = (r.get("posts") or [{}])[0]
        if not post.get("id"):
            print(f"{slug}: not found")
            rc = 1
            continue

        html = post.get("html") or ""
        new = html
        hits = 0
        for old, rep in pairs:
            n = len(re.findall(old, new))
            if n:
                new = re.sub(old, rep, new)
                hits += n
                print(f"{slug}\n    {n}x  {old[:64]!r}")

        if not hits:
            print(f"{slug}: nothing to change")
            continue

        if args.dry_run:
            continue

        api_call("PUT", f"posts/{post['id']}/?source=html", {
            "posts": [{"html": new, "updated_at": post.get("updated_at")}]
        })
        chk = api_call("GET", f"posts/{post['id']}/?formats=html&fields=html")
        stored = ((chk.get("posts") or [{}])[0]).get("html") or ""
        if stored.strip() == html.strip():
            print("    FAIL: body unchanged")
            rc = 1
        else:
            print(f"    verified ({len(stored)} chars)")

    return rc


if __name__ == "__main__":
    sys.exit(main())
