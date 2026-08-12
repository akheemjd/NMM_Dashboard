#!/usr/bin/env python3
"""Content fingerprint — hash of published data values, timestamps excluded.

Deploy only when this changes. A refreshed fetch timestamp must never
produce a new fingerprint; a moved price always must.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
STATE = os.path.join(DATA, ".last_fingerprint")

# Any key matching these is volatile and excluded from the hash.
VOLATILE_KEYS = {
    "updated", "updated_at", "updated_iso", "build_version", "build_id",
    "generated_at", "last_success", "last_attempt", "live_updated",
    "captured_at", "source_note", "dateModified", "captured_utc",
    "fetch_attempted",
}

# Files whose values determine what the site says.
TRACKED = [
    "fuel.json",
    "exchange.json",
    "border.json",
    "theft.json",
    "incidents.json",
    "market.json",
    "news.json",
]


def strip_volatile(obj):
    """Recursively drop volatile keys so timestamps never affect the hash."""
    if isinstance(obj, dict):
        return {
            k: strip_volatile(v)
            for k, v in sorted(obj.items())
            if k not in VOLATILE_KEYS
        }
    if isinstance(obj, list):
        return [strip_volatile(i) for i in obj]
    return obj


def compute():
    h = hashlib.sha256()
    for name in TRACKED:
        path = os.path.join(DATA, name)
        if not os.path.exists(path):
            h.update(f"{name}:MISSING".encode())
            continue
        with open(path) as f:
            data = json.load(f)
        cleaned = strip_volatile(data)
        h.update(name.encode())
        h.update(json.dumps(cleaned, sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()


def last():
    if os.path.exists(STATE):
        with open(STATE) as f:
            return f.read().strip()
    return None


def save(fp):
    with open(STATE, "w") as f:
        f.write(fp + "\n")


if __name__ == "__main__":
    current = compute()
    previous = last()
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        print(f"current:  {current}")
        print(f"previous: {previous}")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "commit":
        save(current)
        print(f"fingerprint saved: {current[:12]}")
        sys.exit(0)
    # Default: exit 0 if changed (deploy), 1 if unchanged (skip)
    if current != previous:
        print(f"CHANGED {(previous or 'none')[:12]} -> {current[:12]}")
        sys.exit(0)
    print(f"UNCHANGED {current[:12]}")
    sys.exit(1)
