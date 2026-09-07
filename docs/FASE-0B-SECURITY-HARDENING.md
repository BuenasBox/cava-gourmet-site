# Fase 0B — Security Hardening: status & activation

Closure of the security backlog from the 360° audit. Code and migrations are
**in the repo and deployed**, but every item that needs a Supabase DDL or an
Auth-dashboard toggle ships **inert** (env-flag off) because the audit
environment has no `psql` / Supabase dashboard / MCP access and no way to run
the Python happy-path tests. Each is a one-step activation for a human with
Supabase + Vercel access.

| Item | Code shipped | Needs to activate | Risk |
|---|---|---|---|
| 0B.1 rls_auto_enable REVOKE | migration `…_0001` | `supabase db push` | none — event trigger unaffected |
| 0B.2 Leaked Password Protection | — | Supabase Dashboard toggle | none |
| 0B.3 scan rate-limit/lockout/dedupe | `api/scan.py` guard (gated) + migration `…_0002` | `db push` + `SCAN_HARDENING=1` | fail-open; can't lock out staff |
| 0B.4 member token V2 | `api/_member_token.py` (V2 dormant) | `MEMBER_TOKEN_V2=1` after smoke test | see MEMBER-TOKEN-V2.md |
| 0B.5 supabase-js pin + SRI | **DONE** — `admin/*.html` pinned to 2.115.0 | — | verified on Preview |
| 0B.6 orphan env vars | — | `vercel env rm` (see below) | none — 0 code consumers |
| 0B.7 service-role key naming | all `api/*.py` read `SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY` | add new-named var, later remove `SUPABASE_KEY` | none — identical while both resolve |
| 0B.8 admin audit log | `api/_auth.py` `audit()` (gated) + migration `…_0003` | `db push` + `ADMIN_AUDIT=1` | best-effort; never blocks a request |

## 0B.1 — `public.rls_auto_enable()`

`supabase/migrations/20260906_0001_revoke_rls_auto_enable_execute.sql`.
Revokes `EXECUTE` from `PUBLIC`/`anon`/`authenticated`; keeps `postgres`. The
`ensure_rls` event trigger keeps firing (event triggers don't consult the
function EXECUTE ACL; SECURITY DEFINER runs as owner regardless).
Verify after apply: create a throwaway `public` table → RLS still auto-enabled.

## 0B.2 — Leaked Password Protection

Supabase Dashboard → Authentication → Policies / Password security →
enable "Check against HaveIBeenPwned". No code. Only affects **new/changed**
passwords, so existing admin logins keep working. Flip it, then confirm one
existing admin can still log in and one password reset with a known-breached
password is rejected.

## 0B.3 — `/api/scan`

Guard in `api/scan.py` (`scan_guard_check` / `scan_record`), table in
migration `…_0002`. Tunables (all env, sane defaults): `SCAN_COOLDOWN_MIN=30`
(no re-registration), `SCAN_MAX_FAILS=5` + `SCAN_LOCKOUT_MIN=15` (PIN
brute-force), `SCAN_RATE_MAX=30` + `SCAN_RATE_WINDOW_MIN=10`. Activate:
`db push`, then `SCAN_HARDENING=1` in Preview → run the QR flow a few times →
Production. Fail-open by design: a missing table or a query error logs a
warning and lets the attempt through.

## 0B.6 — Orphan Vercel env vars (revalidated 0 consumers)

`git grep` across `api/`, `*.html`, `*.js`, `*.json` → no references:

```
vercel env rm NEXT_PUBLIC_SUPABASE_URL            development preview production
vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY       development preview production
vercel env rm NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY development preview production
vercel env rm SCAN_KEY                            development preview production
```

Do **not** touch `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_ANON_KEY`,
`HMAC_SECRET`, `SCAN_PIN`, `GOOGLE_WALLET_KEY`.

## 0B.7 — Service-role key naming

Every `api/*.py` now resolves `SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY`.
Transition: (1) add `SUPABASE_SERVICE_ROLE_KEY` in Vercel = same value as
`SUPABASE_KEY`, all scopes; (2) redeploy, confirm admin + scan + wallet work;
(3) remove `SUPABASE_KEY`. Never expose either to the browser.

## 0B.8 — Admin audit log

`api/_auth.py` `audit()` writes one row per successful `require_admin()` —
actor id/email + `"<METHOD> <path>"` + Origin. No tokens/PII. Table +
admin-only SELECT policy in migration `…_0003`. Activate: `db push` +
`ADMIN_AUDIT=1`. Adds one ~5 s-timeout POST per admin request when on;
fully skipped when off.
