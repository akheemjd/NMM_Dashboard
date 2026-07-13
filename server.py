#!/usr/bin/env python3
"""Northern Mile Dashboard Server
Serves with proper cache headers for Cloudflare compatibility.
JSON data: no-cache (live data). HTML: 2 min cache. Static assets: 24h.
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os, sys

PORT = 8080
ROOT = os.path.dirname(os.path.abspath(__file__))

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        path = self.path.split('?')[0]

        if path.endswith('.json') or '/data/' in path:
            # Live data: never cache
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        elif path.endswith('.html'):
            # HTML: short cache, let Cloudflare refresh often
            self.send_header('Cache-Control', 'public, max-age=120, s-maxage=120')
        elif any(path.endswith(ext) for ext in ['.css','.js','.png','.ico','.svg']):
            # Static assets: cache aggressively
            self.send_header('Cache-Control', 'public, max-age=86400, s-maxage=86400, immutable')
        else:
            self.send_header('Cache-Control', 'no-cache')

        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        # Quiet logging for cron environments
        if '/data/' not in args[0]:
            sys.stderr.write(f"[dashboard] {args[0]}\n")

if __name__ == '__main__':
    os.chdir(ROOT)
    server = HTTPServer(('0.0.0.0', PORT), DashboardHandler)
    print(f'Northern Mile Dashboard → http://0.0.0.0:{PORT}')
    print(f'Serving from: {ROOT}')
    print(f'Cache: JSON=no-cache  HTML=2min  Assets=24h')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down.')
        server.server_close()
