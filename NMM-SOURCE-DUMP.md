# Northern Mile Dashboard — Full Source Dump
## Generated 2026-08-05 for audit before rebuild

──────────────────────────────────────────

## 1. REPO LAYOUT

```
northern-mile-dashboard/
├── .backups/                          # Old cockpit-v3 templates + CSS/JS
├── .gitignore
├── .hermes/plans/                     # Old planning docs
├── LAUNCH_PLAN.md
├── NMM-BRIEF.md
├── assets/                            # HAND-MAINTAINED — shared across all pages
│   ├── app.js                         # Odometer, click handlers, copy link
│   ├── leaflet.css                    # Map library CSS
│   ├── leaflet.js                     # Map library JS
│   └── styles.css                     # Design tokens, all page styles
├── config/
│   └── thresholds.yaml                # Materiality thresholds (v1 provisional)
├── content/                           # HAND-MAINTAINED — blog, briefs, reference
│   ├── backlink-targets.md
│   ├── blog/                          # 4 markdown posts (agent-generated)
│   ├── claude-project-instructions-v3.md  # Current Claude instructions
│   ├── episodes/                      # Podcast transcripts
│   ├── linkedin-dm-tracker.md
│   └── newsletter-issue-002.md, -003.md
├── data/                              # RAW COLLECTOR OUTPUT + NORMALIZED
│   ├── border.json                    # Raw: CBSA crossings
│   ├── exchange.json                  # Raw: BoC FX rate + 30-day history
│   ├── fuel.json                      # Raw: NRCan RSS → provincial averages
│   ├── fuel.norm.json                 # Normalized: template variables
│   ├── home.norm.json                 # Normalized: homepage variables
│   ├── incidents.json                 # Raw: 511 road incidents
│   ├── market.json                    # Raw: GDP + market indicators
│   ├── news.json                      # Raw: headlines
│   ├── theft.json                     # Raw: cargo theft incidents
│   ├── distances.json                 # Static: city codes + distance matrix
│   ├── history/                       # CSV bloat — 171.9 repeated every 30 min
│   │   ├── fuel_diesel.csv
│   │   ├── fuel_gas.csv
│   │   ├── market_pulse.csv
│   │   └── usdcad.csv
│   └── nrcan_diesel.json              # Reference copy of NRCan data
├── scripts/                           # COLLECTORS + BUILD ENGINE
│   ├── build_templates.py             # Fill engine — renders templates → docs/
│   ├── build_seo_pages.py             # SEO helper pages
│   ├── build_fuel_page.py             # (legacy)
│   ├── chart_builder.py               # (unused)
│   ├── collect_border.py              # CBSA border scraper
│   ├── collect_nrcan_diesel.py        # NRCan RSS → fuel.json (72 cities)
│   ├── collector.py                   # Orchestrator — runs all collectors
│   ├── health_tracker.py              # Source health monitoring
│   ├── incidents.py                   # 511 road incident scraper
│   ├── market_pulse.py                # GDP + market indicators
│   ├── normalize.py                   # Raw JSON → template variables
│   ├── theft_incidents.py             # Theft tracker
│   └── build_dashboard.py.DEAD        # Old build script — decommissioned
├── templates/                         # HAND-MAINTAINED HTML templates
│   ├── index.template.html            # Homepage
│   ├── border-wait-times.template.html
│   ├── cargo-theft.template.html
│   ├── exchange-rate.template.html
│   ├── fuel-cost-calculator.template.html
│   ├── fuel-prices.template.html
│   ├── industry-news.template.html
│   ├── market-pulse.template.html
│   ├── methodology.template.html
│   └── road-incidents.template.html
├── deploy.sh                          # BUILD + DEPLOY → GitHub Pages
├── server.py                          # Local dev server (unused in prod)
├── start.sh                           # Legacy start script
└── docs/                              # GENERATED OUTPUT → GitHub Pages
    ├── index.html                     # Built from templates
    ├── assets/                        # Copied from assets/
    ├── v2/                            # Legacy build
    └── data/                          # Raw JSON endpoints served at
        ├── fuel.json                  #   dashboard.northernmilemedia.com/data/fuel.json
        ├── exchange.json              #   dashboard.northernmilemedia.com/data/exchange.json
        └── ...                        #   etc.
```

