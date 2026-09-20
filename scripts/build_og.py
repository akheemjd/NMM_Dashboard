#!/usr/bin/env python3
"""Generate og:image cards as build artifacts. No static files to lose."""
import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")

W, H = 1200, 630

# Brand tokens, matched to assets/nm.css. This card is what every share of the
# dashboard looks like, so it carries the identity. It previously used the
# retired dark/amber palette (#0B0D11 / #F5C518) and DejaVu, so a share of the
# site looked like a different product to the site itself.
PAPER = "#FBFAF8"
INK = "#1A1A17"
MUTED = "#6B6862"
SIGNAL = "#0B5D3B"
LINE = "#E8E4DD"

# Build-only TTFs, the same set blog_visuals.py uses. assets/ is copied to the
# published site, so fonts live in fonts/ and are never deployed.
FONT_DIR = os.path.join(ROOT, "fonts")
FACES = {
    "display": ("SpaceGrotesk-600.ttf", "SpaceGrotesk-500.ttf"),
    "display-bold": ("SpaceGrotesk-700.ttf", "SpaceGrotesk-600.ttf"),
    "body": ("Inter-400.ttf", "Inter-500.ttf"),
    "bold": ("Inter-600.ttf", "Inter-700.ttf"),
    "number": ("IBMPlexMono-600.ttf", "IBMPlexMono-500.ttf"),
}


def font(face, size):
    """Resolve a brand face. System fonts are a last resort, not the default."""
    for name in FACES.get(face, (face,)):
        path = os.path.join(FONT_DIR, name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    for path in ("C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_fuel_card():
    with open(os.path.join(DATA, "fuel.json")) as f:
        fuel = json.load(f)
    nat = fuel["diesel_national_avg"]
    print_date = fuel.get("print_date", "")

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.text((70, 70), "NORTHERN MILE", font=font("display-bold", 28), fill=SIGNAL)
    d.text((70, 115), "Canadian Diesel Prices by Province",
           font=font("body", 34), fill=MUTED)

    d.text((70, 205), f"{nat:.1f}", font=font("number", 150), fill=INK)
    d.text((70, 375), "cents per litre  ·  NMDI national average",
           font=font("body", 30), fill=MUTED)

    provs = fuel.get("provinces", {})
    idx = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]
    vals = [(c, provs[c]["diesel"]) for c in idx if c in provs]
    if vals:
        lo = min(vals, key=lambda x: x[1])
        hi = max(vals, key=lambda x: x[1])
        d.text((70, 460),
               f"Low {lo[0]} {lo[1]:.1f}     High {hi[0]} {hi[1]:.1f}     Spread {hi[1]-lo[1]:.1f}",
               font=font("number", 30), fill=INK)

    d.text((70, 545), f"NRCan weekly survey · {print_date}",
           font=font("body", 24), fill=MUTED)
    d.text((70, 578), "dashboard.northernmilemedia.com",
           font=font("bold", 24), fill=SIGNAL)

    out = os.path.join(DOCS, "og-fuel.jpg")
    img.save(out, "JPEG", quality=88)
    print(f"  og-fuel.jpg written ({nat:.1f})")


def build_home_card():
    with open(os.path.join(DATA, "fuel.json")) as f:
        fuel = json.load(f)
    with open(os.path.join(DATA, "exchange.json")) as f:
        fx = json.load(f)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    d.text((70, 70), "NORTHERN MILE", font=font("display-bold", 28), fill=SIGNAL)
    d.text((70, 115), "Canadian trucking data, published daily",
           font=font("body", 32), fill=MUTED)

    d.text((70, 215), f"{fuel['diesel_national_avg']:.1f}",
           font=font("number", 96), fill=INK)
    d.text((70, 330), "NMDI  ·  cents per litre",
           font=font("body", 26), fill=MUTED)

    d.text((640, 215), f"{fx['current']:.4f}",
           font=font("number", 96), fill=INK)
    d.text((640, 330), "USD/CAD  ·  Bank of Canada",
           font=font("body", 26), fill=MUTED)

    d.text((70, 440), "Diesel  ·  Border waits  ·  Exchange  ·  Cargo theft",
           font=font("body", 30), fill=INK)

    d.text((70, 545), f"NRCan survey {fuel.get('print_date','')}  ·  BoC {fx.get('observation_date','')}",
           font=font("body", 22), fill=MUTED)
    d.text((70, 578), "dashboard.northernmilemedia.com",
           font=font("bold", 24), fill=SIGNAL)

    img.save(os.path.join(DOCS, "og.jpg"), "JPEG", quality=88)
    print("  og.jpg written")


if __name__ == "__main__":
    build_fuel_card()
    build_home_card()
