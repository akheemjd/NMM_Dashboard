#!/usr/bin/env python3
"""The publishing killswitch.

WHY THIS EXISTS
---------------
data/killswitch.json has said this since 2026-07-17:

    {"publish": true, "note": "Set publish to false to pause all publishing.
     Collection, build, and archiving continue."}

Nothing read it. The only reference in the whole repository was in a DEAD
archived builder (archive/orphan-builders/build_dashboard.py.DEAD) and a
documentation dump. Every live path that publishes — the Ghost publisher, the
newsletter sender, and the dashboard deploy — ignored the file entirely, so
setting publish to false and expecting publishing to stop did nothing at all.

That is worse than having no switch. A control someone reaches for during an
incident, which silently does nothing, is a control that turns a bad hour into a
bad week: the operator believes publishing has stopped and stops watching.

This module makes it real. The contract in the note is honoured exactly:

    collection      keeps running
    build           keeps running
    archiving       keeps running
    PUBLISHING      stops

So `publish: false` does not freeze the data. It stops the two things that put
words in front of the public: the Ghost publish and the newsletter send.

FAIL CLOSED ON A BROKEN FILE
----------------------------
If the file exists but cannot be parsed, publishing is BLOCKED rather than
allowed. The whole point of a killswitch is that it is trusted when something
else is wrong, and a half-written JSON file is exactly when you want the safe
answer. A missing file is treated as "publish", because the switch has to be
able to be absent without stopping the site.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "killswitch.json")


def load():
    """Return (allow_publish: bool, reason: str)."""
    if not os.path.exists(PATH):
        return True, "no killswitch file"
    try:
        with open(PATH, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        return False, f"killswitch unreadable ({e}) — blocking publish"
    val = d.get("publish", True)
    if val is False:
        return False, "killswitch is OFF (data/killswitch.json publish=false)"
    if val not in (True, False):
        # Anything that is not an explicit boolean is not a decision to publish.
        return False, f"killswitch has an unusable publish value {val!r} — blocking publish"
    return True, "killswitch is on"


def check(what="publish"):
    """Exit non-zero if publishing is switched off.

    Call at the top of anything that publishes. Prints nothing when publishing is
    allowed, so a healthy run stays silent.
    """
    ok, reason = load()
    if not ok:
        print(f"KILLSWITCH: {what} blocked — {reason}")
        sys.exit(3)
    return True


def status():
    ok, reason = load()
    return {"publish": ok, "reason": reason}


if __name__ == "__main__":
    ok, reason = load()
    print(f"{'PUBLISHING ON ' if ok else 'PUBLISHING OFF'}  ({reason})")
    sys.exit(0 if ok else 3)
