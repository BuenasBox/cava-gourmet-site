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
