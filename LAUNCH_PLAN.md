# Northern Mile Media — Launch Plan

## Target: Live by Wednesday

---

## Phase 1: Dashboard Goes Permanent (Today)

### 1.1 Set up GitHub Pages
- [ ] Create GitHub repo `northernmilemedia/northern-mile-dashboard`
- [ ] Push dashboard files to repo
- [ ] Enable GitHub Pages in repo settings
- [ ] Live at: `northernmilemedia.github.io/northern-mile-dashboard`
- [ ] Test on mobile

### 1.2 Data pipeline
- [ ] Set up cron job to auto-commit + push data JSON every 30 min
- [ ] Verify data updates propagate to GitHub Pages (~1-2 min delay)

### 1.3 Domain prep (for Wednesday)
- [ ] Document the DNS setup: CNAME `dashboard.northernmilemedia.com` → `northernmilemedia.github.io`
- [ ] Document Ghost DNS setup: A record `northernmilemedia.com` → Ghost IP

---

## Phase 2: Content Pipeline (Today-Tuesday)

### 2.1 Blog content — 3 launch posts

| Post | Topic | Status |
|------|-------|--------|
| 1 | "Canadian Diesel Prices by Province — July 2026" | Draft |
| 2 | "What the Weak Loonie Means for Cross-Border Freight" | Draft |
| 3 | "The Dashboard Canadian Trucking Never Had" (launch announcement) | Draft |

Each post:
- 400-600 words
- Embed 1-2 branded SVG charts
- Link to dashboard
- SEO-optimized title + description

### 2.2 LinkedIn — 5 daily posts for launch week

| Day | Post |
|-----|------|
| Mon | "We built a free dashboard. Here's why." |
| Tue | Fuel prices chart + "Know what diesel costs in your province today." |
| Wed | "CAD at 1.38. Here's what it means." |
| Thu | Road incidents map — "This is live. Right now." |
| Fri | "One week. X visitors. What we learned." |

### 2.3 Newsletter — Launch edition

Message: "We built a live dashboard for Canadian trucking. Free. No signup. No ads. Check it out."

---

## Phase 3: Ghost Setup (Wednesday)

### 3.1 Ghost configuration
- [ ] Install Ghost theme (Casper is fine for launch)
- [ ] Set up home page: blog feed
- [ ] Create navigation: Home, Dashboard, About
- [ ] Configure newsletter settings
- [ ] Add Google Analytics ID
- [ ] Set up subscriber form on every post

### 3.2 Duck the dashboard
- [ ] Add DNS CNAME record for `dashboard.northernmilemedia.com`
- [ ] Verify dashboard loads on custom domain
- [ ] Add link in Ghost navigation

### 3.3 Launch content
- [ ] Publish 3 pre-written blog posts
- [ ] Send launch newsletter
- [ ] Post on LinkedIn + Facebook groups
- [ ] Cross-link dashboard ←→ blog

---

## Phase 4: Growth (Week 2+)

- [ ] Post to 10+ Canadian trucking Facebook groups
- [ ] Daily LinkedIn posts (I draft, you post)
- [ ] 1 blog post/week
- [ ] Bi-weekly newsletter
- [ ] Track traffic via GitHub Pages analytics + Ghost analytics

---

## Decisions needed

1. **Domain** — do you already own `northernmilemedia.com`?
2. **GitHub account** — do you have one? Need it for Pages.
3. **Ghost plan** — Starter ($9/mo) or Creator ($25/mo)? Creator enables custom themes and more integrations.
4. **Blog name** — Northern Mile Media? Northern Mile Blog?