**Marked for rebuild:**
- `templates/` — all 10 HTML files (Claude rewrites design)
- `assets/` — CSS + JS (Claude rewrites design)
- `scripts/normalize.py` — hardcoded 165 baseline, no history, no delta computation
- `scripts/build_templates.py` — fill engine (may change with new template format)
- `data/history/` — CSV bloat, no real historical function

**Keep:**
- `scripts/collect_nrcan_diesel.py` — works, NRCan RSS → fuel.json
- `scripts/collect_border.py` — works, CBSA → border.json
- `scripts/collector.py` — orchestrator
- `deploy.sh` — works, every 30 min → GitHub Pages

──────────────────────────────────────────

## 2. BUILD AND DEPLOY

**deploy.sh** — runs every 30 min via cron (job ID: 1493dd117789)
```bash
#!/bin/bash
set -e
cd /home/hermes/northern-mile-dashboard

# 1. Collect fresh data
python3 scripts/collect_border.py
python3 scripts/collector.py && python3 scripts/collect_border.py && \
  python3 scripts/normalize.py && python3 scripts/build_templates.py

# 2. Health check — record status for each source
python3 -c "..."  # health_tracker checks each JSON file exists + has content

# 3. Copy assets to docs/
mkdir -p docs/v2 && cp -r assets docs/

# 4. Git commit + push to GitHub Pages
git add -A
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "(nothing to commit)"
git push origin master
```

**Deploy location:** `https://dashboard.northernmilemedia.com/` (GitHub Pages from `docs/` folder on branch `master`)

──────────────────────────────────────────

## 3. FUEL COLLECTOR

**scripts/collect_nrcan_diesel.py** (160 lines)

Flow:
1. Fetches NRCan RSS feed: `webfeed_e.cfm?priceYear=2026&productID=5&locationID=<72 IDs>`
2. Parses XML: `<title>` = city name, `<description>` = price in $/L
3. Groups cities by province (hardcoded CITY_PROVINCE dict — 72 cities → 12 provinces)
4. Computes provincial average (mean of all cities in province)
5. Computes national average (mean of all provincial averages)
6. Writes `fuel.json`: `{provinces: {CODE: {diesel, gasoline, trend, note}}, diesel_national_avg, source, updated}`

**Source label:** `"Kalibrate DPPS daily survey (used by NRCan for analysis)"` — **BUG: should be "NRCan weekly diesel survey (productID=5)"**

**City count:** 72 — but NRCan says ~70-77 cities. 12 "provinces" includes YT, NT (territories).

**National average calculation:**
```python
all_prices = [result[prov]["diesel"] for prov in result]
national_avg = round(sum(all_prices) / len(all_prices), 1)
```
Mean of provincial averages, not population-weighted. Direct mathematical mean across 12 units.

──────────────────────────────────────────

## 4. HOMEPAGE TEMPLATE

**templates/index.template.html** (131 lines)

Key template variables (filled by normalize.py → build_templates.py):

Fuel section (line 31):
```html
<div class="odo" data-value="{{fuel.national_diesel}}" data-unit="c/L"></div>
<div class="gs">{{fuel.change_7d}} / 7d</div>
```
`change_7d` is hardcoded to `"—"` — no delta computation exists.

Market pulse section (line 69-72):
```html
<!--LOOP:market--><div class="ind">...</div><!--/LOOP:market-->
```
Populated from `market_pulse.py` → indicators include GDP, "Diesel vs baseline" (hardcoded 165 baseline), BC/AB spread, USD/CAD vs 1.35.

Cargo theft section (line 74):
```html
<span class="k">reference · last 90 days</span>
```
The "90 days" is a cosmetic label only — no date filtering logic.

**Hardcoded values found in the template pipeline:**
- Line 106: `var diesel = {{fuel.national_diesel}};` — passed to inline fuel calculator
- Line 67: `KM 172` — decorative divider
- market_pulse.py line 87: `baseline = 165` — hardcoded diesel baseline for comparison

──────────────────────────────────────────

## 5. CURRENT DATA SHAPE

