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


def _hist():
    """The history store, imported lazily so a missing file never stops a send."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import history  # noqa: E402
        return history
    except Exception:
        return None


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _cents(v):
    return f"{v:.1f}{CENT}"


def _move_word(d, up="up", down="down"):
    return up if d > 0 else down


# CBSA measures traffic entering Canada; CBP measures traffic entering the US. Same nine
# crossings as the dashboard cards (normalize.py CBP_FOR_CROSSING).
CBP_FOR_CROSSING = {
    "windsor-detroit": "380001", "sarnia-port-huron": "380201", "fort-erie-buffalo": "090101",
    "queenston-lewiston": "090104", "lacolle-champlain": "071201", "lansdowne-alexandria": "070801",
    "coutts-sweetgrass": "331001", "pacific-blaine": "300401", "emerson-pembina": "340101",
}

US_HOLIDAYS_AND_DATES = None  # built per call in _next_week


def _nth_weekday(year, month, weekday, n):
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def _last_weekday(year, month, weekday):
    d = dt.date(year, month + 1, 1) - dt.timedelta(days=1) if month < 12 else dt.date(year, 12, 31)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def _next_week(today):
    """Known dates in the next 8 days that change a carrier's week. Never invented."""
    y = today.year
    events = []
    for yr in (y, y + 1):
        events += [
            (dt.date(yr, 1, 31), "IFTA return for the fourth quarter is due"),
            (dt.date(yr, 4, 30), "IFTA return for the first quarter is due"),
            (dt.date(yr, 7, 31), "IFTA return for the second quarter is due"),
            (dt.date(yr, 10, 31), "IFTA return for the third quarter is due"),
            (_nth_weekday(yr, 10, 0, 2), "Thanksgiving in Canada. Expect heavier crossings the Friday before and the Monday"),
            (_nth_weekday(yr, 11, 3, 4), "Thanksgiving in the US. Northbound and southbound traffic both build through the long weekend"),
            (_nth_weekday(yr, 9, 0, 1), "Labour Day in Canada and Labor Day in the US"),
            (_last_weekday(yr, 5, 0), "Memorial Day in the US"),
            (dt.date(yr, 5, 25) - dt.timedelta(days=(dt.date(yr, 5, 25).weekday() - 0) % 7 or 7), "Victoria Day in Canada"),
            (dt.date(yr, 7, 1), "Canada Day"),
            (dt.date(yr, 7, 4), "Independence Day in the US"),
            (dt.date(yr, 11, 11), "Remembrance Day in Canada and Veterans Day in the US"),
            (dt.date(yr, 12, 25), "Christmas Day. Plan crossings and fuel around reduced hours"),
            (dt.date(yr, 1, 1), "New Year's Day"),
        ]
    soon = sorted((d, t) for d, t in events if today <= d <= today + dt.timedelta(days=10))
    return [f"{d.strftime('%A')} {d.day} {d.strftime('%B')}: {t}." for d, t in soon]


