# Security Hardening

## Phase 1 - Base headers

Date: 2026-05-25

Implemented via `vercel.json`:

- `Strict-Transport-Security: max-age=15552000; includeSubDomains`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: accelerometer=(), bluetooth=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), usb=()`

No strict CSP was added in this phase.

Production note: the configured HSTS value includes `includeSubDomains`, but the effective public response currently emitted through Cloudflare is `Strict-Transport-Security: max-age=15552000`. SecurityHeaders.com accepts it as present. Enforcing `includeSubDomains` at the edge should be handled later in Cloudflare HSTS settings if required.

## SecurityHeaders.com

Scan URL: `https://securityheaders.com/?q=https%3A%2F%2Fwww.cavagourmet.com%2F&followRedirects=on&hide=on`

Result: `A`

Present:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`

Missing by design in this phase:

- `Content-Security-Policy`

Warnings to evaluate later:

- Public home response reports `Access-Control-Allow-Origin: *`. Sensitive API endpoints remain protected and do not expose permissive CORS to external origins.

## External dependency inventory for CSP Report-Only

Scripts:

- Self-hosted scripts and inline scripts across public pages.
- Vercel Analytics: `/_vercel/insights/script.js`
- Vercel Speed Insights: `/_vercel/speed-insights/script.js`
- Supabase admin client: `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`

Fonts:

- `https://fonts.googleapis.com`
- `https://fonts.gstatic.com`

Images:

- Local assets under `/Assets/`
- `data:` images used in inline CSS/SVG backgrounds.
- TripAdvisor brand asset: `https://static.tacdn.com`
- QR generator in member page: `https://api.qrserver.com`
- Google Wallet logo source in backend flow: `https://raw.githubusercontent.com`

Supabase:

- Project URL: `https://rbfctmcfweckbpgxlkqf.supabase.co`
- Client auth config served through `/api/auth_config`

Google Wallet:

- OAuth token: `https://oauth2.googleapis.com`
- Wallet API: `https://walletobjects.googleapis.com`
- Save link destination: `https://pay.google.com`

External navigation / embeds:

- WhatsApp: `https://wa.me`
- Google Maps short link: `https://maps.app.goo.gl`
- Instagram, Facebook, Spotify, TripAdvisor, Vinetur and authority references in schema/outbound links.
- No iframe embeds found in the current production pages.

Analytics:

- Vercel Analytics and Speed Insights.
- Existing page-level CSP meta references Cloudflare Insights on the home page; no strict header CSP is active yet.

## Production checks

- `/` returns the base headers.
- `/admin/after-office` returns base headers and `X-Robots-Tag: noindex, nofollow`.
- `/journal/el-protocolo-del-vino-empieza-con-la-copa` returns base headers and remains public.
- `/members/` returns base headers.
- `/api/miembros` without auth returns `401`.
- `/api/wallet?email=test@example.com` without member token/admin auth returns `401`.

## Phase 2 - CSP Report-Only preflight

Date: 2026-05-25

### CORS audit

Sensitive API endpoints tested:

- `/api/miembros`
- `/api/registrar`
- `/api/registrar_experiencia`
- `/api/setup`
- `/api/link?email=test@example.com`
- `/api/wallet?email=test@example.com`
- `/api/config`

Result:

- No sensitive API endpoint returned `Access-Control-Allow-Origin: *`.
- Allowed origins return a reflected allowlist origin, for example `https://www.cavagourmet.com`.
- `https://evil.example` receives `403` and no valid `Access-Control-Allow-Origin`.
- Static public routes and assets currently return `Access-Control-Allow-Origin: *` from the platform/CDN layer. This was observed on `/`, `/journal`, `/admin/after-office`, `/members/`, `/site.webmanifest`, `/Assets/logo-cava-mark.webp`, `/robots.txt`, and `/sitemap.xml`.
- No global `Access-Control-Allow-Origin` header is configured in `vercel.json`.

### Admin HTML secret audit

Production `/admin/after-office` source was checked for:

- service role key
- `HMAC_SECRET`
- `GOOGLE_WALLET_KEY`
- `SCAN_PIN`
- `SCAN_KEY`
- private key material
- Supabase service key

Result:

- No private secrets were found in the admin HTML.
- The admin page exposes only the Supabase anon key through `/api/auth_config`, which is expected for Supabase Auth client usage.
- Sensitive API actions still require `Authorization: Bearer <access_token>` plus backend admin role validation.

