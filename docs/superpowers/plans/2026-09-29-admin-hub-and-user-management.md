# Admin Hub + Admin User Management Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a protected `/admin` hub that links the three existing CAVA admin tools together, adds a back-link from each tool to that hub, and lets the `owner` role invite/deactivate admin accounts without touching SQL.

**Architecture:** A new static page (`admin/index.html`) using the same Supabase-auth pattern already proven in `admin/editor-articulo-cava.html`, backed by a new server-side endpoint (`api/admin_users.py`) that follows the exact `BaseHTTPRequestHandler` + `api/_auth.py` pattern already used by `api/journal_publish.py`. Three tiny edits add a "logo links home" back-link to the existing tools.

**Tech Stack:** Vanilla HTML/CSS/JS (no framework, no build step — matches the rest of the site), Python 3.12 stdlib (`http.server`, `urllib`) for the API, Supabase (Auth + PostgREST) as the backend.

## Global Constraints

- No new npm or pip dependencies — everything uses stdlib + the already-loaded Supabase JS client.
- Every new/edited admin HTML page keeps `<meta name="robots" content="noindex,nofollow">`.
- Reuse the exact pinned Supabase JS client already used in `admin/editor-articulo-cava.html`: `<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.115.0/dist/umd/supabase.js" integrity="sha384-CLZeq1dk8+Uzrs7TVvBUdlFoV5F0DMqgRoeHa8g5wJcuPe5SkVfEvdxB0ZuzlnBQ" crossorigin="anonymous"></script>` — do not swap versions or drop the integrity hash.
- Reuse the CAVA admin design tokens exactly as defined in `admin/editor-articulo-cava.html`'s `:root` block (`--ivory`, `--gold`, `--gold-soft`, `--navy`, `--navy-deep`, `--charcoal`, `--charcoal-2`, `--line`, `--display`/`--serif`/`--sans` font stacks) — copy them verbatim into the new page, don't invent new ones.
- `api/admin_users.py` must import `require_admin`, `AuthError`, `add_cors_headers`, `handle_options`, `audit`, `require_server_config`, `SUPABASE_URL`, `SERVICE_ROLE_KEY` from `api/_auth.py` exactly the way `api/journal_publish.py` already does (`try: from ._auth import ... except ImportError: from _auth import ...`) — do not duplicate that logic.
- Every mutating request in `api/admin_users.py` must additionally reject with 403 unless `ctx["profile"]["role"] == "owner"`.
- Do not push to `origin` or open a PR at any point in this plan without the user's explicit go-ahead in that session — stop after the final local commit and ask, exactly as done for PR #13/#14 this session.
- Work happens on a new branch `feature/admin-hub-and-user-management`, created in Task 1 before the first commit.

---

### Task 1: `api/admin_users.py` — validation and guard helpers (TDD)

**Files:**
- Create: `api/admin_users.py`
- Create: `api/tests/test_admin_users_helpers.py`

**Interfaces:**
- Produces: `ValidationError(message: str)` (exception, `.message` attribute), `validate_invite_payload(data: dict) -> dict` (returns `{"email": str, "role": str, "mode": str, "password": str|None}`, raises `ValidationError`), `guard_self_deactivate(target_user_id: str, actor_user_id: str) -> None` (raises `ValidationError`), `guard_last_owner(admins: list[dict], target_user_id: str, new_active: bool) -> None` (raises `ValidationError`; each `admins` item has keys `user_id`, `role`, `active`).

- [ ] **Step 1: Write the failing tests**

