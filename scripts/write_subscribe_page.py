#!/usr/bin/env python3
"""Populate the Ghost /subscribe/ page.

Every subscribe CTA on both sites points here, and the page was a heading with
an empty body. A reader who clicked the dashboard's only conversion link got a
blank page. This writes the actual offer.

The copy states what arrives, when, how often, and what it costs, because the
Portal modal that opens elsewhere in the funnel says none of that either.

Usage: python scripts/write_subscribe_page.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from ghost_publish import api_call, markdown_to_html, lint_markdown, _load_dotenv  # noqa: E402

BODY = """
The Northern Mile Brief is one email a week about what fuel, the border and the
dollar are doing to Canadian carriers.

## What lands in your inbox

- The NRCan diesel print, by province, with the week's move
- Border wait times at the crossings that matter for commercial traffic
- USD/CAD, and what a soft loonie does to a cross-border fill
- What we think is worth acting on before your next set of fills

## What it costs

Nothing. There is no paywall, no ad slot and no upsell. The dashboard stays free
and so does this.

## When it arrives

Wednesday morning, once a week. That is the whole schedule. If a week has
nothing worth your time, you will not hear from us twice to make up for it.

## Where the numbers come from

Every figure is a primary source, named and dated: the Natural Resources Canada
weekly retail survey, the Canada Border Services Agency, the Bank of Canada and
the US Energy Information Administration. Every number we publish carries its
source and a copy-paste citation. If we get something wrong, we correct it in
the next issue and say what changed.

## Unsubscribing

One click, in every email, no questions asked.
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    ok, out = lint_markdown(BODY)
    print(f"voice lint: {out.splitlines()[0] if out else 'no output'}")
    if not ok:
        print("\nREFUSING to write: the copy failed the voice lint.")
        print(out)
        return 1

    _load_dotenv()
    r = api_call("GET", "pages/?limit=all&fields=id,slug,title,status,updated_at")
    page = next((p for p in r.get("pages", []) if p.get("slug") == "subscribe"), None)
    if not page:
        print("no /subscribe/ page found")
        return 1

    html = markdown_to_html(BODY)
    print(f"page:  /{page['slug']}/  status={page.get('status')}")
    print(f"body:  {len(html)} chars")

    if args.dry_run:
        print("\ndry run — nothing written")
        return 0

    api_call("PUT", f"pages/{page['id']}/?source=html", {
        "pages": [{"html": html, "updated_at": page.get("updated_at")}]
    })

    chk = api_call("GET", f"pages/{page['id']}/?formats=html&fields=html,status")
    stored = ((chk.get("pages") or [{}])[0]).get("html") or ""
    print(f"\nnow:   body={len(stored)} chars  status={page.get('status')}")
    if len(stored) < 500:
        print("FAIL: body did not store")
        return 1
    print("verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
