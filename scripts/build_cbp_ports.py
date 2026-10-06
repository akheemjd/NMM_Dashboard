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


# CBP's feed carries a handful of labels that were never written for a reader: names in caps,
# a port repeated inside its own crossing name, and one administrative suffix. A rule kept
# catching some and missing others, so the specific cases are named outright and the rules
# below only handle what is left.
LABEL_FIX = {
    "BOTA CARGO FACILITY — BRIDGE OF AMERICAS CARGO FACILITY":
        "Bridge of the Americas Cargo Facility",
    "Bridge of the Americas (BOTA)": "Bridge of the Americas",
    "Bridge of the Americas Port of Entry": "Bridge of the Americas",
    "ROMA TEXAS": "Roma",
    "YSLETA": "Ysleta",
    "International Bridge - SSM": "International Bridge - Sault Ste. Marie",
}


def reader_label(text):
    """Turn a feed label into something a driver would recognise.

    CBP sends some port names in caps and repeats the port inside its own crossing name. Neither
    is wrong at the source; both read badly on a page.
    """
    if not text:
        return text
    t = text.strip()
    if t in LABEL_FIX:
        return LABEL_FIX[t]

    # drop the administrative suffix - the page already says which port this is
    t = re.sub(r"\s+Port of Entry\s*$", "", t, flags=re.I)
    t = re.sub(r"\s+PORT OF ENTRY\s*$", "", t)

    # a state name inside a row that already shows the state
    t = re.sub(r"\s+(TEXAS|CALIFORNIA|ARIZONA|NEW MEXICO)\s*$", "", t, flags=re.I)

    # "BOTA CARGO FACILITY — BRIDGE OF AMERICAS CARGO FACILITY" is one place named twice
    if "—" in t or " - " in t:
        parts = [x.strip() for x in re.split(r"\s+[—-]\s+", t)]
        if len(parts) == 2:
            a, b = parts
            _a = a.lower().replace(" ", "")
            _b = b.lower().replace(" ", "")
            # CBP uses BOTA as its own short form, so the halves do not match
            # by substring and need the alias named.
            _alias = (("bota" in _a and "bridgeoftheamericas" in _b) or
                      ("bota" in _b and "bridgeoftheamericas" in _a))
            if _alias or _a in _b or _b in _a:
                t = b if len(b) >= len(a) else a

    # all caps, but leave true initialisms and single letters alone
    if t.isupper() and len(t) > 4:
        small = {"of", "the", "and", "at", "on", "in", "del", "de", "la", "las", "los", "el"}
        words = []
        for w in t.split():
            lw = w.lower()
            if lw in small:
                words.append(lw)
            elif lw in ("i", "ii", "iii"):
                words.append(w.upper())
            elif lw in ("bota", "ssm", "roma"):
                # short forms and place names, not initialisms
                words.append(w.capitalize())
            else:
                words.append(w.capitalize())
        t = " ".join(words)
        t = t[0].upper() + t[1:]

    t = t.replace(" - SSM", " - Sault Ste. Marie").replace("SSM", "Sault Ste. Marie")
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


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
    base = reader_label(base_label(port))
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

    # One row per crossing. CBP sends a port and its lanes as separate records, so the same
    # bridge arrives twice under different labels - bare "Ysleta" and "El Paso - Ysleta" - and a
    # reader comparing waits has no way to know they are one place. It reads as two crossings
    # and halves the apparent traffic on each.
    def dedupe(rows):
        best, order = {}, []
        for r in rows:
            key = re.sub(r"[^a-z0-9]+", " ", r["port_name"].lower()).strip()
            if key not in best:
                best[key] = r
                order.append(key)
                continue
            # the row with a published delay is the one worth showing
            if "not reported" in best[key].get("commercial_display", "") and                "not reported" not in r.get("commercial_display", ""):
                best[key] = r
        return [best[k] for k in order]

    _ca_rows = dedupe([row(p, _plan) for p in ca])
    _mx_rows = dedupe([row(p, _plan) for p in mx])

    page_data = {
        "port_count": str(len(_ca_rows) + len(_mx_rows)),
        "ca_count": str(len(_ca_rows)),
        "mx_count": str(len(_mx_rows)),
        "reported_count": str(len(reported)),
        "ca_ports": _ca_rows,
        "mx_ports": _mx_rows,
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

    print(f"  all-ports: {len(_ca_rows) + len(_mx_rows)} crossings ({len(_ca_rows)} CA, {len(_mx_rows)} MX), "
          f"{len(reported)} with a published commercial delay, {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