Create `api/tests/test_admin_users_helpers.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import admin_users as au


def test_validate_invite_payload_ok_invite():
    result = au.validate_invite_payload({"email": "Nueva@CavaGourmet.com", "role": "admin", "mode": "invite"})
    assert result == {"email": "nueva@cavagourmet.com", "role": "admin", "mode": "invite", "password": None}


def test_validate_invite_payload_ok_create():
    result = au.validate_invite_payload({
        "email": "nueva@cavagourmet.com", "role": "admin", "mode": "create", "password": "unaClaveSegura1",
    })
    assert result["mode"] == "create"
    assert result["password"] == "unaClaveSegura1"


def test_validate_invite_payload_rejects_bad_email():
    try:
        au.validate_invite_payload({"email": "no-es-correo", "role": "admin", "mode": "invite"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_rejects_bad_role():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "superadmin", "mode": "invite"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_rejects_bad_mode():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "delete"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_create_requires_password_length():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "create", "password": "corta"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_validate_invite_payload_create_requires_password_present():
    try:
        au.validate_invite_payload({"email": "a@b.com", "role": "admin", "mode": "create"})
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_self_deactivate_blocks_self():
    try:
        au.guard_self_deactivate("u1", "u1")
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_self_deactivate_allows_others():
    au.guard_self_deactivate("u1", "u2")


def test_guard_last_owner_blocks_dropping_to_zero():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "admin1", "role": "admin", "active": True},
    ]
    try:
        au.guard_last_owner(admins, "owner1", False)
        assert False, "debió lanzar ValidationError"
    except au.ValidationError:
        pass


def test_guard_last_owner_allows_when_another_owner_remains():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "owner2", "role": "owner", "active": True},
    ]
    au.guard_last_owner(admins, "owner1", False)


def test_guard_last_owner_ignores_non_owner_targets():
    admins = [
        {"user_id": "owner1", "role": "owner", "active": True},
        {"user_id": "admin1", "role": "admin", "active": True},
    ]
    au.guard_last_owner(admins, "admin1", False)


def test_guard_last_owner_allows_reactivating():
    admins = [{"user_id": "owner1", "role": "owner", "active": False}]
    au.guard_last_owner(admins, "owner1", True)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest api/tests/test_admin_users_helpers.py -v`
