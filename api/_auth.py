import json
import os
import urllib.parse
import urllib.request


SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rbfctmcfweckbpgxlkqf.supabase.co").rstrip("/")
SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY", "")
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
    return {"user": user, "profile": profile}


def respond_auth_error(handler, error, methods="GET, POST, PATCH, DELETE, OPTIONS"):
    _json_response(handler, error.status, {"ok": False, "error": error.message}, methods=methods)
