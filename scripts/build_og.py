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
BG = "#15171A"
INK = "#E8EAEC"
MUTED = "#8B939C"
AMBER = "#F2A900"

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def build_fuel_card():
    with open(os.path.join(DATA, "fuel.json")) as f:
        fuel = json.load(f)
    nat = fuel["diesel_national_avg"]
    print_date = fuel.get("print_date", "")

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.text((70, 70), "NORTHERN MILE", font=font("DejaVuSans-Bold.ttf", 28), fill=AMBER)
    d.text((70, 115), "Canadian Diesel Prices by Province",
           font=font("DejaVuSans.ttf", 34), fill=MUTED)

    d.text((70, 210), f"{nat:.1f}", font=font("DejaVuSans-Bold.ttf", 150), fill=INK)
    d.text((70, 375), "cents per litre  ·  NMDI national average",
           font=font("DejaVuSans.ttf", 30), fill=MUTED)

    provs = fuel.get("provinces", {})
    idx = ["BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL"]
    vals = [(c, provs[c]["diesel"]) for c in idx if c in provs]
    if vals:
        lo = min(vals, key=lambda x: x[1])
        hi = max(vals, key=lambda x: x[1])
        d.text((70, 460),
               f"Low {lo[0]} {lo[1]:.1f}     High {hi[0]} {hi[1]:.1f}     Spread {hi[1]-lo[1]:.1f}",
               font=font("DejaVuSans.ttf", 30), fill=INK)

    d.text((70, 545), f"NRCan weekly survey · {print_date}",
           font=font("DejaVuSans.ttf", 24), fill=MUTED)
    d.text((70, 578), "dashboard.northernmilemedia.com",
           font=font("DejaVuSans.ttf", 24), fill=AMBER)

    out = os.path.join(DOCS, "og-fuel.jpg")
    img.save(out, "JPEG", quality=88)
    print(f"  og-fuel.jpg written ({nat:.1f})")


if __name__ == "__main__":
    build_fuel_card()
