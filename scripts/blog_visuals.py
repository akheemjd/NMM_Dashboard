#!/usr/bin/env python3
"""NMM blog visuals — brand-matched chart engine.

Produces self-contained PNG charts for blog posts. Unlike scripts/charts.py
(which emits SVG styled by nm.css classes for the dashboard), these render
standalone images that can be uploaded to Ghost and sit inside a post.

Design rules:
  - Chart type is chosen by the SHAPE of the data, not applied uniformly.
    Ranking -> ranked bars. Change over time -> trend line. Two-point
    comparison -> dumbbell. Spread -> distribution. Part of whole -> stacked bar.
  - Every chart carries its source line. NMM's promise is that the numbers
    are checkable, so the attribution travels with the image.
  - No chartjunk: no top/right spines, no 3D, no pie charts, no legends when
    direct labels will do.

Usage:
    python scripts/blog_visuals.py --demo            # render one of each type
    python scripts/blog_visuals.py --list            # list available chart types
"""

import argparse
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.ticker import MaxNLocator

# We resolve weights by family name (Google Fonts splits non-regular weights
# into separate families), so matplotlib's "closest weight" notices are noise.
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"  # build-only; assets/ gets copied to the published site
VISUAL_DIR = ROOT / "visuals"

# ── Brand tokens (mirrors assets/nm.css) ───────────────────────
PAPER = "#FBFAF8"
RAISE = "#FFFFFF"
SINK = "#F3F1EC"
INK = "#1A1A17"
INK2 = "#45423C"
MUTED = "#6B6862"
LINE = "#E8E4DD"
SIGNAL = "#0B5D3B"
SIGNAL2 = "#0A4E32"
WASH = "#EDF3EF"
AMBER = "#C8891A"
UP = "#B3261E"
UP_WASH = "#FBECEA"
FOCUS = "#1C6FE0"

# Chart canvas.
#
# Sized for MOBILE-FIRST legibility. What matters is not the pixel count but
# the ratio of text height to canvas width: at a 9in canvas a 10pt label is
# ~1.5% of the width, which renders at about 4px when Ghost scales the image
# to a 343px phone column. Illegible.
#
# A ~6in canvas with proportionally larger type puts labels near 4% of the
# width, so they land around 13px on a phone and stay sharp on desktop
# (the PNG is ~1000px wide at the DPI below, close to 1:1 at typical
# desktop content widths).
FIGSIZE = (6.4, 3.9)
DPI = 155

# Brand faces. Each has static 400-700 TTFs in assets/fonts so matplotlib can
# actually select weights (variable fonts resolve to their light default).
DISPLAY_FONT = "Space Grotesk"   # headings, emphasis
BODY_FONT = "Inter"              # labels, subtitles
DATA_FONT = "IBM Plex Mono"      # numbers

_theme_ready = False
_fonts_loaded = False


def _load_fonts():
    """Register every static weight in assets/fonts. Returns the family names.

    Idempotent, and safe to call before set_theme() — the *_font() helpers
    depend on it having run, and they are used to build figures directly.
    """
    global _fonts_loaded
    if _fonts_loaded:
        return
    _fonts_loaded = True
    if FONT_DIR.exists():
        for f in sorted(FONT_DIR.glob("*.ttf")):
            try:
                fm.fontManager.addfont(str(f))
            except Exception:
                pass


def _available(family):
    """True if the family is registered and usable."""
    _load_fonts()
    try:
        fm.findfont(fm.FontProperties(family=family), fallback_to_default=False)
        return True
    except Exception:
        return False


def display_font(size, weight=600):
    """Space Grotesk if present, else the body face, else system sans."""
    for fam in (DISPLAY_FONT, BODY_FONT, "Segoe UI", "DejaVu Sans"):
        if _available(fam):
            return fm.FontProperties(family=fam, size=size, weight=weight)
    return fm.FontProperties(size=size, weight=weight)


