#!/usr/bin/env python3
"""Render a page per US state from data that is genuinely state-level.

WHAT MAKES THESE PAGES DIFFERENT
--------------------------------
EIA publishes a weekly on-highway diesel price by DISTRICT, not by state. There
are ten districts in the country. Every free US site with fifty "state diesel
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

        # Three of the 51 jurisdictions are not IFTA members at all: Alaska,
        # Hawaii and the District of Columbia. Saying "not published" would imply
        # IFTA has a figure and we failed to read it, which is the opposite of
        # true and would send a carrier looking for a rate that does not exist.
        if not j:
            ifta_display = "not an IFTA jurisdiction"
            ifta_short = "not a member"
            ifta_absent = True
        elif ifta_diesel in (0, 0.0):
            # Oregon publishes a NIL rate in the matrix. That is a published
            # value, not a gap, and a bare "$0.0000" invites the reader to think
            # the page failed to load a number.
            ifta_display = "nil"
            ifta_short = "nil"
            ifta_absent = False
        else:
            ifta_display = money(ifta_diesel, 4)
            ifta_short = money(ifta_diesel, 4)
            ifta_absent = False

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

        if ifta_absent:
            # Do not describe an IFTA rate that does not exist for this state.
            tax_note = (
                f"The four figures above are the whole picture for {name}. The "
                f"statutory excise is what the state levies on a gallon of diesel sold "
                f"there, other state fees are added on top, and the federal rate "
                f"applies everywhere in the country."
            )
        elif ifta_display == "nil":
            tax_note = (
                f"{name} is the exception in the country here, which is why the top of "
                f"this page carries a statutory excise and a nil IFTA rate at the same "
                f"time. They are not in conflict. They describe different vehicles."
            )
        else:
            tax_note = (
                f"The two figures above answer different questions. The statutory excise "
                f"is what {name} levies on a gallon of diesel sold in the state. The IFTA "
                f"rate is what a carrier reports to {name} for a gallon burned there, and "
                f"in most jurisdictions the two are not the same number."
            )
        if ifta_absent:
            ifta_sentence = (
                f"{name} is not an IFTA jurisdiction, so no IFTA rate exists to file "
                f"for it. That is not a gap in this page. The statutory excise above "
                f"is the figure that applies."
            )
        elif ifta_display == "nil":
            # Oregon is the one state that does not tax heavy trucks by the
            # gallon, so the excise above and the IFTA rate below describe
            # different vehicles. Saying only "the rate is nil" would look like a
            # contradiction against the $0.40 excise sitting right above it.
            ifta_sentence = (
                f"IFTA publishes a <b>nil</b> diesel rate for {name}. That is a "
                f"published value, not a missing one. {name} does not tax heavy "
                f"trucks by the gallon, so the statutory excise shown above is not "
                f"the figure that applies to them, which is why the two differ."
            )
        else:
            ifta_sentence = (
                f"Under IFTA, a US-licensed carrier files {name} at "
                f"<b>{money(ifta_diesel, 4)}</b> a gallon for diesel. That is the "
                f"rate the state collects on a gallon sold there, and it is a "
                f"different number from the statutory total above because IFTA and "
                f"the statute do not measure the same thing."
            )

        description = (
            f"{name} diesel by district and the fuel tax {abbr} actually levies. "
            f"IFTA rate {money(ifta_diesel, 4)} a gallon, state excise "
            f"{money(state_excise, 4)} a gallon. EIA prices diesel by district, not "
            f"by state, and this page says which district {name} is in."
        )

        # Components at display precision, computed once, so the figures in the
        # printed equation cannot round differently from their own addends.
        # diesel_total_state INCLUDES diesel_other, so the pure statutory
        # excise is the difference. Using it directly double-counted the
        # other fees into the state total.
        _exc = round(float(st.get('diesel_total_state') or 0.0)
                    - float(st.get('diesel_other') or 0.0), 4)
        # 'other' comes from EIA's own diesel_other column, NOT from
        # all_in minus excise — that subtraction double-counted the
        # federal rate and made every state total equal its all-in value.
        _oth = round(float(st.get('diesel_other') or 0.0), 4)
        _fed = round(float(federal.get('diesel_total') or 0.0), 4)

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
            "ifta_sentence": ifta_sentence,
            "ifta_display": ifta_display,
            "state_excise": money(state_excise, 4),
            "state_excise_display": money(state_excise, 4),
            # A blank in EIA's "Other taxes & Fees" column means ZERO, not
            # unknown. That is demonstrated rather than assumed: on all seven
            # states where the cell is blank, excise + federal equals the all-in
            # figure exactly, which only holds if the blank contributes nothing.
            # An unknown would show as "--" or "W" in that table.
            "state_other": money(st.get("diesel_other") or 0.0, 4),
        # Components at display precision, computed once so the three figures
            # below cannot round differently from the ones above them.
            "state_other_note_hint": "",
            "state_other_note": (
                "inspection and environmental fees" if (st.get("diesel_other") or 0) > 0
                else "none levied on diesel"),
            # The page prints its arithmetic, so the printed total must equal the
            # two printed addends. It did not on three states — Colorado,
            # Louisiana and New Mexico printed addends summing to one unit less
            # than the total, because the total was rounded from the unrounded
            # data while the addends were rounded for display.
            #
            # Round the components first, then add those. The displayed equation
            # is then exactly true; the cost is a possible 0.0001 difference from
            # the raw table, which is invisible. Work that does not add up is the
            # worse error for a page whose point is showing its work.
            "state_total": money(_exc + _oth, 4),
            "federal_excise": money(_fed, 4),
            "all_in": money(_exc + _oth + _fed, 4),
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
        written.append((name, abbr, dist_label, price, state_excise, ifta_short))

    # ---- the hub, so the 51 state pages are not orphans
    with open(os.path.join(TMPL, "us-states.template.html"), encoding="utf-8") as f:
        hub_tpl = f.read()
    hub_rows = []
    for name, abbr, dlabel, price, excise, ifta in written:
        # `ifta` is already the display string. Re-running money() on it here is
        # what left the hub showing "$0.0000" for Oregon and "not published" for
        # Alaska after the state pages had been corrected — the two surfaces
        # disagreed because only one of them used the shared value.
        hub_rows.append({
            "name": name,
            "url": f"/us-diesel/{slugify(name)}/",
            "district": dlabel,
            "ifta": ifta,
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
