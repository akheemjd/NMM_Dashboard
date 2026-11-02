"""Editorial layer: restyle the whole dashboard without touching markup.

The site read as Android for structural reasons, not colour ones:

  * 42 border-radius declarations, ten of them 10px and seven of them full pills. Rounded boxes are
    the visual signature of Material Design, and there were rounded boxes on every surface.
  * Headings in Overpass at weight 700 with tight tracking, which reads as an app header rather than
    a publication masthead. Source Serif 4 was already loaded and used only for body prose.
  * Panels with a border AND a radius AND a background, so every data block looked like a tile in a
    grid of tiles rather than a section of a page.
  * One green applied to labels everywhere, which turns an accent into decoration and stops it
    meaning anything.

This block overrides all of it in place. Markup, class names, JS hooks and every data binding stay
exactly as they are, so nothing can break: it is CSS only. Appended last so it wins the cascade.

The rules, in order of what changes the impression most:

  1. SERIF HEADINGS   h1/h2/h3 move to Source Serif 4 at 600. This is the single biggest change.
  2. SQUARE EVERYTHING  all radii to 0. Panels become ruled sections, not tiles.
  3. RULE INSTEAD OF BOX  panels drop the border and gain a top rule, so they read as sections.
  4. ONE ACCENT  green reserved for the current page, links, and a single rule per view.
  5. MORE AIR  line-height and section padding up; the page stops feeling dense and appy.
"""

CSS = """
/* ═══ EDITORIAL LAYER ══════════════════════════════════════════════════════
   Restyles the whole dashboard in place. CSS only: no markup, no class names,
   no JS hooks change. Keep this block last. */

/* 1. Headings are a publication, not an app header. */
h1, h2, h3, .lead h1, .lead h2, .sec h2, .chart-head h3, .figures .cn {
  font-family: var(--serif);
  font-weight: 600;
  letter-spacing: -0.02em;
}
h1 { line-height: 1.02; max-width: 24ch; }
h2 { line-height: 1.12; }
h3 { line-height: 1.2; letter-spacing: -0.015em; }
.figure .n, .cstat b, .pickgap b, .rows .r .v b { letter-spacing: -0.03em; }

/* 2. Square everything. This is the Material tell. */
*, *::before, *::after { border-radius: 0 !important; }
:focus-visible { border-radius: 0 !important; outline-offset: 3px; }

/* 3. Panels become ruled sections, not tiles in a grid. */
.figures .fg, .chart-card, .calc, .inc, .links-list, .rows, .pickcard, .dgrp,
.ipop, .drawer, .cstat {
  border: 0;
  border-top: 2px solid var(--ink);
  background: transparent;
  padding-top: 18px;
}
.figures { gap: 0; }
.figures .fg { padding: 18px 24px 0 0; }
.figures .fg + .fg { border-left: 1px solid var(--line); padding-left: 24px; }

/* A single heavy rule under the page head. */
.sec > .lead { border-bottom: 2px solid var(--ink); padding-bottom: 14px; }

/* 4. One accent, used for wayfinding only. */
.eyebrow { color: var(--signal); font-weight: 700; font-size: .8125rem;
  letter-spacing: .12em; text-transform: uppercase; }
.nav .ng.on { color: var(--signal); }
.nav .ng.on::after { background: var(--signal); height: 2px; }
.strip a { padding: 6px 0; background: transparent; border: 0;
  border-bottom: 2px solid transparent; font-weight: 600; }
.strip a.on { border-bottom-color: var(--signal); }
.strip a:hover { border-bottom-color: var(--line); }

/* 5. More air. Dense grids read as software; spaced rules read as a page. */
body { font-size: 1.0625rem; line-height: 1.62; }
.sec { padding-top: clamp(28px, 4vw, 46px); }
.reading p { font-size: 1.1875rem; line-height: 1.7; color: #23282A; max-width: 68ch; }
.stand { font-size: 1.25rem; line-height: 1.6; }
.note, .meta { font-size: .875rem; color: var(--muted); }

/* The hero figures carry the page. Give the number real scale. */
.figures .fg .figure .n, .figure .n { font-size: clamp(2.4rem, 5vw, 3.6rem); line-height: 1; }

/* Tables and rows: rules, not boxes. */
.rows .r { border-bottom: 1px solid var(--line); }
.rows .r:last-child { border-bottom: 0; }

/* Buttons: flat, square, and obvious. */
.btn, .btn--brand, .strip a, .seg, .seg-opt, .navbtn, .fxtog a, .ch a {
  border-radius: 0 !important;
  box-shadow: none !important;
}
.btn, .btn--brand { border: 1px solid var(--ink); padding: 11px 20px; font-weight: 700; }
.btn--brand { background: var(--ink); color: var(--paper); }

/* Charts lose their frames too. */
.chart-svg, .incmap { border: 0; }

/* Small labels stay uppercase and small, but stop shouting in green. */
.pickcard .pflag, .links-list .src, .cstat .l { color: var(--muted); font-weight: 700;
  font-size: .75rem; letter-spacing: .1em; text-transform: uppercase; }
"""


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(r"C:\Users\Akheem\northern-mile-dashboard\assets\nm.css")
    t = p.read_text(encoding="utf-8")
    marker = "EDITORIAL LAYER"
    if marker not in t:
        p.write_text(t.rstrip() + "\n\n" + CSS.strip() + "\n", encoding="utf-8", newline="\n")
        print(f"  appended editorial layer ({len(CSS)} bytes)")
    else:
        # Replace the existing layer so repeat runs are idempotent.
        head = t.split("/* ═══ EDITORIAL LAYER")[0].rstrip()
        p.write_text(head + "\n\n" + CSS.strip() + "\n", encoding="utf-8", newline="\n")
        print("  replaced existing editorial layer")
