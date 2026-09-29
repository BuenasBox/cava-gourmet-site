import json
import re
import urllib.error
import urllib.parse
import urllib.request

try:
    from ._auth import SUPABASE_URL, SERVICE_ROLE_KEY
except ImportError:
    from _auth import SUPABASE_URL, SERVICE_ROLE_KEY


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