def body_font(size, weight=400):
    for fam in (BODY_FONT, "Segoe UI", "DejaVu Sans"):
        if _available(fam):
            return fm.FontProperties(family=fam, size=size, weight=weight)
    return fm.FontProperties(size=size, weight=weight)


def data_font(size, weight=500):
    """Monospace for numerals so columns of figures align.

    Google Fonts ships IBM Plex Mono's non-regular weights as *separate
    families* ("IBM Plex Mono Medium", "IBM Plex Mono SemiBold"), so a
    weight request against the base family silently falls back to 400.
    Resolve the right family name instead.
    """
    candidates = {
        400: ["IBM Plex Mono"],
        500: ["IBM Plex Mono Medium", "IBM Plex Mono"],
        600: ["IBM Plex Mono SemiBold", "IBM Plex Mono Medium", "IBM Plex Mono"],
    }.get(weight, ["IBM Plex Mono"])

    for fam in candidates:
        if _available(fam):
            return fm.FontProperties(family=fam, size=size, weight="normal")
    for fam in ("Consolas", "DejaVu Sans Mono"):
        if _available(fam):
            return fm.FontProperties(family=fam, size=size, weight=weight)
    return fm.FontProperties(size=size, weight=weight)


def set_theme():
    """Apply NMM tokens to matplotlib's global config. Idempotent."""
    global _theme_ready
    if _theme_ready:
        return
    _load_fonts()

    ordered = []
    for want in (BODY_FONT, DISPLAY_FONT, DATA_FONT):
        if _available(want):
            ordered.append(want)
    ordered += ["Segoe UI", "Arial", "DejaVu Sans"]

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ordered,
        "font.weight": 400,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.edgecolor": LINE,
        "axes.labelcolor": INK2,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "axes.labelsize": 10.5,
        "axes.titlesize": 13,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        # NOT 'tight': tight bbox expands the canvas to include text placed
        # outside the axes, which inflates the width and throws off the
        # text-to-width ratio the mobile legibility depends on. Title and
        # source are positioned inside the figure instead.
        "savefig.bbox": "standard",
        "savefig.pad_inches": 0,
        "axes.grid": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.spines.bottom": True,
        "axes.linewidth": 1.0,
        "lines.linewidth": 2.4,
        "lines.solid_capstyle": "round",
        "legend.frameon": False,
        "legend.fontsize": 10,
    })
    _theme_ready = True


def _figure(title=None, subtitle=None, source=None, figsize=None):
    """Create a styled figure. Title/subtitle/source are positioned INSIDE the
    figure bounds so the saved PNG is exactly figsize x DPI, which keeps the
    text-to-width ratio (and therefore mobile legibility) predictable.

    Type sizes are tuned for the ~6.4in canvas: roughly 3% of canvas width for
    body labels, which lands near 11px when a phone scales the image to a
    343px column.
    """
    set_theme()
    fig, ax = plt.subplots(figsize=figsize or FIGSIZE)

    if title:
        fig.text(0.0, 0.985, title,
                 fontproperties=display_font(21, weight=600),
                 color=INK, ha="left", va="top")
    if subtitle:
        fig.text(0.0, 0.925, subtitle,
                 fontproperties=body_font(14.5, weight=400),
                 color=MUTED, ha="left", va="top")
    if source:
        fig.text(0.0, 0.015, f"Source: {source}",
                 fontproperties=body_font(12.5, weight=400),
                 color=MUTED, ha="left", va="bottom")

    fig.subplots_adjust(top=0.855, bottom=0.115, left=0.02, right=0.98)
    return fig, ax


def _xgrid(ax, axis="x"):
    ax.grid(axis=axis, color=LINE, linewidth=0.9, zorder=0)
    ax.set_axisbelow(True)


