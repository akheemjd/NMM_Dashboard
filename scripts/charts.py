#!/usr/bin/env python3
"""Server-rendered SVG charts. No JS, no D3 — the SVG is embedded in the page so
every visual survives if scripts fail. Each function returns an SVG string, or
"" when there is nothing to draw. Colors come from CSS classes defined in
assets/nm.css (fill/stroke via custom properties), not hardcoded here."""

import re
from collections import Counter


def _num(v):
    """Coerce a value to float (data files carry numbers as strings)."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _short_label(road):
    """'HWY 401' -> '401', 'Highway 7' -> '7', 'QEW' -> 'QEW'."""
    m = re.search(r"(\d+)", str(road))
    return m.group(1) if m else str(road)


def diesel_spread_svg(provinces, national):
    """Horizontal bars: diesel price per province, cheapest -> dearest.
    Green = below national average, red = above; dashed line at the average."""
    items = []
    for p in provinces:
        v = _num(p.get("price"))
        if v is not None:
            items.append({"code": p.get("code", ""), "price": v})
    if not items:
        return ""
    items.sort(key=lambda p: p["price"])
    national = _num(national)
    vals = [p["price"] for p in items]
    lo = min(vals) - 4.0
    hi = max(vals) + 4.0
    span = hi - lo or 1.0

    W, LH, RH, ROW, PAD = 560, 34, 50, 26, 10
    bar_area = W - LH - RH
    H = PAD + len(items) * ROW + PAD
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Diesel price by province">']
    if national is not None:
        x = LH + (national - lo) / span * bar_area
        out.append(f'<line class="viz-ref" x1="{x:.1f}" y1="{PAD - 4}" x2="{x:.1f}" y2="{H - PAD + 4}"/>')
        out.append(f'<text class="viz-reflab" x="{x:.1f}" y="{H - PAD + 3}" text-anchor="middle">national {national}</text>')
    y = PAD + ROW / 2
    for p in items:
        code = p["code"]
        v = p["price"]
        frac = (v - lo) / span
        bw = max(frac * bar_area, 2)
        cls = "down" if (national is not None and v <= national) else "up"
        out.append(f'<text class="viz-lab" x="{LH - 6}" y="{y + 3.5}" text-anchor="end">{code}</text>')
        out.append(f'<rect class="viz-bar {cls}" x="{LH}" y="{y - 8}" width="{bw:.1f}" height="16" rx="3"/>')
        out.append(f'<text class="viz-val" x="{W - RH}" y="{y + 3.5}">{v}</text>')
        y += ROW
    out.append("</svg>")
    return "".join(out)


def diesel_change_svg(provinces):
    """Diverging bars: weekly change in ¢/L, green down (cheaper) / red up
    (dearer), centred on zero. Biggest mover at the top."""
    items = []
    for p in provinces:
        c = _num(p.get("change"))
        if c is not None:
            items.append({"code": p.get("code", ""), "change": c})
    if not items:
        return ""
    items.sort(key=lambda p: abs(p["change"]), reverse=True)
    max_abs = max(abs(p["change"]) for p in items) or 1.0

    W, LH, RH, ROW, PAD = 560, 34, 56, 26, 10
    half = (W - LH - RH) / 2.0
    center = LH + half
    H = PAD + len(items) * ROW + PAD
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Weekly diesel change by province">']
    out.append(f'<line class="viz-axis" x1="{center:.1f}" y1="{PAD - 4}" x2="{center:.1f}" y2="{H - PAD + 4}"/>')
    y = PAD + ROW / 2
    for p in items:
        code = p["code"]
        chg = p["change"]
        bw = abs(chg) / max_abs * half
        out.append(f'<text class="viz-lab" x="{LH - 6}" y="{y + 3.5}" text-anchor="end">{code}</text>')
        if chg >= 0:
            out.append(f'<rect class="viz-bar up" x="{center:.1f}" y="{y - 8}" width="{bw:.1f}" height="16" rx="3"/>')
            out.append(f'<text class="viz-val" x="{center + bw + 6:.1f}" y="{y + 3.5}">+{chg}</text>')
        else:
            out.append(f'<rect class="viz-bar down" x="{center - bw:.1f}" y="{y - 8}" width="{bw:.1f}" height="16" rx="3"/>')
            out.append(f'<text class="viz-val" x="{center - bw - 6:.1f}" y="{y + 3.5}" text-anchor="end">{chg}</text>')
        y += ROW
    out.append("</svg>")
    return "".join(out)


def corridor_svg(incidents):
    """Vertical columns: incident count per corridor, sorted desc."""
    counts = Counter(i.get("road") for i in incidents if i.get("road"))
    if not counts:
        return ""
    top = counts.most_common(8)
    max_c = top[0][1]

    W, H, PAD, BL = 560, 250, 14, 30
    n = len(top)
    col_w = (W - 2 * PAD) / n
    chart_h = H - PAD - BL
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Incidents by corridor">']
    for i, (road, c) in enumerate(top):
        cx = PAD + col_w * i + col_w / 2
        bh = c / max_c * chart_h
        out.append(f'<rect class="viz-col" x="{cx - col_w * 0.3:.1f}" y="{PAD + chart_h - bh:.1f}" width="{col_w * 0.6:.1f}" height="{bh:.1f}" rx="3"/>')
        out.append(f'<text class="viz-val" x="{cx:.1f}" y="{PAD + chart_h - bh - 5:.1f}" text-anchor="middle">{c}</text>')
        out.append(f'<text class="viz-lab" x="{cx:.1f}" y="{H - 8:.1f}" text-anchor="middle">{_short_label(road)}</text>')
    out.append("</svg>")
    return "".join(out)


def disruption_donut_svg(n_incidents, n_roadwork):
    """Donut: active incidents (amber) vs scheduled roadwork (blue)."""
    total = n_incidents + n_roadwork
    if total <= 0:
        return ""
    size, r, sw = 150, 56, 20
    c = 2 * 3.14159 * r
    dash_inc = n_incidents / total * c
    dash_rw = n_roadwork / total * c
    cx = cy = size / 2
    out = [f'<svg class="viz viz-donut" viewBox="0 0 {size} {size}" role="img" aria-label="Road disruptions">']
    out.append(f'<circle class="viz-donut-a" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke-width="{sw}" stroke-dasharray="{dash_inc:.1f} {c - dash_inc:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    out.append(f'<circle class="viz-donut-b" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke-width="{sw}" stroke-dasharray="{dash_rw:.1f} {c - dash_rw:.1f}" stroke-dashoffset="{-dash_inc:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    out.append(f'<text class="viz-donut-num" x="{cx}" y="{cy - 2}" text-anchor="middle">{total}</text>')
    out.append(f'<text class="viz-donut-lab" x="{cx}" y="{cy + 17}" text-anchor="middle">disruptions</text>')
    out.append("</svg>")
    return "".join(out)


def _fx_pairs(history):
    """Parse (date, rate) pairs from exchange history, sorted ascending."""
    pairs = []
    for h in history:
        r = _num(h.get("rate"))
        d = h.get("date")
        if r is not None and d:
            pairs.append((d, r))
    pairs.sort(key=lambda p: p[0])
    return pairs


def fx_line_svg(history):
    """Line chart: USD/CAD over the available history, with a 30-day moving average."""
    pairs = _fx_pairs(history)
    if len(pairs) < 2:
        return ""
    vals = [r for _, r in pairs]
    lo = min(vals) - 0.004
    hi = max(vals) + 0.004
    span = hi - lo or 1.0
    W, H, PL, PR, PT, PB = 560, 250, 44, 14, 14, 30
    plot_w = W - PL - PR
    plot_h = H - PT - PB
    n = len(pairs)

    def _x(i): return PL + i / (n - 1) * plot_w
    def _y(r): return PT + (hi - r) / span * plot_h

    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="USD/CAD past year">']
    for gv in (lo, (lo + hi) / 2, hi):
        gy = _y(gv)
        out.append(f'<line class="viz-gridline" x1="{PL}" y1="{gy:.1f}" x2="{W - PR}" y2="{gy:.1f}"/>')
        out.append(f'<text class="viz-lab" x="{PL - 6}" y="{gy + 3}" text-anchor="end">{gv:.4f}</text>')
    raw = " ".join(f"{_x(i):.1f},{_y(r):.1f}" for i, (_, r) in enumerate(pairs))
    ma = []
    for i in range(n):
        w = vals[max(0, i - 20):i + 1]
        ma.append(sum(w) / len(w))
    ma_pts = " ".join(f"{_x(i):.1f},{_y(m):.1f}" for i, m in enumerate(ma))
    out.append(f'<polyline class="viz-line" points="{raw}"/>')
    out.append(f'<polyline class="viz-ma" points="{ma_pts}"/>')
    out.append(f'<text class="viz-lab" x="{PL}" y="{H - 10}" text-anchor="start">{pairs[0][0][:7]}</text>')
    out.append(f'<text class="viz-lab" x="{W - PR}" y="{H - 10}" text-anchor="end">{pairs[-1][0][:7]}</text>')
    lx, ly = _x(n - 1), _y(pairs[-1][1])
    out.append(f'<circle class="viz-dot" cx="{lx:.1f}" cy="{ly:.1f}" r="3.5"/>')
    out.append(f'<text class="viz-val" x="{W - PR}" y="{ly - 7:.1f}" text-anchor="end">{pairs[-1][1]:.4f}</text>')
    out.append("</svg>")
    return "".join(out)


def fx_range_gauge_svg(history):
    """Range gauge: today's position within the 52-week high/low."""
    pairs = _fx_pairs(history)
    if len(pairs) < 2:
        return ""
    w = pairs[-260:] if len(pairs) >= 260 else pairs
    low = min(r for _, r in w)
    high = max(r for _, r in w)
    current = pairs[-1][1]
    if high <= low:
        return ""
    frac = (current - low) / (high - low)
    W, H, M = 560, 84, 48
    track_x, track_w = M, W - 2 * M
    track_y, track_h = 40, 12
    mx = track_x + frac * track_w
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="52-week range">']
    out.append(f'<rect class="viz-track" x="{track_x}" y="{track_y}" width="{track_w}" height="{track_h}" rx="{track_h / 2}"/>')
    out.append(f'<line class="viz-marker" x1="{mx:.1f}" y1="{track_y - 9}" x2="{mx:.1f}" y2="{track_y + track_h + 9}"/>')
    out.append(f'<circle class="viz-marker-dot" cx="{mx:.1f}" cy="{track_y + track_h / 2}" r="6"/>')
    out.append(f'<text class="viz-val" x="{mx:.1f}" y="{track_y - 15}" text-anchor="middle">{current:.4f} today</text>')
    out.append(f'<text class="viz-lab" x="{track_x}" y="{track_y + track_h + 26}" text-anchor="start">{low:.4f} low</text>')
    out.append(f'<text class="viz-lab" x="{track_x + track_w}" y="{track_y + track_h + 26}" text-anchor="end">{high:.4f} high</text>')
    out.append("</svg>")
    return "".join(out)


