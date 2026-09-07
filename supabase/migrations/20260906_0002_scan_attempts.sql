-- Fase 0B.3 — scan endpoint: server-side rate limit / lockout / dedupe
--
-- /api/scan today: global SCAN_PIN, no rate limit, no lockout, weak dedupe.
-- This table is the persistence layer for api/scan.py's _scan_guard(), which
-- stays inert until the env var SCAN_HARDENING=1 is set (see api/scan.py).
--
-- One row per attempt (PIN entry). Keyed by a hash of the member token so we
-- never store the raw email/token here; client IP kept for IP-scoped limits.
--
-- Apply:  supabase db push
-- Then:   set SCAN_HARDENING=1 in Vercel (Production + Preview) to activate.

create table if not exists public.scan_attempts (
  id           bigint generated always as identity primary key,
  token_hash   text        not null,           -- sha256(member token), hex
  ip           text,                            -- x-forwarded-for first hop, nullable
  success      boolean     not null,
  reason       text,                            -- 'ok' | 'bad_pin' | 'locked' | 'cooldown' | 'rate'
  created_at   timestamptz not null default now()
);

create index if not exists scan_attempts_token_time on public.scan_attempts (token_hash, created_at desc);
create index if not exists scan_attempts_ip_time    on public.scan_attempts (ip, created_at desc);

-- RLS on, no policies: anon/authenticated get nothing. The backend uses the
-- service-role key, which bypasses RLS.
alter table public.scan_attempts enable row level security;

-- Retention: keep 30 days. Run from a scheduled job (pg_cron) or the app.
--   delete from public.scan_attempts where created_at < now() - interval '30 days';

comment on table public.scan_attempts is
  'Fase 0B.3 rate-limit/lockout ledger for /api/scan. Written by service-role only.';