def _gather(today):
    """Every figure the brief can talk about, with its change on the week where one exists."""
    fuel, border, fx, eia = load("fuel"), load("border"), load("exchange"), load("eia_diesel")
    cbp, trends, provn = load("cbp_border"), load("border_trends"), load("provinces.norm")
    h = _hist()
    g = {"today": today}

    nat = _f(fuel.get("diesel_national_avg"))
    g["ca"] = {"now": nat, "print": _norm_print_date(fuel.get("print_date") or ""), "d7": None}
    if h and nat is not None:
        then = h.value_at("diesel", "national", 7)
        if then is not None:
            g["ca"]["d7"] = round(nat - then, 1)
    nf = load("fuel.norm") or {}
    nfuel = nf.get("fuel") if isinstance(nf.get("fuel"), dict) else nf
    g["ca"].update({k: nfuel.get(k) for k in ("low_code", "low", "high_code", "high", "spread")})

    # Biggest provincial movers on the week.
    movers = []
    if h:
        for code in INDEX_PROVINCES:
            now_p = h.latest("diesel", code)
            then_p = h.value_at("diesel", code, 7)
            if now_p is not None and then_p is not None:
                movers.append((round(now_p - then_p, 1), code, now_p))
    g["ca"]["movers"] = sorted(movers, key=lambda m: -abs(m[0]))

    us_now = _f(eia.get("us_national_usd_gal"))
    prev = (eia.get("previous_week") or {}).get("us_national_usd_gal")
    g["us"] = {"now": us_now, "week": _fmt_date(eia.get("date")),
               "d7": round(us_now - float(prev), 3) if us_now is not None and prev else None}
    dist = [(v.get("price_usd_gal"), v.get("label", k).split(" (")[0])
            for k, v in (eia.get("districts") or {}).items()
            if v.get("price_usd_gal") and k not in ("east_coast", "west_coast")]
    dist.sort()
    g["us"]["low"], g["us"]["high"] = (dist[0], dist[-1]) if len(dist) >= 2 else (None, None)

    rate = _f(fx.get("current"))
    hist = [x for x in (fx.get("history") or []) if x.get("rate")]
    then_fx = None
    if rate is not None and hist:
        try:
            cur_d = dt.date.fromisoformat(str(fx.get("observation_date"))[:10])
            older = [x for x in hist if dt.date.fromisoformat(x["date"][:10]) <= cur_d - dt.timedelta(days=7)]
            then_fx = _f(older[-1]["rate"]) if older else None
        except Exception:
            then_fx = None
    g["fx"] = {"now": rate, "date": _fmt_date(fx.get("observation_date")),
               "pct7": round((rate - then_fx) / then_fx * 100, 2) if rate and then_fx else None}

    ports = {p.get("port_number"): p for p in cbp.get("ports", [])}
    typical = (trends.get("crossings") or {})
    rows = []
    for c in border.get("crossings") or []:
        cid = c.get("id", "")
        ca = c.get("delay_minutes")
        p = ports.get(CBP_FOR_CROSSING.get(cid, ""))
        us = p.get("commercial_delay") if p and p.get("commercial_reported") else None
        t = typical.get(cid) or {}
        rows.append({"name": c.get("name", cid), "ca": ca, "us": us,
                     "typ": t.get("avg_delay"), "p75": t.get("p75")})
    g["border"] = rows

    g["spot"] = provn.get("provinces") or {}
    g["districts"] = eia.get("districts") or {}
    return g


def _candidates(g):
    """Each possible lead, scored by how much it should change a carrier's week."""
    out = []
    ca, us, fx = g["ca"], g["us"], g["fx"]
    if ca["d7"] is not None:
        out.append(("ca", abs(ca["d7"]) / 3.0))
    if us["d7"] is not None:
        out.append(("us", abs(us["d7"]) / 0.08))
    if fx["pct7"] is not None:
        out.append(("fx", abs(fx["pct7"]) / 0.6))
    worst = max(g["border"], key=lambda r: max(r["ca"] or 0, r["us"] or 0), default=None)
    if worst:
        w = max(worst["ca"] or 0, worst["us"] or 0)
        typ = worst["typ"] or 0
        # Above typical when into Canada (that is what the history measures); else against 10 min.
        base = typ if (worst["ca"] or 0) >= (worst["us"] or 0) else 10
        out.append(("border", max(0.0, (w - base)) / 12.0))
    return sorted(out, key=lambda c: -c[1])


