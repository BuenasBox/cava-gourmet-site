import json
import os
import time
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ISSUER_ID    = "BCR2DN5TZPM6RPTP"

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
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25: return "🔐 Enófilo"
    if exp >= 10: return "🍷 Entusiasta"
    if exp >= 3:  return "🌱 Neófito"
    return "🚪 Invitado"

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
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data   = json.loads(self.rfile.read(length))
        email  = data.get("email","").strip().lower()

        result = supabase_request("GET", f"miembros?email=eq.{email}&select=*")
        if not result or len(result) == 0:
            self._respond(404, {"ok": False, "error": "Miembro no encontrado."})
            return

        miembro = result[0]
        if miembro["experiencias"] < 25:
            self._respond(400, {"ok": False, "error": f"Necesita 25 experiencias. Tiene {miembro['experiencias']}."})
            return

        supabase_request("PATCH", f"miembros?email=eq.{email}", {"es_enofilo": True})

        try:
            access_token = get_google_token()
            safe_id      = email.replace("@", "_at_").replace(".", "_")
            object_id    = f"{ISSUER_ID}.{safe_id}"
            body = json.dumps({
                "secondaryLoyaltyPoints": {"label": "Nivel", "balance": {"string": "🔐 Enófilo"}},
                "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": "Bienvenido al círculo interno. 🔐"}]
            }).encode()
            url = f"https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject/{urllib.parse.quote(object_id, safe='')}"
            req = urllib.request.Request(url, data=body, method="PATCH")
            req.add_header("Authorization", f"Bearer {access_token}")
            req.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(req) as r:
                r.read()
        except Exception:
            pass

        self._respond(200, {"ok": True, "mensaje": f"{miembro['nombre']} ahora es Enófilo 🔐"})

    def do_GET(self):
        result = supabase_request("GET", "miembros?select=*&order=experiencias.desc")
        if "error" in result:
            self._respond(500, {"error": str(result)})
            return

        miembros = []
        for m in result:
            miembros.append({
                "nombre":        m.get("nombre",""),
                "email":         m.get("email",""),
                "experiencias":  m.get("experiencias", 0),
                "nivel":         calcular_nivel(m.get("experiencias",0), m.get("es_enofilo", False)),
                "es_enofilo":    m.get("es_enofilo", False),
                "referido_por":  m.get("referido_por"),
                "referidos":     m.get("referidos") or [],
                "fecha_ingreso": m.get("fecha_ingreso",""),
                "historial":     m.get("historial") or []
            })

        self._respond(200, {"miembros": miembros})

    def do_PATCH(self):
        length = int(self.headers.get("Content-Length", 0))
        data   = json.loads(self.rfile.read(length))
        email  = data.get("email", "").strip().lower()
        campos = {}
        if data.get("nombre", "").strip():
            campos["nombre"] = data["nombre"].strip()
        if "fecha_ingreso" in data:
            campos["fecha_ingreso"] = data["fecha_ingreso"]
        if not email or not campos:
            self._respond(400, {"ok": False, "error": "Email y al menos un campo requeridos"})
            return
        supabase_request("PATCH", f"miembros?email=eq.{urllib.parse.quote(email)}", campos)
        self._respond(200, {"ok": True})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()
        if not email:
            self._respond(400, {"ok": False, "error": "Email requerido"})
            return
        result = supabase_request("DELETE", f"miembros?email=eq.{urllib.parse.quote(email)}")
        if isinstance(result, dict) and "error" in result:
            self._respond(500, {"ok": False, "error": str(result)})
            return
        self._respond(200, {"ok": True})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass
