#!/usr/bin/env python3
"""Render the sponsorship one-pager from its markdown.

content/sponsorship/media-kit.html was hand-made on 17 August 2026 and still
quoted $2,500 a placement, a 7:00 AM send and "launching August 19" weeks after
those stopped being true. A stale leave-behind is worse than none: it is the
document a sponsor reads first and it cannot be corrected after it is sent.

This keeps the HTML generated from media-kit.md so the two cannot drift.

PDF is not generated here. WeasyPrint is installed but cannot load its GTK
libraries on this machine, and pandoc and wkhtmltopdf are absent. Export from a
browser instead, or install the GTK runtime.

Usage: python scripts/build_media_kit.py
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content" / "sponsorship" / "media-kit.md"
OUT = ROOT / "content" / "sponsorship" / "media-kit.html"

CSS = """
:root { --paper:#FBFAF8; --ink:#1A1A17; --muted:#6B6862; --line:#E8E4DD; --signal:#0B5D3B; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 42px 34px; background: var(--paper); color: var(--ink);
  font: 16px/1.62 Inter, -apple-system, Segoe UI, sans-serif;
  max-width: 780px; margin-inline: auto;
}
h1 { font-size: 2rem; line-height: 1.15; letter-spacing: -.02em; margin: 0 0 6px; }
h2 {
  font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted);
  margin: 38px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line); font-weight: 600;
}
h3 { font-size: 1.05rem; margin: 24px 0 8px; }
p { margin: 0 0 13px; }
a { color: var(--signal); }
hr { border: 0; border-top: 1px solid var(--line); margin: 30px 0; }
table { width: 100%; border-collapse: collapse; margin: 0 0 16px; font-size: .95rem; }
th, td { text-align: left; padding: 9px 12px 9px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
ul { padding-left: 20px; margin: 0 0 14px; }
li { margin-bottom: 7px; }
strong { font-weight: 600; }
em { color: var(--muted); }
"""


def main():
    if not SRC.exists():
        print(f"missing {SRC}", file=sys.stderr)
        return 1

    text = SRC.read_text(encoding="utf-8")

    # Strip the italic revision note at the top, which is for us, not a sponsor.
    text = re.sub(r"^\*Rewritten.*?\*\s*\n\s*---\s*\n", "", text, flags=re.S)

    try:
        import markdown
        body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    except ImportError:
        print("python-markdown missing", file=sys.stderr)
        return 1

    html = (
        "<!doctype html>\n<html lang=\"en-CA\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Northern Mile Media — Sponsorship</title>\n"
        f"<style>{CSS}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )

    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html):,} bytes)")

    # Guard against the failure this script exists to prevent.
    stale = [s for s in ("2,500", "$10,000", "7:00 AM", "Launching August") if s in html]
    if stale:
        print(f"FAIL: stale claim(s) survived: {stale}", file=sys.stderr)
        return 1
    print("no stale rate or cadence claims")
    return 0


if __name__ == "__main__":
    sys.exit(main())