Expected: `ModuleNotFoundError: No module named 'admin_users'` (the file doesn't exist yet).

- [ ] **Step 3: Create the branch and write the minimal implementation**

```bash
git checkout master
git pull origin master
git checkout -b feature/admin-hub-and-user-management
```

Create `api/admin_users.py`:

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest api/tests/test_admin_users_helpers.py -v`
Expected: `13 passed`

- [ ] **Step 5: Commit**

```bash
git add api/admin_users.py api/tests/test_admin_users_helpers.py
git commit -m "feat(admin): validation and guard helpers for admin user management"
```

---

### Task 2: `api/admin_users.py` — Supabase network functions

**Files:**
- Modify: `api/admin_users.py` (append below the code from Task 1)

**Interfaces:**
- Consumes: `SUPABASE_URL`, `SERVICE_ROLE_KEY` from `api/_auth.py` (already-existing module-level constants — see `api/_auth.py:10-11`).
- Produces: `SupabaseError(status: int, message: str)` (exception, `.status`/`.message`), `list_admin_profiles() -> list[dict]`, `list_recent_activity(limit: int = 10) -> list[dict]`, `insert_admin_profile(user_id: str, email: str, role: str) -> dict`, `update_admin_active(user_id: str, active: bool) -> dict`, `invite_user(email: str) -> str` (returns new user id), `create_user_with_password(email: str, password: str) -> str` (returns new user id).

- [ ] **Step 1: Append the network functions**

Add to the top of `api/admin_users.py` (after the existing `import re` line):

```python
import json
import urllib.error
import urllib.parse
import urllib.request

try:
    from ._auth import SUPABASE_URL, SERVICE_ROLE_KEY
except ImportError:
    from _auth import SUPABASE_URL, SERVICE_ROLE_KEY
```

Append at the end of `api/admin_users.py`:

```python
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
```

- [ ] **Step 2: Verify the module still imports cleanly**

Run: `python -c "import sys; sys.path.insert(0, 'api'); import admin_users; print('ok')"`
Expected: `ok` (no syntax or import errors — this catches typos since there's no live Supabase project to hit in this environment).

- [ ] **Step 3: Run the full test suite to confirm nothing broke**

Run: `python -m pytest api/tests/ -v`
Expected: all tests still pass (the Task 1 tests plus every pre-existing test in `api/tests/`).

- [ ] **Step 4: Commit**

```bash
git add api/admin_users.py
git commit -m "feat(admin): Supabase GoTrue/PostgREST calls for admin user management"
```

---

### Task 3: `api/admin_users.py` — HTTP handler

**Files:**
- Modify: `api/admin_users.py` (append the handler; import the `_auth` request helpers alongside the constants already imported in Task 2)

**Interfaces:**
- Consumes: everything produced in Task 1 and Task 2, plus `AuthError`, `add_cors_headers`, `audit`, `handle_options`, `require_admin`, `require_server_config`, `respond_auth_error` from `api/_auth.py` (same names `api/journal_publish.py` already imports — see `api/journal_publish.py:16-35` for the exact try/except import shape to copy).
- Produces: `handler` (a `BaseHTTPRequestHandler` subclass — this is what Vercel's Python runtime loads as the serverless function entrypoint, same convention as `api/journal_publish.py`'s `handler` class).

- [ ] **Step 1: Update the `_auth` import block**

Replace the import block added in Task 2:

```python
try:
    from ._auth import SUPABASE_URL, SERVICE_ROLE_KEY
except ImportError:
    from _auth import SUPABASE_URL, SERVICE_ROLE_KEY
```

with:

```python
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
```

- [ ] **Step 2: Append the handler**

Append to the end of `api/admin_users.py`:

```python
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
```

- [ ] **Step 3: Verify the module still imports cleanly**

Run: `python -c "import sys; sys.path.insert(0, 'api'); import admin_users; print('ok')"`
Expected: `ok`

- [ ] **Step 4: Run the full test suite**

Run: `python -m pytest api/tests/ -v`
Expected: all tests pass (this file has no handler-level tests of its own — same as `api/journal_publish.py`'s `handler` class, which is only covered by the pure-function tests plus manual/production verification, since there's no live Supabase project to integration-test against locally).

- [ ] **Step 5: Commit**

```bash
git add api/admin_users.py
git commit -m "feat(admin): HTTP handler for GET/POST/PATCH /api/admin_users, owner-gated"
```

---

### Task 4: `admin/index.html` — hub shell (login + tool cards)

**Files:**
- Create: `admin/index.html`

**Interfaces:**
- Consumes: `GET /api/auth_config` (existing endpoint, returns `{supabaseUrl, supabaseAnonKey}`), Supabase JS client `auth.signInWithPassword`/`auth.getSession`/`auth.onAuthStateChange` (same calls `admin/editor-articulo-cava.html` already makes).
- Produces: a working, loadable page with login gate and three tool links — independently testable before Task 5 adds admin management.

- [ ] **Step 1: Create the file**

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Admin — CAVA Vinoteca</title>
  <meta name="robots" content="noindex,nofollow" />
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.115.0/dist/umd/supabase.js" integrity="sha384-CLZeq1dk8+Uzrs7TVvBUdlFoV5F0DMqgRoeHa8g5wJcuPe5SkVfEvdxB0ZuzlnBQ" crossorigin="anonymous"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,300;6..96,400&family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --ivory:#f6efe3;--ivory-2:#eadcc3;--gold:#b8975a;--gold-soft:#d7b879;
      --navy:#162b43;--navy-deep:#091522;--charcoal:#12100d;--charcoal-2:#1b1813;
      --line:rgba(184,151,90,.2);
      --display:"Bodoni Moda",Georgia,serif;--serif:"Cormorant Garamond",Georgia,serif;
      --sans:"Jost",system-ui,sans-serif;--ease:cubic-bezier(.22,.61,.36,1);
    }
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    body{background:var(--charcoal);color:var(--ivory);font-family:var(--sans);font-weight:300;line-height:1.7;-webkit-font-smoothing:antialiased;min-height:100vh}

    .page-header{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem;background:rgba(9,21,34,.97);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
    .page-brand{display:flex;align-items:center;gap:.75rem;font-family:var(--display);font-size:.9rem;letter-spacing:.14em;font-weight:300;color:var(--gold-soft)}
    .page-badge{font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:rgba(246,239,227,.4);border:1px solid var(--line);padding:.25rem .75rem;border-radius:2px}

    main{max-width:960px;margin:0 auto;padding:2.5rem 2rem 4rem}
    .section-title{font-family:var(--display);font-size:1.1rem;font-weight:300;color:var(--ivory-2);letter-spacing:.02em;margin-bottom:1.25rem}

    .tool-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin-bottom:3rem}
    .tool-card{display:block;padding:1.5rem;background:var(--navy-deep);border:1px solid var(--line);border-radius:6px;text-decoration:none;color:inherit;transition:border-color .2s,transform .2s}
    .tool-card:hover{border-color:var(--gold);transform:translateY(-2px)}
    .tool-card-title{font-family:var(--display);font-size:1.05rem;color:var(--ivory-2);margin-bottom:.4rem}
    .tool-card-desc{font-size:.78rem;color:rgba(246,239,227,.5);line-height:1.5}

    .auth-overlay{position:fixed;inset:0;z-index:2000;background:radial-gradient(circle at 70% 20%,rgba(184,151,90,.12),transparent 32%),var(--navy-deep);display:grid;place-items:center;padding:1.5rem}
    .auth-overlay[hidden]{display:none}
    .auth-card{width:min(430px,100%);padding:2rem;border:1px solid var(--line);border-radius:8px;background:rgba(18,16,13,.92);box-shadow:0 24px 80px rgba(0,0,0,.42)}
    .auth-card h1{font-family:var(--display);font-weight:300;font-size:1.65rem;margin-bottom:.45rem}
    .auth-card p{font-size:.78rem;color:rgba(246,239,227,.55);margin-bottom:1.25rem}
    .auth-card input{width:100%;margin:.4rem 0;padding:.8rem;border:1px solid var(--line);border-radius:4px;background:rgba(255,255,255,.04);color:var(--ivory);font:inherit}
    .btn{display:inline-flex;align-items:center;gap:.5rem;padding:.65rem 1.25rem;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;font-weight:400;cursor:pointer;border-radius:3px;border:1px solid transparent;transition:all .25s var(--ease);font-family:var(--sans);white-space:nowrap}
    .btn:disabled{opacity:.4;cursor:not-allowed}
    .btn-gold{background:var(--gold);color:var(--navy-deep);border-color:var(--gold);width:100%;justify-content:center;margin-top:.75rem}
    .btn-gold:hover:not(:disabled){background:var(--gold-soft)}
    .auth-error{min-height:1.3rem;margin-top:.7rem;color:#e07070;font-size:.72rem}
  </style>
</head>
<body>

<div class="auth-overlay" id="authOverlay">
  <form class="auth-card" id="loginForm">
    <div class="page-brand" style="margin-bottom:1.2rem">CAVA Vinoteca · Admin</div>
    <h1>Acceso administrativo</h1>
    <p>Inicia sesión con tu cuenta administrativa para continuar.</p>
    <input type="email" id="loginEmail" autocomplete="username" placeholder="Correo electrónico" required>
    <input type="password" id="loginPassword" autocomplete="current-password" placeholder="Contraseña" required>
    <button class="btn btn-gold" id="loginBtn" type="submit">Entrar al Admin</button>
    <div class="auth-error" id="loginError" role="alert"></div>
  </form>
</div>

<header class="page-header">
  <div class="page-brand">
    <svg width="24" height="24" viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="8" stroke="#b8975a" stroke-width="1.2"/>
      <circle cx="20" cy="20" r="16" stroke="#b8975a" stroke-width=".6" stroke-dasharray="3 3"/>
    </svg>
    CAVA Vinoteca
  </div>
  <span class="page-badge">Admin — Uso interno</span>
</header>

<main>
  <div class="section-title">Herramientas</div>
  <div class="tool-grid">
    <a class="tool-card" href="/admin/editor-articulo-cava">
      <div class="tool-card-title">Journal</div>
      <div class="tool-card-desc">Escribir, revisar y publicar artículos del Journal.</div>
    </a>
    <a class="tool-card" href="/admin/cava_control_v3">
      <div class="tool-card-title">Control de Consignación</div>
      <div class="tool-card-desc">Inventario, ventas y pagos por proveedor.</div>
    </a>
    <a class="tool-card" href="/admin/enofilios-panel">
      <div class="tool-card-title">Enofilios</div>
      <div class="tool-card-desc">Membresías, tarjetas y experiencias registradas.</div>
    </a>
  </div>

  <div id="adminUsersSection" hidden></div>
</main>

<script>
  let supabaseAdmin = null;
  let adminSession = null;

  document.addEventListener('DOMContentLoaded', async () => {
    document.getElementById('loginForm').addEventListener('submit', loginAdmin);
    try {
      const cfgRes = await fetch('/api/auth_config');
      const cfg = await cfgRes.json();
      if (!cfgRes.ok || !cfg.supabaseUrl || !cfg.supabaseAnonKey) throw new Error('Configuración de acceso incompleta');
      supabaseAdmin = window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseAnonKey);
      const { data } = await supabaseAdmin.auth.getSession();
      setAdminSession(data.session || null);
      supabaseAdmin.auth.onAuthStateChange((_event, session) => setAdminSession(session));
    } catch (error) {
      document.getElementById('loginError').textContent = error.message || 'No se pudo iniciar el acceso administrativo.';
    }
  });

  function setAdminSession(session) {
    adminSession = session;
    document.getElementById('authOverlay').hidden = !!session;
  }

  async function loginAdmin(event) {
    event.preventDefault();
    const button = document.getElementById('loginBtn');
    const errorBox = document.getElementById('loginError');
    button.disabled = true;
    button.textContent = 'Ingresando…';
    errorBox.textContent = '';
    try {
      if (!supabaseAdmin) throw new Error('El servicio de acceso todavía no está listo.');
      const { data, error } = await supabaseAdmin.auth.signInWithPassword({
        email: document.getElementById('loginEmail').value.trim(),
        password: document.getElementById('loginPassword').value,
      });
      if (error) throw error;
      setAdminSession(data.session);
    } catch (error) {
      errorBox.textContent = 'No pudimos iniciar sesión. Revisa el correo y la contraseña.';
    } finally {
      button.disabled = false;
      button.textContent = 'Entrar al Admin';
    }
  }

  async function adminFetch(url, options = {}) {
    if (!adminSession?.access_token) throw new Error('La sesión administrativa venció. Vuelve a iniciar sesión.');
    const headers = new Headers(options.headers || {});
    headers.set('Authorization', 'Bearer ' + adminSession.access_token);
    if (options.body) headers.set('Content-Type', 'application/json');
    return fetch(url, { ...options, headers });
  }
</script>
</body>
</html>
```

- [ ] **Step 2: Serve the file locally and verify it loads clean**

```bash
node -e "
const http = require('http');
const fs = require('fs');
const path = require('path');
const mime = {'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json'};
http.createServer((req,res)=>{
  const fp = path.join(process.cwd(), decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(fp, (err,data)=>{
    if (err) { res.writeHead(404); res.end('not found'); return; }
    res.writeHead(200, {'Content-Type': mime[path.extname(fp)] || 'application/octet-stream'});
    res.end(data);
  });
}).listen(8940, ()=>console.log('listening'));
" &
sleep 1
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8940/admin/index.html
```

Expected: `200`. Then open `http://localhost:8940/admin/index.html` in a real browser (e.g. via the Playwright MCP tools if available) and confirm: the login card renders, no console errors other than the expected `404` on `/api/auth_config` (no local backend), and the three tool cards are visible with correct hrefs. Stop the node process afterward.

- [ ] **Step 3: Commit**

```bash
git add admin/index.html
git commit -m "feat(admin): admin hub shell with login gate and tool links"
```

---

### Task 5: `admin/index.html` — admin user management UI

**Files:**
- Modify: `admin/index.html`

**Interfaces:**
- Consumes: `GET /api/admin_users`, `POST /api/admin_users`, `PATCH /api/admin_users` (built in Task 3), `adminFetch()` (built in Task 4).

- [ ] **Step 1: Add the CSS for the admin-users section**

In `admin/index.html`, insert before the closing `</style>` tag (after the `.auth-error` rule):

```css
    .admin-users{background:var(--navy-deep);border:1px solid var(--line);border-radius:6px;padding:1.5rem}
    .admin-table{width:100%;border-collapse:collapse;margin-bottom:1.5rem}
    .admin-table th{text-align:left;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);padding-bottom:.6rem;border-bottom:1px solid var(--line)}
    .admin-table td{padding:.6rem 0;border-bottom:1px solid rgba(184,151,90,.08);font-size:.8rem}
    .pill{display:inline-block;padding:.15rem .55rem;border-radius:3px;font-size:.62rem;letter-spacing:.08em;text-transform:uppercase}
    .pill-active{background:rgba(74,156,111,.15);color:#7ed4a7}
    .pill-inactive{background:rgba(192,57,43,.15);color:#e07070}
    .btn-outline{background:transparent;color:var(--gold-soft);border-color:var(--gold);padding:.4rem .85rem;font-size:.6rem}
    .btn-outline:hover{background:rgba(184,151,90,.1)}
    .invite-form{display:grid;grid-template-columns:1fr 1fr auto auto;gap:.6rem;align-items:end;margin-top:1.25rem;padding-top:1.25rem;border-top:1px solid var(--line)}
    .invite-form label{display:block;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:rgba(246,239,227,.5);margin-bottom:.35rem}
    .invite-form input,.invite-form select{width:100%;padding:.6rem;border:1px solid var(--line);border-radius:3px;background:rgba(255,255,255,.04);color:var(--ivory);font:inherit;font-size:.8rem}
    .invite-form input[type="password"]{display:none}
    .invite-form.mode-create input[type="password"]{display:block}
    .activity-list{list-style:none;margin-top:2rem;font-size:.75rem;color:rgba(246,239,227,.55)}
    .activity-list li{padding:.5rem 0;border-bottom:1px solid rgba(184,151,90,.08)}
    .form-msg{grid-column:1/-1;font-size:.72rem;min-height:1.2rem}
    .form-msg.error{color:#e07070}
    .form-msg.success{color:#7ed4a7}
    @media(max-width:700px){.invite-form{grid-template-columns:1fr}}
```

- [ ] **Step 2: Add the HTML skeleton**

Replace:

```html
  <div id="adminUsersSection" hidden></div>
```

with:

```html
  <div id="adminUsersSection" hidden>
    <div class="section-title">Usuarios admin</div>
    <div class="admin-users">
      <table class="admin-table">
        <thead>
          <tr><th>Correo</th><th>Rol</th><th>Estado</th><th></th></tr>
        </thead>
        <tbody id="adminUsersBody"></tbody>
      </table>

      <form class="invite-form" id="inviteForm">
        <div>
          <label>Correo</label>
          <input type="email" id="inviteEmail" required>
        </div>
        <div>
          <label>Rol</label>
          <select id="inviteRole">
            <option value="admin">admin</option>
            <option value="owner">owner</option>
          </select>
        </div>
        <div>
          <label><input type="checkbox" id="inviteModeCreate" onchange="toggleInviteMode()"> Contraseña directa</label>
          <input type="password" id="invitePassword" placeholder="Contraseña (mín. 8 caracteres)">
        </div>
        <button class="btn btn-gold" type="submit" style="margin-top:0">Invitar</button>
        <div class="form-msg" id="inviteMsg"></div>
      </form>
    </div>

    <div class="section-title" style="margin-top:2rem">Actividad reciente</div>
    <ul class="activity-list" id="activityList"></ul>
  </div>
```

- [ ] **Step 3: Add the JS**

Replace:

```js
  function setAdminSession(session) {
    adminSession = session;
    document.getElementById('authOverlay').hidden = !!session;
  }
```

with:

```js
  function setAdminSession(session) {
    adminSession = session;
    document.getElementById('authOverlay').hidden = !!session;
    if (session) loadAdminUsers();
  }

  function escapeHTML(str) {
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function toggleInviteMode() {
    document.getElementById('inviteForm').classList.toggle('mode-create', document.getElementById('inviteModeCreate').checked);
  }

  async function loadAdminUsers() {
    try {
      const response = await adminFetch('/api/admin_users');
      if (response.status === 403) {
        document.getElementById('adminUsersSection').hidden = true;
        return;
      }
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'No se pudo cargar la lista de administradores');
      document.getElementById('adminUsersSection').hidden = false;
      renderAdmins(data.admins);
      renderActivity(data.recent_activity);
    } catch (error) {
      document.getElementById('adminUsersSection').hidden = true;
    }
  }

  function renderAdmins(admins) {
    const body = document.getElementById('adminUsersBody');
    body.innerHTML = admins.map(a => `
      <tr>
        <td>${escapeHTML(a.email)}</td>
        <td>${escapeHTML(a.role)}</td>
        <td><span class="pill ${a.active ? 'pill-active' : 'pill-inactive'}">${a.active ? 'Activo' : 'Inactivo'}</span></td>
        <td><button class="btn btn-outline" onclick="toggleActive('${a.user_id}', ${!a.active})">${a.active ? 'Desactivar' : 'Reactivar'}</button></td>
      </tr>
    `).join('');
  }

  function renderActivity(items) {
    const list = document.getElementById('activityList');
    if (!items.length) {
      list.innerHTML = '<li>Sin actividad registrada todavía.</li>';
      return;
    }
    list.innerHTML = items.map(item => `
      <li>${escapeHTML(item.action)} — ${escapeHTML(item.actor_email || 'desconocido')} — ${escapeHTML(item.result)} — ${new Date(item.created_at).toLocaleString('es-CR')}</li>
    `).join('');
  }

  async function toggleActive(userId, nextActive) {
    try {
      const response = await adminFetch('/api/admin_users', {
        method: 'PATCH',
        body: JSON.stringify({ user_id: userId, active: nextActive }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'No se pudo actualizar');
      loadAdminUsers();
    } catch (error) {
      alert(error.message);
    }
  }

  document.getElementById('inviteForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const msg = document.getElementById('inviteMsg');
    msg.textContent = '';
    msg.className = 'form-msg';
    const mode = document.getElementById('inviteModeCreate').checked ? 'create' : 'invite';
    const payload = {
      email: document.getElementById('inviteEmail').value.trim(),
      role: document.getElementById('inviteRole').value,
      mode,
      password: mode === 'create' ? document.getElementById('invitePassword').value : undefined,
    };
    try {
      const response = await adminFetch('/api/admin_users', { method: 'POST', body: JSON.stringify(payload) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'No se pudo crear la cuenta');
      msg.textContent = mode === 'invite' ? 'Invitación enviada.' : 'Cuenta creada.';
      msg.className = 'form-msg success';
      document.getElementById('inviteForm').reset();
      loadAdminUsers();
    } catch (error) {
      msg.textContent = error.message;
      msg.className = 'form-msg error';
    }
  });
```

- [ ] **Step 4: Verify it still loads clean**

Repeat the local-server + browser check from Task 4 Step 2. This time also confirm: with no backend running, `loadAdminUsers()` fails gracefully (the `catch` hides the section) rather than throwing an uncaught error — check the browser console shows no new uncaught exceptions beyond the expected `404` network errors.

- [ ] **Step 5: Commit**

```bash
git add admin/index.html
git commit -m "feat(admin): admin user management UI (invite, deactivate, activity feed)"
```

---

### Task 6: Back-link from the three existing tools to the hub

**Files:**
- Modify: `admin/editor-articulo-cava.html:221-227`
- Modify: `admin/cava_control_v3.html:226-229`
- Modify: `admin/enofilios-panel.html:150-156`

**Interfaces:**
- None — purely additive navigation, no new functions or endpoints.

- [ ] **Step 1: `admin/editor-articulo-cava.html`**

Replace:

```html
  <div class="editor-brand">
    <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="8" stroke="#b8975a" stroke-width="1.2"/>
      <circle cx="20" cy="20" r="16" stroke="#b8975a" stroke-width=".6" stroke-dasharray="3 3"/>
    </svg>
    CAVA Vinoteca
  </div>
```

with:

```html
  <a class="editor-brand" href="/admin" style="text-decoration:none">
    <svg width="28" height="28" viewBox="0 0 40 40" fill="none">
      <circle cx="20" cy="20" r="8" stroke="#b8975a" stroke-width="1.2"/>
      <circle cx="20" cy="20" r="16" stroke="#b8975a" stroke-width=".6" stroke-dasharray="3 3"/>
    </svg>
    CAVA Vinoteca
  </a>
```

- [ ] **Step 2: `admin/cava_control_v3.html`**

Replace:

```html
    <div class="logo-area">
      <span class="logo-icon">🍷</span>
      <div><div class="logo-text">CAVA</div><div class="logo-sub">CONTROL DE CONSIGNACIÓN</div></div>
    </div>
```

with:

```html
    <a class="logo-area" href="/admin" style="text-decoration:none;color:inherit">
      <span class="logo-icon">🍷</span>
      <div><div class="logo-text">CAVA</div><div class="logo-sub">CONTROL DE CONSIGNACIÓN</div></div>
    </a>
```

- [ ] **Step 3: `admin/enofilios-panel.html`**

Replace:

```html
  <div class="header-brand">
    <img src="/Assets/Logo-Cava.png" alt="CAVA Vinoteca" class="header-logo">
    <div class="header-titles">
      <span class="header-name">Enofilios Cava</span>
      <span class="header-sub">Programa de membresías</span>
    </div>
  </div>
```

with:

```html
  <a class="header-brand" href="/admin" style="text-decoration:none;color:inherit">
    <img src="/Assets/Logo-Cava.png" alt="CAVA Vinoteca" class="header-logo">
    <div class="header-titles">
      <span class="header-name">Enofilios Cava</span>
      <span class="header-sub">Programa de membresías</span>
    </div>
  </a>
```

- [ ] **Step 4: Verify each page still loads without console errors**

For each of the three files, serve locally (same node one-liner as Task 4 Step 2, different port if the old one is still bound) and confirm in a browser: the page loads, no new console errors, and the brand/logo area is now a clickable link to `/admin` (hovering shows the link in the status bar / `href` in a DOM snapshot).

- [ ] **Step 5: Commit**

```bash
git add admin/editor-articulo-cava.html admin/cava_control_v3.html admin/enofilios-panel.html
git commit -m "feat(admin): link back to the admin hub from each existing tool"
```

---

### Task 7: Final review and handoff

**Files:** none (verification only)

- [ ] **Step 1: Run the full backend test suite one more time**

Run: `python -m pytest api/tests/ -v`
Expected: all tests pass, including every test added in Task 1.

- [ ] **Step 2: Cross-check every `getElementById`/`adminFetch` call in `admin/index.html` against the ids actually defined in that file**

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('admin/index.html', 'utf8');
const refIds = new Set([...html.matchAll(/getElementById\(['\"]([\w-]+)['\"]\)/g)].map(m => m[1]));
const defIds = new Set([...html.matchAll(/\sid=[\"']([\w-]+)[\"']/g)].map(m => m[1]));
const missing = [...refIds].filter(id => !defIds.has(id)).sort();
console.log('Referenced but NOT defined:', JSON.stringify(missing));
"
```

Expected: `Referenced but NOT defined: []` — this is exactly the check that caught the `#guideFilename` production bug earlier this session; run it here before shipping a new page with the same risk.

- [ ] **Step 3: Stop and ask the user**

Do not push the branch or open a PR. Report back: what was built, the two verification results from Steps 1-2, and ask the user whether to push `feature/admin-hub-and-user-management` and open a PR — same pattern as PR #13 and #14 earlier this session.
