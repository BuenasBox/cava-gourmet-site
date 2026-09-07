-- Fase 0B.3 — scan endpoint: server-side rate limit / lockout / dedupe
--
-- /api/scan today: global SCAN_PIN, no rate limit, no lockout, weak dedupe.
-- Persistence layer for api/scan.py's scan_guard_check() / scan_record(),
-- inert until SCAN_HARDENING=1 (see api/scan.py + docs/FASE-0B-SECURITY-HARDENING.md).
--
-- One row per POST attempt. Keyed by sha256(member token) — the raw token /
-- email is never stored here. `ip` is the first x-forwarded-for hop and backs
-- the cross-token limits (one host cycling many stolen/guessed tokens).
--
-- Apply:  apply_migration / supabase migration up   (or paste into the SQL editor)
-- Then:   set SCAN_HARDENING=1 in Vercel (Production + Preview) to activate.

create table if not exists public.scan_attempts (
  id           bigint generated always as identity primary key,
  token_hash   text        not null,           -- sha256(member token), hex
  ip           text,                            -- x-forwarded-for first hop, nullable
  success      boolean     not null,
  reason       text,                            -- 'ok' | 'bad_pin' | 'cooldown'
                                                --   | 'rate_token' | 'locked_token'
                                                --   | 'rate_ip'    | 'locked_ip'
  created_at   timestamptz not null default now()
);

create index if not exists scan_attempts_token_time on public.scan_attempts (token_hash, created_at desc);
create index if not exists scan_attempts_ip_time    on public.scan_attempts (ip, created_at desc);

-- RLS on, no policies: anon/authenticated get nothing on the Data API. The
-- backend writes/reads with the service-role key, which bypasses RLS.
alter table public.scan_attempts enable row level security;

-- Retention: keep ~30 days. Run from pg_cron or the app.
--   delete from public.scan_attempts where created_at < now() - interval '30 days';

comment on table public.scan_attempts is
  'Fase 0B.3 rate-limit/lockout ledger for /api/scan. Service-role only. token_hash = sha256(member token).';
