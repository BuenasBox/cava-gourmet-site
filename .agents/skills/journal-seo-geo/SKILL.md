---
name: journal-seo-geo
description: Use this skill to plan CAVA/Nazareth Journal articles before drafting or building: SEO, GEO, AI SEO, entity reinforcement, clusters, cannibalization, Vinetur adaptations, internal linking, CTA direction, and schema planning. It creates briefs only; it must not write full articles or generate final HTML.
---

# Journal SEO/GEO

Use this skill before writing, adapting, or approving any article for the CAVA Journal. It creates the strategic brief for a Journal piece. It does not write the full article, generate final HTML, or modify site files.

The canonical editorial section is `/journal`. Block `/blog` for new work.

## Brief Persistence Requirement

Every approved brief must be persisted before the article moves to drafting or HTML build.

Persist the brief at:

```text
admin/briefs/[slug].md
```

Rules:

- Use the final recommended slug without the `/journal/` prefix for the filename.
- Record status as one of:
  - `draft`
  - `listo para build`
  - `listo para publicacion`
- Record whether the page should remain `noindex,nofollow`.
- Record cannibalization review against:
  - existing Journal articles,
  - planned or existing Aprende pages,
  - `data/pages.json`.
- Record the recommended image only after it has been checked against `admin/journal-image-inventory.md`.
- Do not let a brief advance to builder if it exists only in chat.
- Do not modify `journal.html`, `sitemap.xml`, `data/pages.json`, or `llms.txt` from this skill.

## Core Purpose

Plan Journal articles that strengthen:

- CAVA as a vinoteca experiencial in Perez Zeledon, Zona Sur, Costa Rica.
- Nazareth Padilla Montero as a cultural and expert voice in wine.
- Costa Rica wine culture, education without intimidation, hospitality, and experience.
- AI-search clarity: the article should answer real human questions in a way ChatGPT/Gemini can cite or summarize accurately.

Every article must have a reason to exist. If it does not add a clear angle, entity signal, local relevance, or practical answer, recommend not publishing it.

## Inputs To Request Or Infer

For each article plan, gather:

- Working topic or draft title.
- Source status: original Journal idea, Vinetur adaptation, existing draft, or content cluster item.
- Desired article type.
- Target reader and emotional/practical intent.
- Known source URL if previously published elsewhere.
- Related existing Journal articles.
- Relevant entries from `data/pages.json` if the topic overlaps a planned hub.

If key facts are unknown, state assumptions instead of inventing.

## Article Type Classification

Choose one primary type and, if useful, one secondary type:

- **Editorial profundo**: opinion or cultural thesis; best for intimidation, elitism, hospitality, perception, wine culture.
- **Evergreen SEO**: durable explanation of a common wine question; answer early, avoid essay drift.
- **Practico**: decision support; how to choose, store, serve, pair, buy, or recover from uncertainty.
- **Observacional corto**: one scene or repeated phrase from the vinoteca; short, focused, no need to cover the whole topic.
- **Adaptacion Vinetur**: based on a published Vinetur article; must add CAVA/Nazareth context and avoid literal duplication.
- **Refuerzo de entidad Nazareth**: supports her authority, credentials, point of view, international relevance, or media presence.
- **Local Costa Rica/Perez Zeledon**: anchors wine culture, climate, food, hospitality, or premium experiences outside the GAM.

The type controls depth. Do not turn every topic into an editorial manifesto.

## Intent Model

Assign one dominant intent:

- Informational: wants a clear answer.
- Practical: wants to decide or do something.
- Anxious: afraid of not knowing wine.
- Cultural: wants a perspective on wine and society.
- Local: wants context in Costa Rica/Perez Zeledon/Zona Sur.
- Authority: wants to understand Nazareth, CAVA, or why this voice matters.
- Conversational AI: likely to ask ChatGPT/Gemini a natural question.

Then state the exact human question the article should answer.

