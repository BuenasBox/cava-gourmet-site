import json
import os
import time
import jwt
import urllib.parse
from http.server import BaseHTTPRequestHandler

ISSUER_ID = "BCR2DN5TZPM6RPTP"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()

        if not email:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Email requerido")
            return

        try:
            key_data  = json.loads(os.environ.get("GOOGLE_WALLET_KEY", "{}"))
            safe_id   = email.replace("@", "_at_").replace(".", "_")
            object_id = f"{ISSUER_ID}.{safe_id}"
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
            self.send_header("Cache-Control", "no-store, no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def log_message(self, *args):
        pass