**Raw fuel.json:**
```json
{
  "provinces": {
    "AB": {"diesel": 200.3, "gasoline": null, "trend": "flat",
           "note": "Kalibrate DPPS survey — 6 locations"},
    "BC": {"diesel": 233.2, ...},
    ...
  },
  "diesel_national_avg": 224.8,
  "gasoline_national_avg": null,
  "updated": "2026-08-05T17:59:58+00:00",
  "source": "Kalibrate DPPS daily survey (used by NRCan for analysis)",
  "location_count": 72
}
```
12 provinces/territories: BC, AB, SK, MB, ON, QC, NB, NS, PE, NL, YT, NT

**Normalized fuel.norm.json (what templates receive):**
```json
{
  "fuel": {
    "national_diesel": "224.8",
    "series": "NMDI",
    "national_nmdi": "224.8",
    "change_7d": "—",
    "change_7d_band": "noise",
    "low_code": "AB", "low": "200.3",
    "high_code": "QC", "high": "253.6",
    "spread": "53.3",
    "fuel_top": [6 province entries with code/name/price/change/rowclass]
  },
  "fx": {"usd_cad": "1.4162", "direction": "weaker CAD", "change": "+0.0142"},
  "provinces": [10 province entries],
  "border_fuel": [cross-border fuel cost comparison],
  "tax": [tax breakdown per province],
  "ifta": [IFTA reference data],
  "updated_at": "2026-08-05 21:30"
}
```

Data flows: Collector → raw JSON → normalize.py → .norm.json → build_templates.py → HTML → GitHub Pages

No intermediate caching. Each 30-min build is a fresh run from collectors to deploy.

──────────────────────────────────────────

## 6. THREE GREPS

**grep -rn "165" — hardcoded diesel baseline**

```
scripts/market_pulse.py:86:    # Compare to a rough baseline of 165 cents
scripts/market_pulse.py:87:    baseline = 165
scripts/market_pulse.py:94:    detail = f"{fuel_pct:+.1f}% vs 165¢ baseline"
```
The 165¢ baseline appears on the Market Pulse page as "Diesel vs baseline" indicator. It's a hardcoded constant with no source or methodology. This is the single most important hardcoded value to fix in the rebuild — it's displayed prominently to users as a comparison point.

**grep -rn "90 days" — cosmetic label only**

```
templates/index.template.html:74:    <div class="mod">...<span class="k">reference · last 90 days</span>
templates/cargo-theft.template.html:24:    <span>Public bulletins · last 90 days</span>
```
No date filtering logic exists. The theft page shows all 8 hand-curated incidents regardless of date. The "90 days" text is purely cosmetic — a design element, not a functional filter.

**grep -rn "172" — decorative elements**

```
templates/index.template.html:67:    <div class="km"><span class="post">KM 172</span>
templates/fuel-prices.template.html:62:    <div class="km"><span class="post">KM 172</span>
```
"KM 172" is a visual divider element used on the page. No operational significance. Also appears in old chart demo data as a diesel price value.

──────────────────────────────────────────

## 7. PERSISTENCE CHECK

**No database. No persistent storage. Each build is stateless.**

The `data/history/` directory contains four CSV files:
- `fuel_diesel.csv` — 171.9 repeated thousands of times (old hardcoded era)
- `fuel_gas.csv` — same
- `market_pulse.csv` — GDP + spread values, same repetition pattern
- `usdcad.csv` — FX rate snapshots from old era

These CSVs are append-only bloat — never read, never used for computation. All values are from the pre-NRCan era (171.9 = hardcoded diesel price before the collector was built).

**What's possible today:**
- ❌ 7-day diesel change — `change_7d` is hardcoded to `"—"` in normalize.py
- ❌ 30-day comparison — not implemented
- ❌ Year-over-year — not implemented
- ❌ Percentile computation — not implemented
- ❌ Border delta — feed is current-state only, no history snapshots stored
- ✅ Current values only — what you see is what you get, no past context

**What the rebuild needs:**
- Daily/weekly snapshots of all series to enable deltas
- The Bank of Canada Valet API can backfill FX history to 2017 (2,392 daily closes)
- The NRCan RSS feed can only return current values — history must be collected over time
- Border needs its own snapshot store (CBSA feed has no history)

──────────────────────────────────────────

## END OF DUMP
