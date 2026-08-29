#!/usr/bin/env python3
"""Northern Mile Dashboard — Weekly email digest builder and sender.

Reads raw JSON data files from the project's data/ directory, assembles a
plain-text digest in NMM voice, writes it to output/, and can send it via
SMTP using only Python stdlib (smtplib + email).

Entry points (via argparse):
    python scripts/digest_email.py              -- generate only, print digest
    python scripts/digest_email.py --send        -- generate and send via SMTP
    python scripts/digest_email.py --dry-run     -- same as generate-only
    python scripts/digest_email.py --date YYYY-MM-DD  -- override today
"""

import argparse
import json
import logging
import os
import smtplib
import sys
from datetime import date, datetime
from email.mime.text import MIMEText
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
log = logging.getLogger("nmm_digest")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_FILE = PROJECT_ROOT / "config" / "digest_config.yml"
OUTPUT_DIR = PROJECT_ROOT / "output"

PROVINCE_NAMES = {
    "AB": "Alberta",
    "BC": "British Columbia",
    "MB": "Manitoba",
    "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador",
    "NS": "Nova Scotia",
    "NT": "Northwest Territories",
    "NU": "Nunavut",
    "ON": "Ontario",
    "PE": "Prince Edward Island",
    "QC": "Quebec",
    "SK": "Saskatchewan",
    "YT": "Yukon",
}


# ---------------------------------------------------------------------------
# Public helpers (imported by tests)
# ---------------------------------------------------------------------------


def _find_project_root():
    """Return path to repository root (parent of this scripts/ dir)."""
    return str(Path(__file__).resolve().parent.parent)