def _finalize(fig, ax):
    """Reserve margin for what was actually drawn.

    Fixed fractions (left=0.02, bottom=0.11) clip tick labels once the type is
    large enough to read on a phone, and let the source line collide with the
    x-axis labels. Measure the real artists instead.

    Tick labels are measured directly rather than via ax.get_tightbbox(): the
    tight bbox did not reliably include them here, which silently dropped the
    y-axis numbers off the left edge.

    Call this last, just before returning a figure.
    """
    try:
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        fw = fig.get_size_inches()[0] * fig.dpi
        fh = fig.get_size_inches()[1] * fig.dpi
        ab = ax.get_window_extent()

        # Left: widest y tick label, plus a gutter.
        widest = 0.0
        for t in ax.get_yticklabels():
            if t.get_text().strip():
                widest = max(widest, t.get_window_extent(renderer=r).width)
        left_px = widest + 14 if widest else 10

        # Bottom: how far the x tick labels hang below the axes, plus room for
        # the source line (drawn at figure y=0.015).
        below = 0.0
        for t in ax.get_xticklabels():
            if t.get_text().strip():
                bb = t.get_window_extent(renderer=r)
                below = max(below, ab.y0 - bb.y0)
        bottom_px = below + 48

        fig.subplots_adjust(
            left=min(0.46, left_px / fw),
            bottom=min(0.34, bottom_px / fh),
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# Chart primitives — each takes data and returns a Figure
# ══════════════════════════════════════════════════════════════

def ranked_bars(labels, values, title=None, subtitle=None, source=None,
                unit="", highlight=None, average=None):
    """Horizontal bars, sorted ascending. For RANKINGS (provinces, cities, ports).

    Values should already be in the display unit. `average` draws a reference line.
    Bars at or above the average take the amber accent; the rest stay green.
    """
    set_theme()
    pairs = [(str(l), float(v)) for l, v in zip(labels, values)
             if v is not None]
    if not pairs:
        return None
    pairs.sort(key=lambda p: p[1])

    labs = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]

    # More rows need more vertical room, or the labels crowd at phone width.
    # A 12-province chart gets a taller canvas than a 5-port one.
    h = max(FIGSIZE[1], 0.30 * len(labs) + 1.9)
    fig, ax = _figure(title, subtitle, source, figsize=(FIGSIZE[0], h))
    ypos = range(len(labs))

    colors = []
    for v in vals:
        if highlight and labs[vals.index(v)] == highlight:
            colors.append(AMBER)
        elif average is not None and v >= average:
            colors.append(AMBER)
        else:
            colors.append(SIGNAL)

    ax.barh(list(ypos), vals, color=colors, height=0.62, zorder=3)
    ax.set_yticks(list(ypos))
    ax.set_yticklabels(labs, fontproperties=body_font(15, weight=500))

    _xgrid(ax, "x")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(data_font(13.5, weight=400))

    # Direct value labels at the bar ends — avoids needing a legend
    span = max(vals) - min(vals) or 1
    for i, v in enumerate(vals):
        ax.text(v + span * 0.015, i, f"{v:,.1f}{unit}",
                va="center", ha="left",
                fontproperties=data_font(14.5, weight=500),
                color=INK2, zorder=4)

    if average is not None:
        ax.axvline(average, color=INK2, linewidth=1.1, linestyle=(0, (4, 3)),
                   zorder=4, alpha=0.75)
        # Place the caption below the plot so it never collides with a bar
        ax.text(average, -1.35, f"average {average:,.1f}{unit}",
                fontproperties=body_font(12.5, weight=500),
                color=INK2, va="top", ha="center", zorder=5)

    ax.set_xlim(min(vals) - span * 0.06, max(vals) + span * 0.20)
    ax.set_ylim(-1.9, len(labs) - 0.2)
    ax.xaxis.set_major_locator(MaxNLocator(5))
    _finalize(fig, ax)
    return fig


def trend_line(dates, values, title=None, subtitle=None, source=None,
               unit="", label=None, annotate_last=True, fill=True,
               reference=None, reference_label=None, decimals=1):
    """Line over time. For CHANGE OVER TIME (price history, trend series).

    `dates` may be datetimes or ISO strings. `reference` draws a horizontal
    benchmark line. The last point is annotated with its value unless disabled.

    `decimals` matters: an FX rate shown at 1 decimal reads "1.4" when the rate
    is 1.4002, which is a different number. Pass 4 for rates, 1 for cents.
    """
    set_theme()
    import datetime as _dt
    import matplotlib.dates as mdates

    parsed = []
    for d, v in zip(dates, values):
        if v is None:
            continue
        if isinstance(d, str):
            try:
                d = _dt.date.fromisoformat(d[:10])
            except ValueError:
                continue
        parsed.append((d, float(v)))
    if len(parsed) < 2:
        return None
    parsed.sort(key=lambda p: p[0])
    xs = [p[0] for p in parsed]
    ys = [p[1] for p in parsed]

    fig, ax = _figure(title, subtitle, source)

    if fill:
        ax.fill_between(xs, ys, min(ys) - (max(ys) - min(ys)) * 0.35,
                        color=WASH, zorder=1, linewidth=0)

    ax.plot(xs, ys, color=SIGNAL, zorder=3, label=label)

    if reference is not None:
        ax.axhline(reference, color=AMBER, linewidth=1.2,
                   linestyle=(0, (4, 3)), zorder=2)
        if reference_label:
            ax.text(xs[0], reference, f" {reference_label}",
                    fontproperties=body_font(13, weight=500),
                    color=AMBER, va="bottom", ha="left")

    _xgrid(ax, "y")
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(axis="both", length=0)

    ylo, yhi = min(ys), max(ys)
    yrange = (yhi - ylo) or 1
    ax.set_ylim(ylo - yrange * 0.18, yhi + yrange * 0.30)

    # Reserve margin to the right of the final point so the end label has
    # clear space to sit in rather than landing on top of the line.
    xlo, xhi = min(xs), max(xs)
    xspan = (xhi - xlo)
    if xspan.total_seconds() > 0:
        pad = xspan * 0.16
        ax.set_xlim(xlo - xspan * 0.02, xhi + pad)

    # Date ticks: let matplotlib pick a sensible count and format them
    # concisely, otherwise dense daily data prints overlapping ISO strings.
    locator = mdates.AutoDateLocator(minticks=4, maxticks=7)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    for lbl in ax.get_xticklabels():
        lbl.set_fontproperties(data_font(13.5, weight=400))

    if annotate_last:
        ax.plot([xs[-1]], [ys[-1]], "o", color=SIGNAL, markersize=6, zorder=4)
        ax.annotate(f"{ys[-1]:,.{decimals}f}{unit}",
                    xy=(xs[-1], ys[-1]),
                    xytext=(8, 0), textcoords="offset points",
                    fontproperties=data_font(16, weight=600),
                    color=INK, ha="left", va="center", zorder=5)

    if label:
        ax.legend(loc="upper left", fontsize=13.5)
    _finalize(fig, ax)
    return fig


def dumbbell(labels, value_a, value_b, name_a="Before", name_b="Now",
             title=None, subtitle=None, source=None, unit="", sort=True):
    """Two points joined by a connector. For TWO-POINT COMPARISONS
    (this period vs last, CAD vs USD, before vs after).
    """
    set_theme()
    rows = [(str(l), float(a), float(b))
            for l, a, b in zip(labels, value_a, value_b)
            if a is not None and b is not None]
    if not rows:
        return None
    if sort:
        rows.sort(key=lambda r: abs(r[2] - r[1]))

    labs = [r[0] for r in rows]
    a_vals = [r[1] for r in rows]
    b_vals = [r[2] for r in rows]
    ypos = list(range(len(rows)))

    fig, ax = _figure(title, subtitle, source)

    for y, a, b in zip(ypos, a_vals, b_vals):
        ax.plot([a, b], [y, y], color=LINE, linewidth=2.6, zorder=2,
                solid_capstyle="round")

    ax.scatter(a_vals, ypos, s=62, color=MUTED, zorder=4, label=name_a)
    ax.scatter(b_vals, ypos, s=62, color=SIGNAL, zorder=4, label=name_b)

    ax.set_yticks(ypos)
    ax.set_yticklabels(labs, fontsize=15)
    _xgrid(ax, "x")
    ax.tick_params(axis="both", length=0)
    ax.spines["bottom"].set_visible(False)
    ax.legend(loc="lower right", fontsize=13.5, ncol=2)
    _finalize(fig, ax)
    return fig