## Cluster And Hub Mapping

Map the piece to one cluster:

- `journal`: editorial reflections and CAVA/Nazareth point of view.
- `aprende`: beginner education and evergreen explanations.
- `experiencias`: catas, after office, hospitality, events, gift or group intent.
- `vinos`: varietals, styles, wine vocabulary, comparisons.
- `maridaje`: food, Costa Rican meals, occasions, pairing logic.
- `perez-zeledon`: local discovery, tourism, premium experiences outside GAM.
- `cultura`: broader wine culture in Costa Rica.
- `nazareth`: authority, media, credentials, personal platform, Vinetur/international visibility.

Use `/journal/[slug]` for articles. If the topic is better as a landing page from `data/pages.json`, say so and do not force it into the Journal.

## Keyword Rules

Define:

- Primary keyword: one natural phrase.
- Secondary keywords: 3-5 supporting phrases.
- Conversational AI questions: 3-5 natural questions.

Rules:

- Prefer natural Spanish over keyword stuffing.
- Do not repeat geographic phrases unless they add meaning.
- Avoid generic head terms if CAVA cannot compete or add a local angle.
- Use long-tail questions when the article is evergreen or practical.

## Entity Reinforcement

Choose the main entity reinforced:

- CAVA Gourmet Market / CAVA Vinoteca
- Nazareth Padilla Montero
- Nazareth Wine Journey
- Perez Zeledon / Zona Sur
- Costa Rica wine culture
- CAVA Journal

State the entity contribution in one sentence. Example: "This article reinforces Nazareth as a translator of wine language for emerging wine consumers in Costa Rica."

Never invent credentials, awards, statistics, or publication status.

## Cannibalization Review

Before recommending publication, compare with existing Journal content and planned registry topics.

Existing Journal reference points:

- `/journal/el-miedo-silencioso-de-no-saber-de-vino`: intimidation, perception, emerging markets, Vinetur pattern.
- `/journal/vino-menos-elitismo-mas-experiencia`: anti-elitism, education through experience.
- `/journal/como-se-construye-cultura-del-vino`: Costa Rica wine culture, first approach, vinoteca as trust space.
- `/journal/contenido-digital-experiencia-real-vinoteca-costa-rica`: content, community, physical experience.

Registry risks from `data/pages.json` include beginner education, wine vocabulary, storage, serving, pairing, local Perez Zeledon pages, and experience pages.

Also check Aprende explicitly. If a Journal topic overlaps an Aprende route, define the separation:

- Journal: editorial, experiential, voice-led, human context.
- Aprende: structured beginner education, glossary, step-by-step guidance, technical basics.

Name the competing or adjacent Aprende slug in the brief.

Classify risk:

- **Low**: unique angle and distinct query.
- **Medium**: overlaps, but can be differentiated by intent or format.
- **High**: likely duplicate or should merge with an existing/planned page.

If risk is medium or high, recommend:

- new angle,
- narrower query,
- different article type,
- internal link strategy,
- or do not publish.

## Internal Linking Rules

Recommend internal links, but do not edit files.

Always consider:

- `/journal` as hub return.
- `/nazareth` when expertise, authority, Vinetur, or Nazareth Wine Journey matters.
- `/cata-de-vinos-perez-zeledon` when the article has learning, experience, tasting, or booking intent.
- `/after-office-vino-perez-zeledon` when the article references conversation, hospitality, shared table, or weekly ritual.
- Related Journal articles when the concept continues a published argument.
- `/nuestra-historia` when the article reinforces origin, moat, or CAVA’s evolution.

Block:

- New links to `/blog`.
- Generic anchors such as "click here", "ver mas", "leer aqui".
- Excessive internal links that make an article feel mechanical.

Recommend 3-5 links max for a normal article unless the strategy requires more.

## CTA Direction

Recommend a CTA only if it fits the article type.

