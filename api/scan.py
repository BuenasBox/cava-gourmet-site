import json
import os
import logging
import hmac
import hashlib
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
try:
    from ._member_token import validar_token
    from ._levels import calcular_nivel
except ImportError:
    from _member_token import validar_token
    from _levels import calcular_nivel

logger = logging.getLogger("cava.scan")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rbfctmcfweckbpgxlkqf.supabase.co").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY", "")
HMAC_SECRET  = os.environ.get("HMAC_SECRET", "")
SCAN_PIN     = os.environ.get("SCAN_PIN", "")
ISSUER_ID    = "3388000000023147327"

# --- Fase 0B.3: server-side rate limit / lockout / dedupe -------------------
# Inert until SCAN_HARDENING=1 AND the scan_attempts table exists
# (supabase/migrations/20260906_0002_scan_attempts.sql).
#
# Scoping:
#   token  -> success cooldown (dedupe double-registration), per-token rate,
#             per-token PIN-lockout
#   IP     -> cross-token request rate, cross-token PIN-lockout  (stops one
#             attacker cycling many stolen/guessed tokens from one host)
#
# Fail-open policy: ONLY a genuine infrastructure failure (the ledger fetch
# raised — table missing, network, 5xx) lets the request through. A ledger
# that answers and yields a block decision blocks. This means a misconfig
# can't lock out CAVA staff, but a real limit is enforced.
SCAN_HARDENING       = os.environ.get("SCAN_HARDENING") == "1"


def _guard_cfg():
    def _int(name, default):
        try:
            return int(os.environ.get(name, "") or default)
        except (TypeError, ValueError):
            return default
    return {
        "cooldown_min":    _int("SCAN_COOLDOWN_MIN", 30),
        "rate_window_min": _int("SCAN_RATE_WINDOW_MIN", 10),
        "rate_max_token":  _int("SCAN_RATE_MAX", 30),
        "rate_max_ip":     _int("SCAN_RATE_MAX_IP", 60),
        "lockout_min":     _int("SCAN_LOCKOUT_MIN", 15),
        "max_fails_token": _int("SCAN_MAX_FAILS", 5),
        "max_fails_ip":    _int("SCAN_MAX_FAILS_IP", 15),
    }


def _token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _client_ip(handler):
    fwd = (handler.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    return fwd or None


def _iso_minutes_ago(minutes):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - minutes * 60))


def _parse_ts(value):
    """PostgREST timestamptz (ISO, UTC) -> epoch seconds. Assumes UTC if naive."""
    s = str(value).strip().replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def evaluate_scan_guard(now_ts, token_rows, ip_rows, cfg):
    """Pure decision. `token_rows`/`ip_rows` are lists of {"reason", "ts"} (ts
    = epoch seconds). `ip_rows` may be None (no client IP). Returns
    (allowed: bool, reason: str). No I/O — unit-tested in api/tests/."""

    def within(rows, minutes):
        cut = now_ts - minutes * 60
        return [r for r in rows if r.get("ts", 0) >= cut]

    if any(r.get("reason") == "ok" for r in within(token_rows, cfg["cooldown_min"])):
        return False, "cooldown"
    if len(within(token_rows, cfg["rate_window_min"])) >= cfg["rate_max_token"]:
        return False, "rate_token"
    if sum(1 for r in within(token_rows, cfg["lockout_min"]) if r.get("reason") == "bad_pin") >= cfg["max_fails_token"]:
        return False, "locked_token"
    if ip_rows is not None:
        if len(within(ip_rows, cfg["rate_window_min"])) >= cfg["rate_max_ip"]:
            return False, "rate_ip"
        if sum(1 for r in within(ip_rows, cfg["lockout_min"]) if r.get("reason") == "bad_pin") >= cfg["max_fails_ip"]:
            return False, "locked_ip"
    return True, "ok"


