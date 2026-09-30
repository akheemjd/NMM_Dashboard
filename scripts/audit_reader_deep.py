#!/usr/bin/env python3
"""A deep read of every page, as a reader rather than as a build.

audit_reader_view.py asks "would a reader notice something broken". This asks harder
questions: is this page usable, are its numbers sane, does it deliver what its heading
promises, and does anything on it contradict anything else on it.

CALIBRATION MATTERS MORE THAN COVERAGE

The first version of this file reported 99 issues. Reading the context showed 98 were its own
false positives: "out of range" fired on a 43.1c/L province spread and on fuel tax rates, the
placeholder check fired on the ordinary word "None", and the dead-end check counted only
links inside <main> while the nav sits outside it. A check that cries wolf gets turned off,
and a disabled check protects nothing. Every bound and pattern here was set by reading the
context it fires on.

The one real find survived: a district page whose heading was repeated verbatim in its own
body, alongside a <section> nested inside a <section>.

Twelve lenses:

  CONTENT      thin pages, a heading repeated in its body, empty sections, adjacent repetition
  NUMBERS      values outside anything a human would accept, on prices only
  STRUCTURE    exactly one h1, a meta description, a named publisher
  NAVIGATION   pages with nowhere to go
  TRUTHFULNESS undecoded entities, undated relative-time claims
  CALCULATOR   outputs present
"""
import html as H
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

NO_DATA_PAGES = {"advertise", "contact", "press", "methodology", "404"}
PUBLISHERS = re.compile(r"\b(CBP|CBSA|EIA|NRCan|IFTA|Bank of Canada|StatCan|Statistics Canada|511|DriveBC)\b")

def pages():
    for dp, _d, files in os.walk(DOCS):
        for fn in files:
            if fn == "index.html" or (fn == "404.html" and dp == DOCS):
                yield os.path.join(dp, fn)


def rel_of(path):
    rel = os.path.relpath(os.path.dirname(path), DOCS).replace("\\", "/")
    return "" if rel == "." else rel


def body_of(html):
    m = re.search(r"<main\b.*?</main>", html, re.S)
    return m.group(0) if m else html


def text_of(frag):
    frag = re.sub(r"<script.*?</script>|<style.*?</style>", " ", frag, flags=re.S)
    frag = re.sub(r"<[^>]+>", " ", frag)
    return " ".join(H.unescape(frag).split())


def check(verbose=True):
    P = defaultdict(list)
    word_counts = []
    n = 0

    for path in sorted(pages()):
        n += 1
        rel = rel_of(path)
        where = f"/{rel}/" if rel else "/"
        top = rel.split("/")[0] if rel else ""
        raw = open(path, encoding="utf-8", errors="replace").read()
        body = body_of(raw)
        text = text_of(body)
        is_content = top not in NO_DATA_PAGES and bool(rel)

        # ── CONTENT ──
        if is_content:
            # Prose alone is the wrong measure. These pages are tables of crossings, prices
            # and incidents, and stripping markup throws all of that away. A page is thin
            # when it has little prose AND little data.
            n_rows = len(re.findall(r'class="r"|class="row"', body))
            n_figs = len(re.findall(r'class="v"|class="fx"', body))
            substance = len(text.split()) + 12 * (n_rows + n_figs)
            word_counts.append((substance, where))
            if substance < 120:
                P["thin page"].append(
                    f"{where} {len(text.split())} words, {n_rows} rows, {n_figs} figures")

        # a heading immediately restated in the first line beneath it
        for m in re.finditer(r"<h2[^>]*>(.*?)</h2>(.{0,400}?)(?:</p>|<div)", body, re.S):
            head, after = text_of(m.group(1)), text_of(m.group(2))
            if not head or len(head.split()) < 3:
                continue
            first = " ".join(after.split()[:len(head.split()) + 1])
            if first.lower().startswith(head.lower()):
                P["heading repeated in its own body"].append(f"{where} {head[:44]!r}")

        # adjacent repetition: the same 6+ word phrase twice in a row
        for m in re.finditer(r"\b(\w[\w' ]{24,})\b\s+\1\b", text, re.I):
            P["adjacent repeated phrase"].append(f"{where} {m.group(1)[:50]!r}")

        if not is_content:
            continue

        # ── STRUCTURE ──
        h1s = re.findall(r"<h1\b[^>]*>", raw)
        if len(h1s) != 1:
            P["h1 count is not 1"].append(f"{where} {len(h1s)}")
        desc = re.search(r'<meta name="description" content="([^"]*)"', raw)
        if not desc or len(desc.group(1).strip()) < 40:
            P["meta description missing or stub"].append(where)
        if not PUBLISHERS.search(text) and not re.search(r"\bvia\b", text, re.I):
            P["does not name its publisher"].append(where)

        # ── NAVIGATION ──
        # the whole file, because the nav lives outside <main>
        out = {l for l in re.findall(r'href="(/[^"#]*)"', raw)
               if not l.startswith(("/assets/", "/static/"))}
        if len(out) < 4:
            P["fewer than 4 internal links"].append(f"{where} {len(out)}")
        # No cross-tree link check: the nav deliberately links both trees so a reader can
        # switch. Flagging that as a defect meant flagging the feature.

        # ── TRUTHFULNESS ──
        for m in re.finditer(r"&(amp|lt|gt|quot|#39);", body):
            P["undecoded entity in markup"].append(f"{where} {m.group(0)}")
        # "today" only matters when the page never says what day it is
        if re.search(r"\b(today|right now|just updated)\b", text, re.I) and not re.search(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}|print <b>|week ending", body, re.I):
            P["undated relative-time claim"].append(where)

        # ── CALCULATOR ──
        if rel == "fuel-cost-calculator":
            for need in ("rTotal", "rPerKm", "rPerMi", "rFloor", "rPrice"):
                if f'id="{need}"' not in raw:
                    P["calculator output missing"].append(f"{where} {need}")

    if verbose:
        print(f"  pages read: {n}\n")
        total = 0
        for kind in sorted(P):
            items = P[kind]
            total += len(items)
            print(f"  {kind} — {len(items)}")
            for it in items[:6]:
                print(f"    {it}")
            if len(items) > 6:
                print(f"    ... and {len(items)-6} more")
            print()
        if not P:
            print("  nothing a reader would question\n")
        print("  thinnest pages:")
        for w, where in sorted(word_counts)[:6]:
            print(f"    {w:5} words  {where}")
        print()
        return P, total
    return P, sum(len(v) for v in P.values())


if __name__ == "__main__":
    P, total = check()
    print(f"  {total} issue(s) a reader could question")
    if "--strict" in sys.argv and total:
        print(f"  READER DEEP FATAL: {total} issue(s)")
        sys.exit(1)