Production `/api/auth_config` currently returns Supabase project URL `https://qkmgzyxknhhkucndbdsh.supabase.co`.

### Existing meta CSP

The following files already contain blocking `<meta http-equiv="Content-Security-Policy">` policies:

- `index.html`
- `after-office-vino-perez-zeledon.html`
- `cata-de-vinos-perez-zeledon.html`
- `nuestra-historia.html`
- `blog.html`
- `journal.html`
- `admin/plantilla-articulo.html`
- `blog/vino-menos-elitismo-mas-experiencia.html`
- `blog/contenido-digital-experiencia-real-vinoteca-costa-rica.html`
- `blog/como-se-construye-cultura-del-vino.html`
- `journal/vino-menos-elitismo-mas-experiencia.html`
- `journal/que-significa-cuerpo-en-el-vino.html`
- `journal/como-se-construye-cultura-del-vino.html`
- `journal/el-protocolo-del-vino-empieza-con-la-copa.html`
- `journal/el-miedo-silencioso-de-no-saber-de-vino.html`
- `journal/contenido-digital-experiencia-real-vinoteca-costa-rica.html`

Most use:

`default-src 'self'; script-src 'self' 'unsafe-inline' https://va.vercel-scripts.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://vitals.vercel-insights.com;`

The home page additionally allows `https://static.cloudflareinsights.com` and `https://cloudflareinsights.com`.

These meta CSP policies are blocking policies and can still affect those pages even while the new header-level CSP is only Report-Only.

### CSP Report-Only implementation

Implemented via `vercel.json` as `Content-Security-Policy-Report-Only` only. No blocking `Content-Security-Policy` response header was added.

Policy:

`default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://va.vercel-scripts.com https://static.cloudflareinsights.com; script-src-elem 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://va.vercel-scripts.com https://static.cloudflareinsights.com; script-src-attr 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src-elem 'self' 'unsafe-inline' https://fonts.googleapis.com; style-src-attr 'unsafe-inline'; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: blob: https:; connect-src 'self' https://vitals.vercel-insights.com https://cloudflareinsights.com https://qkmgzyxknhhkucndbdsh.supabase.co https://rbfctmcfweckbpgxlkqf.supabase.co; frame-src 'self' https://pay.google.com; child-src 'self' https://pay.google.com; worker-src 'self' blob:; manifest-src 'self'; media-src 'self'; upgrade-insecure-requests`

### CSP Report-Only production checks

- `/` returns `Content-Security-Policy-Report-Only` and no blocking CSP response header.
- `/admin/after-office` returns `Content-Security-Policy-Report-Only`, no blocking CSP response header, and `X-Robots-Tag: noindex, nofollow`.
- `/members/` returns `Content-Security-Policy-Report-Only` and no blocking CSP response header.
- `/journal` returns `Content-Security-Policy-Report-Only` and no blocking CSP response header.
- `/journal/el-protocolo-del-vino-empieza-con-la-copa` returns `Content-Security-Policy-Report-Only` and no blocking CSP response header.
- `/api/miembros`, `/api/setup`, `/api/link?email=test@example.com`, and `/api/wallet?email=test@example.com` remain `401` without auth.
- Admin HTML still includes Supabase Auth client loading from `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2` and fetches `/api/auth_config`.
- Members page still references `/api/member`, `/api/config`, and `https://api.qrserver.com` for the public member Wallet/QR flow.
- External origin `https://evil.example` receives no valid CORS header from sensitive APIs.

## End-of-day security snapshot

Date: 2026-05-25

Status: production stable, hardened, and documented. No CSP enforcement, SEO changes, architecture changes, SSR/middleware migration, or large refactors were applied in this closeout.

### Current production state

- Base security headers are active through `vercel.json`.
- `Content-Security-Policy-Report-Only` is active globally.
- No new blocking `Content-Security-Policy` response header is active.
- Sensitive APIs remain protected by backend admin validation.
- Admin remains `noindex, nofollow`.
- Public pages remain indexable where intended.

### Active headers

