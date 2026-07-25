# The Bulletin — Design Exploration Plan

> **For Hermes:** Plan only. Do not execute. This is a design direction exploration. The user wants to evaluate before committing.

**Goal:** Redesign the Northern Mile dashboard with a truck stop bulletin-board aesthetic — industrial, high-contrast, black + yellow, built for legibility.

**Current design backed up at:** `.backups/cockpit-v3/`

---

## Direction: The Bulletin

Think: truck stop corkboard. Safety-yellow headlines. Bold weights. One color does all the work. Nothing decorative. Everything earns its space. Built for a driver glancing at a phone in a cab.

### Visual DNA

| Element | Cockpit (current) | Bulletin (proposed) |
|---------|-------------------|---------------------|
| Background | Blue-black #0B0D11 | Flat black #0D0D0D |
| Primary color | Green | Safety yellow #FFD600 |
| Secondary | Amber + Red | Black + white only |
| Typography | Saira + Inter + Mono | One display font + one mono |
| Gradients | Radial green glow | None — flat, hard edges |
| Cards | Rounded, raised | Sharp, bordered |
| Status | Green/Amber/Red lights | Yellow = attention, nothing else |
| Energy | Instrument cluster | Corkboard / dispatch board |

### Design Tokens (draft)

```css
:root {
  --bg: #0D0D0D;
  --surface: #141414;
  --surface-2: #1A1A1A;
  --border: #2A2A2A;
  --hair: #1F1F1F;
  
  --ink: #FFFFFF;
  --ink-2: #CCCCCC;
  --ink-3: #777777;
  
  --yellow: #FFD600;
  --yellow-dim: #3D3200;
  --red: #FF3B30;
  
  --rc: 0px;  /* hard edges — no rounding */
}
```

### Typography (draft)

- **Display:** Bebas Neue or Industry — condensed, bold, uppercase. For section headers, hero numbers, nav.
- **Mono:** JetBrains Mono or IBM Plex Mono. For data tables, prices, timestamps.
- **No Inter.** No Saira. Two fonts max.

### Layout Changes

- Header: black bar, white logo, yellow accent stripe at top (2px)
- Nav: bold uppercase tabs, yellow underline for active
- Cards: flat black, 1px gray border, no shadow, no radius
- Hero numbers: huge, white, no odometer animation — just the number
- Status: yellow dot = active, gray dot = clear, no green, no red
- Dividers: thin yellow rules (1px)
- CTAs: black background, yellow border, white text

### What Stays the Same

- Template kit architecture
- LOOP/OPTIONAL/IF markers
- 30-min data pipeline
- 9-page structure
- All data modules

### What Changes

- styles.css — complete rewrite
- All .template.html files — strip complex markup, simplify to bulletin structure
- Remove odometer JS (flat numbers)
- Remove Leaflet map styling (simpler dark tiles)
- Simplify nav to 5 items max

### Risks

- Too stark — the flat black + yellow could feel harsh over time
- Legibility — white on black with no gray midtones might strain eyes
- Distinction from NMM — we lose the brand recognition of the current cockpit
- Mobile — bold industrial style needs careful spacing on small screens

### Open Questions

1. One accent color (yellow only) or two (yellow + a muted blue/gray)?
2. Sharp corners (0px radius) or subtle rounding (2px)?
3. Hero numbers: plain text or keep some animation?
4. Map styling: dark tiles or keep standard OSM?
5. Font: free (Bebas Neue on Google Fonts) or paid (Industry by Fort Foundry)?