def _fetch_attempts(field, value, since_iso):
    """Raises on infra failure (table missing / network). [] means 0 rows."""
    res = supabase_request(
        "GET",
        f"scan_attempts?{field}=eq.{urllib.parse.quote(value)}"
        f"&created_at=gte.{urllib.parse.quote(since_iso)}"
        "&select=reason,created_at&order=created_at.desc&limit=500",
    )
    if not isinstance(res, list):
        raise RuntimeError("scan_attempts fetch failed: %r" % (res,))
    rows = []
    for r in res:
        try:
            rows.append({"reason": r.get("reason"), "ts": _parse_ts(r["created_at"])})
        except Exception:
            continue
    return rows


def scan_guard_check(token_hash, ip):
    """(allowed, reason). Fail-open only on infrastructure failure."""
    if not SCAN_HARDENING:
        return True, "ok"
    cfg = _guard_cfg()
    widest = max(cfg["cooldown_min"], cfg["lockout_min"], cfg["rate_window_min"])
    since = _iso_minutes_ago(widest)
    try:
        token_rows = _fetch_attempts("token_hash", token_hash, since)
    except Exception:
        logger.warning("scan_guard: token ledger fetch failed -> fail-open", exc_info=True)
        return True, "infra"
    ip_rows = None
    if ip:
        try:
            ip_rows = _fetch_attempts("ip", ip, since)
        except Exception:
            logger.warning("scan_guard: ip ledger fetch failed -> ip checks skipped", exc_info=True)
            ip_rows = None
    return evaluate_scan_guard(time.time(), token_rows, ip_rows, cfg)


def scan_record(token_hash, ip, success, reason):
    if not SCAN_HARDENING:
        return
    try:
        supabase_request("POST", "scan_attempts", {
            "token_hash": token_hash,
            "ip": ip,
            "success": bool(success),
            "reason": reason,
        })
    except Exception:
        logger.warning("scan_guard: no se pudo registrar el intento", exc_info=True)
# --------------------------------------------------------------------------


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
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read()
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()}

def mensaje_progreso(exp, es_enofilo=False):
    if es_enofilo:  return "Parte del círculo interno de CAVA. 🔐"
    if exp >= 25:   return "Candidato a Enófilo — pendiente de invitación."
    if exp >= 10:   return f"Faltan {25 - exp} experiencias para ser candidato a Enófilo."
    if exp >= 3:    return f"Faltan {10 - exp} para Entusiasta 🍷"
    return f"Faltan {3 - exp} para Neófito 🌱"

def get_google_token():
    import jwt
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

def actualizar_wallet(email, exp, es_enofilo):
    try:
        nivel     = calcular_nivel(exp, es_enofilo)
        progreso  = mensaje_progreso(exp, es_enofilo)
        safe_id   = email.replace("@", "_at_").replace(".", "_")
        object_id = f"{ISSUER_ID}.{safe_id}"
        body = json.dumps({
            "loyaltyPoints":          {"label": "Experiencias", "balance": {"int": exp}},
            "secondaryLoyaltyPoints": {"label": "Nivel",        "balance": {"string": nivel}},
            "textModulesData": [{"id": "progreso", "header": "Tu progreso", "body": progreso}]
        }).encode()
        url = f"https://walletobjects.googleapis.com/walletobjects/v1/loyaltyObject/{urllib.parse.quote(object_id, safe='')}"
        access_token = get_google_token()
        req = urllib.request.Request(url, data=body, method="PATCH")
        req.add_header("Authorization", f"Bearer {access_token}")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=12) as r:
            r.read()
    except Exception:
        logger.exception("scan: no se pudo actualizar el objeto de Google Wallet")

