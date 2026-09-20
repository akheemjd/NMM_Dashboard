#!/usr/bin/env python3
"""Render content docs to standalone HTML.

These are the documents that leave the building: the sponsorship kit, the data
hub offer. They get attached, forwarded and read by people who will not open a
markdown file, and a stale one is worse than none, because it is the first thing
a buyer reads and it cannot be corrected after it is sent.

Every doc listed here is rendered from its markdown sibling, so the two cannot
drift. Each render is checked for the specific stale claims that already shipped
once.

PDF is not produced here. WeasyPrint is installed but cannot load its GTK
libraries on this machine, and pandoc and wkhtmltopdf are absent. Export from a
browser, or install the GTK runtime.

Usage: python scripts/build_docs.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# doc markdown -> strings that must NOT survive into the render
DOCS = {
    "content/sponsorship/media-kit.md": ["2,500", "$10,000", "7:00 AM", "Launching August"],
    "content/services/data-hub-offer.md": ["$2,500", "per placement"],
}

CSS = """
:root { --paper:#FBFAF8; --ink:#1A1A17; --muted:#6B6862; --line:#E8E4DD; --signal:#0B5D3B; }
* { box-sizing: border-box; }
body {
  margin: 0 auto; padding: 44px 34px; max-width: 800px;
  background: var(--paper); color: var(--ink);
  font: 16px/1.62 Inter, -apple-system, Segoe UI, sans-serif;
}
h1 { font-size: 2rem; line-height: 1.15; letter-spacing: -.02em; margin: 0 0 8px; }
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
ul, ol { padding-left: 20px; margin: 0 0 14px; }
li { margin-bottom: 7px; }
strong { font-weight: 600; }
em { color: var(--muted); }
"""

HEAD = (
    '<!doctype html>\n<html lang="en-CA">\n<head>\n'
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>@TITLE@</title>\n'
    f'<style>{CSS}</style>\n</head>\n<body>\n'
)


def render(src: Path) -> tuple[str, str]:
    md = src.read_text(encoding="utf-8")
    first = next((l for l in md.splitlines() if l.startswith("# ")), src.stem)
    title = re.sub(r"^#\s*", "", first).strip()
    # Drop a leading italic editorial note. Internal notes about why a doc was
    # rewritten do not belong in the version a buyer reads.
    md = re.sub(r"^\s*\*[^*].*?\*\s*\n", "", md, count=1, flags=re.S)
    import markdown
    body = markdown.markdown(md, extensions=["tables", "sane_lists"])
    # .replace, not .format: the stylesheet is full of braces, which .format
    # tries to read as replacement fields and dies on.
    html = HEAD.replace("@TITLE@", title) + body + "\n</body>\n</html>\n"
    return title, html


def main() -> int:
    rc = 0
    for rel, stale in DOCS.items():
        src = ROOT / rel
        if not src.exists():
            print(f"MISSING {rel}", file=sys.stderr)
            rc = 1
            continue

        title, html = render(src)
        out = src.with_suffix(".html")
        out.write_text(html, encoding="utf-8")

        hits = [s for s in stale if s in html]
        if hits:
            print(f"FAIL {out.relative_to(ROOT)}: stale claim(s) survived: {hits}", file=sys.stderr)
            rc = 1
        else:
            print(f"  {out.relative_to(ROOT)}  ({len(html):,} bytes)  no stale claims")

    return rc


if __name__ == "__main__":
    sys.exit(main())
