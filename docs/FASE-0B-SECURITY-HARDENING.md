# Fase 0B — Security Hardening: status & activation

**ACTIVATED 2026-09-08.** All three migrations are applied to the CAVA Supabase
project (`rbfctmcfweckbpgxlkqf`) and the gated code paths are switched on in
Vercel (Preview + Production). This file is the record of the final state.

| Item | State | Switch | Notes |
|---|---|---|---|
| 0B.1 `rls_auto_enable` REVOKE | **ACTIVE** | migration `…_0001` | anon/authenticated cannot `EXECUTE` it; `ensure_rls` event trigger intact |
| 0B.2 Leaked Password Protection | **DEFERRED — PLAN LIMITATION** | — | HaveIBeenPwned check is a Supabase **Pro** feature; project is on Free. Not a roadmap blocker. |
| 0B.3 scan rate-limit / lockout / dedupe | **ACTIVE** | migration `…_0002` + `SCAN_HARDENING=1` | token + IP scoped; fail-open **only** on infra failure |
| 0B.4 member token V2 | **ACTIVE (issuance on, V1 grace)** | `MEMBER_TOKEN_V2=1` + `MEMBER_TOKEN_SALT` + `MEMBER_TOKEN_V2_TTL_DAYS=120` | new links are V2; existing V1 QRs still validate; **no** `MEMBER_TOKEN_V1_SUNSET` |
| 0B.5 supabase-js pin + SRI | **DONE** | — | `admin/*.html` pinned to `2.115.0` + SRI |
| 0B.6 orphan env vars | **DONE** | — | `NEXT_PUBLIC_SUPABASE_*` + `SCAN_KEY` removed (0 code consumers) |
| 0B.7 service-role key naming | **OPTIONAL — not a blocker** | — | every `api/*.py` resolves `SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY`; renaming the Vercel var is cosmetic |
| 0B.8 admin audit log | **ACTIVE** | migration `…_0003` + `ADMIN_AUDIT=1` | `admin_audit_log` = RLS ON, **no client policies**; best-effort, never blocks a request |

## 0B.1 — `public.rls_auto_enable()`

`supabase/migrations/20260906_0001_revoke_rls_auto_enable_execute.sql`, applied.
`EXECUTE` revoked from `PUBLIC`/`anon`/`authenticated`; `postgres` keeps it. The
`ensure_rls` event trigger keeps firing (event triggers don't consult the
function `EXECUTE` ACL; `SECURITY DEFINER` runs as owner regardless).
Verified live: `has_function_privilege('anon'|'authenticated', 'public.rls_auto_enable()', 'execute')` = `false`; `ensure_rls` present and enabled.

## 0B.2 — Leaked Password Protection

**DEFERRED — PLAN LIMITATION.** Supabase Auth's HaveIBeenPwned check requires a
**Pro** plan; CAVA is on Free. Compensating controls in place: public signup
disabled, anonymous sign-ins disabled, existing admin accounts only, RLS on
every table, server-side `require_admin` on every admin API. Revisit if the
project moves to Pro. **ROADMAP BLOCKER: NO.**

## 0B.3 — `/api/scan`

`api/scan.py`: a pure `evaluate_scan_guard(now, token_rows, ip_rows, cfg)`
(unit-tested in `api/tests/test_scan_guard.py`) behind an I/O wrapper
`scan_guard_check(token_hash, ip)`.

- **token-scoped:** success cooldown (dedupe double-registration), request
  rate, PIN-lockout.
- **IP-scoped** (stops one host cycling many tokens): request rate + PIN-lockout
  across all tokens.
- **Fail-open only on an infrastructure failure** (the `scan_attempts` fetch
  raised → reason `infra`). A ledger that answers and yields a block decision
  blocks — reason `cooldown | rate_token | locked_token | rate_ip | locked_ip`
  (client sees HTTP 429, no detail).

