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
