"""Build the brand home at www.northernmilemedia.com/.

Second pass. The first version was a masthead and three text links: it explained nothing and looked
like a placeholder. This one leads with the live numbers, which is both the fastest way to say what
Northern Mile is and the only honest way to prove it exists.

Design rules the account holds to, from the same editor who rejected the card-grid look:
editorial serif headlines, ruled sections instead of boxes, square corners, one accent colour, and
real data on screen rather than an illustration of it.

Reads data/fuel.norm.json, eia_diesel.json and border.norm.json - the same normalised files the
dashboard and the paid report use, so the home page cannot drift from them.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output", "www")
BRAND = "https://www.northernmilemedia.com/"
DASH = "https://dashboard.northernmilemedia.com"


def load(name):
    p = os.path.join(DATA, name)
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def load_provinces():
    fuel = load("fuel.norm.json")
    prov = fuel.get("provinces")
    rows = []
    if isinstance(prov, list):
        for rec in prov:
            if not isinstance(rec, dict):
                continue
            nm = rec.get("name") or rec.get("code")
            v = num(rec.get("price") or rec.get("national_diesel"))
            if nm and v:
                rows.append((nm, v))
    rows.sort(key=lambda x: x[1])
    return rows


def diesel_series(weeks=104):
    """Canada national diesel, weekly, oldest first. Reads data/history/series.csv.

    The chart is the page's visual anchor: without it the home page was a column of text, which is
    what the editor rejected on first review.
    """
    import csv
    path = os.path.join(DATA, "history", "series.csv")
    rows = []
    try:
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("series") == "diesel" and r.get("key") == "national":
                    try:
                        rows.append((r["date"], float(r["value"])))
                    except (KeyError, ValueError):
                        continue
    except OSError:
        return []
    rows.sort()
    return rows[-weeks:]


def sparkline(points, w=1040, h=150):
    """Inline SVG, no library. One line, a filled area, and the latest point marked."""
    if len(points) < 3:
        return ""
    vals = [v for _, v in points]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1
    pad = 8
    n = len(points)
    coords = []
    for i, v in enumerate(vals):
        x = pad + (i / (n - 1)) * (w - 2 * pad)
        y = h - pad - ((v - lo) / span) * (h - 2 * pad)
        coords.append((x, y))
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(coords))
    area = f"{line} L{coords[-1][0]:.1f},{h - pad} L{coords[0][0]:.1f},{h - pad} Z"
    lx, ly = coords[-1]
    first, last = points[0][0], points[-1][0]
    return f"""<figure class="chart">
  <svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img"
       aria-label="Canadian national diesel, {first} to {last}, {lo:.1f} to {hi:.1f} cents per litre">
    <path d="{area}" fill="#0a5c3b" fill-opacity="0.08"/>
    <path d="{line}" fill="none" stroke="#0a5c3b" stroke-width="2.5" stroke-linejoin="round"/>
    <circle cx="{lx:.1f}" cy="{ly:.1f}" r="4.5" fill="#0a5c3b"/>
  </svg>
  <figcaption>
    <span>Canadian national diesel, weekly</span>
    <span>{first} to {last} &nbsp;·&nbsp; low {lo:.1f}&cent;/L, high {hi:.1f}&cent;/L</span>
  </figcaption>
