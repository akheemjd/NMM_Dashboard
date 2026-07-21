#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
echo "[1/5] Collecting border data from CBSA..."
python3 scripts/collect_border.py
echo "[2/5] Collecting other data..."
python3 scripts/collector.py && python3 scripts/collect_border.py && python3 scripts/normalize.py && python3 scripts/build_templates.py 2>&1
COLLECT_EXIT=$?

# 2. Health check — record status for each source
echo "[3/5] Health check..."
python3 -c "
import json, os, sys
sys.path.insert(0, 'scripts')
from health_tracker import record_success, record_failure

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

for src, filename in sources.items():
    path = os.path.join(data_dir, filename)
    try:
        if os.path.exists(path):
            with open(path) as f:
                d = json.load(f)
            # Check if data has content (not empty)
            if d and (d.get('updated') or d.get('current') or len(d.get('incidents', [])) > 0 or 
                      len(d.get('headlines', [])) > 0 or d.get('diesel_national_avg')):
                record_success(src)
            else:
                record_failure(src, 'Empty data')
        else:
            record_failure(src, 'File missing')
    except Exception as e:
        record_failure(src, str(e))
print('Health recorded.')
" 2>&1

# 3. Copy data skipped — template engine handles everything
echo "[4/5] Skipped (templates handle data)"

# 4. Rebuild both
echo "[5/5] Building..."
# DISABLED: python3 scripts/build_dashboard.py production
# DISABLED: python3 scripts/build_dashboard.py staging

# 5. Commit and push
echo "=== Git push ==="
git add -A
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
git push origin master || echo "  Push failed — check GitHub auth"
echo "Done."
