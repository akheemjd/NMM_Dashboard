# Northern Mile Media — Email Digest System

## Overview

`scripts/digest_email.py` generates a plain-text weekly email digest from the project's local JSON data files (fuel, exchange, border, news, incidents) and optionally sends it via SMTP. Uses **only Python standard library** — no pip install needed.

## Quick start

```bash
# Generate digest only (writes to output/digest_YYYY-MM-DD.txt)
python scripts/digest_email.py --date 2026-08-29

# Generate and send via SMTP
python scripts/digest_email.py --send --date 2026-08-29

# Override config path and password for testing
python scripts/digest_email.py --send \
  --config config/digest_config.yml \
  --smtp-password "your-gmail-app-password"
```

## Configuration

### config/digest_config.yml

```yaml
smtp:
  host: "smtp.gmail.com"      # Your SMTP server
  port: 587                    # TLS port (use 465 for SSL)
  sender_address: "digest@northernmilemedia.com"
  password_env_var_name: "NMM_SMTP_PASSWORD"   # env var holding the password
  use_tls: true

recipients:
  - "subscriber-list@example.com"

subject_prefix: "[NMM]"
from_name: "Northern Mile"
```

### Setting the SMTP password

The password must come from an environment variable — never hard-coded. For Gmail:

```bash
# Linux/Mac
export NMM_SMTP_PASSWORD="your-app-password-here"

# Windows (PowerShell)
$env:NMM_SMTP_PASSWORD="your-app-password-here"
```

For Gmail you need an [App Password](https://support.google.com/accounts/answer/185833), not your regular password. Enable 2-Step Verification first, then generate one under Security > App Passwords.

## Manual trigger

Run manually from the project root:

```bash
# From the terminal:
python scripts/digest_email.py --send
```

Or set up a cron job:

```cron
# Every Wednesday at 06:00 UTC (Canadian truckers' morning)
0 6 * * 3 cd /path/to/northern-mile-dashboard && python scripts/digest_email.py --send >> /var/log/nmm-digest.log 2>&1
```

## Project integration

The digest can be triggered after `deploy.sh` completes by adding this line near the end:

```bash
# After successful deploy, send digest (optional)
python scripts/digest_email.py --send || echo "Digest send skipped (non-fatal)" >&2
```

The `--send` flag uses `|| echo ...` so a failed email send does NOT break the deployment pipeline.

## What sections are included?

| Section | Data source | Description |
|---------|-------------|-------------|
| Diesel Prices | `data/fuel.json` | National avg, cheapest/dearest province, spread |
| Exchange Rate | `data/exchange.json` | USD/CAD rate with daily move % |
| Border Wait Times | `data/border.json` | Top 5 crossings sorted by delay, slow alerts |
| Industry News | `data/news.json` | Top 5 headlines, Canadian-flagged first |
| Road Incidents | `data/incidents.json` | Notable closures, collisions, fires |

Each section is formatted in NMM voice: direct, short sentences, numbers speak for themselves. No throat-clearing intros.

## Testing

```bash
# Run all tests (requires pytest)
python -m pytest tests/test_digest.py -v

# Or compile-check without pytest
python -c "import py_compile; py_compile.compile('tests/test_digest.py', doraise=True)"
```

Tests cover:
- `generate_digest()` — file creation, content checks per section, missing data handling
- `format_section()` — dispatcher for known/unknown sections, slow-border alert
- `load_config()` — defaults when file missing, real YAML loading
- `send_digest()` — mocked SMTP success/auth failure/connection error/no recipients/no password
- Edge cases — fuel national avg None, empty crossings, minor-only incidents, headline ordering

## API reference

All public functions accept keyword arguments only.

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `generate_digest(date_str=None, project_root=None, output_dir=None)` | `(str, str, str)` | `(plaintext, output_path)` | Build digest text from JSON files |
| `format_section(section_name, data)` | `(str, dict)` | `str` | Dispatch section to formatter |
| `send_digest(config_path=None, plaintext=None, date_str=None, smtp_password=None)` | optional | `bool` | Send via SMTP, False on any error |

Sections: `"fuel"`, `"exchange"`, `"border"`, `"news"`, `"incidents"`
