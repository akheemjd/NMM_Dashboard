#!/usr/bin/env python3
"""Render /border-wait-times/all-ports/ from the CBP feed.

Closes the coverage gap: the crossing pages cover 9 Canada-bound crossings from
CBSA, and this page carries all 85 ports CBP publishes in the US-bound
direction, on both borders, with commercial, passenger and pedestrian lanes.

The one rule that matters here: a port with no published commercial delay is
rendered as "not reported", never as 0. At fetch time roughly 37 of 85 ports
report a figure. Printing "No delay" for the other 48 would claim a measurement
the agency never made, on the exact page a driver would use to decide whether to
roll. check_data_integrity.py asserts the underlying distinction too.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")

sys.path.insert(0, HERE)
from build_templates import fill, load_json  # noqa: E402

SLUG = "all-ports"


def delay_text(minutes):
    """None is NOT zero. This is the whole point of the module."""
    if minutes is None:
        return "not reported"
    if minutes == 0:
        return "No delay"
    return f"{minutes} min"


def lane_summary(port, key):
    """Compact lane readout: delay, lanes open, whether FAST is offered."""
    block = port.get(key) or {}
    std = block.get("standard") or {}
    fast = block.get("fast") or {}
    bits = [delay_text(std.get("delay"))]
    if std.get("lanes_open"):
        bits.append(f"{std['lanes_open']} lanes")
    if fast.get("delay") is not None:
        bits.append(f"FAST {delay_text(fast['delay'])}")
    return " · ".join(bits)


def row(port):
    name = port.get("port_name") or ""
    crossing = port.get("crossing_name") or ""
    # CBP repeats the port name as the crossing name for single-crossing ports
    # (Pembina, Sumas). Printing "Pembina Pembina" reads like a bug.
    suffix = f" — {crossing}" if crossing and crossing != name else ""
    # Two Naco, Arizona ports exist (260301 and 260305) and CBP gives
    # neither a crossing name, so both rendered as a bare "Naco": the page
    # showed 84 rows for 85 ports and one port had no row of its own.
    if not suffix and port.get("port_number"):
        suffix = f" — port {port['port_number']}"
    juris = ""
    if port.get("us_state") and port.get("ca_province"):
        juris = f" · {port['us_state']}–{port['ca_province']}"
        if port.get("ca_city"):
            juris += f" → {port['ca_city']}"
    return {
        "port_name": name,
        "crossing_suffix": suffix,
        "jurisdiction": juris,
        "commercial_display": lane_summary(port, "commercial"),
        "slug": port.get("slug") or "",
    }


def main():
    cbp = load_json("cbp_border")
    ports = cbp.get("ports") or []
    if not ports:
        raise SystemExit("cbp_border.json carries no ports — run the collector first")

    ca = [p for p in ports if p.get("border") == "Canadian Border"]
    mx = [p for p in ports if p.get("border") == "Mexican Border"]

    # Sort by jurisdiction then name so the list is scannable, and so unknown
    # jurisdictions group at the end rather than interleaving.
    ca.sort(key=lambda p: ((p.get("us_state") or "zz"), (p.get("port_name") or ""),
                           (p.get("crossing_name") or "")))
    mx.sort(key=lambda p: ((p.get("port_name") or ""), (p.get("crossing_name") or "")))

    reported = [p for p in ports if p.get("commercial_reported")]

    page_data = {
        "port_count": str(len(ports)),
        "ca_count": str(len(ca)),
        "mx_count": str(len(mx)),
        "reported_count": str(len(reported)),
        "ca_ports": [row(p) for p in ca],
        "mx_ports": [row(p) for p in mx],
    }
    # Page-level chrome values the shared head/foot expect.
    border = load_json("border.norm")
    page_data.setdefault("updated_at", border.get("updated_at", ""))
    page_data.setdefault("updated_iso", border.get("updated_iso", ""))
    page_data.setdefault("build_version", border.get("build_version", ""))
    page_data.setdefault("sponsor_page", {})

    tpl = os.path.join(TMPL, "cbp-ports.template.html")
    if not os.path.exists(tpl):
        raise SystemExit("cbp-ports.template.html missing — run gen_templates.py first")
    with open(tpl, encoding="utf-8") as f:
        html = fill(f.read(), page_data)

    # Guard the promise the page makes in prose.
    if "not reported" not in html and len(reported) < len(ports):
        raise SystemExit("page claims a figure for every port but some have none")

    out_dir = os.path.join(DOCS, "border-wait-times", SLUG)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  all-ports: {len(ports)} ports ({len(ca)} CA, {len(mx)} MX), "
          f"{len(reported)} with a published commercial delay, {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
