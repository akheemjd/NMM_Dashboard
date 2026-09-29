#!/usr/bin/env python3
"""Collect road incidents from provincial 511 APIs.
Ontario 511 and BC DriveBC provide free, open incident data.
"""

import json, os, urllib.request
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env(name):
    """Read a setting from the environment or the repo .env.

    The deploy cron runs in a fresh shell with no exports, so .env is the source of truth.
    Same reasoning as ghost_publish._load_dotenv.
    """
    v = os.environ.get(name)
    if v:
        return v.strip()
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return ""
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, val = line.split("=", 1)
        if k.strip() == name:
            return val.strip()
    return ""


ON511_KEY = _env("NMM_ON511_API_KEY")

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def _coords(geo):
    """Latitude and longitude from a GeoJSON Point or LineString.

    DriveBC returns both. Handling only Point dropped 32 of its 50 events before the
    relevance filter even mattered. For a LineString the first coordinate is the start of
    the affected segment, which is the end a driver reaches first.
    """
    if not isinstance(geo, dict):
        return None, None
    t = geo.get("type")
    c = geo.get("coordinates")
    if not c:
        return None, None
    if t == "Point":
        lng, lat = c[0], c[1]
    elif t == "LineString":
        lng, lat = c[0][0], c[0][1]
    elif t == "MultiLineString":
        lng, lat = c[0][0][0], c[0][0][1]
    else:
        return None, None
    try:
        return float(lat), float(lng)
    except (TypeError, ValueError, IndexError):
        return None, None


def collect_incidents():
    incidents = []

    # Ontario 511 — requires a developer key.
    if not ON511_KEY:
        print("  ON 511: NMM_ON511_API_KEY is not set — Ontario incidents will be missing. "
              "Get a free key at https://511on.ca/developers/resources")
    else:
        try:
            data = fetch_json("https://511on.ca/api/v2/get/event?format=json"
                              f"&key={ON511_KEY}")
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError(data["error"])
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
                # Extract coordinates from geography — Point or LineString
                lat, lng = _coords(ev.get("geography"))

                if lat is not None and lng is not None:
                    # roads is a list of dicts, not strings. Assigning roads[0] put a raw
                    # Python dict into the highway field, so BC rows would have rendered
                    # "{'name': 'Highway 1', 'from': 'Trans-Canada H..." on the page.
                    roads = ev.get("roads") or []
                    road_name = ""
                    if roads:
                        r0 = roads[0]
                        road_name = (r0.get("name", "") if isinstance(r0, dict)
                                     else str(r0))
                        # "Highway 37 near Highway 37" reads as a bug. Only add the
                        # landmark when it says something the road name does not.
                        frm = r0.get("from", "") if isinstance(r0, dict) else ""
                        if frm and frm.strip().lower() not in road_name.strip().lower():
                            road_name = f"{road_name} near {frm}" if road_name else str(frm)
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

    # Per source, not global. A single newest-50 cut let ON's 516 fresher events fill every
    # slot and starve BC entirely — the file held 50 incidents and all of them were ON
    # while the log claimed "ON + BC". A cap that lets one source crowd out another is
    # worse than no cap, because it looks like coverage.
    PER_SOURCE = 25
    kept, seen = [], {}
    for i in incidents:
        prov = i.get("province", "?")
        seen[prov] = seen.get(prov, 0) + 1
        if seen[prov] <= PER_SOURCE:
            kept.append(i)
    incidents = kept

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

    by_prov = {}
    for i in incidents:
        by_prov[i.get("province", "?")] = by_prov.get(i.get("province", "?"), 0) + 1
    parts = ", ".join(f"{k} {v}" for k, v in sorted(by_prov.items())) or "none"
    print(f"  Incidents: {len(incidents)} road events ({parts})")

if __name__ == "__main__":
    collect_incidents()
