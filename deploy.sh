#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
DRY_RUN="${DRY_RUN:-0}"
cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
python3 scripts/collector.py && python3 scripts/normalize.py && python3 scripts/build_templates.py 2>&1

# 2. Health check — freshness-based for the four sources with an honest date signal
python3 -c "
import json, os, sys
from datetime import date, datetime, timezone
sys.path.insert(0, 'scripts')
from health_tracker import record_success, record_failure

CEILINGS = {'fuel': 10, 'exchange': 5, 'incidents': 1, 'news': 3}

def obs_date(d, src):
    if src == 'fuel':
        pd = d.get('print_date')
        if pd:
            return datetime.strptime(pd, '%a, %d %b %Y').date()
    if src == 'exchange':
        od = d.get('observation_date')
        if od:
            return date.fromisoformat(od)
    u = d.get('updated')
    if u:
        return date.fromisoformat(u[:10])
    return None

for src, filename in {'fuel':'fuel.json','exchange':'exchange.json','incidents':'incidents.json','news':'news.json'}.items():
    path = os.path.join('data', filename)
    try:
        if not os.path.exists(path):
            record_failure(src, 'File missing'); print(f'  {src}: MISSING'); continue
        with open(path) as f:
            d = json.load(f)
        od = obs_date(d, src)
        if od is None:
            record_failure(src, 'No observation date'); print(f'  {src}: NO DATE'); continue
        age = (datetime.now(timezone.utc).date() - od).days
        if age > CEILINGS[src]:
            record_failure(src, f'Stale: {age}d old, ceiling {CEILINGS[src]}d')
            print(f'  {src}: STALE {age}d')
        else:
            record_success(src)
            print(f'  {src}: ok ({age}d)')
    except Exception as e:
        record_failure(src, str(e)); print(f'  {src}: ERROR {e}')
print('Health recorded.')
" 2>&1

# 3. Copy data skipped — template engine handles everything

# 4. Rebuild both

echo "[5/6] Copying docs..."
mkdir -p docs/assets && cp -r assets/. docs/assets/
echo "[6/6] Deploying..."
# Commit and push
echo "=== Coverage validation ==="
python3 scripts/coverage.py validate || { echo "COVERAGE VALIDATION FAILED — aborting deploy"; exit 1; }
echo "=== Git push ==="
if [ "$DRY_RUN" = "1" ]; then
  echo "  DRY_RUN=1 — skipping commit and push"
else
  git add -A
  SUBSTANTIVE=$(git diff --cached --numstat -- docs/ data/ \
    | awk '$1+$2 > 2 {print $3}' \
    | grep -v -E 'data/(health|coverage)\.json' || true)
  if [ -z "$SUBSTANTIVE" ]; then
    echo "  No substantive change — resetting index, skipping deploy"
    git reset >/dev/null
  else
    echo "  Changed: $(echo "$SUBSTANTIVE" | tr '\n' ' ')"
    git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
    git push origin master || echo "  Push failed — check GitHub auth"
  fi
fi
echo "Done."