def fx_change_bars_svg(history):
    """Diverging bars: percent change over 1d/7d/30d/1y, green down / red up."""
    pairs = _fx_pairs(history)
    if len(pairs) < 2:
        return ""
    windows = [("1 day", 1), ("7 days", 5), ("30 days", 21), ("1 year", 260)]
    changes = []
    for label, n in windows:
        if len(pairs) > n:
            base = pairs[-1 - n][1]
            changes.append((label, (pairs[-1][1] - base) / base * 100))
        else:
            changes.append((label, 0.0))
    max_abs = max(abs(c) for _, c in changes) or 1.0
    W, LH, RH, ROW, PAD = 560, 72, 62, 30, 12
    half = (W - LH - RH) / 2
    center = LH + half
    H = PAD + len(changes) * ROW + PAD
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Recent moves">']
    out.append(f'<line class="viz-axis" x1="{center:.1f}" y1="{PAD - 4}" x2="{center:.1f}" y2="{H - PAD + 4}"/>')
    y = PAD + ROW / 2
    for label, pct in changes:
        bw = abs(pct) / max_abs * half
        out.append(f'<text class="viz-lab" x="{LH - 6}" y="{y + 3.5}" text-anchor="end">{label}</text>')
        if pct < 0:
            out.append(f'<rect class="viz-bar down" x="{center - bw:.1f}" y="{y - 8}" width="{bw:.1f}" height="16" rx="3"/>')
            out.append(f'<text class="viz-val" x="{center - bw - 6:.1f}" y="{y + 3.5}" text-anchor="end">{pct:+.2f}%</text>')
        else:
            out.append(f'<rect class="viz-bar up" x="{center:.1f}" y="{y - 8}" width="{bw:.1f}" height="16" rx="3"/>')
            out.append(f'<text class="viz-val" x="{center + bw + 6:.1f}" y="{y + 3.5}">{pct:+.2f}%</text>')
        y += ROW
    out.append("</svg>")
    return "".join(out)


