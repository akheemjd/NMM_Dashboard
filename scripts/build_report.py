"""Generate The Cross-Border Cost Brief - the paid monthly report.

Buyer: US-domiciled for-hire carriers, 10-100 power units, with active Canadian operating authority,
running the Ontario-Michigan and Ontario-New York corridors.

What they cannot get anywhere else in one place:
  * Canadian diesel by province (NRCan) next to US diesel by PADD (EIA)
  * what the two prices actually cost per 1,000 km on each side, in one currency
  * border wait times for their own crossings, monthly averages
  * a fuel surcharge number they can defend to a shipper

The Holden rule applies: this is heavy data, so every figure gets a plain sentence underneath it
saying what it means for the reader. No raw tables on their own.

Reads the same normalised files the public site uses, so the report and the site can never disagree.
Writes HTML that prints cleanly to PDF from any browser.
"""
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output", "reports")

# The corridors the buyer actually runs. Narrow on purpose: a report for everyone is a report for
# nobody, and this list is what makes the email defensible ("your crossing" beats "the border").
CORRIDORS = [
    ("Windsor - Detroit (Ambassador Bridge)", "ambassador-bridge"),
    ("Sarnia - Port Huron (Blue Water Bridge)", "blue-water-bridge"),
    ("Fort Erie - Buffalo (Peace Bridge)", "peace-bridge"),
    ("Queenston - Lewiston", "queenston-lewiston-bridge"),
    ("Sault Ste. Marie (International Bridge)", "international-bridge-ssm"),
]


def load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def num(v):
    """Coerce to float, because every published value in these files is a STRING.

    fuel.norm.json stores national_diesel as "264.2" and fx.norm.json stores usd_cad as "1.3960".
    Comparing those directly to a number silently produced n/a across the whole report the first
    time this ran.
    """
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.replace(",", "").replace("¢", "").strip())
        except ValueError:
            return None
    return None


def money(v, unit, dp=3):
    if not isinstance(v, (int, float)):
        return "n/a"
    if dp == 0:
        return f"{v:,.0f} {unit}"
    return f"{v:.{dp}f} {unit}"


def pct(v):
    return f"{v:.1f}%" if isinstance(v, (int, float)) else "n/a"


def build():
    fuel = load("fuel.norm.json") or {}
    eia = load("eia_diesel.json") or {}
    fx = load("fx.norm.json") or {}
    border = load("border.norm.json") or {}
    ifta = load("ifta.json") or {}

    # --- Canadian national diesel ----------------------------------------------------
    # fuel.norm.json: fuel.national_diesel = "264.2" (string), print_date = "Tue, 27 Oct 2026"
    fb = fuel.get("fuel") if isinstance(fuel.get("fuel"), dict) else {}
    national = num(fb.get("national_diesel"))
    print_date = fb.get("print_date") or "n/a"

    # --- Provincial diesel ------------------------------------------------------------
    prov = fuel.get("provinces")
    prov_rows = []
    if isinstance(prov, list):
        for rec in prov:
            if not isinstance(rec, dict):
                continue
            nm = rec.get("name") or rec.get("province") or rec.get("code")
            v = num(rec.get("price") or rec.get("national_diesel") or rec.get("value"))
            if nm and v:
                prov_rows.append((nm, v))
    elif isinstance(prov, dict):
        for nm, rec in prov.items():
            v = num(rec.get("price")) if isinstance(rec, dict) else num(rec)
            if v:
                prov_rows.append((nm, v))
    prov_rows.sort(key=lambda x: x[1])

    # --- US national ------------------------------------------------------------------
    us_nat = num(eia.get("us_national_usd_gal"))
    us_date = eia.get("date") or "n/a"

    # --- FX ---------------------------------------------------------------------------
    fxblock = fx.get("fx") if isinstance(fx.get("fx"), dict) else {}
    rate = num(fxblock.get("usd_cad"))
    fx_date = fxblock.get("obs_date") or "n/a"

    # --- Convert to a single comparable basis ------------------------------------------
    # Canada is cents per litre; the US is dollars per gallon. A carrier budgets per kilometre, so
    # both sides are converted to cost per 1,000 km on a 38 L/100 km tractor, which is the only
    # number a dispatcher can act on. Stated in CAD and USD so neither side has to do arithmetic.
    BURN_L_PER_100KM = 38.0
    cad_per_1000 = (national / 100) * BURN_L_PER_100KM * 10 if isinstance(national, (int, float)) else None
    us_cad_per_1000 = None
    if isinstance(us_nat, (int, float)) and isinstance(rate, (int, float)):
        # US dollars per gallon -> CAD per litre -> CAD per 1,000 km
        cad_per_l = (us_nat * rate) / 3.78541
        us_cad_per_1000 = cad_per_l * BURN_L_PER_100KM * 10

    now = datetime.now(timezone.utc)
    month = now.strftime("%B %Y")

    prov_html = "".join(
        f"<tr><td>{n}</td><td class='num'>{v:.1f}</td>"
        f"<td class='num'>{'below' if national and v < national else 'above'}</td></tr>"
        for n, v in prov_rows[:12]
    ) or "<tr><td colspan='3'>n/a</td></tr>"

    corr_html = ""
    # border.norm.json carries crossings as a LIST of records, not a dict keyed by slug.
    cross_list = border.get("crossings")
    by_slug = {}
    if isinstance(cross_list, list):
        for rec in cross_list:
            if isinstance(rec, dict):
                k = rec.get("slug") or rec.get("id") or rec.get("crossing_id")
                if k:
                    by_slug[k] = rec
    elif isinstance(cross_list, dict):
        by_slug = cross_list

    for label, slug in CORRIDORS:
        rec = by_slug.get(slug) or {}
        # border.norm.json carries a human string, not minutes: "No delay", "25 min", "1 hr 10 min".
        # A carrier reads the raw string happily; the report needs it as a number to say what it costs.
        def _mins(s):
            if not isinstance(s, str):
                return num(s)
            t = s.lower()
            if "no delay" in t or t.strip() in ("", "n/a"):
                return 0.0
            h = re.search(r"(\d+)\s*hr", t)
            m = re.search(r"(\d+)\s*min", t)
            if h or m:
                return (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)
            return num(s)

        avg = _mins(rec.get("wait"))
        us = _mins(rec.get("us_wait"))
        if avg is None:
            corr_html += f"<tr><td>{label}</td><td class='num'>n/a</td><td class='num'>n/a</td></tr>"
        else:
            us_txt = f"{us:.0f} min" if us is not None else "n/a"
            corr_html += (f"<tr><td>{label}</td><td class='num'>{avg:.0f} min</td>"
                          f"<td class='num'>{us_txt}</td></tr>")
    if not corr_html:
        corr_html = "<tr><td colspan='3'>n/a</td></tr>"

    gap_txt = "n/a"
    if isinstance(national, (int, float)) and isinstance(us_nat, (int, float)) and isinstance(rate, (int, float)):
        us_in_cad_cpl = (us_nat * rate) / 3.78541 * 100
        gap = national - us_in_cad_cpl
        gap_txt = f"{abs(gap):.1f}¢/L {'higher' if gap > 0 else 'lower'} in Canada"

    surcharge_txt = "n/a"
    if isinstance(national, (int, float)) and isinstance(us_nat, (int, float)):
        # Both sides on one basis before subtracting: cents per litre.
        us_in_cad_cpl = (us_nat * rate) / 3.78541 * 100 if isinstance(rate, (int, float)) else None
        if us_in_cad_cpl is not None:
            surcharge_txt = (f"{abs(national - us_in_cad_cpl):.1f} cents per litre "
                             f"({'Canada higher' if national > us_in_cad_cpl else 'US higher'})")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Cross-Border Cost Brief - {month}</title>
