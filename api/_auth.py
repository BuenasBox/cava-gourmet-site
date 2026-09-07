import json
import logging
import os
import urllib.parse
import urllib.request


logger = logging.getLogger("cava.auth")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rbfctmcfweckbpgxlkqf.supabase.co").rstrip("/")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY", "")
AUDIT_ENABLED = os.environ.get("ADMIN_AUDIT") == "1"
ALLOWED_ORIGINS = {
    origin.strip().rstrip("/")
    for origin in os.environ.get(
        "CAVA_ALLOWED_ORIGINS",
        "https://www.cavagourmet.com,https://cavagourmet.com,http://localhost:3000,http://localhost:5173,http://127.0.0.1:5500",
    ).split(",")
    if origin.strip()
}
MAX_JSON_BODY_BYTES = 64 * 1024


class AuthError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def read_json_body(handler, max_bytes=MAX_JSON_BODY_BYTES):
    content_type = (handler.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        raise AuthError(415, "Content-Type application/json requerido")

    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except (TypeError, ValueError):
        raise AuthError(400, "Content-Length inválido")

    if length <= 0:
        raise AuthError(400, "Cuerpo JSON requerido")
    if length > max_bytes:
        raise AuthError(413, "Cuerpo de solicitud demasiado grande")

    try:
        data = json.loads(handler.rfile.read(length))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise AuthError(400, "JSON inválido")

    if not isinstance(data, dict):
        raise AuthError(400, "El cuerpo JSON debe ser un objeto")
    return data


def require_server_config(**values):
    if any(not value for value in values.values()):
        raise AuthError(503, "Configuración del servidor incompleta")


def _json_response(handler, status, body, methods="GET, POST, PATCH, DELETE, OPTIONS"):
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    add_cors_headers(handler, methods=methods)
    handler.end_headers()
    handler.wfile.write(json.dumps(body, ensure_ascii=False).encode())


def get_allowed_origin(handler):
    origin = (handler.headers.get("Origin") or "").rstrip("/")
    if origin in ALLOWED_ORIGINS:
        return origin
    return ""


def add_cors_headers(handler, methods="GET, POST, PATCH, DELETE, OPTIONS"):
    origin = get_allowed_origin(handler)
    if origin:
        handler.send_header("Access-Control-Allow-Origin", origin)
        handler.send_header("Vary", "Origin")
    handler.send_header("Access-Control-Allow-Methods", methods)
    handler.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")


def handle_options(handler, methods="GET, POST, PATCH, DELETE, OPTIONS"):
    origin = handler.headers.get("Origin")
    if origin and not get_allowed_origin(handler):
        _json_response(handler, 403, {"ok": False, "error": "Origen no permitido"}, methods=methods)
        return
    handler.send_response(204)
    add_cors_headers(handler, methods=methods)
    handler.end_headers()


def require_allowed_origin(handler):
    origin = handler.headers.get("Origin")
    if origin and not get_allowed_origin(handler):
        raise AuthError(403, "Origen no permitido")


def get_bearer_token(handler):
    auth = handler.headers.get("Authorization", "")
    prefix = "Bearer "
    if not auth.startswith(prefix):
        raise AuthError(401, "Authorization Bearer requerido")
    token = auth[len(prefix):].strip()
    if not token:
        raise AuthError(401, "Token requerido")
    return token


def get_supabase_user(access_token):
    if not SERVICE_ROLE_KEY:
        raise AuthError(500, "SUPABASE_SERVICE_ROLE_KEY no configurado")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {access_token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise AuthError(401, "Token inválido")
        raise AuthError(502, "No se pudo validar la sesión")
    except Exception:
        raise AuthError(502, "No se pudo validar la sesión")


def get_admin_profile(user_id):
    endpoint = (
        "admin_profiles?"
        f"user_id=eq.{urllib.parse.quote(user_id)}"
        "&active=eq.true"
        "&select=user_id,email,role,active"
        "&limit=1"
    )
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{endpoint}",
        headers={
            "apikey": SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            rows = json.loads(response.read())
    except urllib.error.HTTPError:
        raise AuthError(500, "No se pudo consultar perfil admin")
    except Exception:
        raise AuthError(500, "No se pudo consultar perfil admin")
    return rows[0] if rows else None


def audit(handler, ctx, result="ok", action=None, object_type=None, object_id=None):
    """Best-effort admin audit row. No-op unless ADMIN_AUDIT=1.

    Never raises and never blocks the request on failure. Stores only the
    actor's own id/email + the request line + Origin -- no tokens, no PII.

    Two call sites, by design:
      * require_admin() logs result="authorized" -- this request passed the
        admin gate. It does NOT assert the downstream action succeeded.
      * a mutating endpoint calls this again AFTER its write, with
        result="ok"/"error" and a specific action/object_type/object_id.
    """
    if not AUDIT_ENABLED:
        return
    try:
        ctx = ctx or {}
        profile = ctx.get("profile") or {}
        user = ctx.get("user") or {}
        path = urllib.parse.urlparse(handler.path).path
        row = {
            "actor_user_id": user.get("id") or profile.get("user_id"),
            "actor_email": profile.get("email") or user.get("email"),
            "action": action or f"{getattr(handler, 'command', '?')} {path}",
            "object_type": object_type,
            "object_id": None if object_id is None else str(object_id),
            "result": result,
            "origin": handler.headers.get("Origin"),
        }
        body = json.dumps({k: v for k, v in row.items() if v is not None}).encode()
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/admin_audit_log",
            data=body,
            method="POST",
            headers={
                "apikey": SERVICE_ROLE_KEY,
                "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
    except Exception:
        logger.warning("audit: no se pudo registrar la acción admin", exc_info=True)


def require_admin(handler):
    require_allowed_origin(handler)
    token = get_bearer_token(handler)
    user = get_supabase_user(token)
    user_id = user.get("id")
    if not user_id:
        raise AuthError(401, "Sesión inválida")
    profile = get_admin_profile(user_id)
    if not profile or profile.get("role") not in ("owner", "admin"):
        raise AuthError(403, "Admin requerido")
    ctx = {"user": user, "profile": profile}
    audit(handler, ctx, result="authorized")
    return ctx


def respond_auth_error(handler, error, methods="GET, POST, PATCH, DELETE, OPTIONS"):
    _json_response(handler, error.status, {"ok": False, "error": error.message}, methods=methods)
