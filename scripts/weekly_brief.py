#!/usr/bin/env python3
"""The Northern Mile Brief — the weekly newsletter.

The dashboard's subscribe CTA has promised "Fuel, border and market shifts.
Every Wednesday, 6am. One email a week." since it was built. Nothing has ever
sent it. This generates that email.

DESIGN NOTES

One email a week, not one per post. The blog publishes Mon/Wed/Fri. If every
post emailed the list, subscribers would get three messages a week and the
promise on the subscribe page would be false. So blog posts never carry a
newsletter field. Only this brief does.

Delivered through Ghost's own newsletter rather than the old SMTP path in
digest_email.py. Ghost handles the subscriber list, the unsubscribe link, and
deliverability. That matters legally: Canada's anti-spam law requires working
consent and unsubscribe handling on every commercial email, and hand-rolling
that over SMTP is a liability, not a shortcut.

SAFETY

Default action is --dry-run. Nothing is created or sent unless a flag says so.
Sending is irreversible, so the destructive paths are opt-in.
"""

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Ghost newsletter id, read from .env so it is not hard-coded here.
NEWSLETTER_ENV = "NMM_GHOST_NEWSLETTER_ID"
DEFAULT_NEWSLETTER_ID = "6a4401ecbeca4900088aab88"

CENT = "\u00a2"
DASH = "\u2014"


