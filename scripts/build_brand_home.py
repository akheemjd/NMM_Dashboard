"""Build www.northernmilemedia.com/ - the brand home.

Why this page exists: until now "www" redirecting to /blog/ meant the blog WAS the front door, and
the dashboard's logo pointed at the dashboard's own chooser. So clicking a masthead anywhere took the
reader back to the half of the site they were already in. That reads as a dead link, and it is
unfixable by changing the link alone - the brand had no home for it to point at.

One page, three doors: Data, Writing, The Brief. With the live diesel figure on both sides so a
visitor sees the product before they click, rather than a brochure promising one.

Reads data/fuel.norm.json and data/eia_diesel.json: the same normalised files the dashboard and the
paid report use, so this page cannot drift from them.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")
BRAND = "https://www.northernmilemedia.com/"


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


def build():
    fuel = load("fuel.norm.json")
    eia = load("eia_diesel.json")
    fb = fuel.get("fuel") if isinstance(fuel.get("fuel"), dict) else {}
    ca = num(fb.get("national_diesel"))
    ca_date = fb.get("print_date") or "n/a"
    us = num(eia.get("us_national_usd_gal"))
    us_date = eia.get("date") or "n/a"

    ca_html = f"{ca:.1f}<em>¢/L</em>" if ca else "n/a"
    us_html = f"{us:.3f}<em>$/gal</em>" if us else "n/a"

    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="/assets/favicon.ico" sizes="any">
<title>Northern Mile Media — North American trucking data, cited and dated</title>
<meta name="description" content="Free Canadian and US diesel prices, border wait times and exchange rates for North American trucking, from primary sources. Plus the writing that explains what the numbers mean.">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{BRAND}">
<meta property="og:title" content="Northern Mile Media">
<meta property="og:description" content="North American trucking data, cited and dated. Free diesel, border and rate data, plus the writing that explains it.">
<meta property="og:type" content="website">
<meta property="og:url" content="{BRAND}">
<meta property="og:image" content="{BRAND}og.jpg">
<link rel="stylesheet" href="/assets/nm.css">
<style>
  body{{background:#faf9f7}}
  .home{{max-width:1000px;margin:0 auto;padding:0 22px}}
  .mast{{padding:64px 0 40px;border-bottom:2px solid #1a1a1a}}
  .mast .kick{{text-transform:uppercase;letter-spacing:.14em;font-size:11px;color:#0a5c3b;font-weight:700}}
  .mast h1{{font:600 clamp(38px,7vw,68px)/1.04 Georgia,serif;letter-spacing:-.025em;margin:14px 0 16px;max-width:16em}}
  .mast p{{font-size:19px;line-height:1.55;color:#333;max-width:34em;margin:0}}
  .doors{{display:grid;gap:0;margin:0;padding:0;list-style:none}}
  .door{{display:block;text-decoration:none;color:inherit;padding:34px 0;border-bottom:1px solid #d8d8d8}}
  .door:hover{{background:#f4f2ee}}
  .door .n{{text-transform:uppercase;letter-spacing:.12em;font-size:10.5px;color:#0a5c3b;font-weight:700}}
  .door h2{{font:600 30px/1.2 Georgia,serif;margin:8px 0 6px;letter-spacing:-.015em}}
  .door p{{margin:0;color:#444;font-size:15px;line-height:1.55;max-width:46em}}
  .door .fig{{font:600 26px/1 Georgia,serif;margin:10px 0 0;color:#1a1a1a}}
  .door .fig em{{font-style:normal;font-size:13px;color:#666;margin-left:3px}}
  .door .go{{display:inline-block;margin-top:12px;font:600 13px/1 system-ui,sans-serif;border-bottom:2px solid #1a1a1a;padding-bottom:3px}}
  .foot{{padding:34px 0 60px;font-size:12px;color:#666;line-height:1.6}}
  .foot a{{color:#333}}
  @media(max-width:640px){{.mast{{padding:40px 0 28px}}.door{{padding:26px 0}}.door h2{{font-size:24px}}}}
</style>
</head>
<body>
<div class="home">

  <div class="mast">
    <div class="kick">Northern Mile Media</div>
    <h1>North American trucking data, cited and dated.</h1>
    <p>Every figure names its source and the day it was observed. Free to read, no account. Plus the
    writing that explains what the numbers mean for a carrier.</p>
  </div>

  <ul class="doors">
    <li><a class="door" href="https://dashboard.northernmilemedia.com/">
      <span class="n">Data</span>
      <h2>Diesel, border waits and rates</h2>
      <p>Canadian provincial diesel from the NRCan weekly survey. US diesel by EIA district. Live
      booth waits at every Canada-US crossing. The Bank of Canada rate. All free.</p>
      <div class="fig">{ca_html} Canada &nbsp;·&nbsp; {us_html} US</div>
      <span class="go">Open the dashboard</span>
    </a></li>

    <li><a class="door" href="/blog/">
      <span class="n">Writing</span>
      <h2>What the numbers mean</h2>
      <p>Cross-border fuel, IFTA filing, CRA audits, detention, customs paperwork. Written for the
      person running the truck, not the person writing about it.</p>
      <span class="go">Read the writing</span>
    </a></li>

    <li><a class="door" href="https://dashboard.northernmilemedia.com/report/">
      <span class="n">The Brief</span>
      <h2>The Cross-Border Cost Brief</h2>
      <p>For US carriers running Ontario to Michigan or New York: what a tractor burns per 1,000 km
      on each side, the spread to quote against, and your own crossings. Monthly, $249.</p>
      <span class="go">See the report</span>
    </a></li>
  </ul>

  <div class="foot">
    Northern Mile Media publishes North American trucking data from primary sources: Natural Resources
    Canada, US Energy Information Administration, Bank of Canada, Canada Border Services Agency, US
    Customs and Border Protection, and IFTA Inc. Where a source has not published, we say so rather
    than carrying the old number forward.<br><br>
    <a href="https://dashboard.northernmilemedia.com/methodology/nmdi/">Methodology</a> &nbsp;·&nbsp;
    <a href="https://dashboard.northernmilemedia.com/contact/">Contact</a> &nbsp;·&nbsp;
    <a href="https://dashboard.northernmilemedia.com/press/">Press</a>
    <br><br>
    Diesel print {ca_date}. US diesel week ending {us_date}. &copy; 2026 Northern Mile Media.
  </div>

</div>
</body>
</html>"""


def main():
    html = build()
    path = os.path.join(OUT, "home.html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print(f"  docs/home.html ({len(html):,} bytes) - copied to the www repo by build_www.py")


if __name__ == "__main__":
    main()
