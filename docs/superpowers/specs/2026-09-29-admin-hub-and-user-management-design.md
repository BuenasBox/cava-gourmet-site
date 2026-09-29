# Admin hub + admin user management — design

**Date:** 2026-09-29
**Status:** Approved by owner, ready for implementation plan

## Problem

CAVA's admin tools (`admin/editor-articulo-cava.html`, `admin/cava_control_v3.html`,
`admin/enofilios-panel.html`) are three disconnected pages — no shared entry point, no
link between them. There's also no way to add or remove admin accounts except by the
owner running raw SQL by hand in the Supabase SQL Editor (done twice this session, for
Nazareth's and the owner's own account) — a single point of failure if the current owner
is unavailable.

## Goals

1. One protected entry point (`/admin`) linking to the three existing tools.
2. A lightweight way back to that entry point from inside each tool.
3. Self-service admin account management: invite a new admin by email (they set their own
   password) or, as a fallback, create one with an owner-chosen password directly —
   without touching SQL. Restricted to the `owner` role only.
4. A short recent-activity view on the hub, reusing the audit log that already exists.

## Non-goals

- No redesign of the three existing tools themselves.
- No new analytics/tracking beyond what `admin_audit_log` already records.
- No self-service password reset flow for existing admins (out of scope; the invite flow
  covers new admins, and an existing admin who forgets their password is a rare enough
  event to stay a manual SQL/dashboard action for now).

## Architecture

### New: `admin/index.html`

Static page, same Supabase-auth pattern as `editor-articulo-cava.html` (bootstrap via
`/api/auth_config`, `supabase.auth.signInWithPassword`, session gates the content behind
an `auth-overlay`). On load, calls `GET /api/admin_users`:

- **200** → caller is `owner`. Render the "Usuarios admin" section with the returned
  `admins` list and `recent_activity` list.
- **403** → caller is `admin` (not `owner`). Hide the "Usuarios admin" section entirely —
  this is an expected, silent state, not an error toast.

Always renders the three tool cards regardless of role — every active admin can reach
every tool; only account management is owner-gated.

Card links (Vercel `cleanUrls: true` strips `.html`):
`/admin/editor-articulo-cava`, `/admin/cava_control_v3`, `/admin/enofilios-panel`.

`<meta name="robots" content="noindex,nofollow">`, same as the other three admin pages —
`/admin/` is already `Disallow`'d in `robots.txt`, this keeps the per-page signal
consistent.

### Edited: the three existing tool pages

Add one small "← Admin" link in each header, pointing to `/admin`. No other changes to
these files.

### New: `api/admin_users.py`

Same `BaseHTTPRequestHandler` shape as `api/journal_publish.py`, reusing
`api/_auth.py`'s `require_admin`, `AuthError`, `add_cors_headers`, `handle_options`,
`audit`, `require_server_config` unchanged. Every handler additionally enforces:

```python
if ctx["profile"].get("role") != "owner":
    raise AuthError(403, "Solo el rol owner puede gestionar administradores")
```

**`GET`** → `{ admins: [{user_id, email, role, active, created_at}], recent_activity: [{action, actor_email, object_type, object_id, result, created_at}] }`
(admins from `admin_profiles`, recent_activity = last 10 rows of `admin_audit_log`, both
via a service-role PostgREST call — same pattern `api/miembros.py` already uses to query
`public` tables server-side.)

**`POST`** → body `{ mode: "invite" | "create", email, role, password? }`

- Validate `email` (basic regex), `role` in `("owner", "admin")`, and for `mode=="create"`,
  `password` at least 8 characters.
- `mode == "invite"`: `POST {SUPABASE_URL}/auth/v1/invite` with the service-role key —
  GoTrue creates the unconfirmed user and emails them an invite link to set their own
  password. Response gives the new user's `id`.
- `mode == "create"`: `POST {SUPABASE_URL}/auth/v1/admin/users` with
  `{email, password, email_confirm: true}` — creates the user immediately, already
  confirmed, with the password the owner chose in the form.
- Either way, insert one row into `admin_profiles` (`user_id`, `email`, `role`,
  `active: true`). If that insert fails after the auth user was created, surface a clear
  error telling the owner the login exists but has no admin role yet — this is a rare
  partial-failure edge case, not silently swallowed.
- `audit()` with `action="admin_users.invite"` or `"admin_users.create"`.
- Errors: GoTrue 422 (email already registered) → 409 "Ya existe una cuenta con ese
  correo"; GoTrue 5xx / network failure on the invite call → 502 "No se pudo enviar la
  invitación — intenta crear la cuenta con contraseña directa" (this is the SMTP-risk
  fallback surfaced as an actionable message, not a dead end).

**`PATCH`** → body `{ user_id, active }`

- Reject if `user_id == ctx["user"]["id"]` → 400 "No puedes desactivar tu propia cuenta".
- If `active == false`: count currently-active `owner` rows excluding this one; if zero
  would remain → 400 "Debe quedar al menos un owner activo".
- Update `admin_profiles.active`. No GoTrue call needed — `require_admin()` re-reads
  `admin_profiles` on every request, so a deactivated admin loses access on their very
  next call even with a still-valid Supabase session (verified: this is exactly how the
  existing `require_admin()` already behaves, nothing new to build here).
- `audit()` with `action="admin_users.deactivate"` or `"admin_users.reactivate"`.

### `vercel.json`

No change needed — `functions["api/**/*.py"].excludeFiles` (shipped in PR #13) already
covers any new file under `api/`.

## Data flow

```
Owner opens /admin → login → GET /api/admin_users
  → 200: render tool cards + admin table + activity feed
  → 403: render tool cards only

Owner clicks "Invitar admin" → fills email + role → POST /api/admin_users {mode:"invite"}
  → success: toast "Invitación enviada", refresh admin table
  → 502 (email failed): toast suggests the "crear con contraseña" fallback, form stays filled

Owner clicks "Desactivar" on a row → PATCH /api/admin_users {user_id, active:false}
  → success: row updates to inactive in place
  → 400 (last owner / self): toast explains why, no change made
```

## Testing

`api/tests/test_admin_users_helpers.py`, same style as
`test_journal_publish_helpers.py` — pure-function unit tests, no network:

- payload validation (email format, role enum, password length)
- the "can't deactivate self" guard
- the "can't drop to zero active owners" guard (given a fake roster list)

## Security notes

- Mutating this endpoint is `owner`-only by role check, independent of and in addition to
  the existing `require_admin()` gate — an `admin` account (e.g. Nazareth's) gets a clean
  403 on every method except the already-covered read of the tool-card page itself.
- Service-role key usage here matches the existing pattern in `api/_auth.py` /
  `api/miembros.py` — never sent to the browser, only used server-side for the GoTrue
  admin calls and the `admin_profiles` write.
- No new secrets — reuses `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` (or its
  `SUPABASE_KEY` fallback) that's already configured in Vercel.
