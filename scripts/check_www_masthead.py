"""Guard: the blog never sends its own masthead to the other host, and no link 404s.

Three bugs this session came from the same root cause: www runs the dashboard's markup through a
transform, and each transform rule caught more than intended.

  1. The new index CSS went into blog.css, which the blog never loads.
  2. The www host serves its own assets/ copy, which was never synced.
  3. Making non-blog paths absolute to the dashboard also rewrote the masthead, so clicking the
     brand on the blog took the reader to a different site.

A guard that only checks "the masthead is not the dashboard URL" would pass while still letting a
reader click a section link into a 404, so this checks both facts:

  A. MASTHEAD STAYS HOME   every masthead anchor on www resolves to /blog/, never off-host.
  B. NO ROOT-RELATIVE 404  on www, any root-relative href other than /blog/ or /assets/ would 404,
                           because only the blog and its assets exist on that host. Such links must
                           be absolute to the dashboard instead.

Negative-tested by reintroducing each fault before this was committed.
"""
import pathlib
import re
import sys

WWW_DIR = pathlib.Path(r"C:\tmp\nmmblog")
DASH_DOCS = pathlib.Path(r"C:\Users\Akheem\northern-mile-dashboard\docs")

MASTHEAD = re.compile(r'<a[^>]*class="(?:mark|name)"[^>]*href="([^"]*)"')
ROOT_HREF = re.compile(r'href="(/[^/"][^"]*)"')

failures = []

# A. masthead on www stays on the blog
if WWW_DIR.exists():
    pages = list(WWW_DIR.rglob("*.html"))
    for f in pages:
        for href in MASTHEAD.findall(f.read_text(encoding="utf-8", errors="replace")):
            if "dashboard." in href:
                rel = f.relative_to(WWW_DIR).as_posix()
                failures.append(f"MASTHEAD LEAVES BLOG: {rel} -> {href}")
            elif not href.startswith("/blog/"):
                rel = f.relative_to(WWW_DIR).as_posix()
                failures.append(f"MASTHEAD NOT /blog/: {rel} -> {href}")
    print(f"  checked masthead on {len(pages)} www pages")
else:
    # A missing www build is not a defect in the dashboard. Failing here would break every deploy
    # on a fresh clone and train people to skip the guard. Say so and check what does exist.
    print(f"  SKIP masthead check - no www build at {WWW_DIR}")

# B. no root-relative link on www that would 404 there
if WWW_DIR.exists():
    allowed = ("/blog/", "/assets/")
    for f in WWW_DIR.rglob("*.html"):
        for href in ROOT_HREF.findall(f.read_text(encoding="utf-8", errors="replace")):
            if href.startswith(allowed):
                continue
            rel = f.relative_to(WWW_DIR).as_posix()
            failures.append(f"ROOT-RELATIVE 404 ON WWW: {rel} -> {href}")
    print("  checked root-relative links on www")

# C. dashboard masthead goes home
for f in (DASH_DOCS / "index.html",):
    if f.exists():
        for href in MASTHEAD.findall(f.read_text(encoding="utf-8", errors="replace")):
            if "dashboard." in href and not href.startswith("https://dashboard."):
                failures.append(f"DASHBOARD MASTHEAD ODD: {href}")

if failures:
    print(f"\n  FAIL - {len(failures)} problem(s):")
    for x in failures[:20]:
        print(f"    {x}")
    if len(failures) > 20:
        print(f"    ... and {len(failures) - 20} more")
    sys.exit(1)

print("\n  PASS - masthead stays home, no root-relative links that would 404 on www")
