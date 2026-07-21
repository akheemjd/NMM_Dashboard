#!/usr/bin/env python3
"""Template fill engine v2 — .template.html files, nested tokens, loops, optionals, conditionals."""
import json, os, re, shutil
from datetime import datetime

BASE = os.path.expanduser("~/northern-mile-dashboard")
TMPL = os.path.join(BASE, "templates")
DATA = os.path.join(BASE, "data")
DOCS = os.path.join(BASE, "docs")
ASSETS = os.path.join(BASE, "assets")

def load_json(name):
    p = os.path.join(DATA, name + ".json")
    return json.load(open(p)) if os.path.exists(p) else {}

def resolve_token(data, token):
    """Resolve nested tokens like fuel.national_diesel, border.gauge_class"""
    parts = token.split(".")
    val = data
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        elif isinstance(val, list):
            # For loop context: item.key
            return val
        else:
            return None
    return val

def fill(template, data):
    """Fill a template with data."""

    # 1. Resolve {{nested.tokens}}
    def replace_token(match):
        key = match.group(1)
        val = resolve_token(data, key)
        if val is None:
            return ""  # clean missing tokens silently
        if isinstance(val, (dict, list)):
            return match.group(0)  # leave complex objects for loops
        return str(val)

    template = re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_token, template)

    # 2. LOOP blocks — repeat inner content per item
    template = fill_loops(template, data)

    # 3. OPTIONAL blocks — keep only if key exists and is truthy
    template = fill_optionals(template, data)

    # 4. IF blocks — keep if condition true
    template = fill_ifs(template, data)

    # 5. Build meta
    template = template.replace("{{updated_at}}", datetime.utcnow().strftime("%Y-%m-%d %H:%M"))
    template = template.replace("{{build_id}}", datetime.utcnow().strftime("%Y%m%d%H%M%S"))

    return template

def fill_loops(template, data):
    for match in re.finditer(r'<!--LOOP:(\w+(?:\.\w+)*)-->(.*?)<!--/LOOP:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        items = resolve_token(data, key)
        if not isinstance(items, list):
            items = []
        expanded = ""
        for item in items:
            block = inner
            if isinstance(item, dict):
                # Replace {{key}} within loop with item's keys
                for k, v in item.items():
                    block = block.replace("{{" + k + "}}", str(v) if not isinstance(v, (dict, list)) else "")
            expanded += block
        template = template.replace(match.group(0), expanded)
    return template

def fill_optionals(template, data):
    for match in re.finditer(r'<!--OPTIONAL:(\w+(?:\.\w+)*)-->(.*?)<!--/OPTIONAL:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        val = resolve_token(data, key)
        if val:
            template = template.replace(match.group(0), inner)
        else:
            template = template.replace(match.group(0), "")
    return template

def fill_ifs(template, data):
    for match in re.finditer(r'<!--IF:(\w+(?:\.\w+)*)-->(.*?)<!--/IF:\1-->', template, re.DOTALL):
        key = match.group(1)
        inner = match.group(2)
        val = resolve_token(data, key)
        if val:
            template = template.replace(match.group(0), inner)
        else:
            template = template.replace(match.group(0), "")
    return template

def build_page(name, data):
    """Build one page from template + data."""
    tmpl_path = os.path.join(TMPL, name + ".template.html")
    if not os.path.exists(tmpl_path):
        print(f"  SKIP: /{name}/ (no template)")
        return None

    with open(tmpl_path) as f:
        template = f.read()

    # Inject shared CSS/JS inline
    css_path = os.path.join(ASSETS, "styles.css")
    if os.path.exists(css_path) and "styles.css" not in template:
        with open(css_path) as f:
            template = template.replace("</head>", "<style>\n" + f.read() + "\n</style>\n</head>")

    js_path = os.path.join(ASSETS, "app.js")
    if os.path.exists(js_path) and "app.js" not in template:
        with open(js_path) as f:
            template = template.replace("</body>", "<script>\n" + f.read() + "\n</script>\n</body>")

    html = fill(template, data)

    # Write output
    dir_name = "" if name == "index" else name
    out_dir = os.path.join(DOCS, dir_name)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "index.html")
    with open(out_path, "w") as f:
        f.write(html)

    return len(html)

def build_all():
    print(f"Build started: {datetime.utcnow().isoformat()[:19]}")

    # Copy static assets
    for f in ["styles.css", "app.js", "leaflet.css", "leaflet.js"]:
        src = os.path.join(ASSETS, f) if os.path.exists(os.path.join(ASSETS, f)) else os.path.join(BASE, "docs", f)
        dst = os.path.join(DOCS, f)
        if os.path.exists(src) and src != dst:
            shutil.copy2(src, dst)

    # Load all data
    home_data = load_json("home")
    page_data = {
        "index": home_data,
        "fuel-prices": load_json("fuel"),
        "exchange-rate": load_json("fx"),
        "border-wait-times": load_json("border"),
        "road-incidents": load_json("incidents"),
        "cargo-theft": load_json("theft"),
        "market-pulse": load_json("market"),
        "industry-news": load_json("news"),
        "fuel-cost-calculator": load_json("fx"),  # reuses fx data
    }

    built = []
    for name in page_data:
        sz = build_page(name, page_data[name])
        if sz:
            built.append(f"  /{name if name != 'index' else ''} ({sz:,} bytes)")

    print(f"Built {len(built)} pages")
    for b in built:
        print(b)

if __name__ == "__main__":
    build_all()
