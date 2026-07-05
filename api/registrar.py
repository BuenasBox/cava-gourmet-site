import json
import os
import time
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
try:
    from ._auth import AuthError, add_cors_headers, handle_options, read_json_body, require_admin, require_server_config, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, read_json_body, require_admin, require_server_config, respond_auth_error

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ISSUER_ID    = "3388000000023147327"
CLASS_SUFFIX = "AfterOfficeClub"

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
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

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

def crear_loyalty_object(email, nombre):
    access_token = get_google_token()
    safe_id      = email.replace("@", "_at_").replace(".", "_")
    object_id    = f"{ISSUER_ID}.{safe_id}"
    class_id     = f"{ISSUER_ID}.{CLASS_SUFFIX}"
    body = json.dumps({
        "id":        object_id,
        "classId":   class_id,
        "state":     "ACTIVE",
        "accountName": nombre,
        "accountId":   email,
        "loyaltyPoints": {
            "balance": {"int": 0},
            "label":   "Experiencias"
        },
        "secondaryLoyaltyPoints": {
            "balance": {"string": "🚪 Invitado"},
            "label":   "Nivel"
        }
    }, ensure_ascii=False).encode()
    url = "https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject"
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
    except urllib.error.HTTPError as e:
        # 409 = object already exists — not an error
        if e.code != 409:
            raise

def generar_link_wallet(email):
    import jwt
    key_data  = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
    safe_id   = email.replace("@","_at_").replace(".","_")
    object_id = f"{ISSUER_ID}.{safe_id}"
    claims = {
        "iss":     key_data.get("client_email",""),
        "aud":     "google",
        "origins": ["https://cavagourmet.com"],
        "iat":     int(time.time()),
        "typ":     "savetowallet",
        "payload": {"loyaltyObjects": [{"id": object_id}]}
    }
    token = jwt.encode(claims, key_data.get("private_key",""), algorithm="RS256")
    return f"https://pay.google.com/gp/v/save/{token}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            require_server_config(SUPABASE_URL=SUPABASE_URL, SUPABASE_KEY=SUPABASE_KEY)
            require_admin(self)
            data = read_json_body(self)
        except AuthError as exc:
            respond_auth_error(self, exc, methods="POST, OPTIONS")
            return

        email        = data.get("email","").strip().lower()
        nombre       = data.get("nombre","").strip()
        fecha        = data.get("fecha_ingreso", time.strftime("%d/%m/%Y"))
        referido_por = data.get("referido_por") or None

        if not email or not nombre:
            self._respond(400, {"ok": False, "error": "Nombre y email requeridos"})
            return

        # Verificar si ya existe
        existing = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(email)}&select=id")
        if existing and len(existing) > 0:
            self._respond(409, {"ok": False, "error": "Este email ya está registrado."})
            return

        # Insertar en Supabase
        miembro = {
            "nombre":        nombre,
            "email":         email,
            "experiencias":  0,
            "es_enofilo":    False,
            "referido_por":  referido_por,
            "referidos":     [],
            "fecha_ingreso": fecha,
            "historial":     []
        }
        result = supabase_request("POST", "miembros", miembro)

        if "error" in result:
            self._respond(500, {"ok": False, "error": "No se pudo registrar el miembro"})
            return

        # Actualizar referidos del que lo refirió
        if referido_por:
            ref = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(referido_por)}&select=id,referidos")
            if ref and len(ref) > 0:
                ref_doc = ref[0]
                nuevos  = (ref_doc.get("referidos") or []) + [email]
                supabase_request("PATCH", f"miembros?email=eq.{urllib.parse.quote(referido_por)}", {"referidos": nuevos})

        # Crear Loyalty Object en Google Wallet
        try:
            crear_loyalty_object(email, nombre)
        except Exception:
            pass

        try:
            link = generar_link_wallet(email)
        except Exception:
            link = ""

        self._respond(200, {"ok": True, "nivel": "🚪 Invitado", "link": link})

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
