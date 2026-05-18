import json
import os
import hmac
import hashlib
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
HMAC_SECRET  = os.environ.get("HMAC_SECRET", "")
SCAN_KEY     = os.environ.get("SCAN_KEY", "")
BASE_URL     = "https://www.cavagourmet.com"

def generar_token(email):
    return hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()

def validar_token(email, token):
    return hmac.compare_digest(generar_token(email), token)

def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25: return "🔐 Enófilo"
    if exp >= 10: return "🍷 Entusiasta"
    if exp >= 3:  return "🌱 Neófito"
    return "🚪 Invitado"

def get_miembro(email):
    url     = f"{SUPABASE_URL}/rest/v1/miembros?email=eq.{urllib.parse.quote(email)}&select=*"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            rows = json.loads(r.read())
            return rows[0] if rows else None
    except Exception:
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed    = urllib.parse.urlparse(self.path)
        params    = urllib.parse.parse_qs(parsed.query)
        email     = params.get("e", [""])[0].strip().lower()
        token     = params.get("t", [""])[0]
        admin_key = params.get("admin_key", [""])[0]

        if not email:
            self._json(400, {"ok": False, "error": "Email requerido"})
            return

        # Modo admin: genera el link del miembro
        if admin_key:
            if admin_key != SCAN_KEY:
                self._json(403, {"ok": False, "error": "No autorizado"})
                return
            t    = generar_token(email)
            link = f"{BASE_URL}/members/?t={t}&e={urllib.parse.quote(email)}"
            self._json(200, {"ok": True, "link": link})
            return

        # Modo miembro: valida token y devuelve datos
        if not token or not validar_token(email, token):
            self._json(403, {"ok": False, "error": "Token inválido"})
            return

        miembro = get_miembro(email)
        if not miembro:
            self._json(404, {"ok": False, "error": "Miembro no encontrado"})
            return

        exp      = miembro.get("experiencias", 0)
        enofilo  = miembro.get("es_enofilo", False)
        t        = generar_token(email)
        scan_url = f"{BASE_URL}/api/scan?email={urllib.parse.quote(email)}&t={t}"

        self._json(200, {
            "ok":           True,
            "nombre":       miembro.get("nombre", ""),
            "email":        email,
            "experiencias": exp,
            "nivel":        calcular_nivel(exp, enofilo),
            "es_enofilo":   enofilo,
            "fecha_ingreso": miembro.get("fecha_ingreso", ""),
            "historial":    miembro.get("historial") or [],
            "scan_url":     scan_url,
            "wallet_url":   f"{BASE_URL}/api/wallet?email={urllib.parse.quote(email)}"
        })

    def do_OPTIONS(self):
        self._json(200, {})

    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, *args):
        pass
