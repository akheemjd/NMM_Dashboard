#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
python3 scripts/collector.py && python3 scripts/normalize.py && python3 scripts/build_templates.py 2>&1
COLLECT_EXIT=$?

# 2. Health check — record status for each source based on data freshness
python3 -c "
import json, os, sys
from datetime import date, datetime, timezone
sys.path.insert(0, 'scripts')
from health_tracker import record_success, record_failure

CEILINGS = {'fuel': 10, 'exchange': 5, 'incidents': 1, 'news': 3}

data_dir = 'data'
sources = {
    'fuel': 'fuel.json',
    'exchange': 'exchange.json',
    'border': 'border.json',
    'incidents': 'incidents.json',
    'market': 'market.json',
    'news': 'news.json',
    'theft': 'theft.json'
}

def extract_obs_date(src, d):
    if src == 'fuel':
        s = d.get('print_date')
        if s:
            return datetime.strptime(s, '%a, %d %b %Y').date()
        return None
    if src == 'exchange':
        s = d.get('observation_date')
        if not s:
            hist = d.get('history', [])
            s = max((h.get('date') for h in hist if h.get('date')), default=None)
        return date.fromisoformat(s[:10]) if s else None
    if src == 'incidents':
        incs = d.get('incidents', [])
        dates = []
        for i in incs:
            s = i.get('start') or i.get('updated')
            if isinstance(s, str):
                dates.append(s[:10])
            elif isinstance(s, (int, float)):
                dates.append(datetime.fromtimestamp(s, tz=timezone.utc).strftime('%Y-%m-%d'))
        return date.fromisoformat(max(dates)) if dates else None
    if src == 'news':
        heads = d.get('headlines', [])
        dates = [h.get('date_iso')[:10] for h in heads if h.get('date_iso')]
        return date.fromisoformat(max(dates)) if dates else None
    return date.today()

for src, filename in sources.items():
    path = os.path.join(data_dir, filename)
    try:
        if not os.path.exists(path):
            record_failure(src, 'File missing')
            continue
        with open(path) as f:
            d = json.load(f)
        ceiling = CEILINGS.get(src)
        if ceiling is None:
            record_success(src) if d else record_failure(src, 'Empty data')
            continue
        obs = extract_obs_date(src, d)
        if obs is None:
            record_failure(src, 'No observation date found')
            continue
        staleness = (date.today() - obs).days
        if staleness > ceiling:
            record_failure(src, f'Stale: {staleness} days (ceiling {ceiling})')
        else:
            record_success(src)
    except Exception as e:
        record_failure(src, str(e))
print('Health recorded (freshness-based).')
" 2>&1

# 3. Copy data skipped — template engine handles everything

# 4. Rebuild both

echo "[5/6] Copying docs..."
mkdir -p docs/v2 docs/assets && cp -r assets/. docs/assets/
echo "[6/6] Deploying..."
# Commit and push
echo "=== Git push ==="
git add -A
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
git push origin master || echo "  Push failed — check GitHub auth"
echo "Done."
