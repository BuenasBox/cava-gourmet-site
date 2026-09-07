"""Member QR / Wallet token — single source of truth (V1 + optional V2).

V1 token: hex HMAC-SHA256(HMAC_SECRET, email). Deterministic, no expiry,
no per-member revocation. member.py, scan.py and wallet.py each carried
their own copy of this logic.

V2 token: "v2.<exp_unix>.<sig>" where sig = HMAC-SHA256(HMAC_SECRET,
"v2:<email>:<exp>"). Versioned, expiring, and revocable-by-rotation
(bump MEMBER_TOKEN_SALT to invalidate every outstanding V2 link).

Rollout (all env-driven, default = today's behavior):
  * unset                     -> issue V1, accept V1 (and V2 if any exist)
  * MEMBER_TOKEN_V2=1         -> issue V2, still accept V1 (grace period)
  * MEMBER_TOKEN_V1_SUNSET=YYYY-MM-DD -> after that date, reject V1
See docs/MEMBER-TOKEN-V2.md.
"""

import hmac
import hashlib
import os
import time

HMAC_SECRET = os.environ.get("HMAC_SECRET", "")
_SALT = os.environ.get("MEMBER_TOKEN_SALT", "")
_V2_ENABLED = os.environ.get("MEMBER_TOKEN_V2") == "1"
_V2_TTL_DAYS = int(os.environ.get("MEMBER_TOKEN_V2_TTL_DAYS", "120") or "120")
_V1_SUNSET = os.environ.get("MEMBER_TOKEN_V1_SUNSET", "").strip()  # YYYY-MM-DD


def _v1_sig(email):
    return hmac.new(HMAC_SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()


def _v2_sig(email, exp):
    msg = f"v2:{_SALT}:{email}:{exp}".encode()
    return hmac.new(HMAC_SECRET.encode(), msg, hashlib.sha256).hexdigest()


def _v1_sunset_passed(now=None):
    if not _V1_SUNSET:
        return False
    try:
        y, m, d = (int(x) for x in _V1_SUNSET.split("-"))
        # Costa Rica is UTC-6, no DST. Sunset takes effect at local midnight,
        # i.e. epoch = (that calendar day 00:00 UTC) + 6h.
        import calendar
        cutoff = calendar.timegm((y, m, d, 0, 0, 0)) + 6 * 3600
        return (time.time() if now is None else now) > cutoff
    except (ValueError, TypeError):
        return False


def generar_token_v2(email, ttl_days=None, now=None):
    """Issue a fresh V2 token for `email`. Empty string if misconfigured."""
    if not HMAC_SECRET:
        return ""
    ttl = (ttl_days or _V2_TTL_DAYS) * 86400
    exp = int(time.time() if now is None else now) + ttl
    return f"v2.{exp}.{_v2_sig(email, exp)}"


def generar_token(email):
    """Issue a token for `email` in the currently configured scheme.

    Empty string if the server is misconfigured (states already blocked
    upstream by require_server_config).
    """
    if not HMAC_SECRET:
        return ""
    if _V2_ENABLED:
        return generar_token_v2(email)
    return _v1_sig(email)


def validar_token(email, token, now=None):
    """Constant-time check of a member token (V1 or V2)."""
    if not HMAC_SECRET or not token:
        return False
    ref = time.time() if now is None else now

    if token.startswith("v2."):
        parts = token.split(".")
        if len(parts) != 3:
            return False
        _, exp_str, sig = parts
        try:
            exp = int(exp_str)
        except (ValueError, TypeError):
            return False
        if exp < int(ref):
            return False  # expired
        return hmac.compare_digest(_v2_sig(email, exp), sig)

    # V1
    if _v1_sunset_passed(ref):
        return False
    return hmac.compare_digest(_v1_sig(email), token)
