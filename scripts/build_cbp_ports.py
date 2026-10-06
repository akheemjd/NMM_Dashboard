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
import re
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


# Crossings that already have a page under the name CBSA gives them. The two agencies name
# the same bridge differently - CBP says "Champlain" where CBSA says "Lacolle", CBP says
# "Sweetgrass" where CBSA says "Coutts-Sweetgrass" - so slugify(CBP label) does not find the
# page that exists. This maps the CBP label to the slug already on disk.
CBSA_NAMED_PAGE = {
    "Bluewater Bridge": "blue-water-bridge",
    "Sweetgrass": "coutts-sweetgrass",
    "Pembina": "emerson-pembina",
    "Champlain": "lacolle-border-crossing",
    "Pacific Highway": "pacific-highway-crossing",
    "Lewiston Bridge": "queenston-lewiston-bridge",
}


def slugify(s):
    """Same rule build_border_pages.py uses, so the two agree on a port URL."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


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


def base_label(port):
    """The name a reader sees before any disambiguation."""
    name = port.get("port_name") or ""
    crossing = port.get("crossing_name") or ""
    # CBP repeats the port name as the crossing name for single-crossing ports
    # (Pembina, Sumas). Printing "Pembina Pembina" reads like a bug.
    return f"{name} — {crossing}" if crossing and crossing != name else name


def label_plan(ports):
    """Decide, across every row, which labels actually need disambiguating.

    Only collisions get a suffix. The old code appended " — port <number>" to any row
    without a crossing name, so Fort Hancock read "Fort Hancock — port l24501" even though
    nothing else on the page said Fort Hancock. That hid a database key in a reader's label
    for no reason.
    """
    counts = {}
    for p in ports:
        counts[base_label(p)] = counts.get(base_label(p), 0) + 1

    plan = {}
    for p in ports:
        label = base_label(p)
        if counts.get(label, 0) < 2:
            plan[p.get("port_number")] = ""
            continue
        # A real collision. The state is what separates Gateway, TX from Brownsville's
        # Gateway crossing, so try that first.
        st = (p.get("us_state") or "").strip()
        plan[p.get("port_number")] = f" — {st}" if st else " — (unnamed crossing)"

    # A state that does not separate them is no separation. Both Naco records are in AZ with
    # no crossing name, so "Naco — AZ" appeared twice and told the reader nothing. CBP tracks
    # them as two rows reporting different waits, so keep both and number them rather than
    # dropping one or printing a port code.
    seen = {}
    for p in ports:
        key = base_label(p) + plan.get(p.get("port_number"), "")
        seen[key] = seen.get(key, 0) + 1
    for p in ports:
        key = base_label(p) + plan.get(p.get("port_number"), "")
        if seen.get(key, 0) > 1:
            n = plan.get("_n_" + str(key), 0) + 1
            plan["_n_" + str(key)] = n
            plan[p.get("port_number")] = (plan.get(p.get("port_number"), "") +
                                          f" ({n} of {seen[key]})")
    return plan


def row(port, plan=None):
    name = port.get("port_name") or ""
    crossing = port.get("crossing_name") or ""
    suffix = (plan or {}).get(port.get("port_number"), "")
    base = base_label(port)
    # Same name, same state, no crossing name to tell them apart - which is exactly the two
    # Naco records. Say so in plain words instead of printing a CBP port code, which reads
    # as a data leak rather than a border crossing.
    if suffix == " — (unnamed crossing)":
        suffix = f" — {port.get('us_state') or ''} (unnamed crossing)".replace("  ", " ")
    juris = ""
    if port.get("us_state") and port.get("ca_province"):
        juris = f" · {port['us_state']}–{port['ca_province']}"
        if port.get("ca_city"):
            juris += f" → {port['ca_city']}"
    # Link to the port's own page when one exists. The Mexican-border ports have no page, and
    # a link to a page that was never built is worse than plain text in what is meant to be
    # the index of the border.
    # build_border_pages.py writes these pages at slugify(label). CBP's own slug field
    # is region-prefixed - "detroit-ambassador-bridge" for the page "ambassador-bridge" -
    # so looking up the CBP slug found no directory and the list linked to nothing.
    # The label, not base: base is the PORT name ("Calais") while the page was built from
    # the crossing label ("Ferry Point"), and Calais covers three separate crossings.
    _label = port.get("label") or base
    _slug = CBSA_NAMED_PAGE.get(_label) or slugify(_label)
    _built = bool(_slug) and os.path.isdir(os.path.join(DOCS, "border-wait-times", _slug))

    return {
        # base_label carries the crossing name. Returning the bare port_name here dropped
        # every crossing from the page - Brownsville rendered four times with no B&M, no
        # Gateway - which is worse than the port codes I was replacing.
        "port_name": (f'<a href="/border-wait-times/{_slug}/">{base}</a>'
                      if _built else base),
        "_built": _built,
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

    # One plan across every port, so a collision between two rows of the same border is
    # caught the same way as one across borders.
    _plan = label_plan(list(ca) + list(mx))

    page_data = {
        "port_count": str(len(ports)),
        "ca_count": str(len(ca)),
        "mx_count": str(len(mx)),
        "reported_count": str(len(reported)),
        "ca_ports": [row(p, _plan) for p in ca],
        "mx_ports": [row(p, _plan) for p in mx],
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
