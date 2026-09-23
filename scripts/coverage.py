#!/usr/bin/env python3
"""Coverage report — tracks data freshness for every collector, every run."""
import json, os
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COVERAGE_PATH = os.path.join(ROOT, "data", "coverage.json")
HISTORY_CSV = os.path.join(ROOT, "data", "history", "series.csv")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def empty_block():
    return {
        "records": 0,
        "history_days": 0,
        "latest_observation": None,
        "staleness_days": None,
        "comparable_7d": False,
        "comparable_yoy": False,
    }


def history_span(series, key):
    """Days between oldest and newest snapshot for this series/key."""
    if not os.path.exists(HISTORY_CSV):
        return 0
    pts = []
    with open(HISTORY_CSV) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 4 and parts[1] == series and parts[2] == key:
                try:
                    pts.append(datetime.fromisoformat(parts[0]).date())
                except ValueError:
                    continue
    if len(pts) < 2:
        return 0
    pts.sort()
    return (pts[-1] - pts[0]).days


def has_snapshot_near(series, key, days_ago, tolerance=3):
    """True if a snapshot exists within tolerance of N days ago."""
    if not os.path.exists(HISTORY_CSV):
        return False
    target = date.today() - date.resolution * days_ago
    with open(HISTORY_CSV) as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 4 and parts[1] == series and parts[2] == key:
                try:
                    d = datetime.fromisoformat(parts[0]).date()
                    if abs((d - target).days) <= tolerance:
                        return True
                except ValueError:
                    continue
    return False


def compute(records, series, key, latest_obs):
    """Build a category block from collected data."""
    block = empty_block()
    block["records"] = records
    block["history_days"] = history_span(series, key)
    block["latest_observation"] = latest_obs
    if latest_obs:
        try:
            obs_date = date.fromisoformat(latest_obs[:10])
            block["staleness_days"] = (date.today() - obs_date).days
        except (ValueError, TypeError):
            block["staleness_days"] = None
    block["comparable_7d"] = has_snapshot_near(series, key, 7)
    block["comparable_yoy"] = has_snapshot_near(series, key, 365, tolerance=10)
    
    # Border: add quantitative_field
    if series == "border":
        block["quantitative_field"] = "delay_minutes"
    
    # Theft: add field_completeness (computed by caller)
    if series == "theft":
        block["field_completeness"] = {}
    
    return block


def write(fuel_records, fx_records, border_records, theft_records,
          fuel_obs=None, fx_obs=None, border_obs=None, theft_obs=None,
          cbp_border_records=0, cbp_border_obs=None,
          ifta_records=0, ifta_obs=None,
          us_fuel_tax_records=0, us_fuel_tax_obs=None):
    """Write the full coverage report. Called by collectors."""
    report = {
        "generated_at": now_iso(),
        "categories": {
            "fuel":   compute(fuel_records,   "diesel",  "national", fuel_obs),
            "fx":     compute(fx_records,     "fx",      "usd_cad",  fx_obs),
            "border": compute(border_records, "border",  "all",      border_obs),
            "theft":  compute(theft_records,  "theft",   "incidents", theft_obs),
            "cbp_border": compute(cbp_border_records, "cbp_border", "ports", cbp_border_obs),
            "ifta": compute(ifta_records, "ifta", "jurisdictions", ifta_obs),
            "us_fuel_tax": compute(us_fuel_tax_records, "us_fuel_tax",
                                   "states", us_fuel_tax_obs),
        }
    }
    # CBP is a live, hourly feed rather than a surveyed series, so the historical
    # comparability flags do not apply to it. Mark them false explicitly rather
    # than leaving a snapshot-history claim that will never come true.
    report["categories"]["cbp_border"]["quantitative_field"] = "commercial_delay"
    report["categories"]["cbp_border"]["comparable_7d"] = False
    report["categories"]["cbp_border"]["comparable_yoy"] = False

    # IFTA is a quarterly published table, not a survey series, so year-on-year
    # comparison is meaningful only if we keep past quarters. Until that history
    # exists the flags say so rather than implying a comparison we cannot make.
    report["categories"]["ifta"]["quantitative_field"] = "diesel_rate"

    # The EIA motor fuel tax table is semiannual. Same reasoning as IFTA: without
    # kept history there is no year-on-year comparison to claim.
    report["categories"]["us_fuel_tax"]["quantitative_field"] = "diesel_total_state"
    report["categories"]["us_fuel_tax"]["comparable_7d"] = False
    report["categories"]["us_fuel_tax"]["comparable_yoy"] = False
    report["categories"]["ifta"]["comparable_7d"] = False

    health_path = os.path.join(ROOT, "data", "health.json")
    if os.path.exists(health_path):
        try:
            with open(health_path) as hf:
                health = json.load(hf)
            report["source_health"] = {
                k: v.get("status") for k, v in health.get("sources", {}).items()
            }
        except Exception:
            report["source_health"] = {}
    else:
        report["source_health"] = {}

    os.makedirs(os.path.dirname(COVERAGE_PATH), exist_ok=True)
    with open(COVERAGE_PATH, "w") as f:
        json.dump(report, f, indent=2)
    return report


def validate():
    """Build assertion: fail if any category missing or incomplete."""
    if not os.path.exists(COVERAGE_PATH):
        raise AssertionError("coverage.json missing — no collectors ran")
    with open(COVERAGE_PATH) as f:
        report = json.load(f)
    required = ["fuel", "fx", "border", "theft", "cbp_border", "ifta",
                "us_fuel_tax"]
    fields = ["records", "history_days", "latest_observation",
              "staleness_days", "comparable_7d", "comparable_yoy"]
    border_extras = ["quantitative_field"]
    theft_extras = ["field_completeness"]
    for cat in required:
        if cat not in report.get("categories", {}):
            raise AssertionError(f"coverage.json missing category: {cat}")
        for field in fields:
            if field not in report["categories"][cat]:
                raise AssertionError(f"coverage.json missing field {cat}.{field}")
        if cat == "border":
            for f in border_extras:
                if f not in report["categories"][cat]:
                    raise AssertionError(f"coverage.json missing border field {f}")
        if cat == "theft":
            for f in theft_extras:
                if f not in report["categories"][cat]:
                    raise AssertionError(f"coverage.json missing theft field {f}")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        try:
            validate()
            print("coverage.json: valid")
        except AssertionError as e:
            print(f"FAIL: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Standalone run: dump current state
        if os.path.exists(COVERAGE_PATH):
            print(json.dumps(json.load(open(COVERAGE_PATH)), indent=2))
        else:
            print("No coverage report yet")
