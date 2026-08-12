#!/usr/bin/env python3
"""One-shot theme migration. Every replacement is asserted."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "assets", "styles.css")

OLD_ROOT = """:root{
--bg:#0B0D11;--surface-1:#111419;--surface-2:#161A21;--raise:#1B2028;
--border:#20262F;--hair:#191E26;
--ink:#FFFFFF;--ink-2:#E6E9F0;--ink-3:#C8CFD8;
--green:#1E9E66;--green-dim:#12613F;--yellow:#F5C518;--red:#E5484D;
--rc:6px}"""

NEW_ROOT = """:root{
--bg:#0B0D11;--surface-1:#111419;--surface-2:#161A21;--raise:#1B2028;
--border:#20262F;--hair:#191E26;
--ink:#FFFFFF;--ink-2:#E6E9F0;--ink-3:#C8CFD8;

/* Brand. Amber is the only decorative accent. Never used to signal data. */
--brand:#F5C518;--brand-dim:#8A6E08;--brand-glow:rgba(245,197,24,.12);

/* Directional. Cost series only: rising cost is bad, falling cost is good.
   These four are never used for decoration. */
--up:#E5484D;--down:#1E9E66;--warn:#F5C518;--alert:#E5484D;

/* Retained aliases so no rule silently loses its colour. */
--green:#1E9E66;--green-dim:#12613F;--yellow:#F5C518;--red:#E5484D;--amber:#F5C518;
--rc:6px}"""

REPLACEMENTS = [
    # --- brand accent ---
    ("a{color:var(--green);text-decoration:none}",
     "a{color:var(--brand);text-decoration:none}"),

    ("radial-gradient(120% 70% at 50% -10%,rgba(30,158,102,.05),transparent 60%)",
     "radial-gradient(120% 70% at 50% -10%,rgba(245,197,24,.05),transparent 60%)"),

    (".nav a.on{color:var(--ink);border-color:var(--green)}",
     ".nav a.on{color:var(--ink);border-color:var(--brand)}"),

    (".strip b{color:var(--green);font-weight:600}",
     ".strip b{color:var(--brand);font-weight:600}"),

    ("background:var(--yellow);box-shadow:0 0 0 3px rgba(245,197,24,.14)",
     "background:var(--brand);box-shadow:0 0 0 3px var(--brand-glow)"),

    (".readlabel .tick{color:var(--green)}",
     ".readlabel .tick{color:var(--brand)}"),

    (".sechead .more{font-size:.75rem;color:var(--green);",
     ".sechead .more{font-size:.75rem;color:var(--brand);"),

    (".sechead::before{content:'';width:14px;height:14px;background:var(--green);border-radius:2px;flex-shrink:0;box-shadow:0 0 0 3px rgba(30,158,102,.12)}",
     ".sechead::before{content:'';width:14px;height:14px;background:var(--brand);border-radius:2px;flex-shrink:0;box-shadow:0 0 0 3px var(--brand-glow)}"),

    (".mod-live .tab,.mod .tab{width:22px;height:14px;background:var(--green);border-radius:2px;flex-shrink:0;box-shadow:0 0 0 3px rgba(30,158,102,.12)}",
     ".mod-live .tab,.mod .tab{width:22px;height:14px;background:var(--brand);border-radius:2px;flex-shrink:0;box-shadow:0 0 0 3px var(--brand-glow)}"),

    ("border-left:2px solid var(--green-dim)",
     "border-left:2px solid var(--brand-dim)"),

    (".sp .c{margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;font-weight:600;color:var(--green)}",
     ".sp .c{margin-left:auto;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;font-weight:600;color:var(--brand)}"),

    (".xr .v{margin-top:11px;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;font-weight:600;color:var(--green)}",
     ".xr .v{margin-top:11px;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;font-weight:600;color:var(--brand)}"),

    ("border:1px solid var(--green-dim);color:var(--green);padding:10px 16px",
     "border:1px solid var(--brand-dim);color:var(--brand);padding:10px 16px"),

    ("background:var(--green-dim);color:#CFF3E2;padding:3px 7px",
     "background:var(--brand-dim);color:#0B0D11;padding:3px 7px"),

    ("border-top:2px solid var(--yellow);border-radius:var(--rc);padding:22px 24px",
     "border-top:2px solid var(--brand);border-radius:var(--rc);padding:22px 24px"),

    ("text-transform:uppercase;color:var(--yellow);font-weight:600}",
     "text-transform:uppercase;color:var(--brand);font-weight:600}"),

    (".share a:hover,.share button:hover{border-color:var(--green);color:var(--ink)}",
     ".share a:hover,.share button:hover{border-color:var(--brand);color:var(--ink)}"),

    (".related a:hover{border-color:var(--green);color:var(--ink)}",
     ".related a:hover{border-color:var(--brand);color:var(--ink)}"),

    ("[data-href]:focus-visible{outline:2px solid var(--green);outline-offset:-2px}",
     "[data-href]:focus-visible{outline:2px solid var(--brand);outline-offset:-2px}"),

    ("background:var(--yellow);color:#0B0D11;border:none",
     "background:var(--brand);color:#0B0D11;border:none"),

    (".tft .val{color:var(--amber);",
     ".tft .val{color:var(--brand);"),

    (".gauge.good .gv{color:var(--ink)}.gauge.warn .gv{color:var(--amber)}",
     ".gauge.good .gv{color:var(--ink)}.gauge.warn .gv{color:var(--warn)}"),

    # --- directional, the actual bug ---
    (".up{color:var(--green)}.down{color:var(--green)}.flat{color:var(--ink-3)}",
     ".up{color:var(--up)}.down{color:var(--down)}.flat{color:var(--ink-3)}"),

    (".clus-gauges .g.lo .gv{color:var(--green)}.clus-gauges .g.hi .gv{color:var(--green)}",
     ".clus-gauges .g.lo .gv{color:var(--down)}.clus-gauges .g.hi .gv{color:var(--up)}"),

    (".tbl tr.hi td{box-shadow:inset 2px 0 0 var(--yellow)}",
     ".tbl tr.hi td{box-shadow:inset 2px 0 0 var(--up)}"),

    (".tbl tr.lo td{box-shadow:inset 2px 0 0 var(--green)}",
     ".tbl tr.lo td{box-shadow:inset 2px 0 0 var(--down)}"),

    ("margin-top:14px;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;color:var(--green)}",
     "margin-top:14px;font-family:'IBM Plex Mono',monospace;font-size:.6875rem;color:var(--ink-2)}"),

    # --- pills: add missing .ok, correct heavy ---
    (".pill.mod{color:var(--green);background:rgba(30,158,102,.12)}\n.pill.heavy{color:var(--green);background:rgba(245,197,24,.12)}\n.pill.closed{color:var(--red);background:rgba(229,72,77,.12)}",
     ".pill.ok{color:var(--down);background:rgba(30,158,102,.12)}\n.pill.mod{color:var(--warn);background:rgba(245,197,24,.12)}\n.pill.heavy{color:var(--up);background:rgba(229,72,77,.12)}\n.pill.closed{color:var(--up);background:rgba(229,72,77,.20)}"),

    # --- fonts: collapse Saira into Saira Condensed ---
    (".sechead h2{font-family:'Saira',sans-serif;",
     ".sechead h2{font-family:'Saira Condensed',sans-serif;"),
    (".mod h2{font-family:'Saira',sans-serif;",
     ".mod h2{font-family:'Saira Condensed',sans-serif;"),
    (".faq dt{font-family:'Saira',sans-serif;",
     ".faq dt{font-family:'Saira Condensed',sans-serif;"),
    ("font-size:.9375rem;font-family:'Saira',sans-serif;margin-bottom:4px}",
     "font-size:.9375rem;font-family:'Saira Condensed',sans-serif;margin-bottom:4px}"),
    (".empty b{color:var(--green);",
     ".empty b{color:var(--brand);"),

    # --- dead duplicate declaration ---
    (".tft .m{font-family:'Inter',-apple-system,sans-serif;color:var(--ink-3);font-size:.6875rem;font-family:'IBM Plex Mono',monospace;margin-top:3px}",
     ".tft .m{color:var(--ink-3);font-size:.6875rem;font-family:'IBM Plex Mono',monospace;margin-top:3px}"),
]


def main():
    with open(CSS) as f:
        css = f.read()

    if OLD_ROOT not in css:
        print("FATAL: :root block not found verbatim. Aborting.", file=sys.stderr)
        sys.exit(1)
    css = css.replace(OLD_ROOT, NEW_ROOT, 1)

    failed = []
    for old, new in REPLACEMENTS:
        if old not in css:
            failed.append(old[:70])
            continue
        css = css.replace(old, new, 1)

    if failed:
        print("FATAL: targets not found, no changes written:", file=sys.stderr)
        for t in failed:
            print(f"  MISS: {t}", file=sys.stderr)
        sys.exit(1)

    with open(CSS, "w") as f:
        f.write(css)
    print(f"Theme migration applied: {len(REPLACEMENTS)} replacements + :root")


if __name__ == "__main__":
    main()