- Evergreen/practical: soft CTA to learn in person or ask for guidance.
- Editorial profundo: usually softer, often toward `/nazareth`, `/journal`, or a related experience.
- Local/Perez Zeledon: reservation or visit intent may be appropriate.
- Vinetur adaptation: avoid making the article feel like an ad; use authority and context first.

Primary reservation CTA is WhatsApp CAVA: `+506 8632 5260`.
Use Nazareth direct contact only for public figure, media, winery/importer, or collaboration context.

## Vinetur Similarity Check Gate

This gate is mandatory for any article marked as a "Vinetur candidate" or "Vinetur submission". Run it before drafting or approving the brief. Do not plan, approve, or persist a Vinetur-destination brief without completing this check.

### When to activate

Activate if any of these apply:

- The article is intended for submission to Vinetur before or alongside the Journal version.
- The source status is "Vinetur candidate" or "Vinetur submission".
- The article topic falls in known Vinetur editorial categories: wine culture, wine vocabulary, fear of wine, wine education, Costa Rica wine, pairing, practical storage or serving tips, wine buying, regional wine.

### How to run the check

Search the following in Vinetur using `site:vinetur.com`:

1. The exact working title or the equivalent phrase.
2. The main synonyms of the topic.
3. The primary search intent rephrased as a natural question.
4. Recent articles in the same topic category.
5. Older archived articles on the same theme.
6. Articles by external authors covering the same or adjacent topic.

If internet access is not available, mark the check result as "pendiente de verificación externa". Do not advance the brief to Vinetur submission status until the check is completed manually and the result is documented.

### Similarity scale

Classify the result as one of:

- **Libre**: no substantially similar article found. The topic can proceed as a Vinetur candidate.
- **Similar pero diferenciable**: a similar article exists but a clear angle, format, scope, or geographic difference makes a new submission viable. Document the differentiation strategy explicitly.
- **Bloqueado**: a substantially similar article exists and no credible differentiation is possible. Do not submit to Vinetur.

### Blocked topic rules

If the result is "Bloqueado":

- Do not submit the article to Vinetur.
- Recommend converting it into an internal Journal article with a CAVA/Nazareth/Costa Rica angle not covered by the Vinetur article.
- Or recommend changing the editorial angle radically enough that no substantial overlap exists.
- Record the blocking reason and the redirect recommendation in `admin/briefs/[slug].md`.

### Example risk case

The topic "cómo guardar una botella de vino ya abierta" must not be submitted to Vinetur. A substantially similar article already exists:

```text
https://www.vinetur.com/20260513100625/como-conservar-el-vino-abierto-durante-varios-dias.html
```

Older Vinetur articles also cover the same topic, making the space saturated. This topic should be redirected to the Journal with a CAVA/Nazareth/Costa Rica angle — for example, what Nazareth recommends to customers who buy a bottle and cannot finish it, or the reality of opened bottles in a warm tropical climate like Zona Sur.

### Vinetur similarity check output block

Produce this block as part of the brief whenever the gate is activated:

```text
VINETUR SIMILARITY CHECK

Topic checked:
Checked on: [date or "no internet — pendiente de verificación externa"]

URLs found:
- [URL] — [angle / theme summary]

Similarity result:
- Libre / Similar pero diferenciable / Bloqueado

Reason:
- [Why this result was assigned]

Recommendation:
- Enviar a Vinetur — proceed with Vinetur submission
- Redirigir al Journal — publish only as an internal CAVA Journal article
- Reescribir con otro ángulo — submit to Vinetur with a clearly differentiated approach
- Descartar — topic has no viable angle for either channel
```

## Vinetur Adaptation Rules

For articles originally published in Vinetur:

