import json
import os
import time
from http.server import BaseHTTPRequestHandler
import urllib.request

SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ISSUER_ID    = "BCR2DN5TZPM6RPTP"
CLASS_SUFFIX = "AfterOfficeClub"
LOGO_URL     = "https://raw.githubusercontent.com/BuenasBox/cava-gourmet-site/refs/heads/master/Assets/Logo-Cava.png"
WALLET_SCOPE = ["https://www.googleapis.com/auth/wallet_object.issuer"]

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

def mensaje_progreso(exp, es_enofilo=False):
    if es_enofilo:   return "Bienvenido al círculo interno. 🔐"
    if exp >= 25:    return "25 experiencias ✓ — Pendiente de invitación CAVA."
    if exp >= 10:    return f"Te faltan {25 - exp} experiencias para ser candidato a Enófilo."
    if exp >= 3:     return f"Te faltan {10 - exp} experiencias para Entusiasta."
    return f"Te faltan {3 - exp} experiencias para Neófito."

def actualizar_wallet(miembro):
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        key_data = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
        creds    = service_account.Credentials.from_service_account_info(key_data, scopes=WALLET_SCOPE)
        service  = build("walletobjects", "v1", credentials=creds)

        email      = miembro["email"]
        exp        = miembro["experiencias"]
        enofilo    = miembro.get("es_enofilo", False)
        nivel      = calcular_nivel(exp, enofilo)
        progreso   = mensaje_progreso(exp, enofilo)
        safe_id    = email.replace("@","_at_").replace(".","_")
        object_id  = f"{ISSUER_ID}.{safe_id}"
        class_id   = f"{ISSUER_ID}.{CLASS_SUFFIX}"

        service.loyaltyObject().patch(
            resourceId=object_id,
            body={
                "loyaltyPoints": {"label": "Experiencias", "balance": {"int": exp}},
                "secondaryLoyaltyPoints": {"label": "Nivel", "balance": {"string": nivel}},
                "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": progreso}]
            }
        ).execute()
    except Exception:
        pass  # No interrumpir si falla la actualización de Wallet

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data   = json.loads(self.rfile.read(length))

        email = data.get("email","").strip().lower()
        nota  = data.get("nota", "Enofilios Cava")

        if not email:
            self._respond(400, {"ok": False, "error": "Email requerido"})
            return

        # Obtener miembro
        result = supabase_request("GET", f"miembros?email=eq.{email}&select=*")
        if not result or len(result) == 0:
            self._respond(404, {"ok": False, "error": "Miembro no encontrado. Regístralo primero."})
            return

        miembro    = result[0]
        nuevas_exp = miembro["experiencias"] + 1
        historial  = miembro.get("historial") or []
        historial.append({"fecha": time.strftime("%d/%m/%Y"), "nota": nota})

        # Actualizar en Supabase
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
