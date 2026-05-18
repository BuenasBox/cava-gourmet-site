import json
import os
import time
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ISSUER_ID    = "BCR2DN5TZPM6RPTP"
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
        length = int(self.headers.get("Content-Length", 0))
        data   = json.loads(self.rfile.read(length))

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
            self._respond(500, {"ok": False, "error": str(result)})
            return

        # Actualizar referidos del que lo refirió
        if referido_por:
            ref = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(referido_por)}&select=id,referidos")
            if ref and len(ref) > 0:
                ref_doc = ref[0]
                nuevos  = (ref_doc.get("referidos") or []) + [email]
                supabase_request("PATCH", f"miembros?email=eq.{urllib.parse.quote(referido_por)}", {"referidos": nuevos})

        try:
            link = generar_link_wallet(email)
        except Exception:
            link = ""

        self._respond(200, {"ok": True, "nivel": "🚪 Invitado", "link": link})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass
