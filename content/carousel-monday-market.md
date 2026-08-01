# Monday Carousel Template — Market/FX

Build a 5-slide LinkedIn carousel PDF for Northern Mile Media. Export as 1080×1080 px square slides, PDF format. Dark theme.

## Design System
Background: #0B0D11 (deep blue-black)
Primary text: #F2F4F7 (near-white)
Secondary text: #A8B2BE (gray)
Accent: #1E9E66 (green)
Red: #E5484D
Font: system sans-serif (no web fonts needed)

## Brand
Northern Mile Media — Canadian trucking dashboard and newsletter. Voice: dispatcher-analyst. Data-first, no fluff.

## Data (pull live from dashboard before building)
Fetch: https://dashboard.northernmilemedia.com/data/exchange.json
→ current rate, change, 30-day high from history array
Fetch: https://dashboard.northernmilemedia.com/data/fuel.json
→ diesel national avg, BC and AB diesel

## Slide Content

### Slide 1 — Cover
Logo: "NORTHERN MILE" top left, green. Slide number: "1/5" top right, gray.
Headline: "What the loonie did this week" (or adapt to current trend)
Subtitle: One sentence on why this matters for cross-border trucking
Footer: Today's date

### Slide 2 — The Number
Big number centered: current USD/CAD rate in green, 160px+
Subtitle: "1 US dollar buys [rate] Canadian dollars today"
Tag: "DOWN/UP X¢ this week" in green or red badge
Footer: "Bank of Canada · updated every 30 min"

### Slide 3 — 30-Day Trend
Headline: "30-day trend"
Visual: down/up arrow in red or green
Line: "[30-day high] → [current]" in green
Three stat boxes:
- X.X% (green/red) / "30-day change"
- [30-day high] / "30-day high"
- [current] / "Current"
Footer: Brief trend observation

### Slide 4 — Impact
Headline: "What this means for your lanes"
Three bullet sections:
- Red down arrow: Cross-border loads pay less/more in CAD. Show actual dollar difference on a standard US load.
- Green up arrow: Equipment and parts cost less/more in CAD terms.
- Gray dash: Diesel priced in CAD is unaffected. Current BC-AB spread.
Footer: "Source: Northern Mile dashboard — live data"

### Slide 5 — CTA
Headline: "We track fuel, border, FX and theft every week. Free. No signup."
URL in green: "northernmilemedia.com"
Subtitle: "Get the Wednesday Snapshot"
Footer: "dashboard.northernmilemedia.com — free Canadian trucking data"

## Rules
No emojis, no AI vocabulary, no fluff. Clean typography, strong hierarchy. Dark theme throughout. Each slide = one idea. 5 pages, 1080×1080 each.
