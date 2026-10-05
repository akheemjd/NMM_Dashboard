#!/usr/bin/env python3
"""No page compares a country to its own average.

WHY THIS EXISTS

/us/ once read "Canada higher than the Canadian average of 189.9¢/L" - a sentence that cannot
be true. A guard was written for it in check_data_integrity.py and it has never fired on a real
page, for two independent reasons found by negative-testing every guard in the suite.

1. The separator was [^.] - which cannot cross a decimal point. Every real sentence has a price
   like 12.4 between the country and the comparison:

       "Canada runs 12.4 cents higher than the Canadian national average."  -> no match
       "Canada runs 12 cents higher than the Canadian national average."    -> match

   The cleaner the sentence, the more reliably it was missed.

2. It only fired when the page belonged to the OTHER country, so the mirrored defect - a US page
   reading "the United States runs higher than the US average" - passed.

Both are fixed in check_data_integrity.py and the corrected pattern is verified here against the
module's own source strings.

WHY A STANDALONE SCRIPT

With both faults fixed the registered check still returns 0 on a page that visibly contains the
sentence, while this file finds it. That is the second time in one session a function reached
through check_data_integrity.CHECKS has disagreed with identical code run directly - the earlier
one was the head-markup check, which shipped as scripts/check_head_markup.py for the same reason.
The suite harness is itself now suspect and deserves its own audit; until then, a check that
demonstrably fires is worth more than one that reads correctly and does nothing.

Exit 0 clean, 1 on any page comparing a country to its own average.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

# A decimal is allowed; a sentence end still stops the match.
_SEP = r"(?:[^.!?]|\.(?=\d))"
PAT = re.compile(
    r"\b(Canada|Canadian|US|United States|American)\b" + _SEP + r"{0,80}?"
    r"\b(higher|lower|above|below|more|less|cheaper|dearer)\b" + _SEP + r"{0,90}?"
    r"\b(Canadian|US|United States|American)\s+(?:national\s+)?average",
    re.I,
)
US_WORDS = ("us", "united", "american")


def is_us_side(text):
    low = text.strip().lower()
    return low.startswith(US_WORDS)


def main():
    if not os.path.isdir(DOCS):
        print("XBRDCHECK SKIP: no docs/")
        return 0

    bad = []
    scanned = 0
    for dirpath, _dirs, files in os.walk(DOCS):
        if "index.html" not in files:
            continue
        rel = os.path.relpath(dirpath, DOCS).replace(os.sep, "/")
        if rel == ".":
            rel = ""
        if not (rel == "us" or rel.startswith("us-diesel") or rel == "ca"
                or rel.startswith("diesel-prices") or rel == "fuel-prices"):
            continue
        scanned += 1
        html = open(os.path.join(dirpath, "index.html"), encoding="utf-8",
                    errors="replace").read()
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        for m in PAT.finditer(text):
            if is_us_side(m.group(1)) == is_us_side(m.group(3)):
                bad.append(f"/{rel}/: {m.group(0)[:84]}")

    if bad:
        print(f"XBRDCHECK FAIL: {len(bad)} sentence(s) compare a country to its own average")
        for b in bad[:10]:
            print(f"  - {b}")
        return 1

    print(f"XBRDCHECK OK: no page compares a country to its own average ({scanned} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
