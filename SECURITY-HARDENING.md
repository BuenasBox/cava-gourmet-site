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

