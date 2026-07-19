#!/usr/bin/env python3
"""Collect CBSA border wait times from public JSON endpoint."""
import json, urllib.request, os
from datetime import datetime

CBSA_URL = "https://www.cbsa-asfc.gc.ca/bwt-taf/bwt-eng.json"
OUT = os.path.expanduser("~/northern-mile-dashboard/data/border.json")

# Load existing border data
existing = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        existing = json.load(f)

# Map CBSA port names to our crossing IDs
# CBSA port name → crossing ID
CBSA_MAP = [
    ("Ambassador Bridge", "windsor-detroit"),
    ("Blue Water Bridge", "sarnia-port-huron"),
    ("Peace Bridge", "fort-erie-buffalo"),
    ("Queenston Lewiston", "queenston-lewiston"),
    ("Lacolle", "lacolle-champlain"),
    ("St-Bernard-de-Lacolle", "lacolle-champlain"),
    ("Thousand Islands", "lansdowne-alexandria"),
    ("Coutts", "coutts-sweetgrass"),
    ("Pacific Highway", "pacific-blaine"),
    ("Emerson", "emerson-pembina"),
]

req = urllib.request.Request(CBSA_URL, headers={"User-Agent": "NorthernMileMedia/1.0"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8-sig").split("//")[0])
except Exception as e:
    print(f"CBSA fetch failed: {e}")
    data = {"waitTimes": []}

# Update crossing data
updated = datetime.utcnow().isoformat()
live_count = 0

for cbsa in data.get("waitTimes", []):
    name = cbsa.get("poe-name", "")
    # Match CBSA name against our map
    matched = None
    for cbsa_name, our_id in CBSA_MAP:
        if cbsa_name.lower() in name.lower():
            matched = our_id
            break
    
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
                crossing["source"] = "cbsa"
                live_count += 1
                break

existing["updated"] = updated
existing["source_note"] = f"Live CBSA data. {live_count}/{len(CBSA_MAP)} crossings updated."

with open(OUT, "w") as f:
    json.dump(existing, f, indent=2)

print(f"Border updated: {live_count}/{len(CBSA_MAP)} crossings live from CBSA")
