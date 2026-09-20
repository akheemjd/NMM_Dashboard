#!/usr/bin/env python3
"""Fetch static font weights for the NMM brand faces.

Google's CSS API returns per-weight static TrueType files when requested
without a browser user agent string. Variable fonts render too light in
matplotlib (it resolves them to the default instance weight), so we want
the static cuts.

Writes into assets/fonts/ as <Family>-<Weight>.ttf
"""

import re
import sys
import urllib.request
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

FAMILIES = {
    "Inter": "Inter:wght@400;500;600;700",
    "SpaceGrotesk": "Space+Grotesk:wght@400;500;600;700",
    "IBMPlexMono": "IBM+Plex+Mono:wght@400;500;600",
}

CSS_URL = "https://fonts.googleapis.com/css2?family={spec}"
UA = "curl/8.0"  # a non-browser UA gets us TTF rather than woff2


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", errors="replace")


def main():
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    for family, spec in FAMILIES.items():
        try:
            css = fetch(CSS_URL.format(spec=spec))
        except Exception as e:
            print(f"  {family}: CSS fetch failed: {e}")
            continue

        # Each @font-face block carries a weight and a src url
        blocks = re.findall(
            r"font-weight:\s*(\d+);.*?url\((https://[^)]+\.ttf)\)",
            css, re.DOTALL
        )
        if not blocks:
            print(f"  {family}: no TTF urls in CSS")
            continue

        for weight, url in blocks:
            out = FONT_DIR / f"{family}-{weight}.ttf"
            try:
                data = fetch(url, binary=True)
                out.write_bytes(data)
                print(f"  {out.name:28} {len(data) // 1024:>4} KB")
                total += 1
            except Exception as e:
                print(f"  {family}-{weight}: download failed: {e}")

    print(f"\n{total} font files in {FONT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
