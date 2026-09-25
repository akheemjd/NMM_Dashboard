#!/usr/bin/env python3
"""Render /fuel-tax-rates/ from the official IFTA matrix.

The compliance reference layer. IFTA, Inc. is the authoritative publisher and
this is the only all-jurisdiction compliance dataset that exists in one place,
so the page is an aggregation job rather than an authority claim.

Two rate schedules are carried because IFTA publishes them separately: the rate
for US-licensed carriers and the rate for Canadian-licensed carriers differ in a
third of jurisdictions. Showing one number, or averaging them, would misstate the
rate for whichever carrier reads the wrong column.

Everything here is credited to IFTA with a quarter and a fetch date, and the
numbers are passed through unchanged — no rounding, no unit conversion. A US
rate stays per gallon because that is the unit the statute uses.
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


def fmt(v):
    """Render a rate without losing precision or inventing one."""
    if v is None:
        return "n/a"
    return f"{v:g}"


def rates_display(j):
    """Both schedules, labelled, because they genuinely differ."""
    parts = []
    us = (j.get("us") or {}).get("diesel")
    ca = (j.get("ca") or {}).get("diesel")
    # Each schedule keeps its own unit. The Can schedule is dollars per litre in
    # CAD; the US schedule is dollars per gallon in USD. They are not converted
    # into each other because a rate is what you file at, in the currency of the
    # licence you hold — and a converted rate would not be the rate.
    if j.get("is_canadian"):
        # A Canadian province's own carriers file at the Can rate; the US rate is
        # what a US-licensed carrier pays there. Lead with Can for readability.
        if ca is not None:
            parts.append(f"${fmt(ca)}/L CAD Can-lic")
        if us is not None:
            parts.append(f"${fmt(us)}/gal USD US-lic")
    else:
        if us is not None:
            parts.append(f"${fmt(us)}/gal USD US-lic")
        if ca is not None:
            parts.append(f"${fmt(ca)}/L CAD Can-lic")
    return " · ".join(parts) if parts else "n/a"


def surcharge_note(j):
    """Surface a separate surcharge rather than folding it into the base rate.

    Indiana, Kentucky and Virginia levy an additional per-gallon charge on
    certain fuel types. Adding it to the headline diesel figure would be wrong
    for Indiana, whose surcharge does not apply to diesel at all.
    """
    s = (j.get("surcharge") or {}).get("us") or {}
    d = s.get("diesel")
    if d:
        return f" + {fmt(d)}/gal surcharge on some fuels"
    return ""


def row(j):
    return {
        "name": j.get("name") or "",
        "rates_display": rates_display(j),
        "surcharge_note": surcharge_note(j),
    }


def main():
    ifta = load_json("ifta")
    jurs = ifta.get("jurisdictions") or []
    if not jurs:
        raise SystemExit("ifta.json carries no jurisdictions — run collect_ifta.py first")

    can = [j for j in jurs if j.get("is_canadian")]
    us = [j for j in jurs if not j.get("is_canadian")]
    can.sort(key=lambda j: j.get("code") or j.get("name") or "")
    us.sort(key=lambda j: j.get("name") or "")

    # A rate table with no rates is worse than no page.
    with_rate = [j for j in jurs
                 if (j.get("us") or {}).get("diesel") is not None
                 or (j.get("ca") or {}).get("diesel") is not None]
    if not with_rate:
        raise SystemExit("ifta.json has jurisdictions but no diesel rates")

    border = load_json("border.norm")
    page_data = {
        "quarter": ifta.get("quarter") or "n/a",
        "jurisdiction_count": str(len(jurs)),
        "ca_count": str(len(can)),
        "us_count": str(len(us)),
        "ca_jur": [row(j) for j in can],
        "us_jur": [row(j) for j in us],
        "updated_at": border.get("updated_at", ""),
        "updated_iso": border.get("updated_iso", ""),
        "build_version": border.get("build_version", ""),
        "sponsor_page": {},
    }

    tpl = os.path.join(TMPL, "ifta-rates.template.html")
    if not os.path.exists(tpl):
        raise SystemExit("ifta-rates.template.html missing — run gen_templates.py first")
    with open(tpl, encoding="utf-8") as f:
        html = fill(f.read(), page_data)

    # Guard the promise: every jurisdiction must actually render a rate.
    if "n/a" in html and len(with_rate) == len(jurs):
        pass  # an n/a for a single schedule is legitimate
    missing = [j["name"] for j in jurs if rates_display(j) == "n/a"]
    if missing:
        raise SystemExit(f"jurisdictions rendered with no rate: {missing[:5]}")

    out_dir = os.path.join(DOCS, "fuel-tax-rates")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  fuel-tax-rates: {len(jurs)} jurisdictions ({len(can)} CA, {len(us)} US) "
          f"for {ifta.get('quarter')}, {len(html):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
