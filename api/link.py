import json
import os
import time
from http.server import BaseHTTPRequestHandler

ISSUER_ID = "BCR2DN5TZPM6RPTP"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Extraer email del query string: /api/link?email=...
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()

        if not email:
            self._respond(400, {"error": "Email requerido"})
            return

        try:
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
            link  = f"https://pay.google.com/gp/v/save/{token}"
            self._respond(200, {"link": link})

        except Exception as e:
            self._respond(500, {"error": str(e)})

    def do_OPTIONS(self):
        self._respond(200, {})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, *args):
        pass
