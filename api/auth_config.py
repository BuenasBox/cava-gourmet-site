import json
import os
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import add_cors_headers, handle_options
except ImportError:
    from _auth import add_cors_headers, handle_options


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rbfctmcfweckbpgxlkqf.supabase.co").rstrip("/")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        add_cors_headers(self, methods="GET, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps({
            "ok": True,
            "supabaseUrl": SUPABASE_URL,
            "supabaseAnonKey": SUPABASE_ANON_KEY,
        }).encode())

    def do_OPTIONS(self):
        handle_options(self, methods="GET, OPTIONS")

    def log_message(self, *args):
        pass
