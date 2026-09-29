import json
import re
import urllib.error
import urllib.parse
import urllib.request

from http.server import BaseHTTPRequestHandler

try:
    from ._auth import (
        AuthError,
        SERVICE_ROLE_KEY,
        SUPABASE_URL,
        add_cors_headers,
        audit,
        handle_options,
        require_admin,
        require_server_config,
        respond_auth_error,
    )
except ImportError:
    from _auth import (
        AuthError,
        SERVICE_ROLE_KEY,
        SUPABASE_URL,
        add_cors_headers,
        audit,
        handle_options,
        require_admin,
        require_server_config,
        respond_auth_error,
    )


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def validate_invite_payload(data):
    email = str(data.get("email") or "").strip().lower()
    role = str(data.get("role") or "").strip()
    mode = str(data.get("mode") or "").strip()
    password = data.get("password")

    if not EMAIL_RE.match(email):
        raise ValidationError("Correo inválido")
    if role not in ("owner", "admin"):
        raise ValidationError("El rol debe ser owner o admin")
    if mode not in ("invite", "create"):
        raise ValidationError("Modo inválido")
    if mode == "create":
        if not password or len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
    else:
        password = None
    return {"email": email, "role": role, "mode": mode, "password": password}


def guard_self_deactivate(target_user_id, actor_user_id):
    if target_user_id == actor_user_id:
        raise ValidationError("No puedes desactivar tu propia cuenta")


def guard_last_owner(admins, target_user_id, new_active):
    if new_active:
        return
    target = next((a for a in admins if a["user_id"] == target_user_id), None)
    if not target or target["role"] != "owner":
        return
    remaining_active_owners = [
        a for a in admins
        if a["role"] == "owner" and a["active"] and a["user_id"] != target_user_id
    ]
    if not remaining_active_owners:
        raise ValidationError("Debe quedar al menos un owner activo")


class SupabaseError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def _request(url, method="GET", body=None, prefer=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SupabaseError(exc.code, detail) from exc
    except Exception as exc:
        raise SupabaseError(502, "No se pudo conectar con Supabase") from exc


def list_admin_profiles():
    url = f"{SUPABASE_URL}/rest/v1/admin_profiles?select=user_id,email,role,active,created_at&order=created_at.asc"
    return _request(url) or []


def list_recent_activity(limit=10):
    url = (
        f"{SUPABASE_URL}/rest/v1/admin_audit_log"
        f"?select=action,actor_email,object_type,object_id,result,created_at"
        f"&order=created_at.desc&limit={limit}"
    )
    return _request(url) or []


def insert_admin_profile(user_id, email, role):
    url = f"{SUPABASE_URL}/rest/v1/admin_profiles"
    body = {"user_id": user_id, "email": email, "role": role, "active": True}
    result = _request(url, "POST", body, prefer="return=representation")
    return result[0] if isinstance(result, list) else result


def update_admin_active(user_id, active):
    quoted = urllib.parse.quote(user_id)
    url = f"{SUPABASE_URL}/rest/v1/admin_profiles?user_id=eq.{quoted}"
    result = _request(url, "PATCH", {"active": active}, prefer="return=representation")
    return result[0] if isinstance(result, list) else result


def invite_user(email):
    url = f"{SUPABASE_URL}/auth/v1/invite"
    result = _request(url, "POST", {"email": email})
    return result["id"]


def create_user_with_password(email, password):
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    result = _request(url, "POST", {"email": email, "password": password, "email_confirm": True})
    return result["id"]


MAX_BODY_BYTES = 64 * 1024


def _require_owner(ctx):
    if (ctx.get("profile") or {}).get("role") != "owner":
        raise AuthError(403, "Solo el rol owner puede gestionar administradores")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ctx = None
        try:
            require_server_config(SUPABASE_URL=SUPABASE_URL, SERVICE_ROLE_KEY=SERVICE_ROLE_KEY)
            ctx = require_admin(self)
            _require_owner(ctx)
            self._json(200, {
                "ok": True,
                "admins": list_admin_profiles(),
                "recent_activity": list_recent_activity(),
            })
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, POST, PATCH, OPTIONS")
        except SupabaseError as exc:
            self._json(502, {"ok": False, "error": "No se pudo consultar Supabase"})

    def do_POST(self):
        ctx = None
        try:
            require_server_config(SUPABASE_URL=SUPABASE_URL, SERVICE_ROLE_KEY=SERVICE_ROLE_KEY)
            ctx = require_admin(self)
            _require_owner(ctx)
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._json(413, {"ok": False, "error": "Solicitud demasiado grande"})
                return
            data = json.loads(self.rfile.read(length))
            payload = validate_invite_payload(data)

            if payload["mode"] == "invite":
                new_user_id = invite_user(payload["email"])
            else:
                new_user_id = create_user_with_password(payload["email"], payload["password"])
            insert_admin_profile(new_user_id, payload["email"], payload["role"])

            audit(self, ctx, result="ok", action=f"admin_users.{payload['mode']}",
                  object_type="admin_profile", object_id=payload["email"])
            self._json(201, {"ok": True, "user_id": new_user_id, "email": payload["email"]})
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, POST, PATCH, OPTIONS")
        except ValidationError as exc:
            self._json(400, {"ok": False, "error": exc.message})
        except SupabaseError as exc:
            if ctx:
                audit(self, ctx, result="error", action="admin_users.invite_or_create",
                      object_type="admin_profile")
            if exc.status == 422:
                self._json(409, {"ok": False, "error": "Ya existe una cuenta con ese correo"})
            else:
                self._json(502, {
                    "ok": False,
                    "error": "No se pudo enviar la invitación — intenta crear la cuenta con contraseña directa",
                })
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"ok": False, "error": "Solicitud inválida"})

    def do_PATCH(self):
        ctx = None
        try:
            require_server_config(SUPABASE_URL=SUPABASE_URL, SERVICE_ROLE_KEY=SERVICE_ROLE_KEY)
            ctx = require_admin(self)
            _require_owner(ctx)
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._json(413, {"ok": False, "error": "Solicitud demasiado grande"})
                return
            data = json.loads(self.rfile.read(length))
            target_user_id = str(data.get("user_id") or "")
            new_active = bool(data.get("active"))
            if not target_user_id:
                self._json(400, {"ok": False, "error": "Falta user_id"})
                return

            actor_user_id = (ctx.get("user") or {}).get("id")
            guard_self_deactivate(target_user_id, actor_user_id)
            admins = list_admin_profiles()
            guard_last_owner(admins, target_user_id, new_active)

            updated = update_admin_active(target_user_id, new_active)
            audit(self, ctx, result="ok",
                  action="admin_users.reactivate" if new_active else "admin_users.deactivate",
                  object_type="admin_profile", object_id=target_user_id)
            self._json(200, {"ok": True, "admin": updated})
        except AuthError as exc:
            respond_auth_error(self, exc, methods="GET, POST, PATCH, OPTIONS")
        except ValidationError as exc:
            self._json(400, {"ok": False, "error": exc.message})
        except SupabaseError:
            if ctx:
                audit(self, ctx, result="error", action="admin_users.set_active", object_type="admin_profile")
            self._json(502, {"ok": False, "error": "No se pudo actualizar el estado del administrador"})
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"ok": False, "error": "Solicitud inválida"})

    def do_OPTIONS(self):
        handle_options(self, methods="GET, POST, PATCH, OPTIONS")

    def _json(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        add_cors_headers(self, methods="GET, POST, PATCH, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def log_message(self, *args):
        pass
