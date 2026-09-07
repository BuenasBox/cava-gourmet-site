-- Fase 0B.8 — admin action audit trail
--
-- Written by api/_auth.py -> audit(), gated by ADMIN_AUDIT=1:
--   * require_admin()     -> one row per authenticated admin request (result='authorized')
--   * mutating endpoints  -> one row after the write               (result='ok' | 'error')
-- Stores only the actor's own id/email + the request line + Origin. Never a
-- token, password, service-role key, HMAC secret, SCAN_PIN, or unnecessary PII.
--
-- Apply:  apply_migration / supabase migration up
-- Then:   set ADMIN_AUDIT=1 in Vercel (Production + Preview) to activate.

create table if not exists public.admin_audit_log (
  id             bigint generated always as identity primary key,
  actor_user_id  uuid,
  actor_email    text,
  action         text        not null,          -- e.g. 'authorized GET /api/miembros', 'config.update'
  object_type    text,                           -- optional: 'configuracion' | 'miembro' | ...
  object_id      text,                           -- optional: affected key / row id (never a raw email)
  result         text        not null default 'ok',   -- 'authorized' | 'ok' | 'error' | 'denied'
  origin         text,                           -- request Origin header, if present
  created_at     timestamptz not null default now()
);

create index if not exists admin_audit_log_time  on public.admin_audit_log (created_at desc);
create index if not exists admin_audit_log_actor on public.admin_audit_log (actor_user_id, created_at desc);

-- RLS on, NO client policies. anon/authenticated get nothing on the Data API.
-- The backend writes with the service-role key (bypasses RLS). If the panel
-- ever needs to show the trail, expose it through an /api route guarded by
-- require_admin() -- not a Data API policy that would re-derive admin status
-- from admin_profiles (itself RLS-on / 0-policy): brittle and near-circular.
alter table public.admin_audit_log enable row level security;

-- (superseded) an earlier draft added a SELECT policy for authenticated admins;
-- dropped here so re-running the file is idempotent against that version.
drop policy if exists admin_audit_log_select_admins on public.admin_audit_log;

comment on table public.admin_audit_log is
  'Fase 0B.8 admin action trail. Service-role only (RLS on, no policies). No secrets/PII.';