def _lead(kind, g, variant):
    """Two or three sentences on the week's biggest move. Wording rotates week to week."""
    ca, us, fx = g["ca"], g["us"], g["fx"]
    if kind == "ca":
        d = ca["d7"]
        top = ca["movers"][0] if ca["movers"] else None
        first = [
            f"Canadian diesel fell {_cents(abs(d))} a litre on the week, to {_cents(ca['now'])}." if d < 0 else
            f"Canadian diesel rose {_cents(d)} a litre on the week, to {_cents(ca['now'])}.",
            f"The national average {'dropped' if d < 0 else 'climbed'} {_cents(abs(d))} in seven days and now sits at {_cents(ca['now'])} a litre.",
            f"{_cents(abs(d))} a litre. That is how far Canadian diesel {'came down' if d < 0 else 'went up'} this week, to {_cents(ca['now'])}.",
        ][variant % 3]
        if top and abs(top[0]) >= abs(d) + 1:
            first += f" {_prov(top[1])} moved most, {_move_word(top[0])} {_cents(abs(top[0]))} to {_cents(top[2])}."
        on_fill = abs(d) * 5  # 500 litre fill, cents to dollars
        return first + f" On a 500 litre fill that is about ${on_fill:,.0f} {'back in your pocket' if d < 0 else 'more out of it'}."
    if kind == "us":
        d = us["d7"]
        line = [
            f"US diesel {'fell' if d < 0 else 'rose'} {abs(d) * 100:.1f} cents a gallon on the week, to ${us['now']:.3f}.",
            f"The US average moved {abs(d) * 100:.1f} cents a gallon {'lower' if d < 0 else 'higher'} this week and now reads ${us['now']:.3f}.",
            f"${us['now']:.3f} a gallon. US diesel is {'down' if d < 0 else 'up'} {abs(d) * 100:.1f} cents on the week.",
        ][variant % 3]
        on_fill = abs(d) * 150
        return line + f" Across a 150 gallon fill that is about ${on_fill:,.0f} {'saved' if d < 0 else 'added'} per stop."
    if kind == "fx":
        p = fx["pct7"]
        weaker = p > 0  # USD/CAD up means it takes more Canadian dollars to buy one US dollar
        line = (f"The loonie {'lost' if weaker else 'gained'} {abs(p):.2f} per cent against the US dollar this week. "
                f"USD/CAD closed at {fx['now']:.4f} on {fx['date']}.")
        why = (" A weaker loonie makes US fuel and parts dearer for Canadian carriers and makes "
               "Canadian freight cheaper for US shippers." if weaker else
               " A stronger loonie makes US fuel and parts cheaper for Canadian carriers and "
               "trims what a US-paid load is worth in Canadian dollars.")
        return line + why
    if kind == "border":
        worst = max(g["border"], key=lambda r: max(r["ca"] or 0, r["us"] or 0))
        into_ca = (worst["ca"] or 0) >= (worst["us"] or 0)
        mins = worst["ca"] if into_ca else worst["us"]
        typ = worst["typ"]
        line = f"{worst['name']} ran {mins} minutes {'into Canada' if into_ca else 'into the US'} when we checked."
        if into_ca and typ is not None and typ < mins:  # typical is CBSA history: into Canada only
            usual = "it is usually clear" if typ <= 2 else f"its usual wait is about {typ} minutes"
            line += f" For a crossing where {usual}, that is worth routing around if you can."
        return line
    return ""


def _quiet_lead(g):
    ca, us = g["ca"], g["us"]
    bits = []
    if ca["d7"] is not None:
        bits.append(f"Canadian diesel moved {_cents(abs(ca['d7']))}")
    if us["d7"] is not None:
        bits.append(f"US diesel moved {abs(us['d7']) * 100:.1f} cents a gallon")
    return ("A quiet week. " + (" and ".join(bits) + ", and the border stayed mostly clear." if bits
            else "Prices and the border held close to last week."))


def _subject_bits(kind, g):
    ca, us, fx = g["ca"], g["us"], g["fx"]
    if kind == "ca" and ca["d7"] is not None:
        return f"Canadian diesel {_move_word(ca['d7'])} {_cents(abs(ca['d7']))}"
    if kind == "us" and us["d7"] is not None:
        return f"US diesel {_move_word(us['d7'])} {abs(us['d7']) * 100:.0f} cents"
    if kind == "fx" and fx["pct7"] is not None:
        return f"Loonie {'weaker' if fx['pct7'] > 0 else 'stronger'} by {abs(fx['pct7']):.1f}%"
    if kind == "border":
        worst = max(g["border"], key=lambda r: max(r["ca"] or 0, r["us"] or 0))
        return f"{worst['name']} backs up"
    return ""