def load(name):
    try:
        with open(DATA / f"{name}.json", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _fmt_date(d):
    """'Tuesday, 15 September 2026' style is too long for an email header."""
    if not d:
        return ""
    try:
        return dt.date.fromisoformat(str(d)[:10]).strftime("%d %B %Y").lstrip("0")
    except Exception:
        return str(d)


def _norm_print_date(s):
    """NRCan's print date arrives as 'Tue, 15 Sep 2026'.

    Normalise it to the same '15 September 2026' shape used everywhere else in
    the brief, so the email does not mix two date formats.
    """
    s = (s or "").strip()
    for fmt in ("%a, %d %b %Y", "%d %b %Y", "%Y-%m-%d"):
        try:
            d = dt.datetime.strptime(s, fmt).date()
            return f"{d.day} {d.strftime('%B')} {d.year}"
        except Exception:
            continue
    return s


def _article(n):
    """'a' or 'an' for a number read aloud. Covers the realistic spread range.

    'a 82.5 cent spread' is the kind of small wrongness that costs a reader's
    trust in a publication that claims to be precise.
    """
    s = f"{abs(float(n)):.1f}"
    if s.startswith("8"):                              # 8, 80 to 89
        return "an"
    if s.startswith("11.") or s.startswith("18."):     # 11, 18
        return "an"
    return "a"


def build_brief(today=None, recent_posts=None):
    """Return (title, subtitle, markdown). Pure function over the data files.

    `recent_posts` is an optional list of {"title", "url"} for the week's
    published articles. The brief is the newsletter, and a newsletter's job is
    to point at the week's work, not to reproduce it. Without this the closing
    section promised "the longer pieces" and linked to none of them, which made
    the brief read as a thin duplicate of the article it was supposed to be
    pointing at.
    """
    today = today or dt.date.today()
    fuel = load("fuel")
    border = load("border")
    fx = load("exchange")
    market = load("market")

    provs = fuel.get("provinces") or {}
    rows = [(k, v.get("diesel")) for k, v in provs.items()
            if isinstance(v, dict) and v.get("diesel") is not None]
    rows.sort(key=lambda r: r[1])

    nat = fuel.get("diesel_national_avg")
    print_date = fuel.get("print_date") or ""
    locs = fuel.get("location_count")
    n_prov = len(rows)

    # Low, high and spread come from the dashboard's own normalised figures,
    # NOT recomputed from fuel.json. normalize.py computes them across the TEN
    # index provinces. fuel.json carries twelve jurisdictions because Yukon and
    # the NWT are surveyed but excluded from the index. Recomputing here took
    # the NWT as the low and published an 82.5 cent spread against the
    # dashboard's 53.2, so the same property stated two different numbers for
    # one figure.
    nf = load("fuel.norm") or {}
    nfuel = nf.get("fuel") if isinstance(nf.get("fuel"), dict) else nf
    canon = {
        "low_code": nfuel.get("low_code"),
        "low": nfuel.get("low"),
        "high_code": nfuel.get("high_code"),
        "high": nfuel.get("high"),
        "spread": nfuel.get("spread"),
    }

    title = f"The Northern Mile Brief: week of {today.strftime('%d %B %Y').lstrip('0')}"
    subtitle = "Fuel, border and market shifts for Canadian carriers."

    md = []

    # Lead with the national number.
    if nat is not None and rows:
        lo_code = canon["low_code"] or rows[0][0]
        lo = canon["low"] if canon["low"] is not None else rows[0][1]
        hi_code = canon["high_code"] or rows[-1][0]
        hi = canon["high"] if canon["high"] is not None else rows[-1][1]
        spread = canon["spread"]
        if spread is None:
            spread = round(float(hi) - float(lo), 1)
        printed = _norm_print_date(print_date)
        md.append(
            f"Diesel averaged {nat}{CENT} a litre across Canada this week, "
            f"per the NRCan survey printed {printed}."
        )
        md.append(
            f"Across the ten index provinces the cheapest was "
            f"{_prov(lo_code)} at {lo}{CENT} and the dearest "
            f"{_prov(hi_code)} at {hi}{CENT}, {_article(spread)} {spread}{CENT} "
            f"spread for the same product in the same country."
        )

    md.append("## Where fuel sits")
    if rows:
        # Compare against the index only. Listing the territories here put
        # Northwest Territories at 213.8 below a lead that had just called
        # Alberta the cheapest province, because the index excludes them.
        index_rows = [r for r in rows if r[0] in INDEX_PROVINCES]
        terr_rows = [r for r in rows if r[0] not in INDEX_PROVINCES]
        above = [r for r in index_rows if nat is not None and r[1] >= nat]
        below = [r for r in index_rows if nat is not None and r[1] < nat]
        if above:
            md.append(
                "At or above the national average: "
                + ", ".join(f"{_prov(c)} {v}{CENT}" for c, v in reversed(above)) + "."
            )
        if below:
            md.append(
                "Below it: "
                + ", ".join(f"{_prov(c)} {v}{CENT}" for c, v in reversed(below)) + "."
            )
        if terr_rows:
            md.append(
                "Surveyed but outside the index: "
                + ", ".join(f"{_prov(c)} {v}{CENT}" for c, v in terr_rows) + "."
            )

    # Border.
    crossings = border.get("crossings") or []
    if crossings:
        slow = sorted(
            [c for c in crossings if (c.get("delay_minutes") or 0) > 0],
            key=lambda c: -(c.get("delay_minutes") or 0),
        )
        clear = [c for c in crossings if not (c.get("delay_minutes") or 0)]
        md.append("## The border")
        md.append(f"We tracked {len(crossings)} crossings this week.")
        if slow:
            md.append(
                "Carrying delays: "
                + ", ".join(
                    f"{c.get('name')} at {c.get('delay_minutes')} minutes" for c in slow
                ) + "."
            )
        else:
            md.append("Every tracked crossing was clear.")
        if clear:
            names = ", ".join(c.get("name") for c in clear[:6])
            md.append(f"Clear: {names}.")

    # Dollar.
    if fx.get("current") is not None:
        md.append("## The dollar")
        direction = "up" if (fx.get("change") or 0) > 0 else "down"
        pct = abs(fx.get("change_pct") or 0)
        md.append(
            f"The loonie closed at {fx['current']:.4f} against the US dollar "
            f"on {_fmt_date(fx.get('observation_date'))}, {direction} {pct} per cent."
        )
        md.append(
            "Crude is priced in US dollars, so a soft loonie feeds into what "
            "refiners pay to bring it in. It also changes what fuel costs you "
            "on the US side of a cross-border run."
        )

    # Market pulse.
    inds = market.get("indicators") or []
    if inds:
        md.append("## The wider picture")
        for i in inds:
            label = i.get("label") or i.get("name")
            # Standardise the unit. market.json writes "34.6\u00a2/L" while the
            # rest of the brief writes "\u00a2" for anything per litre. Mixing the
            # two in one email reads as careless.
            val = str(i.get("value") or "").replace(f"{CENT}/L", CENT)
            d = i.get("direction") or "steady"
            md.append(f"- {label}: {val} ({d})")

    md.append("## Read this week's posts")
    if recent_posts:
        for p in recent_posts:
            md.append(f"- [{p['title']}]({p['url']})")
        md.append("")
        md.append(
            "Full tables for every figure above are on the "
            "[dashboard](https://dashboard.northernmilemedia.com/)."
        )
    else:
        md.append(
            "Full tables for every figure above are on the "
            "[dashboard](https://dashboard.northernmilemedia.com/)."
        )
    md.append("")

    return title, subtitle, "\n\n".join(md)


PROVINCE_NAMES = {
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba",
    "NB": "New Brunswick", "NL": "Newfoundland and Labrador", "NS": "Nova Scotia",
    "NT": "Northwest Territories", "NU": "Nunavut", "ON": "Ontario",
    "PE": "Prince Edward Island", "QC": "Quebec", "SK": "Saskatchewan",
    "YT": "Yukon",
}

# The ten provinces the Northern Mile Diesel Index is built from. Yukon,
# Nunavut and the NWT are surveyed by NRCan and appear on the dashboard, but
# they are deliberately excluded from the index. Anything comparing a province
# to the national figure must use this set, not every jurisdiction in fuel.json.
INDEX_PROVINCES = {"BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"}


def _prov(code):
    return PROVINCE_NAMES.get(code, code)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate the weekly NMM brief")
    ap.add_argument("--dry-run", action="store_true", default=True,
                    help="Generate and print only (DEFAULT)")
    ap.add_argument("--write", metavar="PATH",
                    help="Write the generated markdown to a file")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args(argv)

    title, subtitle, md = build_brief()

    if args.json:
        print(json.dumps({"title": title, "subtitle": subtitle,
                          "markdown": md}, indent=2))
        return 0

    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"wrote {out}")

    print(f"=== {title} ===")
    print(f"    {subtitle}")
    print()
    print(md)
    print()
    words = len(md.split())
    print(f"--- {words} words ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
