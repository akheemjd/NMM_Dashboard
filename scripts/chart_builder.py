#!/usr/bin/env python3
"""Northern Mile branded chart generator.
Colors: Bold North palette.
Usage: from chart_builder import build_blog_charts; build_blog_charts()
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import json, os
from datetime import datetime

DATA = os.path.expanduser('~/northern-mile-dashboard/data')
OUT = os.path.expanduser('~/northern-mile-dashboard/web')

# Brand palette: Northern Road
PRIMARY = '#1a3a5c'     # Highway Blue
SECONDARY = '#c41e3a'   # Maple Red
MUTED = '#6b7280'       # Pavement Grey
GREEN = '#16a34a'       # Positive
AMBER = '#d97706'       # Caution
BG = '#f8f9fa'          # Snow White

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.spines.left': False,
    'axes.spines.bottom': False,
    'axes.grid': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'text.color': SECONDARY,
    'axes.labelcolor': MUTED,
    'xtick.color': MUTED,
    'ytick.color': MUTED,
})

def load_data(name):
    with open(os.path.join(DATA, f'{name}.json')) as f:
        return json.load(f)

def chart_fuel_prices():
    """Fuel prices by province — diesel vs gasoline."""
    fuel = load_data('fuel')
    ca = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NL']
    diesel = [fuel['provinces'][p]['diesel'] for p in ca]
    gasoline = [fuel['provinces'][p]['gasoline'] for p in ca]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    x = range(len(ca))
    w = 0.34

    # Bars with spacing
    bars1 = ax.bar([i - w/2 for i in x], diesel, w, color=PRIMARY, label='Diesel', edgecolor='white', linewidth=1)
    bars2 = ax.bar([i + w/2 for i in x], gasoline, w, color=SECONDARY, label='Gasoline', edgecolor='white', linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels(ca, fontsize=11, fontweight='600', color=PRIMARY)
    ax.set_ylabel('Cents per litre', fontsize=10, color=MUTED)

    # Legend top right
    ax.legend(frameon=False, fontsize=11, loc='upper right', handlelength=1, handleheight=1)

    # National averages in annotation box
    natl_d = fuel['diesel_national_avg']
    natl_g = fuel['gasoline_national_avg']
    ax.axhline(y=natl_d, color=PRIMARY, linestyle='--', linewidth=1, alpha=0.35)
    ax.axhline(y=natl_g, color=SECONDARY, linestyle='--', linewidth=1, alpha=0.35)

    ax.text(0.98, 0.95, f'Diesel avg  {natl_d}¢\nGas avg  {natl_g}¢',
            transform=ax.transAxes, fontsize=9, color=PRIMARY, ha='right', va='top',
            fontweight='600', linespacing=1.6,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e2e5e9', linewidth=0.5))

    # Value on highest bar only
    max_val = max(diesel + gasoline)
    max_idx = (diesel + gasoline).index(max_val)
    bar_list = list(bars1) + list(bars2)
    bar = bar_list[max_idx]
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f'{max_val:.0f}¢', ha='center', fontsize=10, fontweight='700', color=PRIMARY)

    ax.set_ylim(0, max(diesel + gasoline) * 1.15)
    ax.set_xlim(-0.6, len(ca) - 0.4)
    plt.tight_layout(pad=2)
    plt.savefig(os.path.join(OUT, 'chart-fuel-prices.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-fuel-prices.png'

def chart_exchange():
    """USD/CAD 30-day trend."""
    fx = load_data('exchange')
    history = fx.get('history', [])
    if not history: return None

    dates = [h['date'] for h in history]
    rates = [h['rate'] for h in history]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dates, rates, color=PRIMARY, linewidth=2, solid_capstyle='round')
    ax.fill_between(dates, rates, min(rates)-0.002, alpha=0.08, color=PRIMARY)
    
    # Key dates
    ax.set_ylabel('USD / CAD', fontsize=10)
    step = max(1, len(dates)//5)
    tick_idx = list(range(0, len(dates), step))
    if tick_idx[-1] != len(dates)-1:
        tick_idx.append(len(dates)-1)
    ax.set_xticks([dates[i] for i in tick_idx])
    ax.set_xticklabels([dates[i] for i in tick_idx], fontsize=8)
    
    # Min/max annotations
    min_val, max_val = min(rates), max(rates)
    min_idx = rates.index(min_val)
    max_idx = rates.index(max_val)
    ax.annotate(f'Low {min_val:.4f}', xy=(dates[min_idx], min_val),
                xytext=(dates[min_idx], min_val-0.003), fontsize=8, color=MUTED, ha='center')
    ax.annotate(f'High {max_val:.4f}', xy=(dates[max_idx], max_val),
                xytext=(dates[max_idx], max_val+0.003), fontsize=8, color=MUTED, ha='center')
    
    # Current value
    ax.annotate(f'{rates[-1]:.4f}', xy=(0.98, 0.92), xycoords='axes fraction',
                fontsize=16, fontweight='bold', color=PRIMARY, ha='right',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e2e5e9', linewidth=0.5))
    
    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(OUT, 'chart-exchange.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-exchange.png'

def chart_cost_breakdown():
    """Operating cost pie chart."""
    fig, ax = plt.subplots(figsize=(6.5, 5))
    labels = ['Fuel', 'Labour', 'Equipment\n& Maintenance', 'Insurance', 'Other']
    sizes = [30, 35, 15, 10, 10]
    colors = [PRIMARY, SECONDARY, AMBER, MUTED, '#cbd5e1']
    explode = (0.03, 0, 0, 0, 0)
    
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', startangle=90, pctdistance=0.72,
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},
        textprops={'fontsize': 10, 'fontweight': '600'}
    )
    for t in autotexts: t.set_fontsize(11); t.set_fontweight('700'); t.set_color('white')
    # Fuel label in secondary since it's on red
    autotexts[0].set_color(SECONDARY)
    
    ax.set_title('Where Your Operating Dollar Goes', fontsize=13, fontweight='700', pad=18, color=SECONDARY)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, 'chart-cost-breakdown.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-cost-breakdown.png'

def chart_diesel_spread():
    """Diesel price spread across provinces."""
    fuel = load_data('fuel')
    prods = ['BC','AB','ON','QC','MB','SK','NB','NS','PE','NL']
    values = [fuel['provinces'][p]['diesel'] for p in prods]
    
    # Sort by value descending
    pairs = sorted(zip(values, prods), reverse=True)
    values, prods = zip(*pairs)
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = [PRIMARY if v == max(values) else SECONDARY if v <= sorted(values)[1] else '#cbd5e1' for v in values]
    
    bars = ax.barh(prods, values, color=colors, height=0.6)
    ax.set_xlabel('Cents per litre', fontsize=10)
    
    # Value labels
    for bar, val in zip(bars, values):
        ax.text(val + 1.2, bar.get_y() + bar.get_height()/2, f'{val:.1f}¢',
                va='center', fontsize=11, fontweight='700', color=SECONDARY)
    
    # Spread callout
    spread = max(values) - min(values)
    ax.annotate(f'{spread:.1f}¢\nspread', xy=(0.98, 0.94), xycoords='axes fraction',
                fontsize=10, fontweight='700', color=PRIMARY, ha='right', va='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#e2e5e9'))
    
    ax.set_xlim(0, max(values) * 1.12)
    plt.tight_layout(pad=1.5)
    plt.savefig(os.path.join(OUT, 'chart-diesel-spread.png'), dpi=150, bbox_inches='tight')
    plt.close()
    return 'chart-diesel-spread.png'

def build_all():
    """Generate all blog charts."""
    results = []
    for fn in [chart_fuel_prices, chart_exchange, chart_cost_breakdown, chart_diesel_spread]:
        name = fn.__name__
        try:
            f = fn()
            if f:
                results.append(f)
                print(f'  {name} → {f}')
        except Exception as e:
            print(f'  {name} failed: {e}')
    print(f'\n{len(results)} charts saved to {OUT}/')
    return results

if __name__ == '__main__':
    print(f'Northern Mile Charts — {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    build_all()