Expected response headers:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy-Report-Only`

Admin route:

- `/admin/after-office` also returns `X-Robots-Tag: noindex, nofollow`.

Accepted temporary note:

- HSTS `includeSubDomains` is configured in `vercel.json`, but Cloudflare currently emits `Strict-Transport-Security: max-age=15552000`. Treat Cloudflare HSTS as a future edge configuration item.

### Final production smoke checks

Routes checked:

- `/` returned `200`.
- `/nazareth` returned `200`.
- `/journal` returned `200`.
- `/members/` returned `200`.
- `/admin/after-office` returned `200` and `X-Robots-Tag: noindex, nofollow`.

Sensitive API checks:

- `/api/miembros` returned `401` without auth.
- `/api/setup` returned `401` without auth.
- `/api/link?email=test@example.com` returned `401` without auth.
- `/api/wallet?email=test@example.com` returned `401` without valid member token or admin auth.
- `/api/config` returned `200` with public config behavior.
- `/api/miembros` with `Origin: https://evil.example` returned `403` and no valid CORS header.

Console/loading smoke check:

- Chrome headless smoke checks on `/`, `/nazareth`, `/journal`, `/members/`, and `/admin/after-office` did not report matching breakage patterns for CSP, refused resources, Supabase Auth, fonts, images, analytics, or UI scripts.

### Required environment variables

Required for production:

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_WALLET_KEY`
- `HMAC_SECRET`
- `CAVA_ALLOWED_ORIGINS`

Legacy / compatibility variables still referenced by existing code:

- `SUPABASE_KEY`: fallback for service-role behavior in some API modules. Prefer confirming it is service-role only server-side, or migrating all backend modules to `SUPABASE_SERVICE_ROLE_KEY`.
- `SCAN_PIN`: referenced by the scan/admin-adjacent flow and should remain server-side only.

Current `CAVA_ALLOWED_ORIGINS` should include production origins and intentional local development origins only, for example:

- `https://www.cavagourmet.com`
- `https://cavagourmet.com`
- `http://localhost:3000`
- `http://localhost:5173`
- `http://127.0.0.1:5500`

### Admin flow snapshot

1. Admin opens `/admin/after-office`.
2. Page loads Supabase Auth client from `https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2`.
3. Page fetches `/api/auth_config`.
4. `/api/auth_config` exposes only `SUPABASE_URL` and `SUPABASE_ANON_KEY`, which are expected client-side values.
5. Admin signs in with Supabase Auth.
6. Admin API calls include `Authorization: Bearer <access_token>`.
7. Backend validates the access token with Supabase Auth.
8. Backend checks `admin_profiles` using the service-role key server-side.
9. Only active users with role `owner` or `admin` can perform protected admin actions.

### `admin_profiles` table snapshot

Expected role table:

- Table: `admin_profiles`
- Required columns:
  - `user_id`: Supabase Auth user id.
  - `email`: admin email for auditability.
  - `role`: allowed values currently expected by backend are `owner` or `admin`.
  - `active`: must be `true` for access.

Backend lookup:

- Filters by `user_id`.
- Requires `active=eq.true`.
- Accepts only `role in ("owner", "admin")`.

### Secure deploy process

1. Keep changes small and scoped.
2. Commit and push to `master`.
3. Wait for Vercel production deployment to reach Ready.
4. Verify production headers and routes before assuming success.
5. Re-run sensitive API checks without auth.
6. Re-run CORS checks with an external origin.
7. Confirm admin route remains `noindex, nofollow`.
8. Confirm no new blocking CSP header was introduced unless explicitly intended.
9. Document results in this file.

### Accepted temporary risks / future work

- Static public routes and assets currently return `Access-Control-Allow-Origin: *` from the platform/CDN layer. Sensitive APIs do not.
- Several pages still contain legacy blocking meta CSP policies. These must be cleaned and unified so HTTP headers become the single source of truth.
- CSP is currently Report-Only. Do not move to enforcement until meta CSP inconsistencies are removed and real reports have been observed.
- No CSP reporting endpoint is active yet. Reports are observable through browser/devtools behavior, but not centrally collected.
- HSTS edge behavior is controlled by Cloudflare and should be reviewed before enabling stricter subdomain/preload posture.
- Some backend modules still reference legacy `SUPABASE_KEY`; future cleanup should standardize service-role naming without changing runtime behavior abruptly.

### Do not change next without a separate phase

- Do not enable CSP enforcement.
- Do not make SEO/indexation changes.
- Do not change public site structure.
- Do not migrate to SSR or middleware.
- Do not perform broad refactors.
