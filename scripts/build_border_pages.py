#!/usr/bin/env python3
"""Border crossing page builder — programmatic SEO layer.

Renders templates/border-crossing.template.html once per CBSA crossing,
writing docs/border-wait-times/<slug>/index.html. Each page carries a
hand-written context paragraph from content/border/<slug>.md (a missing or
too-thin prose block is a build failure, same as the city pages).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TMPL = os.path.join(ROOT, "templates")
DOCS = os.path.join(ROOT, "docs")
CONTENT = os.path.join(ROOT, "content", "border")

sys.path.insert(0, HERE)
from build_templates import fill  # noqa: E402

MIN_PROSE_CHARS = 200  # ~30 words; below this the page is thin


# CBP labels that are the same physical crossing as an existing CBSA page. The pages stay
# where they are; this only stops the American pass building a second URL for the same bridge.
CBSA_EQUIVALENT = {
    "pacific-highway",          # -> pacific-highway-crossing
    "peace-arch",               # -> the same Blaine complex
    "peace-bridge",
    "bluewater-bridge",         # -> blue-water-bridge
    "ambassador-bridge",
    "thousand-islands-bridge",
    "lewiston-bridge",          # -> queenston-lewiston-bridge
    "champlain",                # -> lacolle-border-crossing
    "pembina",                  # -> emerson-pembina
    "sweetgrass",               # -> coutts-sweetgrass
}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def load_json(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def load_prose(slug):
    path = os.path.join(CONTENT, f"{slug}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{slug}: no prose at {path}. Crossing pages are not built from data alone."
        )
    with open(path) as f:
        prose = f.read().strip()
    body = re.sub(r"<!--.*?-->", "", prose, flags=re.DOTALL).strip()
    if len(body) < MIN_PROSE_CHARS:
        raise ValueError(
            f"{slug}: prose body is {len(body)} chars, minimum {MIN_PROSE_CHARS}. "
            f"Too thin to justify the page."
        )
    return prose


def main():
    border = load_json("border.norm.json")
    crossings = border.get("crossings") or []
    if not crossings:
        raise ValueError("border.norm.json has no crossings — refusing to build")

    home = load_json("home.norm.json")
    updated_at = home.get("updated_at", "")
    updated_iso = home.get("updated_iso", "")
    build_version = home.get("build_version", "")

    with open(os.path.join(TMPL, "border-crossing.template.html")) as f:
        template = f.read()

    siblings = [{
        "slug": slugify(c.get("name", "")),
        "name": c.get("name", ""),
        "wait": c.get("wait", ""),
        "status_label": c.get("status_label", ""),
        "status_class": c.get("status_class", ""),
    } for c in crossings]

    # ---- the American side ----
    # CBP publishes thirty Canadian-border ports. Nothing read this file, so nineteen of them
    # had no page while we held a live reading for each. Same template, same prose rule.
    us_ports = []
    try:
        _cbp = load_json("cbp_border.json")
        _have = {slugify(c.get("name", "")) for c in crossings}
        for _port in _cbp.get("ports", []):
            if not (_port.get("border") or "").startswith("Canadian"):
                continue
            _label = _port.get("label") or _port.get("port_name") or ""
            _slug = slugify(_label)
            if not _slug or _slug in _have:
                continue
            # The two agencies name the same crossing differently. CBSA's Pacific Highway page
            # is "pacific-highway-crossing" and CBP calls the port "Pacific Highway"; CBSA says
            # "Lacolle" where CBP says "Champlain". Without this map the builder either
            # duplicates a crossing under two URLs or fails looking for prose that should not
            # exist. Every entry here already has a page.
            if _slug in CBSA_EQUIVALENT:
                continue
            _delay = _port.get("commercial_delay")
            _reported = bool(_port.get("commercial_reported")) and _delay is not None
            # an unmeasured lane is not a clear lane
            _wait = f"{_delay} min" if _reported else "not reported"
            _status = ((_port.get("commercial") or {}).get("standard") or {}).get("status") or ""
            if not _reported:
                _status = "not reported"
            _sub_bits = [_port.get("us_state") or "", _port.get("ca_province") or ""]
            _sub = "\u2013".join([b for b in _sub_bits if b])
            if _port.get("ca_city"):
                _sub = f"{_sub} \u2192 {_port['ca_city']}"
            us_ports.append({
                "slug": _slug,
                "name": _label,
                "wait": _wait,
                "status_label": _status,
                "status_class": "hi" if (_reported and _delay and _delay > 0) else "lo",
                "sub": _sub,
            })
    except Exception as e:
        print(f"  CBP ports skipped: {e}")

    siblings = siblings + [{
        "slug": u["slug"], "name": u["name"], "wait": u["wait"],
        "status_label": u["status_label"], "status_class": u["status_class"],
    } for u in us_ports]

    seen = {}
    built = 0
    us_built = 0
    for c in crossings:
        slug = slugify(c.get("name", ""))
        if slug in seen and seen[slug] != c.get("name"):
            raise ValueError(f"crossing slug collision: '{slug}' maps to both "
                             f"{seen[slug]} and {c.get('name')}")
        seen[slug] = c.get("name")

        data = {
            "name": c.get("name", ""),
            "slug": slug,
            "wait": c.get("wait", ""),
            "status_label": c.get("status_label", ""),
            "status_class": c.get("status_class", ""),
            "sub": c.get("sub", ""),
            "agency": "CBSA",
            "prose": load_prose(slug),
            "siblings": [s for s in siblings if s["slug"] != slug],
            "updated_at": updated_at,
            "updated_iso": updated_iso,
            "build_version": build_version,
        }
        html = fill(template, data)
        leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:", "<!--OPTIONAL:") if t in html]
        if leftover:
            raise ValueError(f"{slug}: unresolved template markup remains: {leftover}")

        out_dir = os.path.join(DOCS, "border-wait-times", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(html)
        built += 1

    for u in us_ports:
        slug = u["slug"]
        if slug in seen:
            raise ValueError(f"crossing slug collision: '{slug}' is both a CBSA and a CBP port")
        seen[slug] = u["name"]
        data = {
            "name": u["name"],
            "slug": slug,
            "wait": u["wait"],
            "status_label": u["status_label"],
            "status_class": u["status_class"],
            "sub": u["sub"],
            "agency": "CBP",
            "prose": load_prose(slug),
            "siblings": [x for x in siblings if x["slug"] != slug],
            "updated_at": updated_at,
            "updated_iso": updated_iso,
            "build_version": build_version,
        }
        html = fill(template, data)
        leftover = [t for t in ("{{", "<!--LOOP:", "<!--IF:", "<!--OPTIONAL:") if t in html]
        if leftover:
            raise ValueError(f"{slug}: unresolved template markup remains: {leftover}")
        out_dir = os.path.join(DOCS, "border-wait-times", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(html)
        us_built += 1

    print(f"Built {built} Canadian crossing pages and {us_built} American port pages")


if __name__ == "__main__":
    main()
