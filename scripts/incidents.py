#!/usr/bin/env python3
"""Collect road incidents from provincial 511 APIs.
Ontario 511 and BC DriveBC provide free, open incident data.
"""

import json, os, urllib.request
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

def collect_incidents():
    incidents = []

    # Ontario 511
    try:
        data = fetch_json("https://511on.ca/api/v2/get/event?format=json")
        for ev in data:
            # Filter to trucking-relevant: closures, construction, collisions
            etype = (ev.get("EventType") or "").lower()
            subtype = (ev.get("EventSubType") or "").lower()
            desc = (ev.get("Description") or "")

            # Only keep incidents that affect trucking
            relevant = any(w in etype or w in subtype or w in desc.lower()
                         for w in ["closure", "collision", "accident", "construction",
                                   "incident", "hazard", "roadwork", "emergency"])

            if relevant and ev.get("Latitude") and ev.get("Longitude"):
                incidents.append({
                    "id": f"ON-{ev['ID']}",
                    "province": "ON",
                    "highway": ev.get("RoadwayName", ""),
                    "direction": ev.get("DirectionOfTravel", ""),
                    "description": desc,
                    "event_type": etype,
                    "severity": ev.get("Severity", ""),
                    "closure": ev.get("IsFullClosure", False),
                    "lanes": ev.get("LanesAffected", ""),
                    "lat": float(ev["Latitude"]),
                    "lng": float(ev["Longitude"]),
                    "start": ev.get("StartDate"),
                    "end": ev.get("PlannedEndDate"),
                    "updated": ev.get("LastUpdated"),
                })
    except Exception as e:
        print(f"  ON 511: {e}")

    # BC DriveBC
    try:
        data = fetch_json("https://api.open511.gov.bc.ca/events?format=json&status=ACTIVE")
        for ev in data.get("events", []):
            headline = (ev.get("headline") or "").lower()
            desc = (ev.get("description") or "")

            # Only trucking-relevant
            relevant = any(w in headline or w in desc.lower()
                         for w in ["closure", "collision", "accident", "construction",
                                   "incident", "hazard", "roadwork", "emergency", "debris"])

            if relevant:
                # Extract coordinates from geography
                lat, lng = None, None
                geo = ev.get("geography", {})
                if geo.get("type") == "Point" and geo.get("coordinates"):
                    lng, lat = geo["coordinates"]

                if lat and lng:
                    roads = ev.get("roads", [])
                    road_name = roads[0] if roads else ""
                    incidents.append({
                        "id": ev["id"],
                        "province": "BC",
                        "highway": road_name,
                        "direction": "",
                        "description": ev.get("description", headline),
                        "event_type": headline,
                        "severity": ev.get("severity", ""),
                        "closure": "closed" in headline or "closure" in headline,
                        "lanes": "",
                        "lat": lat,
                        "lng": lng,
                        "start": ev.get("created"),
                        "end": "",
                        "updated": ev.get("updated"),
                    })
    except Exception as e:
        print(f"  BC DriveBC: {e}")

    # Normalize timestamps and sort
    for i in incidents:
        ts = i.get("updated")
        if isinstance(ts, str):
            try:
                i["_sort_ts"] = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except:
                i["_sort_ts"] = 0
        elif isinstance(ts, (int, float)):
            i["_sort_ts"] = float(ts)
        else:
            i["_sort_ts"] = 0

    incidents.sort(key=lambda i: i["_sort_ts"], reverse=True)
    incidents = incidents[:50]

    # Remove sort key
    for i in incidents:
        i.pop("_sort_ts", None)

    path = os.path.join(DATA_DIR, "incidents.json")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w") as f:
        json.dump({
            "incidents": incidents,
            "total": len(incidents),
            "updated": datetime.now(timezone.utc).isoformat(),
            "sources": ["Ontario 511", "BC DriveBC"],
        }, f, indent=2, default=str)

    print(f"  Incidents: {len(incidents)} road events (ON + BC)")

if __name__ == "__main__":
    collect_incidents()
