#!/usr/bin/env python3
"""Collect CBSA border wait times from public JSON endpoint."""
import json, urllib.request, os
from datetime import datetime, timezone

CBSA_URL = "https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.json"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "border.json")

# Map CBSA port names to our crossing IDs
# CBSA port name → crossing ID
# CBSA publishes "<Port>: <Route>". Match the PORT exactly — never by substring.
# A substring matcher let "Lacolle" swallow "St-Bernard-de-Lacolle" because it sat
# first in the list, so three distinct ports shared one entry and the last record
# in the feed won. See the module docstring in fix_border_port_match.py.
CBSA_PORT_MAP = {
    "Ambassador Bridge": "windsor-detroit",
    "Blue Water Bridge": "sarnia-port-huron",
    "Peace Bridge": "fort-erie-buffalo",
    "Queenston Lewiston": "queenston-lewiston",
    "St-Bernard-de-Lacolle": "lacolle-champlain",
    "Thousand Islands": "lansdowne-alexandria",
    "Coutts": "coutts-sweetgrass",
    "Pacific Highway": "pacific-blaine",
    "Emerson": "emerson-pembina",
}

# Real CBSA ports we deliberately do not publish. Listed so the omission is a
# decision on the record rather than an accident, and so the reserved names are
# visible to anyone tempted to add a looser rule.
IGNORED_PORTS = {
    "Lacolle": "Route 221 and Route 223 — secondary crossings, not among the nine curated",
}


def match_port(cbsa_name):
    """Return the crossing id for a CBSA name, or None.

    Splits "<Port>: <Route>" and matches the port exactly. Falls back to a
    longest-first scan of the map keys for names that carry no route suffix,
    which is still exact-per-key rather than arbitrary-substring.
    """
    if not cbsa_name:
        return None
    port = cbsa_name.split(":")[0].strip()
    if port in CBSA_PORT_MAP:
        return CBSA_PORT_MAP[port]
    # Longest key first so a more specific name always beats a shorter one that
    # happens to be contained in it.
    for key in sorted(CBSA_PORT_MAP, key=len, reverse=True):
        if key.lower() == port.lower():
            return CBSA_PORT_MAP[key]
    return None


def collect_border_live():
    # Load existing border data
    existing = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            existing = json.load(f)

    req = urllib.request.Request(CBSA_URL, headers={"User-Agent": "NorthernMileMedia/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8-sig").split("//")[0])
    except Exception as e:
        print(f"CBSA fetch failed: {e}")
        data = {"waitTimes": []}

    # Update crossing data
    updated = datetime.now(timezone.utc).isoformat()
    live_ids = set()

    for cbsa in data.get("waitTimes", []):
        name = cbsa.get("poe-name", "")
        # Match CBSA name against our map
        matched = match_port(name)

        if matched:
            for crossing in existing.get("crossings", []):
                if crossing["id"] == matched:
                    comm_delay = cbsa.get("poe-comm-delay", 0)
                    trav_delay = cbsa.get("poe-trav-delay", 0)
                    # Parse string delays like "3 minutes"
                    if isinstance(comm_delay, str):
                        try: comm_delay = int(comm_delay.split()[0])
                        except: comm_delay = -5
                    if isinstance(trav_delay, str):
                        try: trav_delay = int(trav_delay.split()[0])
                        except: trav_delay = -5

                    if comm_delay >= 0:
                        delay_min = comm_delay
                        status = "Live"
                        delay_str = f"{delay_min} min" if delay_min > 0 else "No delay"
                    elif trav_delay >= 0:
                        delay_min = trav_delay
                        status = "Live"
                        delay_str = f"{delay_min} min" if delay_min > 0 else "No delay"
                    else:
                        status = "Live"
                        delay_str = "Check CBSA"
                        delay_min = 0

                    crossing["status"] = status
                    crossing["delay"] = delay_str
                    crossing["delay_minutes"] = delay_min
                    crossing["live_updated"] = cbsa.get("poe-updated", "")
                    crossing["captured_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    crossing["source"] = "cbsa"
                    live_ids.add(matched)
                    break

    existing["updated"] = updated
    unique_ids = len(set(CBSA_PORT_MAP.values()))
    live_count = len(live_ids)
    if live_count == 0:
        existing["source_note"] = "CBSA fetch returned no matching crossings. Delays below are from the last successful fetch."
        existing["live_fetch_ok"] = False
    else:
        existing["source_note"] = f"CBSA feed: {live_count} of {unique_ids} crossings updated."
        existing["live_fetch_ok"] = True
    existing["fetch_attempted"] = updated

    with open(OUT, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Border updated: {live_count}/{unique_ids} crossings live from CBSA")


if __name__ == "__main__":
    collect_border_live()
