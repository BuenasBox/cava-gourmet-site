"""Google Wallet API auth — single source of truth.

`get_google_token()` was copy-pasted byte-for-byte across miembros.py,
registrar.py, registrar_experiencia.py, scan.py and wallet.py (and miembros.py
had it defined twice in the same file). One copy, one place to fix.
"""

import json
import os
import time
import urllib.parse
import urllib.request

import jwt


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
