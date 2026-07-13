#!/bin/bash
# Deploy dashboard to GitHub Pages
set -e
cd /home/hermes/northern-mile-dashboard

echo "=== Deploy $(date) ==="

# 1. Collect fresh data
echo "[1/3] Collecting data..."
python3 scripts/collector.py

# 2. Copy data to docs
echo "[2/3] Copying data..."
cp data/*.json docs/data/

# 3. Rebuild dashboard
echo "[3/3] Building dashboard..."
python3 scripts/build_dashboard.py

# 4. Commit and push
echo "=== Git push ==="
git add -A
git commit -m "Auto-update $(date '+%Y-%m-%d %H:%M')" || echo "  (nothing to commit)"
git push origin master || echo "  Push failed — check GitHub auth"
echo "Done."
