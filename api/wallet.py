import json
import os
import time
import jwt
import hmac
import hashlib
import urllib.request
import urllib.parse
from http.server import BaseHTTPRequestHandler
try:
    from ._auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error
except ImportError:
    from _auth import AuthError, add_cors_headers, handle_options, require_admin, respond_auth_error

ISSUER_ID    = "3388000000023147327"
CLASS_SUFFIX = "AfterOfficeClub"
SUPABASE_URL = "https://rbfctmcfweckbpgxlkqf.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
HMAC_SECRET  = os.environ.get("HMAC_SECRET", "")

def validar_token(email, token):
    if not HMAC_SECRET:
        return False
    expected = hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)

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
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["access_token"]

def get_nombre_from_supabase(email):
    url     = f"{SUPABASE_URL}/rest/v1/miembros?email=eq.{urllib.parse.quote(email)}&select=nombre"
    headers = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as r:
            rows = json.loads(r.read())
            if rows:
                return rows[0].get("nombre", email)
    except Exception:
        pass
    return email

def ensure_loyalty_object(email, nombre):
    access_token = get_google_token()
    safe_id      = email.replace("@", "_at_").replace(".", "_")
    object_id    = f"{ISSUER_ID}.{safe_id}"
    class_id     = f"{ISSUER_ID}.{CLASS_SUFFIX}"

    # Check if it already exists
    url = f"https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject/{urllib.parse.quote(object_id, safe='')}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {access_token}")
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
            return  # already exists
    except urllib.error.HTTPError as e:
        if e.code != 404:
            return  # unexpected error — skip creation, don't block the redirect

    # Create the object
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
    req = urllib.request.Request(
        "https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject",
        data=body, method="POST"
    )
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
    except urllib.error.HTTPError:
        pass  # 409 = already exists is fine; other errors don't block redirect

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = (params.get("email", [""])[0] or params.get("e", [""])[0]).strip().lower()
        token  = params.get("t", [""])[0]

        if not email:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "private, no-store")
            self.end_headers()
            self.wfile.write(b"Email requerido")
            return

        if token:
            if not validar_token(email, token):
                self.send_response(403)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Cache-Control", "private, no-store")
                self.end_headers()
                self.wfile.write(b"Token invalido")
                return
        else:
            try:
                require_admin(self)
            except AuthError as exc:
                respond_auth_error(self, exc, methods="GET, OPTIONS")
                return

        try:
            key_data  = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
            safe_id   = email.replace("@", "_at_").replace(".", "_")
            object_id = f"{ISSUER_ID}.{safe_id}"

            # Ensure the object exists before redirecting
            nombre = get_nombre_from_supabase(email)
            ensure_loyalty_object(email, nombre)

            claims = {
                "iss":     key_data.get("client_email", ""),
                "aud":     "google",
                "origins": ["https://cavagourmet.com"],
                "iat":     int(time.time()),
                "typ":     "savetowallet",
                "payload": {"loyaltyObjects": [{"id": object_id}]}
            }
            token      = jwt.encode(claims, key_data.get("private_key", ""), algorithm="RS256")
            wallet_url = f"https://pay.google.com/gp/v/save/{token}"

            self.send_response(302)
            self.send_header("Location", wallet_url)
            self.send_header("Cache-Control", "private, no-store")
            add_cors_headers(self, methods="GET, OPTIONS")
            self.end_headers()

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "private, no-store")
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        handle_options(self, methods="GET, OPTIONS")

    def log_message(self, *args):
        pass
