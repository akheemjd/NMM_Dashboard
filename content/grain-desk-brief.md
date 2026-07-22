# Grain Desk — Build Brief
**North American agriculture dashboard · graindesk.com** · v1.0

## What it is

One free dashboard for North American grain farmers, traders, and ag supply chain. Commodity prices, fertilizer, freight, FX, weather, export data — all in one tab. Same playbook as Northern Mile Media but scaled to the continent.

## Brand

**Name:** Grain Desk  
**Tagline:** The board for North American grain  
**Domain:** graindesk.com  
**GitHub:** akheemjd/grain-desk  
**Tone:** Industry-standard. No farmer cosplay, no ag jargon overkill. Write like a Bloomberg terminal trimmed down to what a trader actually checks. Short sentences. Data-first. No emojis, no exclamation marks, no "friendly" voice.

## Audience

- **Primary:** Grain farmers (corn, soy, wheat, canola) — US Midwest + Canadian Prairies
- **Secondary:** Grain traders, elevator operators, commodity analysts
- **Tertiary:** Ag lenders, input suppliers, logistics coordinators

They're checking prices at 5am before the markets open. They want numbers, not stories.

## Data modules (v1)

Every module sources free public data. No paid APIs.

| # | Module | Data | Source |
|---|--------|------|--------|
| 1 | **Grain Prices** | Corn, soybeans, wheat, canola, oats — cash + futures | CBOT/CME, ICE |
| 2 | **Fertilizer Index** | Urea, DAP, potash, anhydrous — regional | USDA, StatsCan |
| 3 | **Fuel & FX** | US diesel, CAD diesel, USD/CAD | EIA, Bank of Canada |
| 4 | **Basis by Region** | Cash – futures spread per crop/region | Calculated |
| 5 | **Grain Freight** | Rail rates, barge rates, truck rates | USDA AMS, ag transport |
| 6 | **Export Pace** | Weekly grain inspections, export sales | USDA FAS |
| 7 | **Weather & GDD** | Growing degree days, precip, drought monitor | Open-Meteo, NOAA |
| 8 | **Market Pulse** | Stock-to-use ratios, planted acreage, WASDE highlights | USDA |

## Design direction

Claude will design the full visual system. Here are the constraints:

- **Dark background** — terminal/trading desk feel. Not highway-signage (NMM). Not cockpit (v3). Think: grain elevator control room at night. Deep brown-black, warm amber accents.
- **One font for data** — monospace for all numbers, tables, prices. A display font for headlines only.
- **Heatmap colors** for regional data — green (low price / surplus) to red (high price / shortage)
- **No charts on the main dashboard** — just the numbers. Charts go on dedicated pages (same architecture as NMM).
- **Mobile = desktop quality** — every module works on a phone in a cab at 4am

## Architecture (same as NMM)

- **Template kit** — `/templates/*.template.html` with `{{tokens}}`, `LOOP`, `OPTIONAL`, `IF`
- **Shared assets** — `assets/styles.css` + `assets/app.js`
- **Fill engine** — Python script reads templates + `/data/*.json` → writes `/docs/*/index.html`
- **30-minute pipeline** — collect → normalize → fill → commit → GitHub Pages
- **Per-feed failure isolation** — one dead feed never blanks the board
- **.nojekyll everywhere** — static HTML, no Jekyll processing

## Pages (all from templates)

| Template | Route | Content |
|----------|-------|---------|
| index | `/` | Dashboard home — all 8 modules |
| grain-prices | `/grain-prices/` | Full price tables, futures, cash, charts |
| fertilizer | `/fertilizer/` | Regional fertilizer index |
| fuel-fx | `/fuel-fx/` | US + CAD diesel, exchange rate |
| basis | `/basis/` | Regional basis by crop |
| freight | `/freight/` | Rail, barge, truck rates |
| exports | `/exports/` | Weekly inspections, sales |
| weather | `/weather/` | GDD, precip, drought maps |
| market-pulse | `/market-pulse/` | WASDE highlights, ratios, acreage |

## Monetization (exact same model as NMM)

- Dashboard free forever — top of funnel
- Newsletter: Grain Desk Weekly — one sponsor, 4 placements/month at $2,500
- Revenue starts at 500 subscribers
- Zero until then

## What Claude should deliver

1. **Design tokens** — colors, fonts, spacing as a CSS :root block
2. **Component library** — hero card, metric card, data table, status strip, nav, footer, CTA
3. **9 template files** — fully designed HTML with `{{tokens}}`, `LOOP`, `OPTIONAL`, `IF` markers
4. **Shared styles.css** — the complete design system
5. **Shared app.js** — odometer, maps (if used), interactive elements
6. **Data contract examples** — one JSON file per module showing the exact shape the templates expect

## What Hermes will do

- Build all data collectors (free APIs only)
- Build the normalize pipeline
- Build the fill engine
- Wire the 30-minute cron
- Handle SEO, sitemaps, Google indexing
- Deploy to GitHub Pages
- Build newsletter + LinkedIn + social strategy
- Handle all engineering and infrastructure

## Reference

- Northern Mile Media: dashboard.northernmilemedia.com
- Same architecture, different industry. Claude: look at `/assets/styles.css` and `/templates/` for the NMM template pattern — replicate the structure, redesign the visuals.