</figure>"""


def build():
    fuel = load("fuel.norm.json")
    eia = load("eia_diesel.json")
    fx = load("fx.norm.json")
    border = load("border.norm.json")

    fb = fuel.get("fuel") if isinstance(fuel.get("fuel"), dict) else {}
    ca = num(fb.get("national_diesel"))
    ca_date = fb.get("print_date") or "n/a"
    us = num(eia.get("us_national_usd_gal"))
    us_date = eia.get("date") or "n/a"
    fxb = fx.get("fx") if isinstance(fx.get("fx"), dict) else {}
    rate = num(fxb.get("usd_cad"))
    fx_date = fxb.get("obs_date") or "n/a"

    # Gap on one basis: both sides in cents per litre.
    gap = gap_word = None
    if ca and us and rate:
        us_cpl = (us * rate) / 3.78541 * 100
        gap = abs(ca - us_cpl)
        gap_word = "Canada higher" if ca > us_cpl else "US higher"

    # The busiest crossing that is actually reporting, for a concrete example.
    crossings = border.get("crossings")
    worst = None
    if isinstance(crossings, list):
        def mins(s):
            if not isinstance(s, str):
                return None
            t = s.lower()
            if "no delay" in t:
                return 0
            h = re.search(r"(\d+)\s*hr", t)
            m = re.search(r"(\d+)\s*min", t)
            if h or m:
                return (int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0)
            return None
        scored = [(mins(r.get("wait")), r.get("name")) for r in crossings if isinstance(r, dict)]
        scored = [(v, n) for v, n in scored if v is not None and n]
        if scored:
            scored.sort(reverse=True)
            worst = scored[0]

    provs = load_provinces()
    cheap = provs[0] if provs else None
    dear = provs[-1] if provs else None

    def fig(v, unit, dp=1):
        return f"{v:.{dp}f}<em>{unit}</em>" if v is not None else "n/a"

    gap_html = (f"{gap:.1f}<em>¢/L</em>" if gap is not None else "n/a")
    border_html = (f"{worst[0]}<em>min</em>" if worst else "n/a")
    fx_html = (f"{rate:.4f}" if rate else "n/a")

    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<title>Northern Mile Media — Canadian and US diesel, border and rate data</title>
<meta name="description" content="Canadian provincial diesel next to US district diesel, live Canada-US border wait times and the Bank of Canada rate. Free, from primary sources, every figure dated. Plus the writing that explains what they mean.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{BRAND}">
<meta property="og:title" content="Northern Mile Media">
<meta property="og:description" content="Canadian and US diesel on one basis, live border waits, and the writing that explains them.">
<meta property="og:type" content="website">
<meta property="og:url" content="{BRAND}">
<meta property="og:image" content="{BRAND}og.jpg">
<style>
  :root{{--ink:#1a1a1a;--accent:#0a5c3b;--rule:#d8d8d8;--paper:#faf9f7;--mute:#5c5c5c}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--paper);color:var(--ink);
       font:16px/1.6 Georgia,'Source Serif 4',serif;-webkit-font-smoothing:antialiased}}
  .wrap{{max-width:1080px;margin:0 auto;padding:0 24px}}
  a{{color:inherit}}

  /* Masthead: name, then the one sentence that says what this is. */
  .top{{border-bottom:2px solid var(--ink);padding:22px 0 0}}
  .top .brand{{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:10px}}
  .top .name{{font:600 17px/1 Georgia,serif;letter-spacing:-.01em;text-decoration:none}}
  .top .name span{{font:400 11px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.14em;
                  color:var(--mute);margin-left:10px}}
  .top .nav{{font:500 12px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.1em}}
  .top .nav a{{text-decoration:none;margin-left:20px;padding-bottom:3px;border-bottom:2px solid transparent}}
  .top .nav a:hover{{border-bottom-color:var(--ink)}}

  .hero{{padding:42px 0 34px}}
  .hero .kick{{font:700 11px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;
              color:var(--accent);margin-bottom:18px}}
  .hero h1{{font:600 clamp(30px,4.6vw,50px)/1.08 Georgia,serif;letter-spacing:-.025em;margin:0 0 20px;max-width:17ch}}
  .hero .sub{{font-size:19px;line-height:1.6;color:#333;max-width:40em;margin:0}}
  .hero .sub b{{font-weight:600;color:var(--ink)}}

  /* The numbers. Real, dated, on screen. This is what the site is. */
  .strip{{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink);
         border-bottom:1px solid var(--rule)}}
  .cell{{padding:18px 16px 18px 0;border-right:1px solid var(--rule)}}
  .cell:last-child{{border-right:0;padding-right:0}}
  .cell .lab{{font:600 10px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;
             color:var(--mute);margin-bottom:9px}}
  .cell .v{{font:600 30px/1 Georgia,serif;letter-spacing:-.02em}}
  .cell .v em{{font-style:normal;font-size:12px;color:var(--mute);margin-left:3px;letter-spacing:0}}
  .cell .d{{font-size:11.5px;color:var(--mute);margin-top:7px}}

  /* Sections: ruled, not boxed. Square corners throughout. */
  .sec{{padding:34px 0;border-bottom:1px solid var(--rule)}}
  .sec .row{{display:grid;grid-template-columns:190px 1fr;gap:32px;align-items:start}}
  .sec .lab{{font:700 10.5px/1.5 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.14em;
            color:var(--accent);padding-top:5px}}
  .sec h2{{font:600 27px/1.2 Georgia,serif;letter-spacing:-.015em;margin:0 0 10px}}
  .sec p{{margin:0 0 14px;color:#3a3a3a;max-width:44em}}
  .sec .go{{display:inline-block;font:600 13px/1 system-ui,sans-serif;text-decoration:none;
           border-bottom:2px solid var(--ink);padding-bottom:4px}}
  .sec .go:hover{{color:var(--accent);border-bottom-color:var(--accent)}}
  .facts{{margin:16px 0 0;padding:0;list-style:none;font-size:14px;color:#3a3a3a}}
  .facts li{{padding:7px 0;border-bottom:1px solid #e8e8e8}}
  .facts li:last-child{{border-bottom:0}}
  .facts b{{font-weight:600;font-variant-numeric:tabular-nums}}

  .chart{{margin:30px 0 0;padding:0}}
  .chart svg{{display:block;width:100%;height:150px}}
  .chart figcaption{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;
                     font:400 11.5px/1.5 system-ui,sans-serif;color:var(--mute);
                     border-top:1px solid var(--rule);padding-top:9px;margin-top:6px}}
  .foot{{padding:32px 0 64px;font-size:12.5px;line-height:1.75;color:var(--mute)}}
  .foot a{{color:#333;text-decoration:none;border-bottom:1px solid #ccc}}
  .foot .src{{margin-top:14px}}

  @media(max-width:820px){{
    .strip{{grid-template-columns:repeat(2,1fr)}}
    .cell:nth-child(2){{border-right:0}}
    .cell:nth-child(1),.cell:nth-child(2){{border-bottom:1px solid var(--rule)}}
    .sec .row{{grid-template-columns:1fr;gap:10px}}
    .hero{{padding:38px 0 32px}}
  }}
  @media(max-width:520px){{
    /* Keep the 2x2. Four stacked rows pushed the numbers past a full screen. */
    .strip{{grid-template-columns:1fr 1fr}}
    .cell{{padding:14px 10px 14px 0}}
    .cell:nth-child(odd){{padding-right:10px}}
    .cell .v{{font-size:26px}}
    .top .nav a{{margin:0 12px 0 0}}
    .hero h1{{font-size:clamp(28px,8vw,38px);max-width:none}}
    .hero .sub{{font-size:16.5px}}
    .sec h2{{font-size:22px}}
    .sec{{padding:30px 0}}
  }}
</style>
</head>
<body>

<div class="top"><div class="wrap"><div class="brand">
  <a class="name" href="{BRAND}">Northern Mile Media<span>Est. 2026</span></a>
  <nav class="nav">
    <a href="{DASH}/">Data</a>
    <a href="/blog/">Writing</a>
    <a href="{DASH}/report/">The Brief</a>
    <a href="{DASH}/methodology/nmdi/">Method</a>
  </nav>
</div></div></div>

<div class="wrap">

  <div class="hero">
    <div class="kick">Canadian and US trucking data</div>
    <h1>What diesel costs on both sides of the border, this week.</h1>
    <p class="sub">Provincial Canadian diesel next to US district diesel, converted to one basis so
    they can be compared. Live booth waits at every Canada-US crossing. The Bank of Canada rate.
    <b>Free, from primary sources, and every figure carries the day it was observed.</b></p>
  </div>

  <div class="strip">
    <div class="cell">
      <div class="lab">Canada national</div>
      <div class="v">{fig(ca, '¢/L')}</div>
      <div class="d">NRCan print {ca_date}</div>
    </div>
    <div class="cell">
      <div class="lab">United States</div>
      <div class="v">{fig(us, '$/gal', 3)}</div>
      <div class="d">EIA week {us_date}</div>
    </div>
    <div class="cell">
      <div class="lab">The gap</div>
      <div class="v">{gap_html}</div>
      <div class="d">{gap_word or 'n/a'}, on one basis</div>
    </div>
    <div class="cell">
      <div class="lab">USD / CAD</div>
      <div class="v">{fx_html}</div>
      <div class="d">Bank of Canada, {fx_date}</div>
    </div>
  </div>

  {sparkline(diesel_series())}

  <div class="sec"><div class="row">
    <div class="lab">The data</div>
    <div>
      <h2>One page that updates itself, from primary sources.</h2>
      <p>Canadian diesel by province and city, US diesel by EIA district, border waits at every
      Canada-US crossing, exchange rate, IFTA rates and fuel tax by jurisdiction. No account, no
      paywall, no tracking.</p>
      <ul class="facts">
        <li>Cheapest province this week: <b>{f'{cheap[0]} at {cheap[1]:.1f}¢/L' if cheap else 'n/a'}</b></li>
        <li>Dearest: <b>{f'{dear[0]} at {dear[1]:.1f}¢/L' if dear else 'n/a'}</b></li>
        <li>Longest wait reporting right now: <b>{f'{worst[1]}, {worst[0]} min' if worst else 'n/a'}</b></li>
      </ul>
      <a class="go" href="{DASH}/">Open the dashboard</a>
    </div>
  </div></div>

  <div class="sec"><div class="row">
    <div class="lab">The writing</div>
    <div>
      <h2>The part a price table cannot tell you.</h2>
      <p>Why the two numbers are not comparable as published. What the CRA asks before it calls your
      corporation a personal services business. Which IFTA filing mistakes trigger an audit, and what
      they cost. Written for the person running the truck, not the person writing about it.</p>
      <a class="go" href="/blog/">Read the writing</a>
    </div>
  </div></div>

  <div class="sec"><div class="row">
    <div class="lab">The Brief</div>
    <div>
      <h2>For carriers running Ontario to Michigan or New York.</h2>
      <p>A monthly page you can quote from: what a tractor burns per 1,000 km on each side of the
      border, the spread to carry into a fuel surcharge, provincial prices where you fuel before the
      return leg, and the booth waits on your own crossings. <b>$249 a month.</b></p>
      <a class="go" href="{DASH}/report/">See the report</a>
    </div>
  </div></div>

  <div class="foot">
    Northern Mile Media publishes North American trucking data from primary sources: Natural
    Resources Canada, US Energy Information Administration, Bank of Canada, Canada Border Services
    Agency, US Customs and Border Protection, and IFTA Inc. Where a source has not published, we say
    so rather than carrying the old number forward.
    <div class="src">
      <a href="{DASH}/methodology/nmdi/">Methodology</a> &nbsp;·&nbsp;
      <a href="{DASH}/press/">Press</a> &nbsp;·&nbsp;
      <a href="{DASH}/contact/">Contact</a> &nbsp;·&nbsp;
      <a href="{DASH}/advertise/">Advertise</a>
      <br><br>&copy; 2026 Northern Mile Media.
    </div>
  </div>

</div>
</body>
</html>"""


def main():
    os.makedirs(OUT, exist_ok=True)
    html = build()
    path = os.path.join(OUT, "home.html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {path} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