1. Wait for the public Vinetur URL before planning the Journal version as published.
2. Create an adapted Journal version, not a literal copy.
3. Use a self-referencing canonical plan for `/journal/[slug]`.
4. Include a visible note: "Publicado originalmente en Vinetur" with date and link when available.
5. Include a contextual external link to the Vinetur article.
6. Preserve Nazareth authorship and authority signals without overstating the relationship.
7. Suggest schema references only when they reflect visible content, such as `citation`, `subjectOf`, or `isBasedOn`.
8. Keep the Journal version useful on its own by adding CAVA/Nazareth/Costa Rica context.

If Vinetur approval is pending and no URL exists, recommend holding publication or keeping any draft non-public until the external source is live.

## Schema Planning Rules

Provide a schema plan only; do not generate final markup.

Allowed planning types for Journal articles:

- `BlogPosting`
- `Article`
- `WebPage`
- `Person` for Nazareth when relevant
- `Organization` for CAVA when relevant
- `BreadcrumbList`
- `FAQPage` only if visible FAQ is planned

Rules:

- Schema must reflect visible content.
- No invented awards, stats, or credentials.
- No `Winery` schema. CAVA does not produce wine.
- For Vinetur adaptations, suggest `citation`, `subjectOf`, or `isBasedOn` only when the note/link is visible in the article.

## Hard Blocks

Reject or flag plans that rely on:

- `/blog` routes for new content.
- Thin content or generic explanations without local/editorial value.
- Duplicate articles under different slugs.
- Keyword stuffing.
- Claims that cannot be verified.
- Schema unsupported by visible content.
- `Winery` schema.
- Programmatic SEO with no unique human angle.
- Articles that should actually be landing pages, service pages, or merged into existing content.
- Vinetur-candidate articles where the Vinetur similarity check has not been completed or is "pendiente de verificación externa" and the article is advancing to Vinetur submission without resolving it.
- Topics where the Vinetur similarity check returned "Bloqueado" and no validated alternative angle is documented in the brief.

## Output Format

Return this brief, not a full article:

```text
JOURNAL SEO/GEO BRIEF

Brief file:
Status:
Robots recommendation:

Article type:
Primary intent:
Human question answered:

Recommended slug:
Title tag:
Meta description:
Suggested H1:

Primary keyword:
Secondary keywords:
Conversational AI questions:

Entity reinforced:
Cluster / hub:
Brand moat contribution:

Suggested structure:
- H2:
  - H3, if useful:

Internal links:
- Anchor text -> URL -> reason

CTA recommendation:

Vinetur similarity check:
- Not applicable / pendiente de verificación externa / Libre / Similar pero diferenciable [differentiation strategy] / Bloqueado [reason and redirect recommendation]
- URLs reviewed: [list or none found]

Vinetur status:
- Not applicable / pending URL / published URL available
- Required visible note, if applicable

Schema plan:
- Types:
- External reference plan, if applicable:

Cannibalization risk:
- Low / Medium / High
- Reason:
- Checked against Journal:
- Checked against Aprende:
- Checked against data/pages.json:
- Differentiation strategy:

Recommendation:
- Write as Nazareth / evergreen assisted / hold / merge / use as landing page instead

Assumptions and risks:
```

## Final Gate

Before approving the brief, verify:

- Route is `/journal/[slug]`, not `/blog`.
- The approved brief is persisted at `admin/briefs/[slug].md`.
- Status is recorded as `draft`, `listo para build`, or `listo para publicacion`.
- Article type matches depth.
- The angle differs from existing Journal articles.
- Cannibalization has been checked against Journal, Aprende, and `data/pages.json`.
- The piece reinforces at least one strategic entity.
- There is a clear internal linking plan.
- Any Vinetur source is public before publication.
- For Vinetur-candidate articles: the Vinetur similarity check is complete with result "Libre" or "Similar pero diferenciable" with a documented differentiation strategy, or is marked "pendiente de verificación externa" and is not advancing to Vinetur submission until resolved.
- For Vinetur-blocked topics: the redirection to an internal Journal angle is documented in `admin/briefs/[slug].md`.
- No generic SEO article is being disguised as editorial content.
