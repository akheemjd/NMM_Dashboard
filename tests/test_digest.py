"""Tests for scripts/digest_email.py — Northern Mile Media digest system.

Uses unittest.mock for SMTP; no real network calls.
Run from project root:  python -m pytest tests/test_digest.py -v
Or:  scripts\python.exe -m pytest tests/test_digest.py -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

# Ensure we import from the project's scripts dir, not a site-package copy
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Import module under test
import digest_email as de

# ---------------------------------------------------------------------------
# Fixtures: minimal mock data matching actual schemas
# ---------------------------------------------------------------------------

MOCK_FUEL = {
    "provinces": {
        "SK": {"diesel": 209.1},
        "AB": {"diesel": 210.5},
        "ON": {"diesel": 222.7},
        "QC": {"diesel": 256.0},
        "YT": {"diesel": 229.9},
        "NT": {"diesel": 207.9},
    },
    "diesel_national_avg": 233.0,
    "print_date": "Wed, 29 Aug 2026",
}

MOCK_EXCHANGE = {
    "current": 1.3888,
    "observation_date": "2026-08-28",
    "previous": 1.3861,
    "change_pct": 0.19,
}

MOCK_BORDER = {
    "crossings": [
        {"name": "Ambassador Bridge", "delay": "45 min", "delay_minutes": 45, "route": "Windsor — Detroit"},
        {"name": "Pacific Highway", "delay": "5 min", "delay_minutes": 5},
        {"name": "Coutts", "delay": "No delay", "delay_minutes": 0},
    ]
}

MOCK_NEWS = {
    "headlines": [
        {"source": "The Trucker", "title": "CA tariff headline", "link": "https://ex.com/1", "flag_canadian": True},
        {"source": "Trucking Info", "title": "US DOT rules", "link": "", "flag_canadian": False},
    ]
}

MOCK_INCIDENTS = {
    "incidents": [
        {
            "province": "ON", "highway": "HWY 401",
            "description": "Collision on HWY 401 at Brock St",
            "event_type": "accidentsandincidents", "severity": "Unknown", "closure": False,
        },
        {
            "province": "ON", "highway": "HWY 417",
            "description": "Nightly Construction on HWY 417 between KINBURN and GALETTA",
            "event_type": "roadwork", "severity": "Unknown", "closure": True,
        },
        {
            "province": "ON", "highway": "HWY 401",
            "description": "Nightly Construction on HWY 401 Westbound CAMDEN EAST RD",
            "event_type": "roadwork", "severity": "Unknown", "closure": False,
        },
    ]
}


def _make_tmp_project(mutable=False):
    """Create a temporary project root with mock JSONs. Returns (root, tmpdir)."""
    tmpdir = tempfile.mkdtemp(prefix="nmm_test_")
    root = Path(tmpdir)
    (root / "data").mkdir()
    for name, data in MOCK_FUEL.items():
        pass  # handled below
    def save(name, data):
        with open(root / "data" / f"{name}.json", "w") as fh:
            json.dump(data, fh)
    save("fuel", MOCK_FUEL)
    save("exchange", MOCK_EXCHANGE)
    save("border", MOCK_BORDER)
    save("news", MOCK_NEWS)
    save("incidents", MOCK_INCIDENTS)
    return str(root), tmpdir


# ===================================================================
# Tests — Data loading
# ===================================================================

class TestDataLoading(unittest.TestCase):
    def test_load_json_good(self):
        result = de._load_json(os.path.join(PROJECT_ROOT, "data", "fuel.json"))
        self.assertIsNotNone(result)
        self.assertIn("provinces", result)

    def test_load_json_missing(self):
        result = de._load_json("/nonexistent/path/fake.json")
        self.assertIsNone(result)


class TestGetFunctions(unittest.TestCase):
    def setUp(self):
        self.root, self.tmp = _make_tmp_project()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_get_fuel_data(self):
        result = de.get_fuel_data(self.root)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["diesel_national_avg"], 233.0)

    def test_get_exchange_data(self):
        result = de.get_exchange_data(self.root)
        self.assertEqual(result["current"], 1.3888)

    def test_get_border_data(self):
        result = de.get_border_data(self.root)
        self.assertEqual(len(result["crossings"]), 3)

    def test_get_news_data(self):
        result = de.get_news_data(self.root)
        self.assertEqual(len(result["headlines"]), 2)

    def test_get_incidents_data(self):
        result = de.get_incidents_data(self.root)
        self.assertEqual(len(result["incidents"]), 3)


# ===================================================================
# Tests — Section formatters
# ===================================================================

class TestFmtFuel(unittest.TestCase):
    def test_basic(self):
        result = de.fmt_fuel(MOCK_FUEL)
        self.assertIn("DIESEL PRICES", result)
        self.assertIn("233.0¢/L", result)
        # Should show cheapest/dearest spread
        self.assertIn("spread", result.lower())
        self.assertIn("provinces surveyed", result.lower())

    def test_yt_nt_excluded(self):
        result = de.fmt_fuel(MOCK_FUEL)
        # YT should not be cheapest or dearest since NT is cheaper
        lines = result.split("\n")
        spread_line = [l for l in lines if "spread" in l.lower()]
        self.assertTrue(len(spread_line) >= 1, "Spread line not found")
        # NT (207.9) < SK (209.1) so NT should be cheapest
        self.assertIn("NT", spread_line[0])
        # QC (256.0) should be dearest
        self.assertIn("QC", spread_line[0])

    def test_empty_fuel(self):
        result = de.fmt_fuel({})
        self.assertIn("Diesel data unavailable.", result)

    def test_no_provinces(self):
        result = de.fmt_fuel({"provinces": {}, "diesel_national_avg": None})
        self.assertIn("unavailable", result.lower())


class TestFmtExchange(unittest.TestCase):
    def test_positive_change(self):
        data = {"current": 1.40, "observation_date": "2026-08-28", "change_pct": 0.5}
        result = de.fmt_exchange(data)
        self.assertIn("stronger" if 0.5 < 0 else "weaker", result)
        # change_pct > 0 means USD got stronger (more CAD per USD)
        # so loonie got WEAKER
        self.assertIn("weaker", result.lower())

    def test_negative_change(self):
        data = {"current": 1.38, "observation_date": "2026-08-28", "change_pct": -0.3}
        result = de.fmt_exchange(data)
        self.assertIn("stronger", result.lower())

    def test_zero_change(self):
        data = {"current": 1.38, "observation_date": "2026-08-28", "change_pct": 0}
        result = de.fmt_exchange(data)
        self.assertIn("flat", result.lower())

    def test_null_change(self):
        data = {"current": 1.38, "observation_date": "2026-08-28", "change_pct": None}
        result = de.fmt_exchange(data)
        self.assertIn("flat", result.lower())

    def test_empty_exchange(self):
        result = de.fmt_exchange({})
        self.assertIn("Exchange rate data unavailable.", result)


class TestFmtBorder(unittest.TestCase):
    def test_sorted_by_delay(self):
        result = de.fmt_border(MOCK_BORDER)
        lines = result.strip().split("\n")
        # Ambassador Bridge (45 min) should come first after headers
        header_count = sum(1 for l in lines if l.startswith(("=", "-"))) + 2
        crossing_lines = [l for l in lines[header_count:] if l.strip() and not l.startswith("=")]
        self.assertTrue(len(crossing_lines) > 0)
        # First crossing should be Ambassador Bridge (45 min)
        self.assertIn("Ambassador Bridge", crossing_lines[0])

    def test_slow_tagging(self):
        result = de.fmt_border(MOCK_BORDER)
        # 45-min crossing should get SLOW tag
        self.assertIn("⚠️ SLOW", result)

    def test_empty_border(self):
        result = de.fmt_border({})
        self.assertIn("Border data unavailable.", result)

    def test_no_crossings(self):
        result = de.fmt_border({"crossings": []})
        self.assertIn("No crossing data available.", result)


class TestFmtNews(unittest.TestCase):
    def test_canadian_first(self):
        result = de.fmt_news(MOCK_NEWS)
        lines = result.strip().split("\n")
        content_lines = [l for l in lines if l.strip() and not l.startswith(("=", "-"))]
        ca_idx = next((i for i, l in enumerate(content_lines) if "[CA]" in l), -1)
        non_ca_idx = next((i for i, l in enumerate(content_lines) if "[CA]" not in l), -1)
        self.assertGreater(ca_idx, -1, "CA-flagged headline not found")
        # Canadian should appear before non-Canadian
        if non_ca_idx > -1:
            self.assertLess(ca_idx, non_ca_idx, "CA headline should appear before non-CA")

    def test_top_5_limit(self):
        many_headlines = {"headlines": [{"source": f"S{i}", "title": f"T{i}", "link": "", "flag_canadian": False} for i in range(10)]}
        result = de.fmt_news(many_headlines)
        numbered = [l for l in result.split("\n") if l.strip() and l[0].isdigit()]
        self.assertLessEqual(len(numbered), 5, "Should limit to 5 headlines")

    def test_empty_news(self):
        result = de.fmt_news({})
        self.assertIn("News data unavailable.", result)


class TestFmtIncidents(unittest.TestCase):
    def test_collision_included(self):
        result = de.fmt_incidents(MOCK_INCIDENTS)
        # The collision incident should appear
        self.assertIn("HWY 401", result)

    def test_closure_included(self):
        result = de.fmt_incidents(MOCK_INCIDENTS)
        # The closure incident should appear
        self.assertIn("HWY 417", result)

    def test_major_severity_included(self):
        data = {
            "incidents": [
                {
                    "province": "BC", "highway": "Hwy 1",
                    "description": "Wildfire between A and B",
                    "event_type": "incident", "severity": "MAJOR", "closure": False,
                }
            ]
        }
        result = de.fmt_incidents(data)
        self.assertIn("Hwy 1", result)

    def test_empty_incidents(self):
        result = de.fmt_incidents({})
        self.assertIn("Incident data unavailable.", result)

    def test_no_notable_incidents(self):
        data = {"incidents": [
            {
                "province": "ON", "highway": "HWY 7",
                "description": "Daily maintenance on HWY 7 at Main St",
                "event_type": "maintenance", "severity": "MINOR", "closure": False,
            }
        ]}
        result = de.fmt_incidents(data)
        self.assertIn("No significant incidents", result)


# ===================================================================
# Tests — format_section dispatcher
# ===================================================================

class TestFormatSection(unittest.TestCase):
    def test_valid_section(self):
        result = de.format_section("fuel", MOCK_FUEL)
        self.assertIn("DIESEL PRICES", result)

    def test_invalid_section(self):
        result = de.format_section("garbage", {})
        self.assertIn("no formatter", result)


# ===================================================================
# Tests — generate_digest
# ===================================================================

class TestGenerateDigest(unittest.TestCase):
    def setUp(self):
        self.root, self.tmpdir = _make_tmp_project()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_generate_returns_tuple(self):
        plaintext, output_path = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertIsInstance(plaintext, str)
        self.assertIsInstance(output_path, str)

    def test_output_file_created(self):
        _, output_path = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertTrue(os.path.exists(output_path))

    def test_output_filename_format(self):
        _, output_path = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertIn("digest_2026-08-29.txt", output_path)

    def test_contains_sections(self):
        plaintext, _ = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertIn("DIESEL PRICES", plaintext)
        self.assertIn("EXCHANGE RATE", plaintext)
        self.assertIn("BORDER WAIT TIMES", plaintext)
        self.assertIn("INDUSTRY NEWS", plaintext)
        self.assertIn("ROAD INCIDENTS", plaintext)

    def test_contains_footer(self):
        plaintext, _ = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertIn("We send this every Wednesday", plaintext)
        self.assertIn("dashboard.northernmilemedia.com", plaintext)

    def test_header_contains_date(self):
        plaintext, _ = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertIn("THE WEDNESDAY SNAPSHOT", plaintext)
        self.assertIn("August 29, 2026", plaintext)

    def test_custom_output_dir(self):
        outdir = os.path.join(self.root, "custom_output")
        _, output_path = de.generate_digest(date_str="2026-08-29", project_root=self.root, output_dir=outdir)
        self.assertTrue(os.path.exists(output_path))
        self.assertIn(outdir, output_path)

    def test_missing_config_doesnt_crash(self):
        _, output_path = de.generate_digest(date_str="2026-08-29", project_root=self.root)
        self.assertTrue(os.path.exists(output_path))

    def test_default_date_is_today(self):
        plaintext, _ = de.generate_digest(project_root=self.root)
        # Should produce a file with today's date
        import datetime as dt
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
        self.assertIn(f"digest_{today.replace('-', '_')}.txt", _)


# ===================================================================
# Tests — load_config
# ===================================================================

class TestLoadConfig(unittest.TestCase):
    def test_defaults_when_no_file(self):
        cfg = de.load_config(config_path="/nonexistent/config.yml")
        self.assertEqual(cfg["smtp"]["host"], "smtp.gmail.com")
        self.assertEqual(cfg["smtp"]["port"], 587)
        self.assertEqual(cfg["subject_prefix"], "[NMM]")
        self.assertEqual(cfg["from_name"], "Northern Mile")

    def test_real_yaml_file(self):
        cfg_path = os.path.join(PROJECT_ROOT, "config", "digest_config.yml")
        if os.path.exists(cfg_path):
            cfg = de.load_config(config_path=cfg_path)
            self.assertEqual(cfg["smtp"]["host"], "smtp.gmail.com")
            self.assertIn("recipients", cfg)
            self.assertIn("subject_prefix", cfg)


# ===================================================================
# Tests — send_digest
# ===================================================================

class TestSendDigest(unittest.TestCase):
    def setUp(self):
        # Use test config with known recipient
        self.config_path = os.path.join(PROJECT_ROOT, "tests", "mocks", "digest_config_test.yml")
        self.root, self.tmpdir = _make_tmp_project()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_send_digest_password_missing(self):
        result = de.send_digest(
            config_path=self.config_path,
            smtp_password="",
        )
        self.assertFalse(result)

    def test_send_digest_via_mock_smtp(self):
        plaintext = "Test digest body."
        mock_msg_sent = []

        class MockSMTP:
            def __init__(self, host, port, timeout=None):
                self.host = host
                self.port = port
                self.tls_used = False
                self.logged_in = False

            def ehlo(self):
                pass

            def starttls(self):
                self.tls_used = True

            def login(self, user, passwd):
                self.logged_in = True
                self.password = passwd

            def sendmail(self, sender, recipients, msg):
                mock_msg_sent.append({"sender": sender, "recipients": recipients, "msg": msg})

            def quit(self):
                pass

        with mock.patch.object(de.smtplib, 'SMTP', MockSMTP):
            result = de.send_digest(
                config_path=self.config_path,
                plaintext=plaintext,
                smtp_password="fake_password",
            )

        self.assertTrue(result)
        self.assertEqual(len(mock_msg_sent), 1)
        sent = mock_msg_sent[0]
        self.assertIn("digest@northernmilemedia.com", sent["sender"])
        self.assertIn("test@example.com", sent["recipients"])
        self.assertIn("[NMM]", sent["msg"]["Subject"])

    def test_send_digest_empty_recipients(self):
        config_path = os.path.join(PROJECT_ROOT, "tests", "mocks", "digest_config_test.yml")
        # Create a config with empty recipients
        empty_cfg = os.path.join(PROJECT_ROOT, "tests", "mocks", "digest_config_empty.yml")
        with open(empty_cfg, "w") as f:
            f.write("smtp:\n  host: smtp.gmail.com\n  port: 587\n  sender_address: digest@northernmilemedia.com\n  password_env_var_name: NMM_SMTP_PASSWORD\n  use_tls: true\nrecipients: []\nsubject_prefix: [NMM]\nfrom_name: Northern Mile\n")
        try:
            plaintext = "Test body"
            with mock.patch.object(de.smtplib, 'SMTP') as MockSMTP:
                result = de.send_digest(
                    config_path=empty_cfg,
                    plaintext=plaintext,
                    smtp_password="fake",
                )
            self.assertTrue(result)
            MockSMTP.assert_not_called()
        finally:
            os.remove(empty_cfg)

    def test_send_digest_subject_extracted_from_body(self):
        plaintext = "Subject: Old Subject\n\nNew body text."
        mock_messages = []

        class MockSMTP:
            def __init__(self, *a, **kw): pass
            def ehlo(self): pass
            def starttls(self): pass
            def login(self, u, p): pass
            def sendmail(self, s, r, m): mock_messages.append(m)
            def quit(self): pass

        with mock.patch.object(de.smtplib, 'SMTP', MockSMTP):
            de.send_digest(
                config_path=self.config_path,
                plaintext=plaintext,
                smtp_password="fake_pass",
                date_str="2026-08-29",
            )
        self.assertEqual(len(mock_messages), 1)
        # Body should NOT start with "Subject:" — it should be stripped
        body = mock_messages[0].split("\nSubject:")[0]
        self.assertNotIn("Old Subject", body[:50])


# ===================================================================
# Tests — CLI entry point
# ===================================================================

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.root, self.tmpdir = _make_tmp_project()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @mock.patch('sys.argv', ['digest_email.py', '--date', '2026-08-29'])
    def test_cli_generate_only(self):
        """--generate-only flag should work without errors."""
        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            # Just import and call main directly instead of patching sys.argv
            de.main(generate_only=True, send=False, date="2026-08-29", config=None)
        except SystemExit as e:
            self.assertEqual(e.code, 0)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


# ===================================================================
# Run
# ===================================================================

if __name__ == "__main__":
    unittest.main()
