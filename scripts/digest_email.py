#!/usr/bin/env python3
"""Northern Mile Dashboard — Weekly email digest builder and sender.

Reads raw JSON data files from the project's data/ directory, assembles a
plain-text digest in NMM voice, writes it to output/, and can send it via
SMTP using only Python stdlib (smtplib + email).

Entry points (via argparse):
    python scripts/digest_email.py              — generate only, no send
    python scripts/digest_email.py --send        — generate and send
    python scripts/digest_email.py --date YYYY-MM-DD  — override today
"""

import argparse
import json
import logging
import os
import re
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.text import MIMEText
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # fall back to manual YAML parsing below

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("nmm.digest")

# ---------------------------------------------------------------------------
# Minimal YAML reader (avoids requiring PyYAML when not installed)
# ---------------------------------------------------------------------------


def _parse_yaml(path):
    """Parse a simple YAML file without external dependencies.

    Supports scalar values, lists (- items), and one level of nesting.
    Raises ValueError if the file is too complex.
    """
    result = {}
    current_key = None

    with open(path, "r", encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, 1):
            stripped = raw.rstrip("\n\r")

            # skip blanks and comments
            if not stripped.strip() or stripped.strip().startswith("#"):
                continue

            indent = len(stripped) - len(stripped.lstrip())

            # top-level key
            if indent == 0 and ":" in stripped:
                current_key, _, val = stripped.partition(":")
                current_key = current_key.strip()
                val = val.strip().strip("\"'")
                if val:
                    # try numeric
                    try:
                        result[current_key] = int(val)
                    except ValueError:
                        try:
                            result[current_key] = float(val)
                        except ValueError:
                            result[current_key] = val
                else:
                    result[current_key] = []
                continue

            # list item under a key
            if indent > 0 and stripped.lstrip().startswith("- "):
                if current_key is not None:
                    item = stripped.lstrip()[2:].strip().strip("\"'")
                    result[current_key].append(item)
                continue

            # nested scalar (simple cases like port: 587 on next line)
            if indent > 0 and ":" in stripped and current_key is not None:
                k, _, v = stripped.partition(":")
                k = k.strip()
                v = v.strip().strip("\"'")
                if isinstance(result.get(current_key), dict):
                    result[current_key][k] = v
                elif isinstance(result.get(current_key), list):
                    # treat as continuation list item
                    result[current_key].append(v)

                continue

    return result


