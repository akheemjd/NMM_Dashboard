#!/bin/bash
# Northern Mile Dashboard — Quick Start
cd /home/hermes/northern-mile-dashboard

echo "=== Northern Mile Dashboard ==="

# 1. Data collector
echo "[1/3] Data collector..."
python3 scripts/collector.py

# 2. Dashboard server with proper cache headers
echo "[2/3] Dashboard server on :8080..."
python3 server.py &
echo "  Server PID: $!"

# 3. Cloudflare tunnel
if [ -f cloudflared ]; then
    echo "[3/3] Cloudflare tunnel..."
    ./cloudflared tunnel --url http://localhost:8080 &
    echo "  Tunnel PID: $!"
fi

echo ""
echo "  Local:  http://localhost:8080/web/index.html"
echo "  Tunnel: check cloudflared output for URL"
echo ""
echo "Cache: JSON=no-cache  HTML=2min  Assets=24h"
