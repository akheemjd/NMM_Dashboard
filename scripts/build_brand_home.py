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


def diesel_series(weeks=None):
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
    return rows[-weeks:] if weeks else rows


def sparkline(points, w=1000, h=200):
    """Inline SVG with an axis, a reference line and a stated finding.

    The first version was a bare line with a caption. A visitor could see it went up but could not
    tell you by how much, against what, or since when - which is decoration, not information. This
    version carries a y-axis, the ten-year average as a reference line, a labelled latest point, and
    a headline sentence computed from the series itself.
    """
    if len(points) < 3:
        return ""
    import statistics
    vals = [v for _, v in points]
    lo, hi = min(vals), max(vals)
    avg = statistics.mean(vals)
    today_v = vals[-1]
    pct_vs_avg = (today_v - avg) / avg * 100

    # Axis from a round floor to a round ceiling, ticks every 50 cents.
    a_lo = int(lo // 50) * 50
    a_hi = int((hi // 50) + 1) * 50
    span = a_hi - a_lo

    L, R, T, B = 46, 54, 10, 26          # margins: left for axis labels, right for the last point
    pw, ph = w - L - R, h - T - B

    def x_at(i):
        return L + (i / (len(vals) - 1)) * pw

    def y_at(v):
        return T + (1 - (v - a_lo) / span) * ph

    coords = [(x_at(i), y_at(v)) for i, v in enumerate(vals)]
    line = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(coords))
    area = f"{line} L{coords[-1][0]:.1f},{T + ph} L{coords[0][0]:.1f},{T + ph} Z"

    ticks = ""
    t = a_lo
    while t <= a_hi:
        y = y_at(t)
        ticks += (f'<line x1="{L}" y1="{y:.1f}" x2="{w - R}" y2="{y:.1f}" '
                  f'stroke="#dfe3e0" stroke-width="1"/>'
                  f'<text x="{L - 8}" y="{y + 3.5:.1f}" text-anchor="end" '
                  f'font-family="system-ui,sans-serif" font-size="10" fill="#8a8a8a">{t}</text>')
        t += 50

    avg_y = y_at(avg)
    lx, ly = coords[-1]

    # Year labels at the first point of each calendar year we have.
    xlabels = ""
    seen = set()
    for i, (d, _) in enumerate(points):
        yr = d[:4]
        if yr not in seen and (i == 0 or d[5:7] <= "01"):
            seen.add(yr)
            xlabels += (f'<text x="{x_at(i):.1f}" y="{h - 6}" text-anchor="middle" '
                        f'font-family="system-ui,sans-serif" font-size="10" fill="#8a8a8a">{yr}</text>')

    first, last = points[0][0], points[-1][0]
    return f"""<figure class="chart">
  <figcaption class="chead">
    <b>Diesel is {abs(pct_vs_avg):.0f}% {'above' if pct_vs_avg > 0 else 'below'} its ten-year average.</b>
    <span>{today_v:.1f}&cent;/L today against a {avg:.1f}&cent;/L average since {first[:4]}.</span>
  </figcaption>
  <svg viewBox="0 0 {w} {h}" role="img"
       aria-label="Canadian national diesel, {first} to {last}. Today {today_v:.1f} cents per litre,
       ten-year average {avg:.1f}. Range {lo:.1f} to {hi:.1f}.">
    {ticks}
    <path d="{area}" fill="#0a5c3b" fill-opacity="0.07"/>
    <path d="{line}" fill="none" stroke="#0a5c3b" stroke-width="2" stroke-linejoin="round"/>
    <line x1="{L}" y1="{avg_y:.1f}" x2="{w - R}" y2="{avg_y:.1f}"
          stroke="#1a1a1a" stroke-width="1" stroke-dasharray="4 3" stroke-opacity="0.55"/>
    <text x="{w - R + 6}" y="{avg_y + 3.5:.1f}" font-family="system-ui,sans-serif"
          font-size="10" fill="#5c5c5c">avg</text>
    <circle cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="#0a5c3b"/>
    <text x="{lx + 8}" y="{ly + 3.5:.1f}" font-family="system-ui,sans-serif" font-size="10.5"
          font-weight="600" fill="#0a5c3b">today</text>
    {xlabels}
  </svg>
  <div class="cfoot">
    <span>Canadian national diesel, weekly, cents per litre</span>
    <span>Low {lo:.1f} &middot; high {hi:.1f}</span>
  </div>
</figure>"""



PAGE_CSS = """
  /* Page-scoped rules for the home view only. Loaded AFTER nm.css so they win where they overlap;
     nothing here redeclares the header or footer, which stay shared. */
  .home{max-width:1000px;margin:0 auto;padding:0 24px}
  .home .hero{padding:46px 0 34px}
  .home .kick{font:700 11px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;
             color:#0a5c3b;margin-bottom:16px}
  .home .hero h1{font:600 clamp(30px,4.6vw,50px)/1.08 Georgia,serif;letter-spacing:-.025em;
                margin:0 0 18px;max-width:17ch}
  .home .sub{font-size:18px;line-height:1.6;color:#333;max-width:40em;margin:0;
            border:0;background:none;padding:0}
  .home .sub b{font-weight:600;color:#1a1a1a}
  .home .strip{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid #1a1a1a;
              border-bottom:1px solid #d8d8d8;margin:0}
  .home .cell{padding:18px 22px;border-right:1px solid #d8d8d8;background:none}
  .home .cell:first-child{padding-left:0}
  .home .cell:last-child{border-right:0;padding-right:0}
  .home .cell .lab{font:600 10px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;
                  color:#5c5c5c;margin-bottom:9px}
  .home .cell .v{font:600 30px/1 Georgia,serif;letter-spacing:-.02em;color:#1a1a1a}
  .home .cell .v em{font-style:normal;font-size:12px;color:#5c5c5c;margin-left:3px}
  .home .cell .d{font-size:11.5px;color:#5c5c5c;margin-top:7px}
  .home .chart{margin:26px 0 0;padding:0;border:0;background:none}
  .home .chart .chead{display:block;margin:0 0 12px;font:400 14px/1.5 system-ui,sans-serif;color:#5c5c5c}
  .home .chart .chead b{display:block;font:600 19px/1.3 Georgia,serif;color:#1a1a1a;margin-bottom:4px}
  .home .chart svg{display:block;width:100%;height:200px}
  .home .chart .cfoot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;
                     font:400 11.5px/1.5 system-ui,sans-serif;color:#5c5c5c;
                     border-top:1px solid #d8d8d8;padding-top:8px;margin-top:4px}
  .home .sec{padding:34px 0;border-bottom:1px solid #d8d8d8;background:none;margin:0}
  .home .sec .row{display:block}
  .home .sec .lab{font:700 10.5px/1.5 system-ui,sans-serif;text-transform:uppercase;
                 letter-spacing:.14em;color:#0a5c3b;margin:0 0 10px;padding:0}
  .home .sec h2{font:600 27px/1.2 Georgia,serif;letter-spacing:-.015em;margin:0 0 10px;
               padding:0;border:0}
  .home .sec p{margin:0 0 14px;color:#3a3a3a;max-width:44em;font-size:16px;line-height:1.6}
  .home .sec .go{display:inline-block;font:600 13px/1 system-ui,sans-serif;text-decoration:none;
                border-bottom:2px solid #1a1a1a;padding-bottom:4px;color:#1a1a1a;background:none}
  .home .facts{margin:16px 0 0;padding:0;list-style:none;font-size:14px;color:#3a3a3a}
  .home .facts li{padding:7px 0;border-bottom:1px solid #e8e8e8;background:none}
  .home .facts li:last-child{border-bottom:0}
  .home .foot{padding:30px 0 54px;font-size:12.5px;line-height:1.75;color:#5c5c5c;
             border:0;background:none;margin:0}
  @media(max-width:820px){
    .home .strip{grid-template-columns:1fr 1fr}
    .home .cell:nth-child(2){border-right:0}
    .home .cell:nth-child(1),.home .cell:nth-child(2){border-bottom:1px solid #d8d8d8}
  }
  @media(max-width:520px){
    .home .strip{grid-template-columns:1fr 1fr}
    .home .cell{padding:14px 12px}
    .home .cell .v{font-size:26px}
    .home .hero h1{font-size:clamp(28px,8vw,38px);max-width:none}
    .home .sec h2{font-size:22px}
  }
"""


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
  .wrap{{max-width:1000px;margin:0 auto;padding:0 24px}}
  a{{color:inherit}}

  /* Masthead: name, then the one sentence that says what this is. */
              flex-wrap:wrap;gap:16px;min-height:74px}}
             font:600 21px/1 Georgia,serif;letter-spacing:-.02em;color:var(--ink);white-space:nowrap}}
            font:600 12px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em}}
              transition:color .12s,border-color .12s}}

  .hero{{padding:42px 0 34px}}
  .hero .kick{{font:700 11px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.16em;
              color:var(--accent);margin-bottom:18px}}
  .hero h1{{font:600 clamp(30px,4.6vw,50px)/1.08 Georgia,serif;letter-spacing:-.025em;margin:0 0 20px;max-width:17ch}}
  .hero .sub{{font-size:19px;line-height:1.6;color:#333;max-width:40em;margin:0}}
  .hero .sub b{{font-weight:600;color:var(--ink)}}

  /* The numbers. Real, dated, on screen. This is what the site is. */
  .strip{{display:grid;grid-template-columns:repeat(4,1fr);border-top:2px solid var(--ink);
         border-bottom:1px solid var(--rule)}}
  .cell{{padding:18px 22px 18px 22px;border-right:1px solid var(--rule)}}
  .cell:first-child{{padding-left:0}}
  .cell:last-child{{border-right:0;padding-right:0}}
  .cell .lab{{font:600 10px/1 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.11em;
             color:var(--mute);margin-bottom:9px}}
  .cell .v{{font:600 30px/1 Georgia,serif;letter-spacing:-.02em}}
  .cell .v em{{font-style:normal;font-size:12px;color:var(--mute);margin-left:3px;letter-spacing:0}}
  .cell .d{{font-size:11.5px;color:var(--mute);margin-top:7px}}

  /* Sections: ruled, not boxed. Square corners throughout. */
  .sec{{padding:34px 0;border-bottom:1px solid var(--rule)}}
  .sec .row{{display:block}}
  .sec .lab{{font:700 10.5px/1.5 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.14em;
            color:var(--accent);margin:0 0 10px}}
  .sec h2{{font:600 27px/1.2 Georgia,serif;letter-spacing:-.015em;margin:0 0 10px}}
  .sec p{{margin:0 0 14px;color:#3a3a3a;max-width:44em}}
  .sec .go{{display:inline-block;font:600 13px/1 system-ui,sans-serif;text-decoration:none;
           border-bottom:2px solid var(--ink);padding-bottom:4px}}
  .sec .go:hover{{color:var(--accent);border-bottom-color:var(--accent)}}
  .facts{{margin:16px 0 0;padding:0;list-style:none;font-size:14px;color:#3a3a3a}}
  .facts li{{padding:7px 0;border-bottom:1px solid #e8e8e8}}
  .facts li:last-child{{border-bottom:0}}
  .facts b{{font-weight:600;font-variant-numeric:tabular-nums}}

  .chart{{margin:26px 0 0;padding:0}}
  .chart .chead{{display:block;margin:0 0 12px;font:400 14px/1.5 system-ui,sans-serif;color:var(--mute)}}
  .chart .chead b{{display:block;font:600 19px/1.3 Georgia,serif;color:var(--ink);margin-bottom:4px;
                  letter-spacing:-.01em}}
  .chart .cfoot{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px;
                font:400 11.5px/1.5 system-ui,sans-serif;color:var(--mute);
                border-top:1px solid var(--rule);padding-top:8px;margin-top:4px}}
  .chart svg{{display:block;width:100%;height:200px}}
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
    .sec .row{{display:block}}
    .hero{{padding:38px 0 32px}}
  }}
  @media(max-width:520px){{
    /* Keep the 2x2. Four stacked rows pushed the numbers past a full screen. */
    .strip{{grid-template-columns:1fr 1fr}}
    .cell{{padding:14px 14px 14px 0}}
    .cell:nth-child(odd){{padding-right:16px}}
    .cell .v{{font-size:26px}}
        .hero h1{{font-size:clamp(28px,8vw,38px);max-width:none}}
    .hero .sub{{font-size:16.5px}}
    .sec h2{{font-size:22px}}
    .sec{{padding:30px 0}}
  }}
</style>
</head>
<body>


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
      <h2>Quote a load without guessing at the fuel.</h2>
      <p>A cross-border quote needs two numbers that agree: what diesel costs where you load, and
      what it costs where you deliver. Most carriers price one side and hope. This gives you both,
      converted to the same basis, on the day the source published it.</p>
      <ul class="facts">
        <li>{f'Cheapest fuel right now is <b>{cheap[0]} at {cheap[1]:.1f}&cent;/L</b>. If your return leg runs through it, that is where to fill.' if cheap else 'n/a'}</li>
        <li>{f'The {dear[0]} figure is <b>{dear[1]:.1f}&cent;/L</b>, {dear[1] - cheap[1]:.1f}&cent; above it. That gap is what a single tank can move.' if cheap and dear else ''}</li>
        <li>{f'Longest booth wait reporting is <b>{worst[1]} at {worst[0]} min</b>. Build the appointment around that one, not the average.' if worst else 'n/a'}</li>
        <li>Free, no account, no paywall. Every figure carries the date the source published it.</li>
      </ul>
      <a class="go" href="{DASH}/">See today&rsquo;s numbers</a>
    </div>
  </div></div>

  <div class="sec"><div class="row">
    <div class="lab">The writing</div>
    <div>
      <h2>Why the two numbers are not comparable as published.</h2>
      <p>Canada quotes diesel by the litre, the US by the gallon, and neither is a price you can
      compare until you convert both. That is the easy one. The harder ones are what the CRA asks
      before it calls your corporation a personal services business, and which IFTA filing mistakes
      trigger an audit. Written for the person running the truck.</p>
      <a class="go" href="/blog/">Read the pieces</a>
    </div>
  </div></div>

  <div class="sec"><div class="row">
    <div class="lab">The Brief</div>
    <div>
      <h2>One page a month, so your surcharge has a number behind it.</h2>
      <p>Built for US carriers running Ontario to Michigan or New York. What a tractor burns per
      1,000 km on each side, the spread to carry into a fuel surcharge, provincial prices where you
      fuel before the return leg, and the booth waits on your own crossings. <b>$249 a month.</b></p>
      <a class="go" href="{DASH}/report/">See what is in it</a>
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

    # Take only the page content and wrap it in gen_templates' own head() and foot(), so the header
    # and footer are byte-identical to every dashboard page and cannot drift again.
    import sys
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import gen_templates as G
    import re as _re
    import datetime as _dt

    m = _re.search(r"<body>(.*?)</body>", html, _re.S)
    body = m.group(1) if m else html
    # The page CSS is scoped under .home. Removing the old header took the wrapper with it, so every
    # .home .strip rule matched nothing and nm.css styled the whole page. Guarantee the wrapper here
    # rather than relying on the markup surviving a future edit.
    if 'class="home"' not in body:
        body = '<div class="home">' + body + "</div>"
    ld = ('{"@context":"https://schema.org","@type":"WebPage",'
          '"name":"Northern Mile Media",'
          f'"url":"{BRAND}"}}')
    html = (G.head("Northern Mile Media — Canadian and US diesel, border and rate data",
                   "Canadian provincial diesel next to US district diesel, live Canada-US border "
                   "wait times and the Bank of Canada rate. Free, from primary sources.",
                   "/", "/og.jpg", ld)
            + body + G.foot())
    # Page CSS goes in AFTER the shared stylesheet link so the home view can size its own blocks
    # without fighting nm.css, and without redeclaring the header or footer.
    html = html.replace("</head>", f"<style>{PAGE_CSS}</style></head>", 1)
    _now = _dt.datetime.now(_dt.timezone.utc)
    html = (html
            .replace("{{build_version}}", _now.strftime("%Y-%m-%d-%H%M"))
            .replace("{{updated_iso}}", _now.strftime("%Y-%m-%dT%H:%M:%SZ"))
            .replace("{{updated_at}}", _now.strftime("%Y-%m-%d %H:%M")))
    path = os.path.join(OUT, "home.html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  {path} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
