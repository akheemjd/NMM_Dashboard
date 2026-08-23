# NMM World Data Model — Design

> North star: the definitive **free, citable, cross-border diesel-cost index**.
> One methodology applied to every country that publishes a government fuel
> survey, normalized to one comparable number, dated + sourced on every figure.
> The **World Diesel Index (WDI)** is the citable flagship; national indexes are
> its building blocks.

---

## 1. What we win (and what we don't)

- **We win:** the free, citable, cross-border fuel-cost index. Public data,
  aggregated with methodology + provenance. Nobody owns this today.
- **We do not win:** proprietary freight rates / load boards / ELD market data.
  That's a capital game (FreightWaves, DAT). Not our lane.

## 2. Core abstraction — the "Market"

A **market** is one country (or region) with:

| Field | Meaning | Example |
|---|---|---|
| fuel source | authoritative government survey | NRCan weekly, EIA weekly |
| currency | → FX to the base (USD) | CAD, EUR, GBP |
| granularity | national / province / state / city | province (CA), national (US) |
| cadence | how often the survey prints | weekly (most) |
| optional | crossing/port data, macro signals | CBSA border, StatsCan GDP |

## 3. The normalized fuel schema (the one contract)

Every collector emits this shape. `normalize.py` consumes **only** this — never a
source-specific field. This is what makes "add a country" a one-collector job.

```python
{
  "market": "CA",             # ISO-3166 alpha-2
  "granularity": "province",  # national | province | state | city
  "name": "Ontario",          # sub-region name (empty if national)
  "diesel": 228.4,            # native price
  "unit": "cpl",              # cpl | usd_gal | eur_l | gbp_l | ...
  "currency": "CAD",
  "print_date": "2026-08-18",
  "source": "Natural Resources Canada weekly diesel survey",
  "source_url": "https://...",
}
```

## 4. Layers

1. **Collector layer** — one script per market (`collect_<market>_diesel.py`),
   fail-isolated, emits the normalized schema. A `markets.json` registry lists
   active markets + their collector + currency + unit.
2. **Normalize layer** — converts every price to the **base (USD per litre)**,
   computes means, applies per-market staleness guards. Country-agnostic.
3. **Index layer** — the same unweighted-mean methodology at every level:
   - **national** index (NMDI = mean of 10 provinces; EIA = US national; EU per-country)
   - **regional** index (NADI = mean of CA + US; EDI = mean of 27 EU states)
   - **world** index (WDI = mean of all active national indexes)
4. **Page layer** — programmatic pages per country/region/city, driven by the
   registry (extend `build_us_pages.py` / `build_city_pages.py`).
5. **FX layer** — one `fx.json`: every currency → USD. Central banks, all free.

## 5. Unit + currency normalization

- 1 US gallon = 3.785411784 L; 1 L = 0.264172052 US gallon.
- `price_usd_per_l = diesel * unit_factor * currency_to_usd`.
- **WDI published in USD/litre** (global comparable); national indexes also shown
  in native units.

## 6. The multi-agent system (3 agents, file handoff)

Same split that already works (`default`=data, `writer`=content). Deterministic
code runs on cron — agents do the reasoning, not the fetching.

| Agent | Role | Created |
|---|---|---|
| **`default`** (operator) | Build collectors, maintain normalize/index, deploy, fix breakage. Runs deterministic scripts; agents don't fetch. | exists |
| **`writer`** (content) | Regional + weekly briefs, newsletter, world-index commentary. Never computes a number. | exists |
| **`research`** (data scout) | For each new market: find the authoritative free source, **verify it** (fetch + parse + confirm schema), write a `collector-spec` markdown, hand off to `default`. | **Phase 2** (EU) |

Handoff is file-based, matching the existing default→writer pattern:
`research` → `design/collector-specs/<market>.md` → `default` → `collect_<market>_diesel.py`.

Optional 4th — **`growth`** (outreach): deferred, manual for now.

**Why `research` is the new bottleneck (not code):** at world scale the hard part
is *finding + verifying 30+ country sources*, each with a different format and
URL. That's exactly what an isolated agent with web tools does well. It's created
in Phase 2 because that's the first moment it's genuinely required.

## 7. Design rules (so we never rebuild)

1. **No country is hardcoded in `normalize.py`** — everything keyed by `market`.
2. **Every collector emits the normalized schema**, fail-isolated.
3. **The index is a pure function of the market list** — add a market = one
   registry entry + one collector.
4. **Staleness + correction guards are per-market** (each survey has its own cadence).

## 8. Phases

| Phase | Scope | Leverage |
|---|---|---|
| 0 | Refactor to the market-driven core (country-agnostic) | the "don't rebuild" step |
| 1 | North America first — NA works, US-weighted distribution | committed |
| 2 | EU — one collector = 27 markets | highest single step |
| 3 | UK / AU / NZ / JP / MX — one-off collectors | long tail |
| 4 | World Diesel Index — the flagship citable asset | the brand |
| 5 | Maintenance (collector watchdog) + distribution engine | durability |
