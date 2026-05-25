import json
import os
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def supabase_request(method, endpoint, body=None):
    url     = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation"
    }
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else []
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        rows = supabase_request("GET", "configuracion?select=*")
        if isinstance(rows, dict) and "error" in rows:
            self._json(500, {"ok": False, "error": rows["error"]})
            return
        config = {r["clave"]: r["valor"] for r in rows}
        self._json(200, {"ok": True, "config": config})

    def do_PATCH(self):
        try:
            require_admin(self)
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, PATCH, OPTIONS")
            return
        length    = int(self.headers.get("Content-Length", 0))
        data      = json.loads(self.rfile.read(length))
        clave     = data.get("clave", "").strip()
        valor     = data.get("valor", "")

        if not clave:
            self._json(400, {"ok": False, "error": "Clave requerida"})
            return

        supabase_request(
            "PATCH",
            f"configuracion?clave=eq.{urllib.parse.quote(clave)}",
            {"valor": valor}
        )
        self._json(200, {"ok": True})

    def do_OPTIONS(self):
        handle_options(self, methods="GET, PATCH, OPTIONS")

    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        add_cors_headers(self, methods="GET, PATCH, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, *args):
        pass
