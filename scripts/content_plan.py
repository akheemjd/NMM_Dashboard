#!/usr/bin/env python3
"""NMM content planner — decides what gets written today.

Maps the day of week to a content pillar, pulls the next unused topic from
data/content_queue.json, and records completion so topics never repeat.

Usage:
    python scripts/content_plan.py                    # today's assignment
    python scripts/content_plan.py --pillar deep      # force a pillar
    python scripts/content_plan.py --peek 3           # next 3 assignments
    python scripts/content_plan.py --complete <id>    # mark a topic done
    python scripts/content_plan.py --status           # queue depth per pillar
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT / "data" / "content_queue.json"

# Mon=0 ... Sun=6. Publishing days are Mon/Wed/Fri.
PILLAR_BY_WEEKDAY = {
    0: "market",   # Monday
    2: "deep",     # Wednesday
    4: "rules",    # Friday
}

PILLAR_LABELS = {
    "market": "Market Pulse",
    "deep": "Deep Dive",
    "rules": "Rules & Money",
}

PILLAR_BRIEF = {
    "market": (
        "Timely recap of this week's live dashboard numbers. 700-1,100 words. "
        "Lead with the single most newsworthy movement. Cover diesel, currency, "
        "and border conditions. Scannable, short paragraphs."
    ),
    "deep": (
        "One dataset examined properly. 1,200-2,000 words. Do not summarise the "
        "week — pick ONE thing and take it apart with the data in the brief. "
        "Include a comparison table. Explain the mechanism, not just the number."
    ),
    "rules": (
        "Explainer on a rule or regulation that costs carriers money. 1,000-1,600 words. "
        "State the rule, then show the arithmetic of compliance versus penalty. "
        "Use dashboard data where it connects, but the regulation is the spine. "
        "This is the blog's strongest performing category — be concrete and specific."
    ),
}


def load_queue():
    if not QUEUE_FILE.exists():
        raise FileNotFoundError(f"Missing topic bank: {QUEUE_FILE}")
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(q):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = QUEUE_FILE.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2, ensure_ascii=False)
    tmp.replace(QUEUE_FILE)


def completed_ids(q):
    return {c["id"] for c in q.get("completed", [])}


def next_topic(pillar, q=None):
    """Return the next unused topic dict for a pillar, or None if exhausted."""
    q = q or load_queue()
    done = completed_ids(q)
    for topic in q["queues"].get(pillar, []):
        if topic["id"] not in done:
            return topic
    return None


def mark_complete(topic_id, when=None, title=None):
    """Move a topic to completed. Idempotent."""
    q = load_queue()
    if topic_id in completed_ids(q):
        return False

    # Find the topic definition so we record its title
    found = None
    for pillar, topics in q["queues"].items():
        for t in topics:
            if t["id"] == topic_id:
                found = (pillar, t)
                break
        if found:
            break

    q.setdefault("completed", []).append({
        "id": topic_id,
        "pillar": found[0] if found else None,
        "title": title or (found[1]["title"] if found else topic_id),
        "completed_on": (when or date.today()).isoformat(),
    })

    if found:
        q.setdefault("last_published", {})[found[0]] = (when or date.today()).isoformat()

    save_queue(q)
    return True


def assignment_for(day, q=None):
    """Return the pillar assignment for a given date, or None on a non-publishing day."""
    pillar = PILLAR_BY_WEEKDAY.get(day.weekday())
    if not pillar:
        return None
    topic = next_topic(pillar, q)
    return {
        "date": day.isoformat(),
        "weekday": day.strftime("%A"),
        "pillar": pillar,
        "pillar_label": PILLAR_LABELS[pillar],
        "topic": topic,
        "writing_brief": PILLAR_BRIEF[pillar],
    }


def queue_status(q=None):
    q = q or load_queue()
    done = completed_ids(q)
    rows = []
    for pillar, topics in q["queues"].items():
        remaining = [t for t in topics if t["id"] not in done]
        rows.append({
            "pillar": pillar,
            "label": PILLAR_LABELS.get(pillar, pillar),
            "total": len(topics),
            "remaining": len(remaining),
            "next": remaining[0]["title"] if remaining else "(exhausted)",
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="NMM content planner")
    ap.add_argument("--pillar", choices=list(PILLAR_BY_WEEKDAY.values()),
                    help="Force a pillar instead of using today's weekday")
    ap.add_argument("--peek", type=int, metavar="N", help="Show the next N publishing days")
    ap.add_argument("--complete", metavar="TOPIC_ID", help="Mark a topic as published")
    ap.add_argument("--status", action="store_true", help="Show queue depth per pillar")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = ap.parse_args()

    if args.complete:
        changed = mark_complete(args.complete)
        print(f"marked complete: {args.complete}" if changed else f"already complete: {args.complete}")
        return 0

    if args.status:
        rows = queue_status()
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        print("Pillar queue depth")
        print("-" * 58)
        for r in rows:
            print(f"  {r['label']:16} {r['remaining']:>2} remaining / {r['total']:>2} total")
            print(f"      next: {r['next']}")
        return 0

    if args.peek:
        q = load_queue()
        day = date.today()
        shown = 0
        while shown < args.peek:
            a = assignment_for(day, q)
            if a:
                if args.json:
                    print(json.dumps(a, indent=2))
                else:
                    t = a["topic"]
                    label = t["title"] if t else "(queue exhausted)"
                    print(f"{a['date']} {a['weekday'][:3]}  {a['pillar_label']:16} {label}")
                shown += 1
                # Simulate consumption so the peek advances
                if a["topic"]:
                    q.setdefault("completed", []).append({"id": a["topic"]["id"]})
            day += timedelta(days=1)
        return 0

    # Default: today's (or forced) assignment
    if args.pillar:
        topic = next_topic(args.pillar)
        a = {
            "date": date.today().isoformat(),
            "weekday": date.today().strftime("%A"),
            "pillar": args.pillar,
            "pillar_label": PILLAR_LABELS[args.pillar],
            "topic": topic,
            "writing_brief": PILLAR_BRIEF[args.pillar],
            "forced": True,
        }
    else:
        a = assignment_for(date.today())

    if a is None:
        print(f"{date.today().strftime('%A')} is not a publishing day (Mon/Wed/Fri).")
        print("Use --pillar to force an assignment.")
        return 0

    if args.json:
        print(json.dumps(a, indent=2))
        return 0

    print(f"=== NMM Assignment — {a['date']} ({a['weekday']}) ===")
    print(f"  Pillar: {a['pillar_label']}")
    if a["topic"]:
        t = a["topic"]
        print(f"  Topic:  {t['title']}")
        print(f"  ID:     {t['id']}")
        print(f"  Keyword:{t['keyword']}")
        print(f"  Angle:  {t['angle']}")
        print(f"  Source: {t['source']}")
    else:
        print("  Topic:  (queue exhausted — add topics to data/content_queue.json)")
    print()
    print(f"  Writing brief: {a['writing_brief']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
