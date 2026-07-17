#!/usr/bin/env python3
"""Health tracker for Northern Mile data sources.
Import and call record_success() or record_failure() after each source collection.
On 2 consecutive failures, writes an alert to data/alerts.json.
"""
import json, os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
HEALTH_PATH = os.path.join(DATA_DIR, 'health.json')
ALERTS_PATH = os.path.join(DATA_DIR, 'alerts.json')

def _load():
    if os.path.exists(HEALTH_PATH):
        with open(HEALTH_PATH) as f:
            return json.load(f)
    return {"sources": {}, "updated": None}

def _save(h):
    h['updated'] = datetime.now(timezone.utc).isoformat()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(HEALTH_PATH, 'w') as f:
        json.dump(h, f, indent=2)

def _add_alert(source, last_success, error):
    """Append an alert to data/alerts.json for the digest to report."""
    os.makedirs(DATA_DIR, exist_ok=True)
    alerts = []
    if os.path.exists(ALERTS_PATH):
        with open(ALERTS_PATH) as f:
            alerts = json.load(f)
    alerts.append({
        'source': source,
        'last_success': last_success,
        'error': str(error)[:200],
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    # Keep last 50 alerts
    with open(ALERTS_PATH, 'w') as f:
        json.dump(alerts[-50:], f, indent=2)

def record_success(source):
    h = _load()
    h['sources'][source] = {
        'last_success': datetime.now(timezone.utc).isoformat(),
        'last_attempt': datetime.now(timezone.utc).isoformat(),
        'consecutive_failures': 0,
        'status': 'ok'
    }
    _save(h)

def record_failure(source, error=None):
    h = _load()
    s = h['sources'].get(source, {
        'last_success': None,
        'last_attempt': None,
        'consecutive_failures': 0,
        'status': 'unknown'
    })
    s['last_attempt'] = datetime.now(timezone.utc).isoformat()
    s['consecutive_failures'] = s.get('consecutive_failures', 0) + 1
    s['status'] = 'failing'
    if s['consecutive_failures'] >= 2:
        s['status'] = 'alert'
        _add_alert(source, s.get('last_success'), error)
    h['sources'][source] = s
    _save(h)

def get_status():
    """Return {source: {status, consecutive_failures, last_success}} for digest."""
    h = _load()
    result = {}
    for src, s in h.get('sources', {}).items():
        result[src] = {
            'status': s.get('status', 'unknown'),
            'consecutive_failures': s.get('consecutive_failures', 0),
            'last_success': s.get('last_success')
        }
    return result

def get_alerts(since_last_digest=True):
    """Return recent alerts. If since_last_digest, filter to unacknowledged."""
    if not os.path.exists(ALERTS_PATH):
        return []
    with open(ALERTS_PATH) as f:
        alerts = json.load(f)
    return alerts[-10:]  # Latest 10

def acknowledge_alerts():
    """Clear alerts after digest has reported them."""
    if os.path.exists(ALERTS_PATH):
        os.remove(ALERTS_PATH)

if __name__ == '__main__':
    # Quick status check
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        status = get_status()
        for src, s in status.items():
            print(f"{src}: {s['status']} (failures: {s['consecutive_failures']})")
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        print("Recording test success...")
        record_success('fuel')
        print("Recording test failure...")
        record_failure('news', 'Test error')
        record_failure('news', 'Test error 2 — should trigger alert')
        print("Alerts:", get_alerts())
    else:
        print("Usage: health_tracker.py [status|test]")
