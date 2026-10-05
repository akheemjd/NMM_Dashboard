#!/usr/bin/env python3
"""Keep every meta description inside the length a search engine will show.

The audit found 72 of 170 pages over 165 characters, 63 of them US-diesel pages. The text was
accurate in every case - the fault was length, not content:

    Texas diesel by district and the fuel tax TX actually levies. IFTA rate $0.2000 a gallon,
    state excise $0.2000 a gallon. EIA prices diesel by district, not by state, and this page
    says which district Texas is in.                                     <- 212 chars

Google shows roughly 155 to 160 characters on desktop and fewer on a phone, so the tail of every
one of those pages was being cut off - often mid-clause, and usually losing the part that said
what the page actually is.

Trimmed at a word boundary, then at a clause boundary if one falls late enough to keep the
sentence whole. Nothing is rewritten: the opening of every description is already the strongest
part, so the job is to stop before the diminishing returns start.

Runs after the builders and before the guards, so the guards see the shipped bytes.
Exit 0 always; it reports what it changed.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

LIMIT = 155          # leaves room for the ellipsis-free cut and any engine-added suffix
MIN_FLOOR = 110      # never cut below this; a shorter description is worse than a long one
DESC_RE = re.compile(r'(<meta name="description" content=")([^"]*)(")')


def trim(text, limit=LIMIT):
    """Shorten to `limit` at a word boundary, preferring a clause end."""
    if len(text) <= limit:
        return text, False
    window = text[:limit]
    # a clause boundary near the end reads better than a chopped word
    for mark in (". ", "; ", ", "):
        i = window.rfind(mark)
        if i >= MIN_FLOOR:
            return window[:i + (1 if mark[0] == "." else 0)].rstrip(), True
    i = window.rfind(" ")
    if i >= MIN_FLOOR:
        return window[:i].rstrip(), True
    return window.rstrip(), True


def main():
    if not os.path.isdir(DOCS):
        print("DESCTRIM SKIP: no docs/")
        return 0

    changed = []
    longest_before = 0
    for root, _dirs, files in os.walk(DOCS):
        if os.sep + "assets" in root or "index.html" not in files:
            continue
        path = os.path.join(root, "index.html")
        html = open(path, encoding="utf-8", errors="replace").read()
        head_end = html.find("</head>")
        head = html[:head_end] if head_end > 0 else html

        def sub(m):
            nonlocal longest_before
            original = m.group(2)
            longest_before = max(longest_before, len(original))
            new, did = trim(original)
            if did:
                rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
                changed.append((rel, len(original), len(new)))
            return m.group(1) + new + m.group(3)

        new_head = DESC_RE.sub(sub, head, count=1)
        if new_head != head:
            open(path, "w", encoding="utf-8").write(new_head + html[head_end:])

    # verify: nothing may remain over the limit
    over = 0
    for root, _dirs, files in os.walk(DOCS):
        if os.sep + "assets" in root or "index.html" not in files:
            continue
        html = open(os.path.join(root, "index.html"), encoding="utf-8",
                    errors="replace").read()
        m = DESC_RE.search(html.split("</head>")[0])
        if m and len(m.group(2)) > LIMIT:
            over += 1

    if over:
        print(f"DESCTRIM WARN: {over} description(s) still over {LIMIT}")
        return 0

    if changed:
        print(f"DESCTRIM: trimmed {len(changed)} of 170 descriptions to <= {LIMIT} chars")
        for rel, a, b in changed[:6]:
            print(f"  {a:>4} -> {b:>4}  {rel}")
    else:
        print(f"DESCTRIM OK: every description is within {LIMIT} chars")
    return 0


if __name__ == "__main__":
    sys.exit(main())
