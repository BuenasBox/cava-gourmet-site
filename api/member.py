import json
import os
import hmac
import hashlib
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import AuthError, add_cors_headers, handle_options, require_admin, require_server_config, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, require_admin, require_server_config, respond_auth_error

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
HMAC_SECRET  = os.environ.get("HMAC_SECRET", "")
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
        with urllib.request.urlopen(req, timeout=12) as r:
            rows = json.loads(r.read())
            return rows[0] if rows else None
    except Exception:
        return None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            require_server_config(
                SUPABASE_URL=SUPABASE_URL,
                SUPABASE_KEY=SUPABASE_KEY,
                HMAC_SECRET=HMAC_SECRET,
            )
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, OPTIONS")
            return
        parsed    = urllib.parse.urlparse(self.path)
        params    = urllib.parse.parse_qs(parsed.query)
        email     = params.get("e", [""])[0].strip().lower()
        token     = params.get("t", [""])[0]

        if not email:
            self._json(400, {"ok": False, "error": "Email requerido"})
            return

        # Modo admin: genera el link del miembro con sesión Supabase admin.
        if not token:
            try:
                require_admin(self)
            except AuthError as exc:
                respond_auth_error(self, exc, methods="GET, OPTIONS")
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
            "wallet_url":   f"{BASE_URL}/api/wallet?e={urllib.parse.quote(email)}&t={t}"
        })

    def do_OPTIONS(self):
        handle_options(self, methods="GET, OPTIONS")

    def _json(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "private, no-store")
        add_cors_headers(self, methods="GET, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, *args):
        pass
