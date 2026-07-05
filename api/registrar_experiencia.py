import json
import os
import time
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import AuthError, add_cors_headers, handle_options, read_json_body, require_admin, require_server_config, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, read_json_body, require_admin, require_server_config, respond_auth_error

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ISSUER_ID    = "3388000000023147327"
LOGO_URL     = "https://raw.githubusercontent.com/BuenasBox/cava-gourmet-site/refs/heads/master/Assets/Logo-Cava.png"

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
        with urllib.request.urlopen(req, timeout=12) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25: return "🔐 Enófilo"
    if exp >= 10: return "🍷 Entusiasta"
    if exp >= 3:  return "🌱 Neófito"
    return "🚪 Invitado"

def mensaje_progreso(exp, es_enofilo=False):
    if es_enofilo:   return "Bienvenido al círculo interno. 🔐"
    if exp >= 25:    return "25 experiencias ✓ — Pendiente de invitación CAVA."
    if exp >= 10:    return f"Te faltan {25 - exp} experiencias para ser candidato a Enófilo."
    if exp >= 3:     return f"Te faltan {10 - exp} experiencias para Entusiasta."
    return f"Te faltan {3 - exp} experiencias para Neófito."

def get_google_token():
    import jwt
    key_data = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
    now      = int(time.time())
    claims   = {
        "iss":   key_data.get("client_email", ""),
        "sub":   key_data.get("client_email", ""),
        "aud":   "https://oauth2.googleapis.com/token",
        "iat":   now,
        "exp":   now + 3600,
        "scope": "https://www.googleapis.com/auth/wallet_object.issuer"
    }
    token = jwt.encode(claims, key_data.get("private_key", ""), algorithm="RS256")
    data  = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion":  token
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read())["access_token"]

def actualizar_wallet(miembro):
    try:
        access_token = get_google_token()
        email     = miembro["email"]
        exp       = miembro["experiencias"]
        enofilo   = miembro.get("es_enofilo", False)
        nivel     = calcular_nivel(exp, enofilo)
        progreso  = mensaje_progreso(exp, enofilo)
        safe_id   = email.replace("@", "_at_").replace(".", "_")
        object_id = f"{ISSUER_ID}.{safe_id}"

        body = json.dumps({
            "loyaltyPoints":          {"label": "Experiencias", "balance": {"int": exp}},
            "secondaryLoyaltyPoints": {"label": "Nivel",        "balance": {"string": nivel}},
            "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": progreso}]
        }).encode()

        url = f"https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject/{urllib.parse.quote(object_id, safe='')}"
        req = urllib.request.Request(url, data=body, method="PATCH")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=12) as r:
            r.read()
    except Exception:
        pass  # No interrumpir si falla la actualización de Wallet

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            require_server_config(SUPABASE_URL=SUPABASE_URL, SUPABASE_KEY=SUPABASE_KEY)
            require_admin(self)
            data = read_json_body(self)
        except AuthError as exc:
            respond_auth_error(self, exc, methods="POST, OPTIONS")
            return

        email = data.get("email","").strip().lower()
        nota  = data.get("nota", "Enofilios Cava")

        if not email:
            self._respond(400, {"ok": False, "error": "Email requerido"})
            return

        result = supabase_request("GET", f"miembros?email=eq.{email}&select=*")
        if not result or len(result) == 0:
            self._respond(404, {"ok": False, "error": "Miembro no encontrado. Regístralo primero."})
            return

        miembro    = result[0]
        nuevas_exp = miembro["experiencias"] + 1
        historial  = miembro.get("historial") or []
        historial.append({"fecha": time.strftime("%d/%m/%Y"), "nota": nota})

        supabase_request("PATCH", f"miembros?email=eq.{email}", {
            "experiencias": nuevas_exp,
            "historial":    historial
        })

        miembro["experiencias"] = nuevas_exp
        actualizar_wallet(miembro)

        nivel    = calcular_nivel(nuevas_exp, miembro.get("es_enofilo", False))
        progreso = mensaje_progreso(nuevas_exp, miembro.get("es_enofilo", False))

        self._respond(200, {
            "ok":           True,
            "experiencias": nuevas_exp,
            "nivel":        nivel,
            "progreso":     progreso
        })

    def do_OPTIONS(self):
        handle_options(self, methods="POST, OPTIONS")

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        add_cors_headers(self, methods="POST, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass
