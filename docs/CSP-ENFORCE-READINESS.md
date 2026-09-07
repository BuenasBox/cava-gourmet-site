# CSP — enforce readiness (Fase 6.6)

**Outcome: stay on `Content-Security-Policy-Report-Only`.** Not because the
policy is wrong — it is essentially enforce-ready for the public site — but
because:

1. `CLAUDE.md` explicitly requires a *dedicated, separate* security sprint for
   any CSP change and forbids mixing it with SEO/content work.
2. The audit environment cannot verify the two surfaces that would actually
   break first under enforce: the **admin panels' authenticated flow**
   (needs a Supabase session) and the **Google Wallet redirect** (needs a
   valid member token). "No hacerlo a ciegas."
3. The Report-Only policy currently has **no `report-uri`/`report-to`**, so no
   real violation data has ever been collected. Flipping to enforce without a
   collection window is the "a ciegas" path the roadmap warns against.

## What the dedicated sprint needs to do

1. Add a report sink first (`report-to` + a `/api/csp-report` collector or a
   third-party endpoint), keep Report-Only, let it run ~1–2 weeks across real
   admin sessions, a real Wallet add, Analytics + Cloudflare Insights beacons.
2. Reconcile the **drifted inline `<meta http-equiv>` CSPs**. `nazareth.html`
   and the 8 `journal/*.html` each carry their own, stricter, *already
   enforcing* meta CSP:
   `script-src 'self' 'unsafe-inline' https://va.vercel-scripts.com;
    connect-src 'self' https://vitals.vercel-insights.com;`
   — i.e. on those pages Cloudflare Insights and jsdelivr/Supabase are
   already blocked. Decide one policy; don't ship header-enforce that
   contradicts the meta layer (CSP composes as intersection).
3. Only then swap the `vercel.json` header key
   `Content-Security-Policy-Report-Only` → `Content-Security-Policy`.

## Current policy assessment (informational)

The `vercel.json` policy keeps `'unsafe-inline'` for `script`/`style` (needed
for inline JSON-LD and inline handlers), so enforce would **not** break the
static pages. Every external host the site uses is already allowlisted:

| Need | Directive | Host | OK |
|---|---|---|---|
| Google Fonts CSS / files | style-src / font-src | fonts.googleapis.com / fonts.gstatic.com | ✅ |
| Vercel Analytics + Speed Insights | script-src / connect-src | va.vercel-scripts.com / vitals.vercel-insights.com | ✅ |
| Cloudflare Insights | script-src / connect-src | static.cloudflareinsights.com / cloudflareinsights.com | ✅ |
| supabase-js (admin) | script-src | cdn.jsdelivr.net | ✅ |
| Supabase Auth/REST (admin) | connect-src | rbfctmcfweckbpgxlkqf.supabase.co | ✅ (wss to same host also allowed) |
| Google Wallet | frame-src / child-src | pay.google.com | ✅ (the /api/wallet 302 is a top-level nav, not frame-gated) |
| all images incl. Assets/images/professional | img-src | 'self' data: blob: https: | ✅ |

Known gap that is **Preview-only, not production**: `vercel.live` feedback
widget (`vercel.live/_next-live/feedback/feedback.js`) is not allowlisted, so
it reports under enforce on Preview deployments. Ignore per `CLAUDE.md` /
audit "falsos problemas" list, or add `https://vercel.live` to `script-src`
during the sprint if Preview noise is unwanted.

`vercel.json` was **not modified** by the Audit Roadmap work.
