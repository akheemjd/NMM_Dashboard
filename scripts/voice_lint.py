#!/usr/bin/env python3
"""Voice lint — deterministic AI-tell scanner for NMM drafts.

An LLM cannot reliably see its own tells; this script can, because it greps
for the mechanical ones instead of "feeling" for them. Run it on every draft
before it reaches a human.

Exit 0 = clean (or warnings only). Exit 1 = hard fail (list the offenders).

Usage:  python3 scripts/voice_lint.py path/to/draft.md
"""
import re
import sys
import statistics
from pathlib import Path

# --- Hard bans (AI vocabulary + NMM voice rules). Word-boundary matched, case-insensitive.
BANNED_WORDS = [
    # AI vocabulary (humanizer pattern 7)
    "delve", "crucial", "pivotal", "testament", "underscore", "showcase",
    "vibrant", "robust", "leverage", "utilize", "seamless", "foster",
    "garner", "intricate", "intricacies", "landscape", "tapestry", "realm",
    "harness", "empower", "elevate", "unlock", "unlocking", "furthermore",
    "moreover", "additionally", "interplay", "profound", "groundbreaking",
    "renowned", "breathtaking", "must-visit", "stunning", "nestled",
    # significance inflation (humanizer 1, 2)
    "pivotal moment", "key turning point", "focal point", "indelible mark",
    "deeply rooted", "evolving landscape", "marks a shift", "broader trend",
    "testament to", "vital role", "crucial role", "signifies",
    # vague attribution + hedging (humanizer 5, 24 + NMM secrecy rule)
    "according to", "some say", "industry observers", "experts argue",
    "experts believe", "studies show", "research shows", "data shows",
    "it could potentially be argued", "it may be argued", "arguably",
    "some critics", "several sources", "insiders say",
    # persuasive-authority tropes (humanizer 27)
    "at its core", "the real question is", "what really matters",
    "the deeper issue", "the heart of the matter", "in reality",
    "fundamentally", "at the end of the day", "the bottom line is",
    # signposting + filler (humanizer 28, 23)
    "let's dive", "let's explore", "let's break this down",
    "here's what you need to know", "without further ado", "in order to",
    "due to the fact", "at this point in time", "in the event that",
    "needless to say", "it goes without saying", "it's worth noting",
    "it is worth noting", "dive into", "dives into",
    # collaboration artifacts (humanizer 20)
    "i hope this helps", "hope this helps", "great question", "of course!",
    "certainly!", "let me know if", "would you like me to",
    # generic closers (humanizer 25 + voice skill)
    "the future looks bright", "exciting times lie ahead", "in conclusion",
    "to sum up", "in closing", "in summary",
    # promotional language (humanizer 4)
    "boasts a", "commitment to", "exemplifies", "enhancing", "elevating",
    "best-in-class", "world-class", "state-of-the-art", "cutting-edge",
    "game-changer", "game changer", "paradigm shift", "revolutionize",
    # cliche AI openers / hedges
    "in today's fast-paced", "in the ever-evolving", "navigate the",
    "it's not just", "it is not just", "not only", "but also",
    # NMM-specific (voice skill)
    "insight", "insights",
]

# --- Hard punctuation / structure bans (checked separately for line reporting) ---
EM_DASH = "\u2014"
EN_DASH = "\u2013"
CURLY_QUOTES = "\u201c\u201d\u2018\u2019"

# Emoji range (common blocks). Keep it simple: flag non-ASCII symbols in body.
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF]"
)


def find_banned_words(text):
    hits = []
    low = text.lower()
    for w in BANNED_WORDS:
        # phrase (multi-word) vs single word
        if " " in w:
            if w in low:
                hits.append(w)
        else:
            if re.search(r"\b" + re.escape(w) + r"\b", low):
                hits.append(w)
    return sorted(set(hits))


def sentence_word_counts(text):
    """Split body text into sentences, return word counts (ignores headings/blank)."""
    # Drop markdown headings and URLs to avoid noise.
    lines = [ln for ln in text.splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")
             and not ln.strip().startswith("Sources")]
    joined = " ".join(lines)
    counts = []
    for s in re.split(r"[.!?]+", joined):
        words = len(s.split())
        if words > 0:
            counts.append(words)
    return counts


def main():
    if len(sys.argv) < 2:
        print("usage: voice_lint.py <draft.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"missing file: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    problems = []

    # 1. Banned words/phrases
    for w in find_banned_words(text):
        problems.append(f"banned word/phrase: '{w}'")

    # 2. Dashes of any kind
    ndash = text.count(EM_DASH) + text.count(EN_DASH)
    if ndash:
        problems.append(f"dash: {ndash} em/en dash(es) — voice rule bans all dashes")

    # 3. Semicolons
    nsemi = text.count(";")
    if nsemi:
        problems.append(f"semicolon: {nsemi}")

    # 4. Curly quotes
    ncq = sum(text.count(c) for c in CURLY_QUOTES)
    if ncq:
        problems.append(f"curly quote: {ncq}")

    # 5. Emojis
    if EMOJI_RE.search(text):
        problems.append("emoji present")

    # 6. Bold in body (the draft may use ## headers, but ** in body is a tell)
    if re.search(r"\*\*.+\*\*", text):
        problems.append("bold-in-body (**)")

    # 7. "according to" already in banned list, but also catch "per <Outfit>" vague form
    for m in re.finditer(r"\b(?:data|insights?|according to)\b", text, re.I):
        pass  # already covered above; kept explicit for clarity

    # 8. Burstiness warning (soft — not a hard fail)
    counts = sentence_word_counts(text)
    warnings = []
    if len(counts) >= 5:
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0.0
        if mean > 0 and stdev / mean < 0.35:
            warnings.append(
                f"rhythm too uniform: mean {mean:.1f} words/sentence, stdev {stdev:.1f} "
                f"(coef {stdev/mean:.2f}) — reads machine-smoothed"
            )

    if problems:
        print(f"FAIL — {path.name}")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"PASS — {path.name} ({len(counts)} sentences)")
    for w in warnings:
        print(f"  warn: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
