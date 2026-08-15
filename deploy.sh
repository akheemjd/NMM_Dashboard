#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
DRY_RUN="${DRY_RUN:-0}"

# Guard against shadowing. The Hermes entry point must remain a thin exec
# wrapper. A full copy of this script there will drift and run stale in
# production, which is what happened Aug 1-12 2026.
EXPECTED="/home/hermes/northern-mile-dashboard/deploy.sh"
HERMES_ENTRY="$HOME/.hermes/scripts/deploy.sh"
if [ -f "$HERMES_ENTRY" ]; then
  ENTRY_LINES=$(grep -cvE '^\s*(#|$)' "$HERMES_ENTRY")
  if [ "$ENTRY_LINES" -gt 3 ] || ! grep -qF "exec $EXPECTED" "$HERMES_ENTRY"; then
    echo "FATAL: $HERMES_ENTRY is not a thin exec wrapper ($ENTRY_LINES logic lines)."
    echo "A stale copy is shadowing the repo script. Refusing to run."
    exit 1
  fi
fi

cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
python3 scripts/collector.py && python3 scripts/normalize.py && python3 scripts/normalize_provinces.py 2>&1

# 1b. Copy assets BEFORE build so a stylesheet/app change lands in this
# deploy alongside the code that needs it (build_templates also copies
# assets; running this first keeps both in agreement).
mkdir -p docs/assets && cp -r assets/. docs/assets/

python3 scripts/build_chart_data.py && python3 scripts/build_templates.py && python3 scripts/build_provinces.py && python3 scripts/build_og.py && python3 scripts/build_sitemap.py && python3 scripts/check_coherence.py 2>&1

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

echo "[6/6] Deploying..."
# Commit and push
echo "=== Asset freshness ==="
for f in nm.css nm.js; do
  if ! cmp -s "assets/$f" "docs/assets/$f"; then
    echo "FATAL: docs/assets/$f differs from assets/$f — asset copy did not run"
    exit 1
  fi
done
echo "  assets in sync"
echo "=== Coverage validation ==="
python3 scripts/coverage.py validate || { echo "COVERAGE VALIDATION FAILED — aborting deploy"; exit 1; }
echo "=== Source-tree guard ==="
if [ -n "$(git status --porcelain -- scripts/ templates/ assets/ config/ '*.yml' '*.sh' 2>/dev/null)" ]; then
  echo "FATAL: uncommitted source changes present. Scheduler will not auto-commit source."
  git status --short -- scripts/ templates/ assets/ config/ '*.yml' '*.sh'
  exit 1
fi
echo "=== Git push ==="
if [ "$DRY_RUN" = "1" ]; then
  echo "  DRY_RUN=1 — skipping commit and push"
else
  if python3 scripts/fingerprint.py; then
    git add data/ docs/
    git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
    if git push origin master; then
      python3 scripts/fingerprint.py commit
    else
      echo "  Push failed — fingerprint not advanced, will retry next run"
    fi
  else
    echo "  No data change — skipping deploy"
    git reset >/dev/null
  fi
fi
echo "Done."
