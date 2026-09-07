-- Fase 0B.8 — admin action audit trail
--
-- Populated by api/_auth.py -> audit() on every successful require_admin()
-- call, gated by the env var ADMIN_AUDIT=1. Never stores secrets/tokens/PII
-- beyond the actor's own id/email and the request line.
--
-- Apply:  supabase db push
-- Then:   set ADMIN_AUDIT=1 in Vercel (Production + Preview) to activate.

create table if not exists public.admin_audit_log (
  id             bigint generated always as identity primary key,
  actor_user_id  uuid,
  actor_email    text,
  action         text        not null,          -- e.g. 'PATCH /api/config'
  object_type    text,                           -- optional: 'miembro' | 'configuracion' | ...
  object_id      text,                           -- optional: affected row id / key
  result         text        not null default 'ok',   -- 'ok' | 'error' | 'denied'
  origin         text,                           -- request Origin header, if present
  created_at     timestamptz not null default now()
);

create index if not exists admin_audit_log_time  on public.admin_audit_log (created_at desc);
create index if not exists admin_audit_log_actor on public.admin_audit_log (actor_user_id, created_at desc);

alter table public.admin_audit_log enable row level security;

-- Admins may read their own org's audit trail through the panel (authenticated
-- session). Writes go through the service-role backend only, so no INSERT
-- policy is defined.
drop policy if exists admin_audit_log_select_admins on public.admin_audit_log;
create policy admin_audit_log_select_admins
  on public.admin_audit_log
  for select
  to authenticated
  using (
    exists (
      select 1 from public.admin_profiles ap
      where ap.user_id = (select auth.uid())
        and ap.active
        and ap.role in ('owner', 'admin')
    )
  );

comment on table public.admin_audit_log is
  'Fase 0B.8 admin action trail. Insert: service-role only. Select: active admins.';
