#!/usr/bin/env python3
"""Collect US-bound border wait times from the CBP public API.

WHY THIS EXISTS
---------------
The dashboard covered 9 crossings from CBSA, which is the Canada-bound feed.
CBP publishes the other direction (US-bound) for **85 ports** with a lane class
the Canadian side does not expose at all: commercial vehicles, broken into
standard and FAST lanes, each with delay_minutes and lanes_open.

So this is not a duplicate of collect_border.py. CBSA answers "how long to get
into Canada" and CBP answers "how long to get into the US". A carrier needs both.

DATA-INTEGRITY RULES (learned the hard way elsewhere in this repo)
------------------------------------------------------------------
1. A MISSING DELAY IS NOT ZERO. At fetch time only ~38 of 85 ports carried a
   numeric commercial delay. The rest read "N/A", "Lanes Closed" or "Update
   Pending". Rendering those as 0 would claim "no delay" at a port that simply
   did not report, which is the single most damaging thing this page could say.
   Missing stays None all the way to the template.
2. Never overwrite a good value with a failed fetch. If the API is down the
   previous cbp_border.json is left untouched and the failure is recorded in
   health_tracker, matching how collect_border.py behaves.
3. Ports are keyed on port_number, which is stable. Names repeat (three ports
   are called "Blaine", four are "Buffalo/Niagara Falls"), so a name-keyed map
   would silently collapse distinct crossings into one.

Source: https://bwt.cbp.gov/api/bwtnew  (US Customs and Border Protection,
public JSON, no key, updated hourly per port)
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CBP_URL = "https://bwt.cbp.gov/api/bwtnew"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "cbp_border.json")

# Curated jurisdiction pairing. CBP does not publish the crossing's jurisdiction,
# so this maps each US port to the US state it sits in and the Canadian province
# it faces. Both sides are named because a carrier reading "Pembina" needs to
# know that means Emerson, MB on the far side.
#
# Keyed on port_number. If CBP adds a port it lands in the output untagged
# rather than being dropped, and the coverage note below counts the gap.
PORT_JURISDICTION = {
    "070801": ("NY", "ON", "Lansdowne"),
    "070401": ("NY", "ON", "Cornwall"),
    "070101": ("NY", "ON", "Prescott"),
    "071201": ("NY", "QC", "Lacolle"),
    "090101": ("NY", "ON", "Fort Erie"),
    "090102": ("NY", "ON", "Niagara Falls"),
    "090103": ("NY", "ON", "Queenston"),
    "090104": ("NY", "ON", "Queenston"),
    "011501": ("ME", "NB", "St. Stephen"),
    "011502": ("ME", "NB", "St. Stephen"),
    "011503": ("ME", "NB", "St. Stephen"),
    "010601": ("ME", "NB", "Woodstock"),
    "010401": ("ME", "QC", "Armstrong"),
    "L01901": ("ME", "NB", "Edmundston"),
    "020901": ("VT", "QC", "Stanstead"),
    "021201": ("VT", "QC", "Philipsburg"),
    "021101": ("VT", "QC", "Stanhope"),
    "300401": ("WA", "BC", "Surrey"),
    "300402": ("WA", "BC", "Surrey"),
    "300403": ("WA", "BC", "Point Roberts"),
    "302301": ("WA", "BC", "Aldergrove"),
    "300901": ("WA", "BC", "Abbotsford"),
    "331001": ("MT", "AB", "Coutts"),
    "340101": ("ND", "MB", "Emerson"),
    "360401": ("MN", "ON", "Fort Frances"),
    "380001": ("MI", "ON", "Windsor"),
    "380002": ("MI", "ON", "Windsor"),
    "380102": ("MI", "ON", "Windsor"),
    "380201": ("MI", "ON", "Sarnia"),
    "380301": ("MI", "ON", "Sault Ste. Marie"),
}

# Values CBP uses for "no figure provided". Anything else is treated as a number.
NO_DATA = {"", "n/a", "na", "null", "none", "update pending", "lanes closed",
           "not applicable", "-", "--"}


def to_minutes(raw):
    """Return an int, or None when CBP did not publish a figure.

    Returning 0 for an unparsable value is the bug this whole module guards
    against. 0 means "we measured no delay", None means "no measurement".
    """
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return int(raw)
    s = str(raw).strip()
    if s.lower() in NO_DATA:
        return None
    # CBP sometimes emits "10 min" / "10 minutes"
    head = s.split()[0]
    try:
        return int(float(head))
    except (ValueError, IndexError):
        return None


def to_int(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if s.lower() in NO_DATA:
        return None
    try:
        return int(float(s))
    except (ValueError, IndexError):
        return None


def lane_block(d):
    """Normalise one lane class (commercial / passenger / pedestrian)."""
    if not isinstance(d, dict):
        return None
    out = {
        "max_lanes": to_int(d.get("maximum_lanes")),
        "automation": (d.get("cv_automation_type") or d.get("pv_automation_type")
                       or d.get("ped_automation_type") or None),
        "standard": None,
        "fast": None,
        "nexus": None,
        "ready": None,
    }

    def sub(key, dmin_key="delay_minutes"):
        s = d.get(key)
        if not isinstance(s, dict):
            return None
        return {
            "delay": to_minutes(s.get(dmin_key)),
            "lanes_open": to_int(s.get("lanes_open")),
            "status": (s.get("operational_status") or None),
            "as_of": (s.get("update_time") or None),
        }

    out["standard"] = sub("standard_lanes")
    # CBP labels the commercial fast lane two different ways depending on class
    out["fast"] = sub("FAST_lanes") or sub("fast_lanes")
    out["nexus"] = sub("NEXUS_SENTRI_lanes")
    out["ready"] = sub("ready_lanes")
    return out


def slugify(port, crossing):
    """Stable URL slug. Port number keeps duplicates distinct."""
    import re
    base = f"{port} {crossing}".strip().lower() if crossing else port.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-")
    return base or "port"


def collect_cbp_border():
    req = urllib.request.Request(CBP_URL, headers={
        "User-Agent": "NorthernMileDashboard/1.0 (+https://dashboard.northernmilemedia.com/)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    captured = datetime.now(timezone.utc)
    ports = []
    for p in raw:
        pnum = str(p.get("port_number") or "").strip()
        port_name = (p.get("port_name") or "").strip()
        crossing = (p.get("crossing_name") or "").strip()
        border = (p.get("border") or "").strip()
        us_state, ca_prov, ca_city = PORT_JURISDICTION.get(pnum, (None, None, None))

        cv = lane_block(p.get("commercial_vehicle_lanes"))
        pv = lane_block(p.get("passenger_vehicle_lanes"))
        ped = lane_block(p.get("pedestrian_lanes"))

        # The headline number. None when unpublished, which the template renders
        # as "not reported" rather than "no delay".
        cv_std = (cv or {}).get("standard") or {}
        cv_delay = cv_std.get("delay")

        ports.append({
            "port_number": pnum,
            "port_name": port_name,
            "crossing_name": crossing,
            "label": crossing or port_name,
            "slug": slugify(port_name, crossing),
            "border": border,
            "country_pair": "CA-US" if border == "Canadian Border" else (
                "MX-US" if border == "Mexican Border" else None),
            "us_state": us_state,
            "ca_province": ca_prov,
            "ca_city": ca_city,
            "jurisdiction_known": bool(us_state),
            "hours": (p.get("hours") or "").strip() or None,
            "port_status": (p.get("port_status") or "").strip() or None,
            "commercial": cv,
            "commercial_delay": cv_delay,
            "commercial_reported": cv_delay is not None,
            "passenger": pv,
            "pedestrian": ped,
            "agency_date": (p.get("date") or None),
            "agency_time": (p.get("time") or None),
        })

    canadian = [x for x in ports if x["border"] == "Canadian Border"]
    mexican = [x for x in ports if x["border"] == "Mexican Border"]
    cv_reported = [x for x in ports if x["commercial_reported"]]
    cv_ca = [x for x in canadian if x["commercial_reported"]]

    # Health: the feed answering is not the same as the feed carrying data. A
    # response with zero parsable commercial delays is a failure worth knowing
    # about, not a success.
    try:
        from health_tracker import record_success, record_failure
        if cv_reported:
            record_success("cbp_border")
        else:
            record_failure("cbp_border", "Feed responded but no commercial delays parsed")
    except Exception as e:
        print(f"  cbp_border health tracking failed: {e}")

    payload = {
        "ports": ports,
        "counts": {
            "total": len(ports),
            "canadian": len(canadian),
            "mexican": len(mexican),
            "commercial_delay_reported": len(cv_reported),
            "commercial_delay_reported_canadian": len(cv_ca),
            "jurisdiction_unknown": sum(1 for x in ports if not x["jurisdiction_known"]),
        },
        "source": "U.S. Customs and Border Protection border wait times API",
        "source_url": CBP_URL,
        "source_note": (f"CBP: {len(cv_reported)} of {len(ports)} ports reported a "
                        f"commercial delay at fetch time. Ports with no published "
                        f"figure are shown as not reported, not as zero."),
        "direction": "US-bound",
        "captured_utc": captured.isoformat(),
        "fetched_date": captured.strftime("%Y-%m-%d"),
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"  CBP border: {len(ports)} ports "
          f"({len(canadian)} CA, {len(mexican)} MX), "
          f"{len(cv_reported)} commercial delays reported "
          f"({len(cv_ca)} on the Canadian border)")
    return payload


if __name__ == "__main__":
    collect_cbp_border()
