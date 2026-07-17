# Northern Mile Media — Product & Brand Brief
## For Claude: review this and suggest updates. Hermes will execute them.

---

## 1. Brand

**Name:** Northern Mile Media
**Tagline:** For the people who keep Canada moving.
**Positioning:** Canada's live data dashboard for the trucking industry. No paywalls. No signup. Free forever.

**Voice:** Casual, confident, understated. Think The Economist meets Canadian trucking. No dashes, no emojis, no AI vocabulary (delve, pivotal, landscape, crucial, showcase). Short sentences. Active voice. Dry humor OK. Canada-wide perspective.

**Visual identity:** Dark theme derived from highway signage. Dark asphalt background (#15171A), dark grey cards (#1E2227), white text (#E8EAEC). Green (#1F6B4A) for positive states — same green as highway gantry signs. Amber (#F2A900) for warnings. Red (#D93A34) for closures/incidents. Barlow Condensed for numbers, Inter for body, IBM Plex Mono for data tables.

**URLs:**
- Dashboard: https://dashboard.northernmilemedia.com
- Blog: https://northernmilemedia.com (Ghost Pro, $9/mo)

**Social:**
- LinkedIn page: linkedin.com/company/109885620/ — daily posts at 5pm
- X: x.com/northernmile

---

## 2. Audience

Fleet operators, dispatchers, and owner-operators in Canadian trucking. Often checking data on a phone, in a cab, in daylight or at night. They need: diesel prices, border crossing status, road incidents, exchange rates. In under five seconds.

---

## 3. Dashboard Modules (8 total)

### Layout
12-column CSS grid. Desktop layout:

| Position | Module | Size |
|----------|--------|------|
| Row 1, full | Fuel Prices | Hero (12) |
| Row 2, left | Border Crossings | Wide (8) |
| Row 2, right | USD / CAD | Compact (4) |
| Row 3, left | Road Incidents | Tall (8, 2 rows) |
| Row 3, right | Fuel Cost Calculator | Standard (4) |
| Row 4, left | Market Pulse | Standard (4) |
| Row 5, left | Industry Headlines | Wide (8) |
| Row 5, right | Cargo Theft Watch | Standard (4) |

Mobile: all stack to full width at 900px.

### Data sources (all free, all $0)
- Fuel prices: public surveys
- Exchange rates: Bank of Canada daily close
- Border crossing status: time-of-day heuristics + CBSA data
- Road incidents: Ontario 511 + BC DriveBC open data
- Cargo theft: industry reports + TAPA
- Market pulse: BLS + EIA for US, public data for Canada
- Headlines: RSS feeds from Truck News, Trucking Info, The Trucker

### Update frequency
Every 30 minutes. Auto-collector script runs on cron, pushes to GitHub Pages.

### Current features per module

**Fuel Prices (HERO):** National average diesel price at top left, province-by-province list on right. Toggle between Diesel and Gas. Day-over-day delta pill. Cards have skeleton loading states.

**Border Crossings:** 9 major Canada-US crossings. Live status (Clear/Moderate/Heavy), delay times, CVSA blitz date calendar.

**USD / CAD:** Current rate, daily change direction, one-line impact text. No chart (removed per design brief — audience wants the number, not a sparkline).

**Road Incidents:** Leaflet map with OpenStreetMap tiles. Points on map + scrollable side list. Click list item to fly to location.

**Fuel Cost Calculator:** Pick two cities → enter L/100km → see total fuel cost. Uses distance data and live fuel prices.

**Market Pulse:** 5 economic indicators (unemployment, wages, diesel PPI, national avg, coast spread). Each shows value + trend arrow + what-it-means insight.

**Industry Headlines:** Latest 15 articles from Canadian trucking news sources. Source label + category pill + timestamp.

**Cargo Theft Watch:** Leaflet map with hotspots + incident markers. Side panel lists recent incidents, risk hotspots, top targeted commodities.

---

## 4. Content Systems

### LinkedIn
- **Page post:** Auto-generated daily at 5pm via cron. Format rotation: Mon Quick Hit, Tue Conversation, Wed Data Story, Thu Industry Take, Fri Behind It.
- **Personal repost:** Akheem reposts from personal profile with 1-2 lines of fresh context. Posts screenshots of dashboard modules.
- **Rules:** Hook in first line, one idea, link in first comment only, 3-5 hashtags. No external source attribution.

### LinkedIn Groups
- **Transportation Network for Freight, Brokers, Supply Chain:** Posts screenshots with professional context. 2-3 lines. Link in comments.
- **Facebook Group — Canadian Truckers (47K members):** Casual intro, personal tone. Introduce Akheem and the dashboard naturally. Link in comments.

### Ghost Blog
- **Schedule:** 1 post/week on Wednesdays (alongside newsletter).
- **Rotation:** Week 1 fuel prices, Week 2 exchange rate, Week 3 border/operational, Week 4 market trend.
- **Format:** 400-500 words, data-heavy, no external source citations. All data from own dashboard.
- **Files organized by episode:** content/episodes/blog/001/post.md, content/episodes/blog/001/chart.png

### Newsletter (Wednesday Fuel & Freight Snapshot)
- Auto-generated every Tuesday at 7pm. Delivered to Ghost subscribers Wednesday morning.

---

## 5. Technical Infrastructure

- **Hosting:** GitHub Pages (akheemjd/NMM_Dashboard, master branch, docs/ folder)
- **Custom domain:** dashboard.northernmilemedia.com
- **Generator:** Python script at ~/northern-mile-dashboard/scripts/build_dashboard.py
- **Data collector:** ~/northern-mile-dashboard/scripts/collector.py (runs every 30 min via cron)
- **Cron jobs:** Dashboard deploy, LinkedIn posting, newsletter generation
- **Maps:** Leaflet, OpenStreetMap tiles
- **Signup:** Ghost embed at bottom of dashboard
- **Analytics:** Google Analytics G-NDXR7ERL80

---

## 6. What We Deliberately Removed

- Charts/sparklines — audience wants the number, not decoration
- Job board — user declined multiple times
- "About" / "Home" nav links — removed from dashboard header
- External source citing in content — never reference TruckNews, DAT, etc. by name
- Ghost signup at top of page — buried it at bottom only
- Haul Analytics (US brand) — PAUSED. Akheem said "I won't have time for it right now"

---

## 7. Revenue Strategy

Sponsorships: $500-2,500/mo per module. Target: $10K+/mo. Invisible sponsor slots built into every module, activated via data/sponsors.json. Sponsorship outreach: Akheem handles sales. Newsletter and blog support the sponsorship pipeline.

---

## 8. Owner's Preferences

- Akheem runs Northern Mile. Hates complexity. Kills ideas fast.
- Wants practical, simple solutions. Prefers fewer features that work perfectly.
- Generates images himself using Claude and Gemini — I provide prompts.
- Head of Ops for Northern Mile. I run content, dashboard, analytics autonomously.
- "It's your job to keep me on track."
- Sudo password for this PC: 2544
