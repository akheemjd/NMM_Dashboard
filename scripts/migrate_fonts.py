#!/usr/bin/env python3
"""One-shot font-size floor migration. Every replacement count is asserted."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "assets", "styles.css")

# (dot-prefixed source, replacement, expected count after .km removal)
MIGRATIONS = [
    (".5rem", ".75rem", 1),
    (".5625rem", ".75rem", 11),
    (".625rem", ".8125rem", 9),
    (".6875rem", ".8125rem", 10),
]


def main():
    with open(CSS) as f:
        css = f.read()

    counts = {}
    ok = True
    for old, new, expected in MIGRATIONS:
        pat = re.compile(r"font-size:\s*" + re.escape(old) + r"(?!\d)")
        n = len(pat.findall(css))
        counts[old] = n
        status = "OK" if n == expected else "MISMATCH"
        if n != expected:
            ok = False
        print(f"  {old} -> {new}: found {n} (expected {expected}) [{status}]")

    if not ok:
        print("FATAL: count mismatch — no changes written.", file=sys.stderr)
        sys.exit(1)

    for old, new, expected in MIGRATIONS:
        pat = re.compile(r"font-size:\s*" + re.escape(old) + r"(?!\d)")
        css = pat.sub("font-size:" + new, css)

    with open(CSS, "w") as f:
        f.write(css)
    print(f"Font-size floor applied: {len(MIGRATIONS)} sizes migrated")


if __name__ == "__main__":
    main()