def load_json(name, data_dir=None):
    """Load a JSON file from the data directory by short name (e.g. 'fuel')."""
    if data_dir is None:
        dp = DATA_DIR
    else:
        dp = Path(data_dir) if isinstance(data_dir, str) else data_dir
    filepath = dp / f"{name}.json"
    try:
        with open(filepath, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        log.warning("Failed to load %s: %s", filepath, exc)
        return {}


def load_config(config_path=None):
    """Load YAML config from config/digest_config.yml."""
    if config_path is None:
        cp = CONFIG_FILE
    else:
        cp = Path(config_path) if isinstance(config_path, str) else config_path
    if yaml is None:
        return {}
    if not cp.exists():
        return {}
    try:
        with open(cp, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
            return cfg if isinstance(cfg, dict) else {}
    except Exception as exc:
        log.warning("Config parse error (%s); continuing without config.", exc)
        return {}


def _load_json(source_name, data_dir=None):
    """Internal alias for _load_json used internally by generators."""
    return load_json(source_name, data_dir=data_dir)


def _province_name(code):
    """Return full province name from a 2-letter code."""
    return PROVINCE_NAMES.get(code, code)


def format_section(name, items=None):
    """Format a section with bullet-like characters (middle dot).

    All arguments must be passed by keyword.

    Args:
        name: Section heading.
        items: List of item strings.

    Returns:
        Formatted string or '' if items is empty/None.
    """
    if not items:
        return ""
    sep = "-" * min(len(name), 20)
    lines = [f"{name}\n{sep}"] + [f"* {i}" for i in items]
    return "\n".join(lines) + "\n\n"


def generate_footer(source=None, url=None, unsubscribe_link=None):
    """Build the email footer.

    All arguments must be passed by keyword.

    Args:
        source: Attribution text. Defaults to 'Northern Mile Media Dashboard'.
        url: Dashboard URL.
        unsubscribe_link: Optional unsubscribe link.

    Returns:
        Footer string starting with '---'.
    """
    if source is None:
        source = "Northern Mile Media Dashboard"
    if url is None:
        url = "https://dashboard.northernmilemedia.com"
    lines = ["---"]
    lines.append(url)
    lines.append("")
    lines.append(source)
    if unsubscribe_link:
        lines.append(f"Unsubscribe: {unsubscribe_link}")
    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal section builders (return list[str])
# ---------------------------------------------------------------------------


def _fuel_section(data):
    """Top diesel prices by province (descending: highest first)."""
    items = []
    provinces = data.get("provinces")
    if not provinces:
        return items
    ranked = sorted(
        [
            (code, info["diesel"])
            for code, info in provinces.items()
            if isinstance(info, dict) and info.get("diesel") is not None
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    if not ranked:
        return items
    for code, price in ranked:
        pname = _province_name(code)
        items.append(f"{pname}: {price}c/L")
    return items


def _border_section(data):
    """Top border wait alerts (commercial crossings, slowest first)."""
    items = []
    crossings = data.get("crossings") or []
    com = [c for c in crossings if c.get("commercial")]
    com.sort(key=lambda c: c.get("delay_minutes", 0), reverse=True)

    if not com:
        return items

    seen_ids = set()
    for c in com[:3]:
        cid = c.get("id") or c.get("name", "unknown")
        if cid in seen_ids:
            continue
        seen_ids.add(cid)
        delay = c.get("delay_minutes", 0)
        name = c.get("name", c.get("id", "unknown"))
        route = c.get("route", "")
        if delay == 0:
            items.append(f"{name}: clear")
        else:
            suffix = f" ({route})" if route else ""
            items.append(f"{name}: {delay} min wait{suffix}")
    return items


def _market_pulse(data):
    """CAD/USD exchange rate pulse."""
    items = []
    current = data.get("current")
    change_pct = data.get("change_pct")
    obs_date_str = data.get("observation_date", "")

    if current is not None:
        direction = "up" if float(change_pct) > 0 else "steady" if change_pct is not None else "?"
        items.append(f"CAD/USD at {current:.4f} ({direction}). Obs: {obs_date_str}")
    else:
        items.append("No exchange rate data.")
    return items


def _incidents_section(data):
    """Weather extremes / major incidents."""
    items = []
    incidents = data.get("incidents", [])
    if not incidents:
        return items

    seen = set()
    for inc in incidents:
        sev = str(inc.get("severity", "")).upper()
        desc = inc.get("description") or ""
        if sev not in ("MAJOR", "CRITICAL") and "wildfire" not in desc.lower():
            continue
        iid = inc.get("id", "")
        if iid in seen:
            continue
        seen.add(iid)
        prov = inc.get("province", "?")
        hwy = inc.get("highway", "")
        if isinstance(hwy, dict):
            hwy = hwy.get("name", "")
        short = (desc or "")[:90]
        # Avoid repeating highway name if it already appears in the description
        if isinstance(hwy, str) and hwy and hwy.lower() in desc.lower():
            items.append(f"{prov}: {short}")
        else:
            items.append(f"{prov} | {hwy}: {short}")
        if len(items) >= 5:
            break
    return items


def _news_section(data):
    """Top news headlines (Canadian-flagged first, newest)."""
    items = []
    headlines = data.get("headlines", [])
    if not headlines:
        return items

    canadian = sorted(
        [h for h in headlines if h.get("flag_canadian")],
        key=lambda h: h.get("date_iso", ""),
        reverse=True,
    )
    others = sorted(
        [h for h in headlines if not h.get("flag_canadian")],
        key=lambda h: h.get("date_iso", ""),
        reverse=True,
    )
    combined = canadian + others

    count = 0
    for h in combined:
        title = h.get("title", "Untitled")
        src = h.get("source", "")
        items.append(f"[{src}] {title}")
        count += 1
        if count >= 3:
            break
    return items


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------


def generate_digest(
    data_dir="",
    output_dir="",
    footer_source="Northern Mile Media Dashboard",
    footer_url="https://dashboard.northernmilemedia.com",
    footer_unsubscribe=None,
    today_override=None,
):
    """Assemble the full digest email body from dashboard JSON files.

    Reads fuel.json, exchange.json, border.json, news.json, incidents.json
    from ./data/ (or a custom directory) and writes plain-text to ./output/.

    All arguments must be passed by keyword.

    Args:
        data_dir: Override data directory path. Empty string uses default ./data/.
        output_dir: Override output directory path. Empty string uses default ./output/.
        footer_source: Attribution text for footer.
        footer_url: Dashboard URL for footer.
        footer_unsubscribe: Optional unsubscribe link.
        today_override: Date string YYYY-MM-DD to use instead of today.

    Returns:
        The complete digest body string.
    """
    global DATA_DIR, OUTPUT_DIR

    if data_dir:
        DATA_DIR = Path(data_dir)
    if output_dir:
        OUTPUT_DIR = Path(output_dir)

    if today_override:
        today = datetime.strptime(today_override, "%Y-%m-%d").date()
    else:
        today = date.today()
    date_str = today.isoformat()

    # Load data sources
    fuel = load_json("fuel")
    exchange = load_json("exchange")
    border = load_json("border")
    news = load_json("news")
    incidents = load_json("incidents")

    # Build sections
    parts = []

    # Header — direct, no throat-clearing
    parts.append(f"NORTHERN MILE DIGEST — {date_str}")
    parts.append("=" * 48)

    fuel_items = _fuel_section(fuel)
    block = format_section("DIESEL PRICES", fuel_items)
    if block:
        parts.append(block)
    else:
        parts.append("DIESEL PRICES\n====================\n\nNo fuel data available.\n\n")

    border_items = _border_section(border)
    block = format_section("BORDER ALERTS", border_items)
    if block:
        parts.append(block)
    else:
        parts.append("BORDER ALERTS\n====================\n\nNo border data available.\n\n")

    market_items = _market_pulse(exchange)
    block = format_section("MARKET PULSE", market_items)
    if block:
        parts.append(block)
    else:
        parts.append("MARKET PULSE\n====================\n\nNo exchange rate data.\n\n")

    incident_items = _incidents_section(incidents)
    block = format_section("ACTIVE INCIDENTS", incident_items)
    if block:
        parts.append(block)
    else:
        parts.append("ACTIVE INCIDENTS\n====================\n\nNo active incidents.\n\n")

    news_items = _news_section(news)
    block = format_section("HEADLINES", news_items)
    if block:
        parts.append(block)
    else:
        parts.append("HEADLINES\n====================\n\nNo news available.\n\n")

    parts.append(generate_footer(
        source=footer_source,
        url=footer_url,
        unsubscribe_link=footer_unsubscribe,
    ))

    body = "\n\n".join(parts)

    # Write output file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"digest_{date_str}.txt"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    log.info("Digest written to %s", out_path)

    return body


# ---------------------------------------------------------------------------
# Email sending
# ---------------------------------------------------------------------------


def send_digest(
    body,
    subject="Northern Mile Digest",
    to_addresses=None,
    from_address=None,
    smtp_host="localhost",
    smtp_port=587,
    password_env_var="SMTP_PASSWORD",
    password=None,
):
    """Send the digest body via SMTP.

    Uses Python built-in smtplib. Password comes from environment variable
    named in config — never hardcoded. On failure logs but does not raise.

    All arguments must be passed by keyword.

    Args:
        body: Full digest body text.
        subject: Email subject line.
        to_addresses: Recipient addresses. Falls back to config recipients.
        from_address: Sender address. Falls back to config sender_address.
        smtp_host: SMTP hostname. Falls back to config.
        smtp_port: SMTP port. Falls back to config.
        password_env_var: Env var name holding the password. From config.
        password: Direct password override. If None, reads from env var.

    Returns:
        True if sent successfully, False otherwise.
    """
    config = load_config()

    if not to_addresses and config.get("recipients"):
        to_addresses = list(config["recipients"])
    if not from_address and config.get("sender_address"):
        from_address = str(config["sender_address"])
    if smtp_host == "localhost" and config.get("smtp_host"):
        smtp_host = str(config["smtp_host"])
    if smtp_port == 587 and config.get("smtp_port"):
        smtp_port = int(config["smtp_port"])
    if not password_env_var and config.get("password_env_var_name"):
        password_env_var = str(config["password_env_var_name"])

    to_addresses = to_addresses or ["nobody@example.com"]
    from_address = from_address or "digest@nmd.ca"

    # Resolve password
    if password is None:
        password = os.environ.get(password_env_var)
        if not password:
            log.error("No SMTP password found. Set env var %s", password_env_var)
            return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(to_addresses)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(from_address, password)
            server.sendmail(from_address, to_addresses, msg.as_string())
        log.info("Digest sent to %s", to_addresses)
        return True
    except Exception as exc:
        log.error("Email send failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv=None):
    """CLI entry point. Supports --send, --dry-run, --date, --generate-only flags."""
    parser = argparse.ArgumentParser(description="NMM Dashboard Email Digest")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send digest via SMTP (requires SMTP credentials)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        dest="dry_run",
        help="Generate digest but do not send",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        default=False,
        dest="generate_only",
        help="Just generate and print the digest (same as omitting --send)",
    )
    parser.add_argument(
        "--subject",
        type=str,
        default="Northern Mile Digest",
        help="Email subject line",
    )
    parser.add_argument(
        "--to",
        type=str,
        action="append",
        default=None,
        help="Recipient address (repeat for multiple)",
    )
    parser.add_argument(
        "--from-addr",
        type=str,
        default=None,
        help="Sender email address",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        dest="date_override",
        help="Override today's date (YYYY-MM-DD)",
    )

    args = parser.parse_args(argv)

    # Generate digest
    try:
        body = generate_digest(today_override=args.date_override)
    except Exception as exc:
        log.error("Failed to generate digest: %s", exc)
        return 1

    # Dry-run or generate-only: print and exit
    if args.dry_run or args.generate_only or not args.send:
        print(body)
        return 0

    # Attempt to send
    success = send_digest(
        body=body,
        subject=args.subject,
        to_addresses=args.to,
        from_address=args.from_addr,
    )
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