def build_brief_parts(today=None, recent_posts=None):
    """The brief as a dict: title (stable, drives the slug), subject (changes with the news),
    subtitle (the inbox preview line) and markdown.

    It used to be one fixed template: the same five sections in the same order, the same
    sentence about crude every week, no week-on-week change and no US diesel. Readers saw the
    same email with new numbers. Now the biggest move of the week leads, every price carries its
    change, both countries get equal space, background is explained only when it moved, a
    spotlight rotates through provinces and US districts, and known dates for next week are
    flagged.
    """
    today = today or dt.date.today()
    g = _gather(today)
    week_no = today.isocalendar()[1]
    title = f"The Northern Mile Brief: week of {today.strftime('%d %B %Y').lstrip('0')}"

    cands = _candidates(g)
    md = []
    lead_kind = cands[0][0] if cands and cands[0][1] >= 1.0 else None
    lead = _lead(lead_kind, g, week_no) if lead_kind else _quiet_lead(g)
    md.append(lead)

    # Subject: the two biggest moves, so the inbox line says what is inside.
    strong = [k for k, s in cands if s >= 1.0][:2]
    bits = [b for b in (_subject_bits(k, g) for k in strong) if b]
    subject = (", ".join(bits) + " | The Northern Mile Brief") if bits else title
    # Preview line in the inbox. Take a second sentence when the first is a fragment
    # ("$6.199 a gallon.") so the preview always says what moved.
    sents = [x.strip().rstrip(".") for x in lead.split(". ") if x.strip()]
    subtitle = sents[0] + "."
    if len(sents[0].split()) < 6 and len(sents) > 1:
        subtitle = f"{sents[0]}. {sents[1]}."

    # Diesel, both sides.
    ca, us = g["ca"], g["us"]
    md.append("## Diesel, both sides of the border")
    if ca["now"] is not None:
        chg = f", {_move_word(ca['d7'])} {_cents(abs(ca['d7']))} on the week" if ca["d7"] else ""
        line = f"Canada: {_cents(ca['now'])} a litre{chg}, NRCan survey printed {ca['print']}."
        if ca.get("low") is not None and ca.get("high") is not None:
            line += (f" {_prov(ca['high_code'])} is dearest at {_cents(_f(ca['high']))} and "
                     f"{_prov(ca['low_code'])} cheapest at {_cents(_f(ca['low']))}.")
        md.append(line)
    if us["now"] is not None:
        chg = f", {_move_word(us['d7'])} {abs(us['d7']) * 100:.1f} cents on the week" if us["d7"] else ""
        line = f"United States: ${us['now']:.3f} a gallon{chg}, EIA week ending {us['week']}."
        if us["low"] and us["high"]:
            line += (f" {us['high'][1]} is dearest at ${us['high'][0]:.3f} and "
                     f"{us['low'][1]} cheapest at ${us['low'][0]:.3f}.")
        md.append(line)

    # Border, both directions. Only what is moving gets a line.
    rows = g["border"]
    if rows:
        md.append("## At the border")
        # Only waits that change a plan get a line. Ten minutes is the bar.
        slow = []
        for r in rows:
            parts = []
            if (r["ca"] or 0) >= 10:
                parts.append(f"{r['ca']} min into Canada")
            if (r["us"] or 0) >= 10:
                parts.append(f"{r['us']} min into the US")
            if parts:
                worst = max(r["ca"] or 0, r["us"] or 0)
                note = ""
                # The typical figure is CBSA history, so it describes the wait INTO Canada only.
                if r["typ"] is not None and (r["ca"] or 0) >= r["typ"] + 10 and (r["ca"] or 0) >= (r["us"] or 0):
                    note = " (usually clear)" if r["typ"] <= 2 else f" (usually about {r['typ']} min)"
                slow.append((worst, f"- {r['name']}: {' and '.join(parts)}{note}"))
        if slow:
            md.append("\n".join(s for _, s in sorted(slow, key=lambda s: -s[0])))
            md.append(f"The other {len(rows) - len(slow)} crossings were under 10 minutes both ways "
                      "when we checked." if len(rows) > len(slow) else "")
        else:
            md.append(f"All {len(rows)} crossings we track were under 10 minutes in both directions "
                      "when we checked.")
        md.append("Waits are commercial lanes: CBSA for traffic into Canada, CBP for traffic into the US.")

    # The dollar. Background only when it moved enough to matter.
    fx = g["fx"]
    if fx["now"] is not None and lead_kind != "fx":
        md.append("## The dollar")
        if fx["pct7"] is not None:
            weaker = fx["pct7"] > 0
            md.append(f"USD/CAD closed at {fx['now']:.4f} on {fx['date']}. The loonie is "
                      f"{'down' if weaker else 'up'} {abs(fx['pct7']):.2f} per cent on the week.")
            if abs(fx["pct7"]) >= 0.5:
                md.append("Crude trades in US dollars, so a move this size shows up at the pump "
                          "in Canada within a week or two.")
        else:
            md.append(f"USD/CAD closed at {fx['now']:.4f} on {fx['date']}.")

    # Spotlight: alternates Canada and the US, rotating through provinces and districts.
    md += _spotlight(g, week_no)

    # This week's posts.
    if recent_posts:
        md.append("## Worth your time this week")
        md.append("\n".join(f"- [{p['title']}]({p['url']})" for p in recent_posts))

    nxt = _next_week(today)
    if nxt:
        md.append("## Coming up")
        md.append("\n".join(f"- {n}" for n in nxt))

    md.append("Every figure above is live and dated on the "
              "[dashboard](https://dashboard.northernmilemedia.com/).")
    md.append("")
    return {"title": title, "subject": subject, "subtitle": subtitle,
            "markdown": "\n\n".join(m for m in md if m != "") + "\n"}


