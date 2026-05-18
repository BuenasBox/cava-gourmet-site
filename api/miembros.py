import json
import os
from http.server import BaseHTTPRequestHandler
import urllib.request

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
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

def calcular_nivel(exp, es_enofilo=False):
    if es_enofilo and exp >= 25: return "🔐 Enófilo"
    if exp >= 10: return "🍷 Entusiasta"
    if exp >= 3:  return "🌱 Neófito"
    return "🚪 Invitado"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Invitar como Enófilo
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

        # Actualizar Google Wallet
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            import os

            ISSUER_ID    = "BCR2DN5TZPM6RPTP"
            CLASS_SUFFIX = "AfterOfficeClub"
            WALLET_SCOPE = ["https://www.googleapis.com/auth/wallet_object.issuer"]

            key_data  = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
            creds     = service_account.Credentials.from_service_account_info(key_data, scopes=WALLET_SCOPE)
            service   = build("walletobjects", "v1", credentials=creds)
            safe_id   = email.replace("@","_at_").replace(".","_")
            object_id = f"{ISSUER_ID}.{safe_id}"

            service.loyaltyObject().patch(
                resourceId=object_id,
                body={
                    "secondaryLoyaltyPoints": {"label": "Nivel", "balance": {"string": "🔐 Enófilo"}},
                    "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": "Bienvenido al círculo interno. 🔐"}]
                }
            ).execute()
        except Exception:
            pass

        self._respond(200, {"ok": True, "mensaje": f"{miembro['nombre']} ahora es Enófilo 🔐"})

    def do_GET(self):
        # Listar todos los miembros
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

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass
