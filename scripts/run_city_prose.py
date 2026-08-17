#!/usr/bin/env python3
"""One-off driver: generate city prose via the writer profile, in batches.

Runs `writer chat -q` once per province batch. Slugs and file paths are
derived from the same slugify() as build_city_pages.py, so there is no
path mismatch. Tightened rule: literal facts only, never infer a price
position that facts.md does not state.
"""
import os
import re
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from collect_nrcan_diesel import CITY_PROVINCE  # noqa: E402

ROOT = "/home/hermes/northern-mile-dashboard"
FACTS = f"{ROOT}/content/cities/facts.md"


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


by_prov = defaultdict(list)
for city, prov in CITY_PROVINCE.items():
    by_prov[prov].append(city)
for prov in by_prov:
    by_prov[prov].sort()

# Calgary + Edmonton already grounded in batch 1; keep them.
# The other four AB cities get regenerated under the tightened rule.
already_good = {"Calgary", "Edmonton"}
ab_redo = [c for c in by_prov["AB"] if c not in already_good]

on = sorted(by_prov["ON"])
batches = [
    ab_redo,
    by_prov["BC"],
    by_prov["MB"] + by_prov["PE"],
    by_prov["NB"],
    by_prov["NL"] + by_prov["SK"],
    by_prov["NS"],
    on[:10],
    on[10:],
    by_prov["QC"],
]

RULES = (
    "Generate Northern Mile city prose. Read " + FACTS + ". "
    "For each city below, write ONE plain paragraph (80-120 words) to the given "
    "file path, explaining why the city prices where it does using ONLY the literal "
    "facts in facts.md. State only what facts.md says; if a city has no explicit price "
    "position there, omit any position claim — do not infer it. No specific prices or "
    "numbers. Northern Mile voice: plain, authoritative, no hedging, no em dashes, no "
    "semicolons. One paragraph per file, no headings, no bullets. Do not run voice_lint; "
    "the orchestrator lints after."
)


def run_batch(cities):
    lines = [f"{c} -> {ROOT}/content/cities/{slugify(c)}.md" for c in cities]
    prompt = RULES + "\n\n" + "\n".join(lines)
    print(f"\n=== batch ({len(cities)} cities): {cities[0]} ... ===", flush=True)
    try:
        r = subprocess.run(
            ["writer", "chat", "-q", prompt],
            capture_output=True, text=True, timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("BATCH TIMED OUT (600s)", flush=True)
        return False
    tail = (r.stdout or "").strip().splitlines()[-3:]
    for line in tail:
        print(line, flush=True)
    if r.returncode != 0:
        print(f"BATCH FAILED (exit {r.returncode}): {(r.stderr or '')[-400:]}", flush=True)
        return False
    return True


ok = 0
for b in batches:
    if run_batch(b):
        ok += 1
print(f"\n=== DONE: {ok}/{len(batches)} batches succeeded ===", flush=True)
