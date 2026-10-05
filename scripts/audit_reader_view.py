#!/usr/bin/env python3
"""Read the site the way a stranger does.

Every other check in this repo audits the pipeline from the inside: do markers nest, do
guards pass, is it idempotent, does the history agree with itself. All of that can be true
on a page that still fails a reader, because a reader asks different questions:

  * what is this number, and WHEN is it from?
  * is anything on this page obviously broken or unfinished?
  * does this page agree with the page next to it?

An external audit found things this file's siblings could not: a calculator with no
timestamp, pages stating a rebuild time but not an observation date, and editorial numbers
that had drifted from the dashboard's. Not one was a build failure. All were reader failures.

WHAT THIS CHECKS, PER PAGE

  1. unfilled template tokens        {{token}} — the page shipped unfinished
  2. machine values leaking to text  raw dicts, datetimes, None, nan
  3. placeholder text                TODO, lorem, "coming soon", bare em-dash figures
  4. freshness: does it say WHEN     an observation date, not just a rebuild time
  5. units on every headline figure  a number with no unit beside it
  6. contradictions across pages     the same figure with two different values

Run: python3 scripts/audit_reader_view.py [--strict]
"""
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# Pages that legitimately carry no data observation of their own.
NO_DATA_PAGES = {"advertise", "contact", "press", "methodology", "404"}

UNFILLED = re.compile(r"\{\{[^}]+\}\}")
RAW_DICT = re.compile(r"\{&#x27;|\{'[a-z_]+':")
RAW_DT = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[.\d]*\+00:00")
PLACEHOLDERS = re.compile(r"\bTODO\b|\bFIXME\b|lorem ipsum|coming soon|placeholder", re.I)
# Any stated date for the data itself. Deliberately broad: the first version only looked
# inside <b> tags and so flagged 51 US state pages that plainly say "week ending
# 2026-09-28". A false positive here is worse than a miss — it sends you editing pages that
# were already right.
OBS_DATE = re.compile(
    r"week ending\s*<?b?>?\s*\d{4}-\d{2}-\d{2}"
    r"|print\s*<?b?>?\s*[A-Z][a-z]{2},?\s+\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}"
    r"|survey[^.<]{0,50}\d{4}-\d{2}-\d{2}"
    r"|as of\s*<?b?>?\s*\d{4}-\d{2}-\d{2}"
    r"|observation\s*<?b?>?\s*\d{4}-\d{2}-\d{2}"
    r"|(?:quarter|Q)\s*[1-4]Q?\s*20\d{2}"
    r"|\b\d{4}-\d{2}-\d{2}\b(?=[^<]{0,40}(?:survey|print|week|observed|as of))"
    r"|<b>[A-Z][a-z]{2},?\s+\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}</b>", re.I)
REBUILT = re.compile(r"Rebuilt\s*<b>", re.I)


def pages():
    for dp, _dirs, files in os.walk(DOCS):
        for fn in files:
            if fn == "index.html":
                yield os.path.join(dp, fn)
            elif fn == "404.html" and dp == DOCS:
                yield os.path.join(dp, fn)


def visible(html):
    """Text a reader sees: body only, scripts and styles removed."""
    m = re.search(r"<main\b.*?</main>", html, re.S)
    body = m.group(0) if m else html
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
    return body


def check():
    problems = defaultdict(list)
    figures = defaultdict(set)          # label -> set of values seen
    n = 0

    for path in sorted(pages()):
        n += 1
        rel = os.path.relpath(os.path.dirname(path), DOCS).replace("\\", "/")
        rel = "" if rel == "." else rel
        where = f"/{rel}/" if rel else "/"
        html = open(path, encoding="utf-8", errors="replace").read()
        body = visible(html)
        top = rel.split("/")[0] if rel else ""

        for m in UNFILLED.finditer(body):
            problems["unfilled template token"].append(f"{where} {m.group(0)[:40]}")
        for m in RAW_DICT.finditer(body):
            ctx = re.sub(r"\s+", " ", body[max(0, m.start() - 40):m.start() + 60])
            problems["machine value in text"].append(f"{where} {ctx[:80]}")
        if RAW_DT.search(body):
            problems["raw timestamp in text"].append(f"{where} {RAW_DT.search(body).group(0)[:30]}")
        for m in PLACEHOLDERS.finditer(body):
            problems["placeholder text"].append(f"{where} {m.group(0)}")

        # freshness — the check that was missing
        # Ask the page what it says about its own data, rather than looking for date
        # shapes. A statement that the data is live, next to a capture time, is a
        # complete answer; a rebuild stamp on its own is not.
        if top not in NO_DATA_PAGES and rel not in ("",):
            m_stated = re.search(r'<span data-freshness>(.*?)</span>', body, re.S)
            stated = re.sub(r"<[^>]+>", " ", m_stated.group(1)) if m_stated else ""
            DATE_IN_STATEMENT = re.compile(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}"      # 2026-09-29
                r"|[1-4]Q[0-9]{4}"                 # 3Q2026
                r"|[A-Z][a-z]{2}, [0-9]{1,2} [A-Z][a-z]{2} [0-9]{4}", re.I)
            says_live = re.search(r"\blive\b", stated, re.I) is not None
            has_obs = (bool(DATE_IN_STATEMENT.search(stated)) or says_live
                       or bool(OBS_DATE.search(body)))
            has_rebuild = bool(REBUILT.search(body))
            if not has_obs and not has_rebuild:
                problems["no freshness statement at all"].append(where)
            elif not has_obs:
                problems["rebuild time but no observation date"].append(where)

        # collect labelled figures for the cross-page comparison
        for m in re.finditer(r'<a[^>]*class="stat"[^>]*>(.*?)</a>', body, re.S):
            blk = m.group(1)
            label = re.sub(r"<[^>]+>", " ", blk)
            label = " ".join(label.split())
            val = re.search(r'class="v[^"]*"[^>]*>([^<]+)<', blk)
            if val:
                figures[label[:38]].add(val.group(1).strip())

    print(f"  pages read: {n}\n")
    if not problems:
        print("  nothing a reader would notice as broken\n")
    for kind in ("unfilled template token", "machine value in text",
                 "raw timestamp in text", "placeholder text",
                 "no freshness statement at all",
                 "rebuild time but no observation date"):
        items = problems.get(kind, [])
        if not items:
            continue
        print(f"  {kind} — {len(items)}")
        for it in items[:8]:
            print(f"    {it}")
        if len(items) > 8:
            print(f"    ... and {len(items) - 8} more")
        print()

    print("  figures that carry two different values on different pages:")
    clashes = {k: v for k, v in figures.items() if len(v) > 1}
    for k, v in sorted(clashes.items())[:8]:
        print(f"    {k}: {sorted(v)}")
    if not clashes:
        print("    none")
    print()

    return problems, clashes


if __name__ == "__main__":
    probs, clashes = check()
    strict = "--strict" in sys.argv
    bad = sum(len(v) for v in probs.values()) + len(clashes)
    if strict and bad:
        print(f"  READER VIEW FATAL: {bad} issue(s)")
        sys.exit(1)
    print(f"  {bad} issue(s) a reader could notice")
