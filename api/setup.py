import json
import os
import time
import jwt
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error

ISSUER_ID    = "3388000000023147327"
CLASS_SUFFIX = "AfterOfficeClub"
LOGO_URL     = "https://raw.githubusercontent.com/BuenasBox/cava-gourmet-site/refs/heads/master/Assets/Logo-Cava.png"

def get_google_token():
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

def wallet_request(method, path, body=None):
    access_token = get_google_token()
    url  = f"https://walletobjects.googleapis.com/walletobjects/v1/{path}"
    data = json.dumps(body, ensure_ascii=False).encode() if body else None
    req  = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            require_admin(self)
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, OPTIONS")
            return
        class_id = f"{ISSUER_ID}.{CLASS_SUFFIX}"

        # Verificar si ya existe
        status, _ = wallet_request("GET", f"loyaltyClass/{urllib.parse.quote(class_id, safe='')}")
        if status == 200:
            self._respond(200, {"ok": True, "status": "exists", "classId": class_id})
            return

        # Crear la clase
        loyalty_class = {
            "id":          class_id,
            "issuerName":  "CAVA Vinoteca",
            "programName": "Enofilios Cava",
            "programLogo": {
                "sourceUri": {"uri": LOGO_URL},
                "contentDescription": {
                    "defaultValue": {"language": "es", "value": "Logo CAVA Vinoteca"}
                }
            },
            "loyaltyPoints": {
                "label":   "Experiencias",
                "balance": {"int": 0}
            },
            "secondaryLoyaltyPoints": {
                "label":   "Nivel",
                "balance": {"string": "🚪 Invitado"}
            },
            "hexBackgroundColor": "#091522",
            "reviewStatus": "UNDER_REVIEW",
            "multipleDevicesAndHoldersAllowedStatus": "MULTIPLE_HOLDERS"
        }

        status, data = wallet_request("POST", "loyaltyClass", loyalty_class)

        if status in (200, 201):
            self._respond(200, {"ok": True, "status": "created", "classId": class_id})
        else:
            self._respond(500, {"ok": False, "error": data})

    def do_OPTIONS(self):
        handle_options(self, methods="GET, OPTIONS")

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        add_cors_headers(self, methods="GET, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode())

    def log_message(self, *args):
        pass
