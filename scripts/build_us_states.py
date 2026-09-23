#!/usr/bin/env python3
"""Render a page per US state from data that is genuinely state-level.

WHAT MAKES THESE PAGES DIFFERENT
--------------------------------
EIA publishes a weekly on-highway diesel price by DISTRICT, not by state. There
are eleven districts in the country. Every free US site with fifty "state diesel
price" pages is serving nine or ten district numbers under fifty URLs, and most
say so only in a footnote. dieselcostpergallon.com states it plainly on its Texas
page: "EIA prices the US, its districts and California only, so state pages show
a district figure."

So a US state page cannot honestly lead with a diesel price. What it CAN lead
with is what really is per-state:

  * the IFTA rate, from IFTA Inc's own quarterly matrix
  * the statutory state excise and the federal rate, from EIA's semiannual table
  * the state's own border ports, from the CBP feed

The diesel figure appears too, attributed to its district and explained. The
attribution is the product. A competitor cannot copy the explanation without
conceding that its fifty state pages carry nine numbers.

BLANK STAYS BLANK
-----------------
A state missing from EIA's tax table, or missing an IFTA row, renders as "not
published". It never renders as 0.00, which would read as a state levying no
fuel tax.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")

sys.path.insert(0, HERE)
from build_templates import fill, load_json  # noqa: E402

CENT = "¢"

# District labels, keyed by the district key used in eia_diesel.json.
DISTRICT_ORDER = [
    "new_england", "central_atlantic", "lower_atlantic", "east_coast",
    "midwest", "gulf_coast", "rocky_mountain", "west_coast",
    "california", "west_coast_ex_california",
]


def slugify(name):
    s = name.lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def money(v, dp=4):
    """None -> 'not published'. Never '0.0000'."""
    if v is None:
        return "not published"
    return f"${v:.{dp}f}"


def delay_text(minutes):
    if minutes is None:
        return "not reported"
    if minutes == 0:
        return "No delay"
    return f"{minutes} min"


def build():
    tax = load_json("us_fuel_tax")
    ifta = load_json("ifta")
    diesel = load_json("eia_diesel")
    cbp = load_json("cbp_border")
    border_chrome = load_json("border.norm")

    states_tax = {s["abbr"]: s for s in tax.get("states", []) if s.get("abbr")}
    federal = tax.get("federal") or {}

    ifta_jur = {}
    for j in ifta.get("jurisdictions", []):
        if not j.get("is_canadian"):
            ifta_jur[j["name"].upper()] = j

    districts = diesel.get("districts") or {}
    state_padd = diesel.get("state_padd") or {}
    us_national = diesel.get("us_national_usd_gal")
    diesel_week = diesel.get("date") or ""

    # Ports grouped by US state, Canadian border first, then Mexican.
    ports_by_state = {}
    for p in cbp.get("ports", []):
        st = p.get("us_state")
        if st:
            ports_by_state.setdefault(st, []).append(p)

    with open(os.path.join(TMPL, "us-state.template.html"), encoding="utf-8") as f:
        template = f.read()

    written = []
    for abbr, st in sorted(states_tax.items(), key=lambda kv: kv[1]["name"]):
        name = st["name"]
        padd_key = state_padd.get(abbr)
        dist = districts.get(padd_key) or {}
        price = dist.get("price_usd_gal")
        dist_label = dist.get("label") or "not published"

        # IFTA: matched on the name as IFTA Inc spells it, which is upper case.
        #
        # The matrix carries two rows per jurisdiction and they are NOT two
        # different taxes. They are the same tax in two units: the "us" row is US
        # dollars per gallon, the "ca" row is Canadian dollars per litre. Alberta
        # reads 0.13 CAD/L and 0.3519 USD/gal, and 0.13 x 3.785 / 1.40 = 0.3515,
        # which is that row. A US state page needs the per-gallon figure.
        j = ifta_jur.get(name.upper())
        ifta_diesel = ((j or {}).get("us") or {}).get("diesel")

        state_excise = st.get("diesel_state_excise")
        all_in = st.get("diesel_all_in")

        # ---- border ports for this state
        plist = sorted(ports_by_state.get(abbr, []),
                       key=lambda p: (p.get("border") != "Canadian Border",
                                      p.get("label") or ""))
        rows = []
        seen = set()
        for p in plist:
            lbl = p.get("label") or p.get("port_name")
            if lbl in seen:
                continue
            seen.add(lbl)
            rows.append({"label": lbl, "delay": delay_text(p.get("commercial_delay"))})
        has_border = bool(rows)

        if has_border:
            can = sum(1 for p in plist if p.get("border") == "Canadian Border")
            mex = sum(1 for p in plist if p.get("border") == "Mexican Border")
            parts = []
            if can:
                parts.append(f"{can} on the Canadian border")
            if mex:
                parts.append(f"{mex} on the Mexican border")
            border_intro = (
                f"US Customs and Border Protection publishes commercial lane waits "
                f"for {len(plist)} ports in {name}, {' and '.join(parts)}. These are "
                f"US-bound figures. A port that did not report is shown as not reported."
            )
        else:
            border_intro = ""

        # ---- prose
        if price is not None:
            price_txt = f"${price:.3f}"
            price_short = f"${price:.3f}"
        else:
            price_txt = "not published"
            price_short = "n/a"

        tax_note = (
            f"The two figures above answer different questions. The statutory excise "
            f"is what {name} levies on a gallon of diesel sold in the state. The IFTA "
            f"rate is what a carrier reports to {name} for a litre burned there, and "
            f"in most jurisdictions the two are not the same number."
        )
        if ifta_diesel is None:
            tax_note = (
                f"IFTA did not publish a separate rate for {name} this quarter, so only "
                f"the statutory excise is shown. " + tax_note
            )

        description = (
            f"{name} diesel by district and the fuel tax {abbr} actually levies. "
            f"IFTA rate {money(ifta_diesel, 4)} a litre, state excise "
            f"{money(state_excise, 4)} a gallon. EIA prices diesel by district, not "
            f"by state, and this page says which district {name} is in."
        )

        data = {
            "state_name": name,
            "abbr": abbr,
            "description": description[:300],
            "path_url": f"/us-diesel/{slugify(name)}/",
            "canonical": f"https://dashboard.northernmilemedia.com/us-diesel/{slugify(name)}/",
            "district_label": dist_label,
            "district_price": price_txt,
            "district_price_short": price_short,
            "district_unit": "USD/gal",
            "diesel_week": diesel_week,
            "ifta_diesel": money(ifta_diesel, 4),
            "ifta_display": money(ifta_diesel, 4),
            "state_excise": money(state_excise, 4),
            "state_excise_display": money(state_excise, 4),
            # A blank in EIA's "Other taxes & Fees" column means ZERO, not
            # unknown. That is demonstrated rather than assumed: on all seven
            # states where the cell is blank, excise + federal equals the all-in
            # figure exactly, which only holds if the blank contributes nothing.
            # An unknown would show as "--" or "W" in that table.
            "state_other": money(st.get("diesel_other") or 0.0, 4),
            "state_other_note": (
                "inspection and environmental fees" if (st.get("diesel_other") or 0) > 0
                else "none levied on diesel"),
            "state_total": money(st.get("diesel_total_state"), 4),
            "federal_excise": money(federal.get("diesel_total"), 4),
            "all_in": money(all_in, 4),
            "tax_note": tax_note,
            "has_border": has_border,
            "border_count": len(plist),
            "border_intro": border_intro,
            "borderrows": rows,
            "updated_at": diesel.get("updated", "")[:16].replace("T", " "),
            # Chrome values the shared head/foot expect. They live on the
            # normalised border payload, which every builder reads for them.
            "updated_iso": border_chrome.get("updated_iso", ""),
            "build_version": border_chrome.get("build_version", ""),
            "sponsor_page": {},
        }

        # The page states that excise + other + federal = all-in. If EIA's own
        # numbers do not satisfy that, the page would be printing an equation
        # that does not hold, so refuse rather than publish it.
        for label, a, b, c, d in [(
            name,
            st.get("diesel_state_excise"), st.get("diesel_other"),
            federal.get("diesel_total"), st.get("diesel_all_in"))]:
            b = b or 0.0
            if None not in (a, c, d) and abs((a + b + c) - d) > 0.0006:
                raise SystemExit(
                    f"{label}: excise {a} + other {b} + federal {c} != all-in {d}")

        html = fill(template, data)
        # A token that never resolved means the data key is wrong. Publishing the
        # literal {{token}} is the silent-failure class this repo keeps hitting.
        leftovers = sorted(set(re.findall(r"\{\{[a-z_0-9.]+\}\}", html)))
        if leftovers:
            raise SystemExit(f"{name}: unresolved tokens {leftovers}")

        outdir = os.path.join(DOCS, "us-diesel", slugify(name))
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        written.append((name, abbr, dist_label, price, state_excise, ifta_diesel))

    # ---- the hub, so the 51 state pages are not orphans
    with open(os.path.join(TMPL, "us-states.template.html"), encoding="utf-8") as f:
        hub_tpl = f.read()
    hub_rows = []
    for name, abbr, dlabel, price, excise, ifta in written:
        hub_rows.append({
            "name": name,
            "url": f"/us-diesel/{slugify(name)}/",
            "district": dlabel,
            "ifta": money(ifta, 4),
            "all_in": money(states_tax[abbr].get("diesel_all_in"), 4),
        })
    hub = fill(hub_tpl, {
        "state_count": str(len(written)),
        "district_count": str(len({r["district"] for r in hub_rows})),
        "diesel_week": diesel_week,
        "updated_at": diesel.get("updated", "")[:16].replace("T", " "),
        "updated_iso": border_chrome.get("updated_iso", ""),
        "build_version": border_chrome.get("build_version", ""),
        "federal": money(federal.get("diesel_total"), 4),
        "states": hub_rows,
        "sponsor_page": {},
    })
    leftovers = sorted(set(re.findall(r"\{\{[a-z_0-9.]+\}\}", hub)))
    if leftovers:
        raise SystemExit(f"hub: unresolved tokens {leftovers}")
    hubdir = os.path.join(DOCS, "us-diesel", "states")
    os.makedirs(hubdir, exist_ok=True)
    with open(os.path.join(hubdir, "index.html"), "w", encoding="utf-8") as f:
        f.write(hub)
    print(f"  us state index: /us-diesel/states/  ({len(hub_rows)} rows)")

    print(f"  us state pages: {len(written)}")
    print(f"  with border ports: {sum(1 for w in written if ports_by_state.get(w[1]))}")
    missing_price = [w[0] for w in written if w[3] is None]
    if missing_price:
        print(f"  districts with no published price: {missing_price}")
    missing_tax = [w[0] for w in written if w[4] is None]
    if missing_tax:
        print(f"  states with no EIA excise: {missing_tax}")
    return 0


if __name__ == "__main__":
    sys.exit(build())
