# Admin/API Security Tests

Run these checks after deploying changes to production.

## Required Environment

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` or existing `SUPABASE_KEY` with service-role privileges
- `GOOGLE_WALLET_KEY`
- `HMAC_SECRET`
- `SCAN_PIN`
- `CAVA_ALLOWED_ORIGINS`

## Supabase Admin Role Table

Create and maintain this table in Supabase:

```sql
create table if not exists public.admin_profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  role text not null check (role in ('owner', 'admin')),
  active boolean not null default true,
  created_at timestamptz not null default now()
);
```

Add one row for each authorized admin user. The backend checks `user_id`, `role`, and `active`.

## Unauthenticated Requests Must Fail

```bash
curl -i https://www.cavagourmet.com/api/miembros
curl -i -X POST https://www.cavagourmet.com/api/registrar
curl -i -X POST https://www.cavagourmet.com/api/registrar_experiencia
curl -i https://www.cavagourmet.com/api/setup
curl -i "https://www.cavagourmet.com/api/link?email=test@example.com"
curl -i "https://www.cavagourmet.com/api/wallet?email=test@example.com"
```

Expected: `401 Unauthorized` or `403 Forbidden`. No member data, Wallet link, or mutation should occur.

## Disallowed Origins Must Fail CORS

```bash
curl -i -H "Origin: https://evil.example" https://www.cavagourmet.com/api/miembros
curl -i -X OPTIONS -H "Origin: https://evil.example" -H "Access-Control-Request-Method: GET" https://www.cavagourmet.com/api/miembros
```

Expected: no trusted `Access-Control-Allow-Origin`; preflight should return `403`.

## Admin Requests Must Pass

Use a Supabase Auth access token for a user present in `admin_profiles`.

```bash
curl -i \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  https://www.cavagourmet.com/api/miembros
```

Expected: `200 OK` with member data only for authorized admins.

## Member Wallet Flow

Public Wallet links must include both member email and member token:

```text
/api/wallet?e=<email>&t=<member-token>
```

Expected:
- valid member token: redirects to Google Wallet
- missing token or email-only request: `401`/`403`

## Admin Panel

1. Open `/admin/enofilios-panel`.
2. Confirm the login screen appears before any member data.
3. Log in with a non-admin Supabase user.
4. Confirm API calls fail with `403`.
5. Log in with an admin listed in `admin_profiles`.
6. Confirm member list, registration, experience update, config update, and Wallet link generation work.
7. Confirm logout hides the panel again.