Tunables (env, defaults): `SCAN_COOLDOWN_MIN=30`, `SCAN_RATE_MAX=30` +
`SCAN_RATE_WINDOW_MIN=10`, `SCAN_MAX_FAILS=5` + `SCAN_LOCKOUT_MIN=15`,
`SCAN_RATE_MAX_IP=60`, `SCAN_MAX_FAILS_IP=15`. `SCAN_HARDENING=1` is set in
Preview + Production. Ledger table `public.scan_attempts` (migration `…_0002`):
RLS ON, 0 client policies, service-role only; `token_hash = sha256(member token)`
— the raw token/email is never stored. Retention ~30 days (run from pg_cron or
the app).

## 0B.4 — member token V2

`api/_member_token.py`. `MEMBER_TOKEN_V2=1` → `generar_token()` now issues
`v2.<exp>.<sig>` where `sig = HMAC-SHA256(HMAC_SECRET, "v2:<SALT>:<email>:<exp>")`.
`MEMBER_TOKEN_SALT` (Secret, ≥48 bytes, identical in Preview + Production) is the
global rotation lever — bump it to invalidate every outstanding V2 link at once.
`MEMBER_TOKEN_V2_TTL_DAYS=120`.

`validar_token()` accepts **both** formats. Existing V1 QRs / Wallet links keep
working — **`MEMBER_TOKEN_V1_SUNSET` is deliberately not set.** When (if) V1 is
retired: reissue member links from the panel, let the grace window pass, then set
`MEMBER_TOKEN_V1_SUNSET=YYYY-MM-DD`. Full matrix in `docs/MEMBER-TOKEN-V2.md`;
tests in `api/tests/test_member_token.py`.

## 0B.6 — Orphan Vercel env vars (done)

`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`,
`NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `SCAN_KEY` — removed from all
environments after re-verifying 0 code consumers. Untouched: `SUPABASE_URL`,
`SUPABASE_KEY`, `SUPABASE_ANON_KEY`, `HMAC_SECRET`, `SCAN_PIN`,
`GOOGLE_WALLET_KEY`.

## 0B.7 — Service-role key naming (optional)

Every `api/*.py` resolves `SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY`, so the
Vercel var can be renamed with no code change: (1) add
`SUPABASE_SERVICE_ROLE_KEY` = same value, all scopes; (2) redeploy, confirm
admin + scan + wallet; (3) remove `SUPABASE_KEY`. Cosmetic — **not a blocker**,
not done.

## 0B.8 — Admin audit log

`api/_auth.py` `audit()`, `ADMIN_AUDIT=1` in Preview + Production. Two call
sites:
- `require_admin()` → one row, `result="authorized"` — this request passed the
  admin gate. It does **not** assert the downstream action succeeded.
- a mutating endpoint calls `audit()` again after its write with
  `result="ok"/"error"` + a specific `action`/`object_type`/`object_id`. Wired
  into `config.py` PATCH (which also now returns **502** instead of a false 200
  on a failed write).

Row content: `actor_user_id`, `actor_email`, `action`, `object_type`,
`object_id` (never a raw email), `result`, `origin`, `created_at`. **No** token,
password, service-role key, HMAC secret, or `SCAN_PIN`.

`public.admin_audit_log` (migration `…_0003`): **RLS ON, no client policies.**
anon/authenticated get nothing on the Data API; the service-role backend writes
by RLS bypass. An earlier draft's near-circular admin SELECT policy (it
re-derived admin status from `admin_profiles`, itself RLS-on / 0-policy) was
dropped. If the panel ever needs to display the trail, expose it through an
`/api` route guarded by `require_admin()`.

## Migration ledger

| Version / name | State |
|---|---|
| `20260906_0001_revoke_rls_auto_enable_execute` | **ACTIVE** |
| `0002_scan_attempts` | **ACTIVE** (RLS ON, 0 client policies, 3 indexes) |
| `0003_admin_audit_log` | **ACTIVE** (RLS ON, 0 client policies, 3 indexes) |
