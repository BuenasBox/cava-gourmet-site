"""Member QR / Wallet token — single source of truth.

V1 token: hex HMAC-SHA256(HMAC_SECRET, email). Deterministic, no expiry,
no per-member revocation. member.py, scan.py and wallet.py each carried
their own copy of this logic. Centralised here so a V2 scheme (versioned,
expiring, revocable) can be introduced in one place — see
docs/MEMBER-TOKEN-V2.md.
"""

import hmac
import hashlib
import os

HMAC_SECRET = os.environ.get("HMAC_SECRET", "")


def generar_token(email):
    """V1 token for `email`. Empty string if the server is misconfigured."""
    if not HMAC_SECRET:
        return ""
    return hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()


def validar_token(email, token):
    """Constant-time check of a V1 token. False if secret or token is missing."""
    if not HMAC_SECRET or not token:
        return False
    expected = hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)