def _styles():
    return """
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:#091522;color:#f6efe3;font-family:'Jost',system-ui,sans-serif;font-weight:300;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:2rem}
    .wrap{max-width:340px;width:100%;text-align:center}
    .nombre{font-family:'Cormorant Garamond',Georgia,serif;font-size:1.9rem;font-weight:300;font-style:italic;color:#d7b879;margin-bottom:.4rem;line-height:1.1}
    .nivel{display:inline-block;border:1px solid rgba(184,151,90,.4);color:#d7b879;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;padding:.3rem .85rem;border-radius:3px;margin-bottom:1.5rem}
    .exp-num{font-family:'Cormorant Garamond',serif;font-size:4rem;font-weight:300;color:#b8975a;line-height:1}
    .exp-label{font-size:.58rem;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,239,227,.45);margin-top:.2rem;margin-bottom:1.25rem}
    .progreso{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.05rem;color:rgba(246,239,227,.7);line-height:1.6;margin-bottom:1.75rem}
    .pin-label{font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:rgba(246,239,227,.5);margin-bottom:.75rem}
    .pin-input{background:rgba(255,255,255,.07);border:1px solid rgba(184,151,90,.3);border-radius:8px;color:#f6efe3;font-family:'Jost',sans-serif;font-size:1.6rem;font-weight:300;letter-spacing:.4em;text-align:center;padding:.7rem 1rem;width:160px;outline:none;-webkit-appearance:none}
    .pin-input:focus{border-color:#b8975a}
    .btn{display:inline-flex;align-items:center;justify-content:center;margin-top:1.25rem;width:100%;background:#b8975a;color:#091522;border:none;border-radius:7px;font-family:'Jost',sans-serif;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;padding:.9rem 1.25rem;cursor:pointer;font-weight:400}
    .btn:hover{background:#d7b879}
    .check{font-size:2.5rem;margin-bottom:1.25rem;color:#b8975a}
    .divider{width:36px;height:1px;background:rgba(184,151,90,.25);margin:1.5rem auto}
    .brand{font-size:.56rem;letter-spacing:.22em;text-transform:uppercase;color:rgba(246,239,227,.25)}
    .error-msg{color:#f0a0a0;font-size:.85rem;margin-top:.75rem}
    """

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not SUPABASE_URL or not SUPABASE_KEY or not HMAC_SECRET or not SCAN_PIN:
            self._html(503, self._page_error("Servicio temporalmente no disponible"))
            return
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        email  = params.get("email", [""])[0].strip().lower()
        token  = params.get("t", [""])[0]

        if not email or not token:
            self._html(400, self._page_error("Parámetros inválidos"))
            return
        if not validar_token(email, token):
            self._html(403, self._page_error("Código QR no válido"))
            return

        result = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(email)}&select=nombre,experiencias,es_enofilo")
        if not result or isinstance(result, dict):
            self._html(404, self._page_error("Miembro no encontrado"))
            return

        miembro = result[0]
        nombre  = miembro.get("nombre", "")
        exp     = miembro.get("experiencias", 0)
        nivel   = calcular_nivel(exp, miembro.get("es_enofilo", False))

        self._html(200, self._page_pin(nombre, nivel, exp, email, token))

    def do_POST(self):
        if not SUPABASE_URL or not SUPABASE_KEY or not HMAC_SECRET or not SCAN_PIN:
            self._html(503, self._page_error("Servicio temporalmente no disponible"))
            return
        parsed  = urllib.parse.urlparse(self.path)
        params  = urllib.parse.parse_qs(parsed.query)
        email   = params.get("email", [""])[0].strip().lower()
        token   = params.get("t", [""])[0]
        length  = int(self.headers.get("Content-Length", 0))
        body    = urllib.parse.parse_qs(self.rfile.read(length).decode())
        pin     = body.get("pin", [""])[0].strip()

        if not email or not token:
            self._html(400, self._page_error("Parámetros inválidos"))
            return
        if not validar_token(email, token):
            self._html(403, self._page_error("Código QR no válido"))
            return

        token_hash = _token_hash(token)
        client_ip  = _client_ip(self)
        allowed, why = scan_guard_check(token_hash, client_ip)
        if not allowed:
            scan_record(token_hash, client_ip, False, why)
            self._html(429, self._page_error("Demasiados intentos. Esperá unos minutos e intentá de nuevo."))
            return

        if not SCAN_PIN or pin != SCAN_PIN:
            scan_record(token_hash, client_ip, False, "bad_pin")
            # Re-fetch member to show form again with error
            result = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(email)}&select=nombre,experiencias,es_enofilo")
            if result and not isinstance(result, dict):
                m      = result[0]
                nombre = m.get("nombre", "")
                exp    = m.get("experiencias", 0)
                nivel  = calcular_nivel(exp, m.get("es_enofilo", False))
                self._html(403, self._page_pin(nombre, nivel, exp, email, token, error=True))
            else:
                self._html(403, self._page_error("PIN incorrecto"))
            return

        result = supabase_request("GET", f"miembros?email=eq.{urllib.parse.quote(email)}&select=*")
        if not result or isinstance(result, dict):
            self._html(404, self._page_error("Miembro no encontrado"))
            return

        miembro    = result[0]
        nombre     = miembro.get("nombre", "")
        nuevas_exp = miembro["experiencias"] + 1
        historial  = miembro.get("historial") or []
        historial.append({"fecha": time.strftime("%d/%m/%Y"), "nota": "Enofilios Cava — After Office"})

        supabase_request("PATCH", f"miembros?email=eq.{urllib.parse.quote(email)}", {
            "experiencias": nuevas_exp,
            "historial":    historial
        })
        scan_record(token_hash, client_ip, True, "ok")
        actualizar_wallet(email, nuevas_exp, miembro.get("es_enofilo", False))

        nivel    = calcular_nivel(nuevas_exp, miembro.get("es_enofilo", False))
        progreso = mensaje_progreso(nuevas_exp, miembro.get("es_enofilo", False))
        self._html(200, self._page_ok(nombre, nuevas_exp, nivel, progreso))

    def _page_pin(self, nombre, nivel, exp, email, token, error=False):
        error_html = '<p class="error-msg">PIN incorrecto. Intenta de nuevo.</p>' if error else ""
        action     = f"/api/scan?email={urllib.parse.quote(email)}&t={urllib.parse.quote(token)}"
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Confirmar visita · CAVA</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Jost:wght@300;400&display=swap" rel="stylesheet">
<style>{_styles()}</style>
</head>
<body>
<div class="wrap">
  <div class="nombre">{nombre}</div>
  <div class="nivel">{nivel} &middot; {exp} exp.</div>
  <form method="POST" action="{action}" style="margin-top:.5rem">
    <p class="pin-label">Ingresa el PIN para confirmar</p>
    <input class="pin-input" type="number" name="pin" inputmode="numeric"
           pattern="[0-9]*" maxlength="6" autofocus placeholder="····" autocomplete="off">
    {error_html}
    <button type="submit" class="btn">Confirmar visita</button>
  </form>
</div>
</body>
</html>"""

    def _page_ok(self, nombre, exp, nivel, progreso):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Visita registrada · CAVA</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;1,300&family=Jost:wght@300;400&display=swap" rel="stylesheet">
<style>{_styles()}</style>
</head>
<body>
<div class="wrap">
  <div class="check">✓</div>
  <div class="nombre">{nombre}</div>
  <div class="nivel">{nivel}</div>
  <div class="exp-num">{exp}</div>
  <div class="exp-label">experiencias</div>
  <div class="progreso">{progreso}</div>
  <div class="divider"></div>
  <div class="brand">Enofilios Cava &middot; CAVA Vinoteca</div>
</div>
</body>
</html>"""

    def _page_error(self, msg):
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Error · CAVA</title>
<style>body{{background:#091522;color:#f0a0a0;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;text-align:center;padding:2rem;font-size:.9rem}}</style>
</head>
<body><p>&#10060; {msg}</p></body>
</html>"""

    def _html(self, code, html):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "private, no-store")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass
