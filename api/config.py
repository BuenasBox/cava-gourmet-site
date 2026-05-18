import json
import os
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SCAN_KEY     = os.environ.get("SCAN_KEY", "")

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
        length    = int(self.headers.get("Content-Length", 0))
        data      = json.loads(self.rfile.read(length))
        admin_key = data.get("admin_key", "")
        clave     = data.get("clave", "").strip()
        valor     = data.get("valor", "")

        if admin_key != SCAN_KEY:
            self._json(403, {"ok": False, "error": "No autorizado"})
            return
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
        self._json(200, {})

    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, *args):
        pass