def _spotlight(g, week_no):
    order_ca = ["ON", "QC", "BC", "AB", "MB", "SK", "NB", "NS", "NL", "PE"]
    order_us = ["gulf_coast", "midwest", "central_atlantic", "lower_atlantic", "rocky_mountain",
                "california", "new_england", "west_coast_ex_california"]
    out = []
    if week_no % 2 == 0:
        code = order_ca[(week_no // 2) % len(order_ca)]
        p = g["spot"].get(code)
        if p:
            out.append(f"## Spotlight: {_prov(code)}")
            vs = _f(p.get("vs_national"))
            s = f"{_prov(code)} diesel is {_cents(_f(p['price']))} a litre"
            if vs is not None:
                s += f", {_cents(abs(vs))} {'above' if vs > 0 else 'below'} the national average"
            s += "."
            if p.get("low_city") and p.get("high_city") and p.get("city_count") not in (None, "1", 1):
                s += (f" Across its {p['city_count']} surveyed cities it runs from {_cents(_f(p['low_price']))} "
                      f"in {p['low_city']} to {_cents(_f(p['high_price']))} in {p['high_city']}.")
            out.append(s)
    else:
        key = order_us[(week_no // 2) % len(order_us)]
        d = g["districts"].get(key)
        us_now = g["us"]["now"]
        if d and d.get("price_usd_gal") and us_now:
            name = d.get("label", key).split(" (")[0]
            gap = d["price_usd_gal"] - us_now
            out.append(f"## Spotlight: {name}")
            out.append(f"{name} diesel is ${d['price_usd_gal']:.3f} a gallon, "
                       f"{abs(gap) * 100:.1f} cents {'above' if gap > 0 else 'below'} the US average.")
    return out


def build_brief(today=None, recent_posts=None):
    """Return (title, subtitle, markdown). Kept for callers that predate build_brief_parts."""
    p = build_brief_parts(today, recent_posts)
    return p["title"], p["subtitle"], p["markdown"]


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
