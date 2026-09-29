import re


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