def distribution(values, title=None, subtitle=None, source=None,
                 unit="", bins=18, median_line=True):
    """Histogram. For SPREAD (how often a crossing is slow, delay distribution)."""
    set_theme()
    vals = [float(v) for v in values if v is not None]
    if len(vals) < 5:
        return None

    fig, ax = _figure(title, subtitle, source)
    ax.hist(vals, bins=bins, color=SIGNAL, alpha=0.88, zorder=3,
            edgecolor=PAPER, linewidth=0.8)

    if median_line:
        import statistics
        med = statistics.median(vals)
        ax.axvline(med, color=AMBER, linewidth=1.6, zorder=4)
        ax.text(med, ax.get_ylim()[1] * 0.94, f" median {med:,.1f}{unit}",
                fontsize=13.5, color=AMBER, va="top", ha="left")

    _xgrid(ax, "y")
    ax.tick_params(axis="both", length=0)
    ax.set_ylabel("observations", fontsize=13.5)
    _finalize(fig, ax)
    return fig


def grouped_bars(categories, series, title=None, subtitle=None, source=None,
                 unit=""):
    """Clustered bars. For COMPARING A FEW CATEGORIES across 2-3 series.

    `series` is an ordered dict: {series_name: [values...]} aligned to categories.
    """
    set_theme()
    import numpy as np

    if not series or not categories:
        return None
    names = list(series.keys())
    n = len(names)
    if n < 2 or n > 3:
        return None

    fig, ax = _figure(title, subtitle, source)
    x = np.arange(len(categories))
    width = 0.78 / n
    palette = [SIGNAL, AMBER, FOCUS]

    for i, name in enumerate(names):
        vals = series[name]
        ax.bar(x + (i - (n - 1) / 2) * width, vals, width * 0.92,
               label=name, color=palette[i], zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels([str(c) for c in categories], fontsize=13.5)
    _xgrid(ax, "y")
    ax.tick_params(axis="both", length=0)
    ax.spines["bottom"].set_visible(False)
    ax.legend(loc="upper left", fontsize=13.5, ncol=n)
    _finalize(fig, ax)
    return fig


def share_bar(segments, title=None, subtitle=None, source=None, unit=""):
    """Single stacked horizontal bar. For PART OF WHOLE.

    `segments` is an ordered dict {label: value}. Values are converted to
    percentages of the total. Use this instead of a pie chart.
    """
    set_theme()
    segs = [(k, float(v)) for k, v in segments.items() if v]
    if len(segs) < 2:
        return None
    total = sum(v for _, v in segs)
    if total <= 0:
        return None

    fig, ax = _figure(title, subtitle, source)
    palette = [SIGNAL, AMBER, MUTED, FOCUS, SIGNAL2]

    left = 0.0
    for i, (label, value) in enumerate(segs):
        pct = value / total * 100
        ax.barh([0], [pct], left=left, height=0.42,
                color=palette[i % len(palette)], zorder=3)
        if pct > 7:
            ax.text(left + pct / 2, 0, f"{pct:.0f}%", ha="center", va="center",
                    color="#FFFFFF", fontsize=15, fontweight="600", zorder=4)
        left += pct

    ax.set_xlim(0, 100)
    ax.set_ylim(-0.6, 0.9)
    ax.axis("off")

    # Direct labels below the bar rather than a legend. Placed inside the
    # figure bounds, since the canvas is saved without a tight bbox.
    handles = []
    for label, value in segs:
        handles.append(f"{label} ({value:,.1f}{unit})")
    fig.text(0.0, 0.06, "   ".join(handles), fontsize=13, color=INK2,
             ha="left", va="bottom")
    return fig


# ══════════════════════════════════════════════════════════════
# Hero card — the post's feature image and social share card
# ══════════════════════════════════════════════════════════════

HERO_W, HERO_H = 1200, 630


def _pil_font(family, weight, size):
    """Load a static brand TTF for PIL. Falls back through families."""
    from PIL import ImageFont
    order = {
        "display": ["SpaceGrotesk-600", "SpaceGrotesk-500", "SpaceGrotesk-400",
                    "Inter-600", "Inter-500", "Inter-400"],
        "body": ["Inter-400", "Inter-500", "SpaceGrotesk-400"],
        "mono": ["IBMPlexMono-600", "IBMPlexMono-500", "IBMPlexMono-400"],
    }.get(family, ["Inter-400"])

    for stem in order:
        p = FONT_DIR / f"{stem}.ttf"
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    # System fallbacks
    for path in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    from PIL import ImageFont as _IF
    return _IF.load_default()


def _wrap(draw, text, font, max_width):
    """Greedy word wrap to a pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def hero_card(headline, eyebrow=None, stat_value=None, stat_label=None,
              source=None, variant="paper"):
    """Build a branded 1200x630 social/feature card with PIL.

    variant="paper" -> light editorial card (default)
    variant="signal" -> deep green card, for higher contrast in feeds
    """
    from PIL import Image, ImageDraw

    if variant == "signal":
        bg, fg, sub, accent = SIGNAL, PAPER, "#CFE0D6", AMBER
    else:
        bg, fg, sub, accent = PAPER, INK, MUTED, SIGNAL

    img = Image.new("RGB", (HERO_W, HERO_H), bg)
    d = ImageDraw.Draw(img)

    pad = 72
    inner_w = HERO_W - pad * 2

    # Top accent rule — a thin bar reads as editorial masthead
    d.rectangle([0, 0, HERO_W, 8], fill=accent)

    # ── Eyebrow (pinned top) ──
    y_eyebrow = pad
    eb = _pil_font("display", 600, 25)
    d.text((pad, y_eyebrow), "NORTHERN MILE", font=eb, fill=accent)
    w_label = d.textlength("NORTHERN MILE", font=eb)
    if eyebrow:
        d.text((pad + w_label + 16, y_eyebrow + 2), f"/ {eyebrow.upper()}",
               font=_pil_font("body", 400, 22), fill=sub)

    # ── Headline (sized to fit) ──
    hf = _pil_font("display", 600, 62)
    avail = inner_w if not stat_value else inner_w * 0.82
    lines = _wrap(d, headline, hf, avail)
    while len(lines) > 4 and hf.size > 34:
        hf = _pil_font("display", 600, hf.size - 4)
        lines = _wrap(d, headline, hf, avail)

    line_h = int(hf.size * 1.18)
    head_h = line_h * len(lines)

    # ── Stat block dimensions ──
    stat_h = 0
    if stat_value:
        stat_h = 52 + 58 + 40 + (30 if stat_label else 0)   # gap + figure + gap + label

    # ── Source sits at the bottom ──
    source_h = 34 if source else 0
    band_top = y_eyebrow + 62
    band_bottom = HERO_H - pad - source_h
    content_h = head_h + stat_h

    # Centre the headline+stat group in the band so the card reads balanced
    # instead of leaving a hole between the two elements.
    y = band_top + max(0, (band_bottom - band_top - content_h) // 2)

    for ln in lines:
        d.text((pad, y), ln, font=hf, fill=fg)
        y += line_h

    if stat_value:
        y += 40
        d.text((pad, y), str(stat_value),
               font=_pil_font("mono", 600, 56), fill=accent)
        y += 68
        if stat_label:
            d.text((pad, y), str(stat_label).upper(),
                   font=_pil_font("body", 400, 21), fill=sub)

    if source:
        sf = _pil_font("body", 400, 19)
        txt = f"Source: {source}"
        tw = d.textlength(txt, font=sf)
        d.text((HERO_W - pad - tw, HERO_H - pad - 22), txt, font=sf, fill=sub)

    return img


def save_hero(img, name, outdir=None):
    outdir = Path(outdir) if outdir else VISUAL_DIR
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.png"
    img.save(path, "PNG", optimize=True)
    return path


# ══════════════════════════════════════════════════════════════
# Output
# ══════════════════════════════════════════════════════════════

def save(fig, name, outdir=None):
    """Write the figure to a PNG and return the path. Closes the figure."""
    outdir = Path(outdir) if outdir else VISUAL_DIR
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}.png"
    fig.savefig(path)
    plt.close(fig)
    return path


CHART_TYPES = {
    "ranked_bars": ranked_bars,
    "trend_line": trend_line,
    "dumbbell": dumbbell,
    "distribution": distribution,
    "grouped_bars": grouped_bars,
    "share_bar": share_bar,
}


def _demo():
    """Render one of each chart type with plausible data, to eyeball the style."""
    out = VISUAL_DIR / "demo"
    made = []

    provs = ["Quebec", "Newfoundland", "British Columbia", "New Brunswick",
             "Prince Edward Island", "Nova Scotia", "Ontario", "Yukon",
             "Manitoba", "Saskatchewan", "Alberta", "NWT"]
    prices = [296.3, 282.3, 277.7, 276.3, 273.0, 270.0, 261.0,
              249.9, 247.3, 244.1, 243.1, 213.8]

    f = ranked_bars(provs, prices,
                    title="Diesel by province",
                    subtitle="Cents per litre, week of September 15",
                    source="Natural Resources Canada weekly diesel survey",
                    unit="c", average=267.1)
    if f:
        made.append(save(f, "demo-ranked-bars", out))

    import datetime as dt
    days = [dt.date(2026, 1, 1) + dt.timedelta(days=i * 14) for i in range(19)]
    series = [188 + i * 2.6 + (i % 3) * 4 for i in range(19)]
    f = trend_line(days, series,
                   title="National diesel average, 2026",
                   subtitle="Cents per litre",
                   source="Natural Resources Canada weekly diesel survey",
                   unit="c", reference=210.0, reference_label="2025 average")
    if f:
        made.append(save(f, "demo-trend-line", out))

    f = dumbbell(["Ambassador", "Blue Water", "Peace", "Coutts"],
                 [12, 8, 22, 5], [26, 14, 41, 9],
                 title="Border waits, last month vs now",
                 subtitle="Average commercial delay, minutes",
                 source="CBSA border wait times", unit=" min")
    if f:
        made.append(save(f, "demo-dumbbell", out))

    import random
    random.seed(7)
    delays = [max(0, int(random.gauss(18, 12))) for _ in range(170)]
    f = distribution(delays,
                     title="How long the Ambassador Bridge actually takes",
                     subtitle="Distribution of 170 observations",
                     source="CBSA border wait times", unit=" min")
    if f:
        made.append(save(f, "demo-distribution", out))

    f = grouped_bars(["Q1", "Q2", "Q3", "Q4"],
                     {"Canada": [245, 251, 238, 233],
                      "United States": [262, 268, 255, 249]},
                     title="Canadian vs American diesel",
                     subtitle="Cents per litre equivalent",
                     source="NRCan and EIA", unit="c")
    if f:
        made.append(save(f, "demo-grouped-bars", out))

    f = share_bar({"Alberta": 41.2, "Saskatchewan": 18.4,
                   "Manitoba": 12.1, "Others": 28.3},
                  title="Where the grain tonnage originates",
                  subtitle="Share of western movement",
                  source="NMM dashboard", unit=" Mt")
    if f:
        made.append(save(f, "demo-share-bar", out))

    print(f"Rendered {len(made)} demo charts to {out}")
    for p in made:
        print(f"  {p.name}  ({p.stat().st_size // 1024} KB)")
    return made


def main():
    ap = argparse.ArgumentParser(description="NMM blog visual engine")
    ap.add_argument("--demo", action="store_true", help="Render one of each chart type")
    ap.add_argument("--list", action="store_true", help="List chart types")
    args = ap.parse_args()

    if args.list:
        for name in CHART_TYPES:
            print(f"  {name}")
        return 0
    if args.demo:
        _demo()
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