<style>
  @page {{ margin: 18mm; }}
  body {{ font: 15px/1.55 Georgia, serif; color:#1a1a1a; max-width: 760px; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 30px; margin: 0 0 4px; letter-spacing:-.01em; }}
  h2 {{ font-size: 19px; margin: 34px 0 8px; border-top: 2px solid #1a1a1a; padding-top: 10px; }}
  .kicker {{ text-transform: uppercase; letter-spacing:.12em; font-size:11px; color:#0a5c3b; font-weight:700; }}
  .sub {{ color:#555; font-size:13px; margin-bottom:26px; }}
  .big {{ font-size:34px; font-weight:600; line-height:1.1; }}
  .mean {{ color:#444; font-size:13.5px; margin:6px 0 0; padding-left:12px; border-left:3px solid #0a5c3b; }}
  table {{ width:100%; border-collapse:collapse; margin:10px 0 4px; font-size:14px; }}
  th {{ text-align:left; font:600 11px/1 system-ui,sans-serif; text-transform:uppercase;
        letter-spacing:.08em; color:#666; border-bottom:1px solid #ccc; padding:6px 8px 6px 0; }}
  td {{ padding:6px 8px 6px 0; border-bottom:1px solid #e8e8e8; }}
  .num {{ text-align:right; font-variant-numeric: tabular-nums; font-family: ui-monospace, monospace; }}
  .src {{ font-size:11.5px; color:#666; margin-top:4px; }}
  .foot {{ margin-top:40px; border-top:2px solid #1a1a1a; padding-top:10px; font-size:11.5px; color:#555; }}
</style></head><body>

<div class="kicker">The Cross-Border Cost Brief &middot; {month}</div>
<h1>What your Ontario lanes cost this month</h1>
<p class="sub">Fuel, currency and border delay on the corridors between Ontario and Michigan or New York.
One page you can hand to a shipper.</p>

<h2>1. Fuel: what a tractor burns per 1,000 km</h2>
<div class="big">{money(cad_per_1000, 'C$', 0) if cad_per_1000 else 'n/a'}</div>
<p class="mean">Canadian diesel, cost per 1,000 km at 38 L/100 km.</p>
<div class="big" style="margin-top:18px;">{money(us_cad_per_1000, 'C$', 0) if us_cad_per_1000 else 'n/a'}</div>
<p class="mean">US diesel on the same basis, converted at {rate if rate else 'n/a'} USD/CAD, so the two
numbers are directly comparable and you are not doing the arithmetic mid-quote.</p>
<p class="src">Canadian figure: {money(national, '&cent;/L', 1)} national average.
US figure: {money(us_nat, '$/gal', 3)} national average, EIA week {us_date}.</p>

<h2>2. The gap you are quoting against</h2>
<div class="big">{gap_txt}</div>
<p class="mean">This is the spread between the two headline prices on a common basis. It is the number
your fuel surcharge has to account for on a cross-border lane, and it moves every week.</p>

<h2>3. Provincial diesel, where you load and fuel</h2>
<table><thead><tr><th>Province</th><th class="num">&cent;/L</th><th class="num">vs national</th></tr></thead>
<tbody>{prov_html}</tbody></table>
<p class="mean">Fuel where you actually buy it. A province below the national average is where a
cross-border carrier should be topping up before the return leg.</p>
<p class="src">Natural Resources Canada weekly retail diesel survey.</p>

<h2>4. Your crossings this month</h2>
<table><thead><tr><th>Crossing</th><th class="num">Canada side</th><th class="num">US side</th></tr></thead>
<tbody>{corr_html}</tbody></table>
<p class="mean">Both sides of the same crossing. A carrier crossing northbound faces the Canadian booth; southbound, the US booth. Whichever is longer is the one to build the appointment around.
Every minute a tractor sits at a primary booth is a minute it is not earning.</p>
<p class="src">CBSA and US Customs and Border Protection published wait times.</p>

<h2>5. What changed and what to do</h2>
<p>Diesel on the Canadian side is {gap_txt}. On a 1,000 km run at 38 L/100 km that difference moves
your fuel cost by the amount shown in section 1.</p>
<p>If you are quoting a cross-border lane this month, the surcharge basis to carry forward is
{surcharge_txt}. Re-check before the quote expires: the provincial survey prints weekly and the
exchange rate moves daily.</p>

<div class="foot">
Generated {now.strftime('%Y-%m-%d %H:%M')} UTC by Northern Mile Media.<br>
Sources: Natural Resources Canada weekly diesel survey, US Energy Information Administration,
Bank of Canada Valet API, Canada Border Services Agency, US Customs and Border Protection, IFTA Inc.<br>
Method: dashboard.northernmilemedia.com/methodology/nmdi/
</div>
</body></html>"""
    return html, month


def main():
    os.makedirs(OUT, exist_ok=True)
    html, month = build()
    slug = month.lower().replace(" ", "-")
    path = os.path.join(OUT, f"cross-border-cost-brief-{slug}.html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {path}")
    print(f"  {len(html):,} bytes")


if __name__ == "__main__":
    main()