def load_config(config_path=None):
    """Load digest configuration from YAML (or fall back to defaults)."""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", "digest_config.yml",
        )

    if not os.path.exists(config_path):
        log.warning("Config not found at %s — using defaults", config_path)
        return {
            "smtp": {
                "host": "smtp.gmail.com",
                "port": 587,
                "sender_address": "digest@northernmilemedia.com",
                "password_env_var_name": "NMM_SMTP_PASSWORD",
                "use_tls": True,
            },
            "recipients": [],
            "subject_prefix": "[NMM]",
            "from_name": "Northern Mile",
        }

    if yaml is not None:
        with open(config_path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
    else:
        cfg = _parse_yaml(config_path)

    smtp = cfg.get("smtp", {})
    recipients = cfg.get("recipients", [])
    subject_prefix = cfg.get("subject_prefix", "[NMM]")
    from_name = cfg.get("from_name", "Northern Mile")

    return {
        "smtp": {
            "host": str(smtp.get("host", "smtp.gmail.com")),
            "port": int(smtp.get("port", 587)),
            "sender_address": smtp.get("sender_address", ""),
            "password_env_var_name": str(
                smtp.get("password_env_var_name", "NMM_SMTP_PASSWORD")
            ),
            "use_tls": bool(smtp.get("use_tls", True)),
        },
        "recipients": recipients if isinstance(recipients, list) else [recipients],
        "subject_prefix": str(subject_prefix),
        "from_name": str(from_name),
    }


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


def _load_json(path):
    """Read a JSON file, return dict or None on failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as e:
        log.warning("Failed to load %s: %s", path, e)
        return None


def get_fuel_data(project_root):
    """Return fuel.json parsed dict."""
    path = os.path.join(project_root, "data", "fuel.json")
    return _load_json(path)


def get_exchange_data(project_root):
    """Return exchange.json parsed dict."""
    path = os.path.join(project_root, "data", "exchange.json")
    return _load_json(path)


def get_border_data(project_root):
    """Return border.json parsed dict."""
    path = os.path.join(project_root, "data", "border.json")
    return _load_json(path)


def get_news_data(project_root):
    """Return news.json parsed dict."""
    path = os.path.join(project_root, "data", "news.json")
    return _load_json(path)


def get_incidents_data(project_root):
    """Return incidents.json parsed dict."""
    path = os.path.join(project_root, "data", "incidents.json")
    return _load_json(path)


# ---------------------------------------------------------------------------
# Section formatters — each produces plain text in NMM voice
# ---------------------------------------------------------------------------


def fmt_fuel(fuel):
    """Format diesel prices section."""
    lines = ["DIESEL PRICES", "=" * 20]

    if not fuel:
        lines.append("Diesel data unavailable.")
        return "\n".join(lines)

    prov = fuel.get("provinces", {})
    national = fuel.get("diesel_national_avg")
    print_date = fuel.get("print_date", "")

    if national is not None:
        lines.append(f"National average: {national}¢/L ({print_date})")
    else:
        lines.append("National average: unavailable")

    # Find cheapest and dearest provinces (skip YT/NT — excluded from index per template)
    ranked = []
    for code, info in prov.items():
        price = info.get("diesel")
        if price is not None and code not in ("YT", "NT"):
            ranked.append((code, price))
    ranked.sort(key=lambda x: x[1])

    if ranked:
        cheapest_code, cheapest_price = ranked[0]
        dearest_code, dearest_price = ranked[-1]
        spread = round(dearest_price - cheapest_price, 1)
        lines.append(
            f"{cheapest_code} {cheapest_price} -> {dearest_code} {dearest_price} · "
            f"spread {spread}¢/L"
        )
    else:
        lines.append("Provincial data incomplete")

    # Top 3 movers would need weekly deltas — show what we have
    total_provinces = sum(
        1 for p in prov.values() if p.get("diesel") is not None
    )
    lines.append(f"{total_provinces} provinces surveyed")

    lines.append("")
    return "\n".join(lines)


def fmt_exchange(exchange):
    """Format USD/CAD exchange rate section."""
    lines = ["EXCHANGE RATE", "=" * 20]

    if not exchange:
        lines.append("Exchange rate data unavailable.")
        return "\n".join(lines)

    current = exchange.get("current")
    obs_date = exchange.get("observation_date", "")
    change_pct = exchange.get("change_pct")

    if current is not None:
        label = "stronger" if change_pct and change_pct < 0 else "weaker" if change_pct and change_pct > 0 else "flat"
        pct_abs = abs(change_pct) if change_pct is not None else 0
        lines.append(f"USD/CAD: {current} on {obs_date}")
        lines.append(
            f"Loonie {label} {pct_abs:.2f}% today."
        )
        lines.append(f"A thousand US dollars converts to C${current*1000:.2f}.")
    else:
        lines.append("Exchange rate unavailable.")

    lines.append("")
    return "\n".join(lines)


def fmt_border(border):
    """Format border wait times section — highlight long delays."""
    lines = ["BORDER WAIT TIMES", "=" * 20]

    if not border:
        lines.append("Border data unavailable.")
        return "\n".join(lines)

    crossings = border.get("crossings", [])
    if not crossings:
        lines.append("No crossing data available.")
        return "\n".join(lines)

    # Sort by delay descending, show top 5
    sorted_crossings = sorted(
        crossings, key=lambda c: c.get("delay_minutes", 0), reverse=True
    )

    slowest_tagged = False
    for c in sorted_crossings[:5]:
        name = c.get("name", c.get("id", "?"))
        delay = c.get("delay", "unknown")
        delay_min = c.get("delay_minutes", 0)
        route = c.get("route", "")
        tag = ""
        if delay_min > 15:
            tag = " ⚠️ SLOW"
            slowest_tagged = True
        elif delay_min > 5:
            tag = ""
        else:
            tag = ""
        route_str = f"\u2014 {route}" if route else ""
        lines.append(f"{name}: {delay}{tag}{route_str}")

    lines.append("")
    return "\n".join(lines)


def fmt_news(news):
    """Format industry news section — Canadian flag first, top 5."""
    lines = ["INDUSTRY NEWS", "=" * 20]

    if not news:
        lines.append("News data unavailable.")
        return "\n".join(lines)

    headlines = news.get("headlines", [])
    if not headlines:
        lines.append("No headlines available.")
        return "\n".join(lines)

    # Canadian-flagged first, then rest
    canadian = [h for h in headlines if h.get("flag_canadian")]
    other = [h for h in headlines if not h.get("flag_canadian")]
    ordered = canadian + other

    for i, h in enumerate(ordered[:5]):
        source = h.get("source", "?")
        title = h.get("title", "Untitled")
        link = h.get("link", "")
        flag_tag = " [CA]" if h.get("flag_canadian") else ""
        link_str = f" ({link})" if link else ""
        lines.append(f"{i+1}. [{source}]{flag_tag} {title}{link_str}")

    lines.append("")
    return "\n".join(lines)


def fmt_incidents(incidents):
    """Format road incidents section — notable closures only."""
    lines = ["ROAD INCIDENTS", "=" * 20]

    if not incidents:
        lines.append("Incident data unavailable.")
        return "\n".join(lines)

    inc_list = incidents.get("incidents", [])
    if not inc_list:
        lines.append("No incident data available.")
        return "\n".join(lines)

    # Filter to meaningful events: collisions, fires, closures, major severity
    notable = []
    for inc in inc_list:
        event = (inc.get("event_type") or "").lower()
        severity = (inc.get("severity") or "").upper()
        desc = inc.get("description", "")
        highway = inc.get("highway", "?")
        province = inc.get("province", "?")

        # Skip minor maintenance/construction noise; focus on accidents, fires, closures
        is_accident = event in ("accidentsandincidents", "incident")
        is_closure = inc.get("closure", False)
        is_major = severity in ("MAJOR", "HIGH")
        is_fire = "fire" in desc.lower() or "collision" in desc.lower()

        if is_accident or is_closure or is_major or is_fire:
            # Extract key info from description
            desc_short = desc[:120].rstrip(".")
            notable.append({
                "highway": highway,
                "province": province,
                "desc": desc_short,
            })

    if not notable:
        lines.append("No significant incidents reported.")
        lines.append("")
        return "\n".join(lines)

    for n in notable[:5]:
        hwy = n["highway"]
        p = n["province"]
        d = n["desc"]
        lines.append(f"[{p}] {hwy}: {d}")

    lines.append("")
    return "\n".join(lines)


# Map of section names to formatters
SECTION_FORMATTERS = {
    "fuel": fmt_fuel,
    "exchange": fmt_exchange,
    "border": fmt_border,
    "news": fmt_news,
    "incidents": fmt_incidents,
}


# ---------------------------------------------------------------------------
# Format section dispatcher
# ---------------------------------------------------------------------------


def format_section(section_name, data, **kwargs):
    """Dispatch a named section to its formatter.

    Args:
        section_name: Key matching SECTION_FORMATTERS (e.g. 'fuel').
        data: Parsed dict from the corresponding JSON file.
        **kwargs: Unused placeholder for extensibility.

    Returns:
        Formatted plain-text string for this section.
    """
    fn = SECTION_FORMATTERS.get(section_name)
    if fn is None:
        log.warning("Unknown section: %s", section_name)
        return f"Section '{section_name}' \u2014 no formatter.\n\n"
    return fn(data)


# ---------------------------------------------------------------------------
# Main digest generator
# ---------------------------------------------------------------------------


def generate_digest(date_str=None, project_root=None, output_dir=None):
    """Build the full digest plain text from local JSON data files.

    Args:
        date_str: Override date string (YYYY-MM-DD). Defaults to today UTC.
        project_root: Project root directory. Defaults to parent of scripts/.
        output_dir: Where to write the digest file. Defaults to output/.

    Returns:
        Tuple of (plaintext_string, output_path).
    """
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Load all data sources
    fuel = get_fuel_data(project_root)
    exchange = get_exchange_data(project_root)
    border = get_border_data(project_root)
    news = get_news_data(project_root)
    incidents = get_incidents_data(project_root)

    # Build date display
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = dt.strftime("%A")
        readable = dt.strftime("%B %d, %Y")
    except ValueError:
        weekday, readable = "", date_str

    # Assemble header
    parts = []
    parts.append(f"Subject: Diesel, rates, borders \u2014 {readable}\n")
    parts.append("THE WEDNESDAY SNAPSHOT\n")
    parts.append(f"{readable}\n")
    parts.append("")

    # Generate each section
    for section in ("fuel", "exchange", "border", "news", "incidents"):
        data_map = {
            "fuel": fuel,
            "exchange": exchange,
            "border": border,
            "news": news,
            "incidents": incidents,
        }
        parts.append(format_section(section, data_map[section]))

    # Footer \u2014 always included
    parts.append("We send this every Wednesday. Get it in your inbox. Free.")
    parts.append("https://dashboard.northernmilemedia.com")
    parts.append("")
    parts.append(
        "Sources: Natural Resources Canada weekly diesel survey. Bank of Canada Valet API. "
        "CBSA (Canada Border Services Agency)."
    )

    plaintext = "\n".join(parts)

    # Write to output/
    if output_dir is None:
        output_dir = os.path.join(project_root, "output")
    os.makedirs(output_dir, exist_ok=True)
    safe_date = date_str.replace("-", "_")
    output_path = os.path.join(output_dir, f"digest_{safe_date}.txt")
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(plaintext)

    log.info("Digest written to %s", output_path)
    return plaintext, output_path


# ---------------------------------------------------------------------------
# Email sender
# ---------------------------------------------------------------------------


def send_digest(config_path=None, plaintext=None, date_str=None, smtp_password=None):
    """Generate (or accept) a digest and send it via SMTP.

    Failure to connect/send logs an error but does NOT raise or crash.

    Args:
        config_path: Path to digest_config.yml. Auto-discovered if omitted.
        plaintext: Pre-built digest text. Generated from data if omitted.
        date_str: Date override for filename/date display.
        smtp_password: Raw SMTP password (for testing). Loaded from env var normally.

    Returns:
        True if sent successfully, False otherwise.
    """
    config = load_config(config_path=config_path)
    smtp_cfg = config["smtp"]

    # Get password: explicit arg > environment variable
    password = smtp_password or os.environ.get(smtp_cfg["password_env_var_name"], "")
    if not password:
        log.error(
            "SMTP password missing \u2014 set env var %s or pass smtp_password.",
            smtp_cfg["password_env_var_name"],
        )
        return False

    sender_addr = smtp_cfg["sender_address"]
    recipients = config["recipients"]
    if not recipients:
        log.warning("No recipients configured \u2014 digest will NOT be sent.")
        # Still return True because generation succeeded; no send attempted.
        if plaintext is None:
            plaintext, _ = generate_digest(date_str=date_str)
        return True

    # Subject prefix + readable date
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        readable = dt.strftime("%B %d, %Y")
    except ValueError:
        readable = date_str

    subject_prefix = config.get("subject_prefix", "[NMM]")
    from_name = config.get("from_name", "Northern Mile")

    if plaintext is None:
        plaintext, _ = generate_digest(date_str=date_str)

    # Strip any leading Subject: line that may be embedded by generate_digest
    body = plaintext
    subject_line_match = re.match(r"^Subject:\s*(.*)", body, re.MULTILINE)
    subject_extra = subject_line_match.group(1).strip() if subject_line_match else ""
    if subject_extra:
        body = body[len(subject_line_match.group(0)):].lstrip("\n")

    full_subject = f"{subject_prefix} Diesel, rates, borders \u2014 {readable}"

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = full_subject
    msg["From"] = f"{from_name} <{sender_addr}>"
    msg["To"] = ", ".join(recipients)

    host = smtp_cfg["host"]
    port = int(smtp_cfg["port"])
    use_tls = bool(smtp_cfg.get("use_tls", True))

    try:
        if use_tls:
            server = smtplib.SMTP(host, port, timeout=30)
            server.ehlo()
            server.starttls()
            server.ehlo()
        else:
            server = smtplib.SMTP(host, port, timeout=30)
        server.login(sender_addr, password)
        server.sendmail(sender_addr, recipients, msg.as_string())
        server.quit()
        log.info("Digest sent to %s via %s:%s", recipients, host, port)
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("SMTP auth failed for %s. Check credentials.", sender_addr)
        return False
    except smtplib.SMTPException as e:
        log.error("SMTP error sending digest: %s", e)
        return False
    except OSError as e:
        log.error("Network error connecting to SMTP server %s:%s: %s", host, port, e)
        return False
    except Exception as e:
        log.error("Unexpected error sending digest: %s", e)
        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(generate_only=False, send=False, date=None, config=None):
    """CLI entry point for digest generation / sending."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "output")

    plaintext, output_path = generate_digest(date_str=date, project_root=project_root)
    print(f"Generated digest: {output_path}")
    print(f"Length: {len(plaintext)} chars, {plaintext.count(chr(10))+1} lines")

    if send:
        success = send_digest(plaintext=plaintext, date_str=date, config_path=config)
        if success:
            print("Digest sent (or skipped due to empty recipient list).")
        else:
            print("Failed to send digest.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NMM Weekly Digest")
    parser.add_argument("--generate-only", action="store_true", help="Generate only, do not send")
    parser.add_argument("--send", action="store_true", help="Send digest via SMTP")
    parser.add_argument("--date", default=None, help="Override date (YYYY-MM-DD)")
    parser.add_argument("--config", default=None, help="Path to digest_config.yml")
    args = parser.parse_args()

    main(
        generate_only=args.generate_only,
        send=args.send,
        date=args.date,
        config=args.config,
    )
