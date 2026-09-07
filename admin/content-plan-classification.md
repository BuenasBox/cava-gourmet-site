# CAVA Journal / Entity SEO — Content Plan Classification

> Derived from `data/pages.json` (108 entries: 9 `publicado`, 99 `pendiente`).
> Produced during the Audit Roadmap closure (Fase 5.5). **This is a
> prioritization plan, not a generation order. Do NOT auto-generate these
> pages.** Each one needs real, locally-differentiated content in CAVA's
> editorial voice (see `CLAUDE.md` → "Voz editorial" and "Prohibiciones
> absolutas": no thin content, no programmatic filler, no duplicated blocks).

## Slug reality check

`data/pages.json` slugs are aspirational and do **not** all match production.
Example: entry #1 is `publicado` as `/experiencias/after-office-vino-perez-zeledon`,
but the live page is `/after-office-vino-perez-zeledon` (no `/experiencias/`
prefix). Before building any hub, decide the canonical URL shape and reconcile
`pages.json`, `sitemap.xml` and internal links in one pass. Do not ship a hub
that redirects to itself or splits link equity across two prefixes.

---

## Tier A — HIGH VALUE (build first, 1–2 at a time, real content)

Commercial intent + reinforce an existing entity/territory + plausibly rank
without a large cluster behind them.

| Slug | Why it earns priority |
|---|---|
| `/experiencias/cata-de-vinos-privada` | Direct booking intent; complements the live `/cata-de-vinos-perez-zeledon`; "cata privada" is a distinct query. |
| `/experiencias/experiencia-romantica-con-vino` | High-margin occasion; pairs with CTA "Planear mi noche especial"; no current page owns it. |
| `/experiencias/experiencia-corporativa-con-vino` | B2B / group bookings; different CTA and copy; real revenue line. |
| `/experiencias/regalo-experiencia-vino` | Gift intent, seasonal spikes; ties to Wallet/loyalty. |
| `/aprende/vino-sin-miedo` | Core brand territory ("vino sin miedo"); strong LLM/GEO answer target; links to `/nazareth` and `/cata-…`. |
| `/aprende/como-elegir-un-vino` | High-volume beginner query; CAVA's "acompañamiento en selección" angle is a genuine differentiator. |
| `/maridaje/comida-costarricense` | Owns territory #6 (maridaje con comida costarricense); almost no credible local competition; very shareable. |
| `/perez-zeledon/vinoteca-perez-zeledon` | Local pack + "vinoteca Pérez Zeledón" head term; should probably be a canonical landing, not a spoke. |
| `/perez-zeledon/donde-tomar-vino-perez-zeledon` | Bottom-funnel local query; short page, high conversion. |
| `/aprende/preguntas-que-da-pena-hacer-sobre-vino` | Signature CAVA voice; FAQ-dense; ideal AI Overview / ChatGPT citation surface. |

## Tier B — NEEDS REAL CONTENT (valid topics, blocked on a human input)

Worth building, but each needs something only CAVA can supply — a real
tasting note, a real event, a photo, Nazareth's actual position. Do not
generate from a template.

- `/experiencias/*` remaining (#3, #7–#20): each needs a real description of
  what the experience *is* (duration, format, price band, what's on the table).
  Several are near-duplicates (`experiencia-vino-para-parejas` vs
  `experiencia-vino-para-amigos` vs `vino-y-conversacion`) — **merge, don't
  ship 3 thin variants.**
- `/aprende/*` fundamentals (#21–#45): legitimate evergreen education. Needs
  Nazareth's plain-language explanations, not a generic wine-blog rewrite.
  Batch by theme (tasting, storage, vocabulary) into fewer, deeper pages.
- `/maridaje/*` Costa-Rican dishes (#72–#74, #81): high uniqueness ceiling,
  but only if the pairings are real recommendations, not invented.
- `/perez-zeledon/*` (#92–#100): need real local detail (hours, parking,
  what's nearby) to beat a directory listing.

## Tier C — DO NOT GENERATE YET (low marginal value / high thin-content risk)

- `/vinos/*` varietal pages (#51–#70): 20 pages of "what is Malbec" duplicate
  what Wikipedia and every importer already rank for. No local moat. Only
  revisit if CAVA maintains a real, in-stock list per varietal (then they
  become inventory pages, not articles).
- `/maridaje/*` generic global dishes (#77–#82 pizza/pasta/sushi/burgers):
  commodity content, no CAVA angle. Skip.
- `/maridaje/*` occasion pages (#85–#90): thin; fold the useful ones into the
  Tier A gift / romantic experience pages instead of standalone.
- Hub index pages (`/experiencias/`, `/aprende/`, `/vinos/`, `/maridaje/`,
  `/perez-zeledon/`, `/cultura-del-vino/`): only create a hub once it has
  ≥4 real spokes. An empty hub is crawl waste.

---

## Recommended sequence

1. Reconcile URL shape + `pages.json` + `sitemap.xml` (technical, no content).
2. Ship Tier A one page per week, each with FAQ + schema + 1 internal link
   outside its hub (per `CLAUDE.md` hub-and-spoke rules).
3. Stand up a hub only after its 4th real spoke.
4. Re-evaluate Tier B/C after the first 6 Tier A pages have 8 weeks of data.

**Technical roadmap status for this item: CLOSED.** Remaining work is
editorial production and belongs to CONTENT follow-up, not engineering.
