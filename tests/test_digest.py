"""Tests for the NMM digest email generator.

Uses mock JSON data to verify every section renders correctly
and that missing keys are handled gracefully.
"""

import json
import os
import shutil
import smtplib
import sys
import tempfile
from datetime import date
from pathlib import Path
from unittest import TestCase, TextTestRunner, TestSuite, main as unittest_main, mock

ROOT = Path(__file__).resolve().parent.parent
scripts_dir = ROOT / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import public API
from digest_email import format_section, generate_digest, generate_footer, send_digest  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_fuel_data() -> dict:
    return {
        "provinces": {
            "BC": {"diesel": 241.7, "trend": "up", "note": "NRCan survey"},
            "AB": {"diesel": 210.5, "trend": "down", "note": "NRCan survey"},
            "ON": {"diesel": 222.7, "trend": "flat", "note": "NRCan survey"},
            "QC": {"diesel": 256.0, "trend": "up", "note": "NRCan survey"},
            "MB": {"diesel": 217.0, "trend": "flat", "note": "NRCan survey"},
            "SK": {"diesel": 209.1, "trend": "flat", "note": "NRCan survey"},
            "YT": {"diesel": 229.9, "trend": "flat", "note": "NRCan survey"},
            "NT": {"diesel": 207.9, "trend": "flat", "note": "NRCan survey"},
            "NB": {"diesel": 242.6, "trend": "up", "note": "NRCan survey"},
            "NS": {"diesel": 242.7, "trend": "flat", "note": "NRCan survey"},
            "PE": {"diesel": 246.3, "trend": "up", "note": "NRCan survey"},
            "NL": {"diesel": 241.6, "trend": "flat", "note": "NRCan survey"},
        },
        "diesel_national_avg": 233.0,
        "updated": "2026-08-29T21:22:44+00:00",
        "print_date": "Tue, 25 Aug 2026",
        "source": "Natural Resources Canada weekly diesel survey",
    }


def _make_border_data() -> dict:
    return {
        "crossings": [
            {
                "id": "windsor-detroit",
                "name": "Ambassador Bridge",
                "route": "Windsor, ON - Detroit, MI",
                "commercial": True,
                "delay_minutes": 70,
            },
            {
                "id": "sarnia-port-huron",
                "name": "Blue Water Bridge",
                "route": "Sarnia, ON - Port Huron, MI",
                "commercial": True,
                "delay_minutes": 0,
            },
            {
                "id": "pac-blaine",
                "name": "Pacific Highway Crossing",
                "route": "Surrey, BC - Blaine, WA",
                "commercial": True,
                "delay_minutes": 45,
            },
            {
                "id": "fort-erie",
                "name": "Peace Bridge",
                "route": "Fort Erie, ON - Buffalo, NY",
                "commercial": True,
                "delay_minutes": 15,
            },
            {
                "id": "coutts",
                "name": "Coutts-Sweetgrass",
                "route": "Coutts, AB - Sweetgrass, MT",
                "commercial": False,
                "delay_minutes": 30,
            },
        ],
    }


def _make_exchange_data() -> dict:
    return {
        "current": 1.3888,
        "observation_date": "2026-08-28",
        "previous": 1.3861,
        "change_pct": 0.19,
    }


def _make_news_data() -> dict:
    return {
        "headlines": [
            {
                "source": "The Trucker",
                "title": "Trump tariffs on Canada raise legal questions",
                "date_iso": "2026-08-29T13:02:32+00:00",
                "flag_canadian": True,
            },
            {
                "source": "Trucking Info",
                "title": "US-Canada trade war means for trucking",
                "date_iso": "2026-08-24T20:50:02+00:00",
                "flag_canadian": True,
            },
            {
                "source": "Trucking Info",
                "title": "Hours of Service pilot programs FMCSA readies",
                "date_iso": "2026-08-27T20:41:45+00:00",
                "flag_canadian": False,
            },
            {
                "source": "The Trucker",
                "title": "Build America Act growing momentum for weight limits",
                "date_iso": "2026-08-29T10:00:51+00:00",
                "flag_canadian": False,
            },
            {
                "source": "Trucking Info",
                "title": "Zero-Emission Truck Corridor Planned for West Coast",
                "date_iso": "2026-08-26T22:00:32+00:00",
                "flag_canadian": False,
            },
        ],
    }