def fx_band_scale_svg(band):
    """Segmented scale: noise/notable/material/alert with today's band marked."""
    segs = [("noise", "viz-seg-noise"), ("notable", "viz-seg-notable"),
            ("material", "viz-seg-material"), ("alert", "viz-seg-alert")]
    idx = next((i for i, (k, _) in enumerate(segs) if k == band), 1)
    W, H, M = 560, 74, 40
    sw = (W - 2 * M) / len(segs)
    track_y = 32
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Move band">']
    for i, (label, cls) in enumerate(segs):
        x = M + i * sw
        out.append(f'<rect class="viz-seg {cls}" x="{x + 2}" y="{track_y}" width="{sw - 4}" height="12" rx="3"/>')
        out.append(f'<text class="viz-lab" x="{x + sw / 2}" y="{track_y + 28}" text-anchor="middle">{label}</text>')
    mx = M + idx * sw + sw / 2
    out.append(f'<circle class="viz-marker-ring" cx="{mx:.1f}" cy="{track_y + 6}" r="8"/>')
    out.append(f'<text class="viz-val" x="{mx:.1f}" y="{track_y - 12}" text-anchor="middle">today: {band}</text>')
    out.append("</svg>")
    return "".join(out)


def fx_histogram_svg(history, bins=10):
    """Histogram: distribution of daily rates, current bucket highlighted."""
    pairs = _fx_pairs(history)
    if len(pairs) < 2:
        return ""
    vals = [r for _, r in pairs]
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        return ""
    bin_w = (hi - lo) / bins
    counts = [0] * bins
    for v in vals:
        i = min(int((v - lo) / bin_w), bins - 1)
        counts[i] += 1
    cur_i = min(int((pairs[-1][1] - lo) / bin_w), bins - 1)
    max_c = max(counts) or 1
    W, H, PAD, BL = 560, 220, 20, 26
    chart_h = H - PAD - BL
    col_w = (W - 2 * PAD) / bins
    out = [f'<svg class="viz" viewBox="0 0 {W} {H}" role="img" aria-label="Rate distribution">']
    for i, c in enumerate(counts):
        x = PAD + i * col_w
        bh = c / max_c * chart_h
        cls = "viz-hist active" if i == cur_i else "viz-hist"
        out.append(f'<rect class="{cls}" x="{x + 1}" y="{PAD + chart_h - bh:.1f}" width="{col_w - 2:.1f}" height="{bh:.1f}" rx="2"/>')
    out.append(f'<text class="viz-lab" x="{PAD}" y="{H - 8}" text-anchor="start">{lo:.4f}</text>')
    out.append(f'<text class="viz-lab" x="{W - PAD}" y="{H - 8}" text-anchor="end">{hi:.4f}</text>')
    out.append("</svg>")
    return "".join(out)
