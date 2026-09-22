#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
DRY_RUN="${DRY_RUN:-0}"

# Derive our own filesystem location — works regardless of $HOME (which differs in cron vs interactive shells)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$SCRIPT_DIR"
if [ -f "$SCRIPT_DIR/deploy.sh" ]; then
  : # we're inside the repo
else
  REPO_DIR="$(cd "$SCRIPT_DIR/../northern-mile-dashboard" && pwd)"
fi
cd "$REPO_DIR" || { echo "FATAL: cannot cd to repo dir $REPO_DIR"; exit 1; }

echo "=== Deploy $(date) ==="

# Auto-detect Python — venv path is absolute and doesn't depend on PATH
PYTHON="/c/Users/Akheem/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
[ -x "$PYTHON" ] || PYTHON="python"
echo "  Using Python: $PYTHON"

# 1. Collect fresh data
$PYTHON scripts/collector.py && $PYTHON scripts/normalize.py && $PYTHON scripts/normalize_provinces.py 2>&1

# 1c. Copy assets BEFORE build
mkdir -p docs/assets && cp -r assets/. docs/assets/
cp assets/favicon.ico docs/favicon.ico

$PYTHON scripts/gen_templates.py && $PYTHON scripts/build_chart_data.py && $PYTHON scripts/build_templates.py && $PYTHON scripts/build_provinces.py && $PYTHON scripts/build_city_pages.py && $PYTHON scripts/build_us_pages.py && $PYTHON scripts/build_border_pages.py && $PYTHON scripts/build_cbp_ports.py && $PYTHON scripts/build_ifta_page.py && $PYTHON scripts/build_border_trends.py && $PYTHON scripts/build_og.py && $PYTHON scripts/build_sitemap.py && $PYTHON scripts/check_coherence.py && $PYTHON scripts/check_links.py && $PYTHON scripts/check_data_integrity.py 2>&1

# 2. Health check
$PYTHON -c "
import json, os, sys
from datetime import date, datetime, timezone
sys.path.insert(0, 'scripts')
from health_tracker import record_success, record_failure

CEILINGS = {'fuel': 10, 'exchange': 5, 'incidents': 1, 'news': 3, 'eia_diesel': 10}

def obs_date(d, src):
    if src == 'fuel':
        pd = d.get('print_date')
        if pd: return datetime.strptime(pd, '%a, %d %b %Y').date()
    if src == 'exchange':
        od = d.get('observation_date')
        if od: return date.fromisoformat(od)
    if src == 'eia_diesel':
        od = d.get('date')
        if od: return date.fromisoformat(od)
    u = d.get('updated')
    if u: return date.fromisoformat(u[:10])
    return None

for src, filename in {'fuel':'fuel.json','exchange':'exchange.json','incidents':'incidents.json','news':'news.json','eia_diesel':'eia_diesel.json'}.items():
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

# 3. Deploy
echo "[6/6] Deploying..."
echo "=== Asset freshness ==="
for f in nm.css nm.js nmdi-chart.js; do
  if ! cmp -s "assets/$f" "docs/assets/$f"; then
    echo "FATAL: docs/assets/$f differs from assets/$f" >&2
    exit 1
  fi
done
echo "  assets in sync"

echo "=== Coverage validation ==="
$PYTHON scripts/coverage.py validate || { echo "COVERAGE VALIDATION FAILED"; exit 1; }

echo "=== Source-tree guard ==="
# Exclude editor/tool scratch files. Hermes writes .hermes-tmp.* into the
# working directory during file operations, and an interrupted write leaves one
# behind, which then blocks every deploy until someone notices. Those are not
# source changes and must not gate the build.
TREE_PATTERNS="scripts/ templates/ assets/ config/ *.yml *.sh"
DIRTY=$(git status --porcelain -- $TREE_PATTERNS 2>/dev/null \
  | grep -vE '(^|/)\.hermes-tmp\.|\.tmp$|~$' || true)
if [ -n "$DIRTY" ]; then
  echo "FATAL: uncommitted source changes present." >&2
  echo "$DIRTY"
  exit 1
fi

echo "=== Git pull & push ==="
if [ "$DRY_RUN" = "1" ]; then
  echo "  DRY_RUN=1 — skipping"
else
  if $PYTHON scripts/fingerprint.py; then
    # Pull first to avoid diverging deploys
    git fetch origin master >/dev/null 2>&1
    if ! git pull --ff-only origin master 2>/dev/null; then
      $PYTHON scripts/collector.py && $PYTHON scripts/normalize.py 2>/dev/null
      git add data/
      git commit -m "Force-sync after pull failure" >/dev/null 2>&1
    fi
    git add data/ docs/
    git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
    if git push origin master; then
      $PYTHON scripts/fingerprint.py commit
    else
      # Second attempt: full resync
      $PYTHON scripts/collector.py && $PYTHON scripts/normalize.py 2>/dev/null
      git add data/ docs/
      git commit --allow-empty -m "Resync $(date '+%Y-%m-%d %H:%M')" >/dev/null 2>&1
      if git push origin master; then
        $PYTHON scripts/fingerprint.py commit
        echo "  Resynced and pushed."
      else
        echo "  Push failed — will retry next run" >&2
      fi
    fi
  else
    echo "  No data change — skipping rebuild"
    git reset >/dev/null
    # A commit that touches scripts/, templates/ or content/ changes no data, so
    # this branch would strand it locally forever. The media kit rewrite sat
    # unpushed for exactly this reason: correct on disk, absent from the repo.
    UNPUSHED=$(git log origin/master..HEAD --oneline 2>/dev/null)
    if [ -n "$UNPUSHED" ]; then
      echo "  Unpushed commits present:"
      echo "$UNPUSHED" | sed 's/^/    /'
      if git push origin master >/dev/null 2>&1; then
        echo "  pushed."
      else
        echo "  push failed — will retry next run" >&2
      fi
    fi
  fi
fi

# 4. (Optional) Generate & send email digest — REMOVED (Akheem: not needed)
# Digest email step disabled 2026-08-31; deploy.sh no longer sends email digests.

echo "Done."
if [ "$DRY_RUN" != "1" ]; then
  # Write heartbeat relative to our known filesystem layout: .hermes/.nmm_deploy_ok
  _HEARTBEAT="$(cd "$(dirname "$0")/.." && pwd)/.nmm_deploy_ok"
  date -u +%s > "$_HEARTBEAT"
fi