def _make_incidents_data() -> dict:
    return {
        "incidents": [
            {
                "id": "bc-fire-001",
                "province": "BC",
                "highway": {"name": "Pear Lake Road"},
                "description": "Wildfire between Pear Lake Road and Mowhich Road. Road closed to all traffic except emergency vehicles.",
                "event_type": "incident",
                "severity": "MAJOR",
                "closure": False,
            },
            {
                "id": "bc-fire-002",
                "province": "BC",
                "highway": {"name": "Silver Skagit Rd"},
                "description": "Provincial Parks closure caused by Hozomeen Mountain Wildfire. Ross Lake Campground and Skagit Valley Park closed.",
                "event_type": "incident",
                "severity": "MAJOR",
                "closure": False,
            },
            {
                "id": "on-roadwork-001",
                "province": "ON",
                "highway": "HWY 417",
                "description": "Nightly Construction On-ramp at MOODIE DR ALL LANES CLOSED.",
                "event_type": "roadwork",
                "severity": "Unknown",
                "closure": True,
            },
            {
                "id": "on-accident-001",
                "province": "ON",
                "highway": "HWY 401",
                "description": "Collision at BROCK ST Left shoulder and 2 left lanes closed.",
                "event_type": "accidentsandincidents",
                "severity": "Unknown",
                "closure": False,
            },
        ],
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFormatSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        (Path(self.tmpdir) / "data").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_basic_bullets(self):
        result = format_section(name="PRICES", items=["AB: 210", "BC: 241"])
        self.assertIn("PRICES\n-----", result)
        self.assertIn("* AB: 210", result)
        self.assertIn("* BC: 241", result)

    def test_empty_items_returns_blank(self):
        self.assertEqual(format_section(name="EMPTY", items=[]), "")

    def test_kwarg_only(self):
        result = format_section(name="TEST", items=["a", "b"])
        self.assertTrue(len(result) > 0)


class TestGenerateFooter(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        (Path(self.tmpdir) / "data").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_defaults(self):
        footer = generate_footer()
        self.assertIn("Northern Mile Media Dashboard", footer)
        self.assertIn("https://dashboard.northernmilemedia.com", footer)

    def test_custom_values(self):
        footer = generate_footer(
            source="CustomSource",
            url="https://custom.local/",
            unsubscribe_link="https://custom.local/unsub",
        )
        self.assertIn("CustomSource", footer)
        self.assertIn("https://custom.local/", footer)
        self.assertIn("Unsubscribe: https://custom.local/unsub", footer)

    def test_no_unsubscribe_when_none(self):
        footer = generate_footer(unsubscribe_link=None)
        self.assertNotIn("Unsubscribe", footer)

    def test_separator(self):
        footer = generate_footer()
        self.assertIn("---", footer)


class TestFuelSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_includes_top_provinces(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("Quebec: 256.0c/L", body)
        self.assertIn("Prince Edward Island: 246.3c/L", body)
        self.assertIn("Alberta: 210.5c/L", body)

    def test_missing_diesel_value_handled(self):
        data = _make_fuel_data()
        data["provinces"]["ON"]["diesel"] = None
        (self.datadir / "fuel.json").write_text(json.dumps(data))
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertNotIn("None", body)

    def test_empty_provinces_dict(self):
        data = {"diesel_national_avg": 230.0}
        (self.datadir / "fuel.json").write_text(json.dumps(data))
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("DIESEL PRICES", body)
        self.assertIn("No fuel data available", body)

    def test_missing_fuel_file_graceful(self):
        (self.datadir / "fuel.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("NORTHERN MILE DIGEST", body)


class TestBorderSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_sorted_by_delay(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("Ambassador Bridge: 70 min wait", body)
        self.assertIn("Pacific Highway Crossing: 45 min wait", body)

    def test_clear_crossings_not_in_top3(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        # Top 3 commercial: Ambassador(70), Pacific(45), Peace(15)
        self.assertIn("Peace Bridge: 15 min wait", body)
        self.assertNotIn("Blue Water Bridge", body)

    def test_missing_border_file(self):
        (self.datadir / "border.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("No border data available", body)


class TestMarketPulseSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_shows_rate_and_direction(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("CAD/USD at 1.3888", body)
        self.assertIn("(up)", body)
        self.assertIn("MARKET PULSE", body)

    def test_missing_exchange_file(self):
        (self.datadir / "exchange.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("No exchange rate data", body)


class TestIncidentsSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_major_incidents_listed(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("wildfire", body.lower())
        self.assertIn("BC", body)

    def test_duplicate_ids_removed(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        pear_count = body.count("Pear Lake Road")
        self.assertEqual(pear_count, 1)

    def test_missing_incidents_file(self):
        (self.datadir / "incidents.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("No active incidents", body)


class TestNewsSection(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_canadian_first(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        lines = body.split("\n")
        canadian_line = us_line = None
        for i, line in enumerate(lines):
            if "tariffs on Canada" in line:
                canadian_line = i
            if "Build America" in line:
                us_line = i
        self.assertIsNotNone(canadian_line)
        self.assertIsNotNone(us_line)
        self.assertLess(canadian_line, us_line,
                        "Non-Canadian headline appears before Canadian one")

    def test_capped_at_three(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        headline_lines = [l for l in body.split("\n") if "[The Trucker]" in l or "[Trucking Info]" in l]
        self.assertLessEqual(len(headline_lines), 3)

    def test_missing_news_file(self):
        (self.datadir / "news.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("No news available", body)


class TestGenerateDigestIntegration(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.datadir = Path(self.tmpdir) / "data"
        self.outputdir = Path(self.tmpdir) / "output"
        self.datadir.mkdir(parents=True)
        self.outputdir.mkdir(parents=True)
        (self.datadir / "fuel.json").write_text(json.dumps(_make_fuel_data()))
        (self.datadir / "border.json").write_text(json.dumps(_make_border_data()))
        (self.datadir / "exchange.json").write_text(json.dumps(_make_exchange_data()))
        (self.datadir / "news.json").write_text(json.dumps(_make_news_data()))
        (self.datadir / "incidents.json").write_text(json.dumps(_make_incidents_data()))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_all_sections_present(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("DIESEL PRICES", body)
        self.assertIn("BORDER ALERTS", body)
        self.assertIn("MARKET PULSE", body)
        self.assertIn("ACTIVE INCIDENTS", body)
        self.assertIn("HEADLINES", body)

    def test_output_file_created(self):
        generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        files = list(self.outputdir.glob("digest_*.txt"))
        self.assertGreaterEqual(len(files), 1)

    def test_footer_present(self):
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("---", body)
        self.assertIn("Northern Mile Media Dashboard", body)

    def test_all_files_missing(self):
        for f in ["fuel", "border", "exchange", "news", "incidents"]:
            (self.datadir / f"{f}.json").unlink()
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("NORTHERN MILE DIGEST", body)

    def test_mixed_missing_keys(self):
        (self.datadir / "fuel.json").write_text("{}")
        (self.datadir / "border.json").write_text("")
        (self.datadir / "exchange.json").write_text("{}")
        (self.datadir / "news.json").write_text("{}")
        (self.datadir / "incidents.json").write_text("{}")
        body = generate_digest(data_dir=str(self.datadir), output_dir=str(self.outputdir))
        self.assertIn("NORTHERN MILE DIGEST", body)

    def test_date_override(self):
        body = generate_digest(
            data_dir=str(self.datadir),
            output_dir=str(self.outputdir),
            today_override="2026-07-15",
        )
        expected = self.outputdir / "digest_2026-07-15.txt"
        self.assertTrue(expected.exists(), f"Expected {expected}")
        self.assertIn("2026-07-15", body)


class TestSendDigestGracefulFailure(TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        (Path(self.tmpdir) / "data").mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_smtp_failure_returns_false(self):
        result = send_digest(
            body="test body",
            smtp_host="nonexistent.invalid.host.xyz",
            smtp_port=25,
        )
        self.assertFalse(result)

    def test_no_password_returns_false(self):
        env_before = os.environ.pop("SMTP_PASSWORD", None)
        try:
            result = send_digest(body="x", password_env_var="NONEXISTENT_VAR_XYZ")
            self.assertFalse(result)
        finally:
            if env_before is not None:
                os.environ["SMTP_PASSWORD"] = env_before


if __name__ == "__main__":
    loader = TestSuite()
    for tc in (
        TestFormatSection,
        TestGenerateFooter,
        TestFuelSection,
        TestBorderSection,
        TestMarketPulseSection,
        TestIncidentsSection,
        TestNewsSection,
        TestGenerateDigestIntegration,
        TestSendDigestGracefulFailure,
    ):
        loader.addTests(unittest_main.TestLoader().loadTestsFromTestCase(tc))

    runner = TextTestRunner(verbosity=2)
    result = runner.run(loader)
    sys.exit(0 if result.wasSuccessful() else 1)
