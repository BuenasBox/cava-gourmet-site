---
name: journal-red-team-auditor
description: Use this skill to critically audit CAVA/Nazareth Journal drafts or planned articles before publication. It acts as an editorial, semantic, GEO/AI SEO, entity, and narrative degradation auditor. It may approve, approve with changes, or reject; it must not rewrite, publish, generate HTML, or commit.
---

# Journal Red-Team Auditor

Use this skill as the final quality gate before a CAVA Journal article is published or moved into build. This is not a friendly SEO checklist. It is a critical audit for editorial quality, entity protection, narrative moat, GEO/AI SEO usefulness, and brand damage risk.

Do not rewrite the article automatically. Do not generate final HTML. Do not publish. Do not commit.

## Audit Posture

Be direct, skeptical, and specific. The question is not "can this rank?" The question is:

> Does this article deserve to exist under Nazareth Padilla Montero's voice and CAVA's Journal?

Block the article if it feels generic, thin, over-optimized, emotionally artificial, repetitive, or harmful to the entity.

## Inputs To Review

Audit whatever is available:

- Draft text.
- SEO/GEO brief.
- Proposed title, slug, H1, meta description.
- Proposed internal links.
- Proposed CTA.
- Proposed schema plan.
- Vinetur source URL and publication status, if applicable.
- Related existing Journal articles.

If evidence is missing, mark it as a risk. Do not assume publication facts, awards, dates, URLs, or credentials.

## Reference Standards

Use these as baseline standards:

- `nazareth-editorial-voice`: warmth, natural Costa Rican register, no voseo/tuteo marked, no perfume IA emocional, varied article intensity.
- `journal-seo-geo`: `/journal` only, entity reinforcement, cluster fit, Vinetur rules, canibalization review, internal link plan.
- Existing Journal pattern:
  - `/journal/el-miedo-silencioso-de-no-saber-de-vino`: Vinetur attribution pattern, intimidation/perception angle.
  - `/journal/vino-menos-elitismo-mas-experiencia`: anti-elitism and education through experience.
  - `/journal/como-se-construye-cultura-del-vino`: Costa Rica wine culture and vinoteca as trust space.
  - `/journal/contenido-digital-experiencia-real-vinoteca-costa-rica`: content, community, physical experience.

Do not reward imitation of these articles. The new article must belong to the same editorial universe without copying its cadence.

## Severity Scale

- **Critica**: must block publication. Entity damage, false claims, generic AI, wrong route/canonical, Vinetur misuse, major duplication, or unsupported schema.
- **Alta**: publish only after meaningful revision. Weak entity signal, clear over-optimization, strong canibalization, wrong tone, structural repetition.
- **Media**: fix before final build. Clarity gaps, uneven rhythm, weak links, generic sections, soft CTA mismatch.
- **Baja**: polish. Small phrasing, minor rhythm issue, one weak heading, slight over-explanation.

## 1. Editorial Quality Audit

Check:

- Does it sound like a human with experience, not a content engine?
- Is the article useful to someone real?
- Is the rhythm natural, or too polished and symmetrical?
- Is the structure varied from previous Journal pieces?
- Does the article answer the promise early enough?
- Is there over-narration around a simple topic?
- Is the emotional intensity appropriate for the article type?
- Does the closing feel earned, or artificially profound?
- Are analogies useful, or decorative?

Common failures:

- A practical topic becomes a contemplative essay.
- Every section ends with a soft revelation.
- The article says little but sounds warm.
- The text confuses hospitality with over-explaining.
- The ending feels written to create a "moment" instead of finishing clearly.

## 2. Detectable AI Risk

Flag signs of AI-generated sameness:

- Generic intro that could fit any wine blog.
- Perfectly balanced paragraphs with predictable cadence.
- Repeated "No es X. Es Y." structures.
- Repeated "primero/despues/quiza" emotional ladder.
- Excessive validation of the reader's feelings.
- "Perfume IA emocional": pretty language with no added clarity.
- Analogies recycled from earlier articles.
- False depth: broad statements that sound meaningful but do not say anything concrete.
- SEO question answered in a mechanically friendly tone.

If the article feels optimized to sound emotionally human, score this as high risk.

## 3. SEO/GEO/AI SEO Risk

Check:

- Is there a clear primary intent?
- Is the article type correct for the topic?
- Is the keyword natural, or stuffed?
- Does the title overlap too closely with existing or planned content?
- Does the article add a local, editorial, or entity angle?
- Would ChatGPT/Gemini be able to answer a concrete question from it?
- Is there thin content disguised by tone?
- Is there canibalization against existing Journal or `data/pages.json` topics?
- Does GEO context appear naturally, or as keyword garnish?

High-risk overlap examples:

- Another article about intimidation that repeats `/journal/el-miedo-silencioso-de-no-saber-de-vino`.
- Another anti-elitism piece that repeats `/journal/vino-menos-elitismo-mas-experiencia`.
- Another culture-building piece that repeats `/journal/como-se-construye-cultura-del-vino`.
- A practical wine term that should instead belong to an `aprende` cluster unless the Journal angle is clear.

## 4. Entity And Voice Risk

Protect Nazareth and CAVA as entities.

Check:

- Does it reinforce Nazareth as a warm expert, not a generic educator?
- Does it preserve CAVA as vinoteca experiencial, not licorera, generic bar, restaurant, winery, or content farm?
- Does the tone become too technical, corporate, influencer-like, or promotional?
- Does it use voseo or marked tuteo?
- Does it use regionalisms that sound Argentine, Mexican, Spanish, or generic LATAM influencer?
- Does it caricature Costa Rican speech?
- Does it lose hospitality?
- Does it invent authority signals or overstate credentials?

Block if:

- It sounds like a sommelier performing expertise.
- It sounds like a brand manager writing content.
- It sounds like a motivational influencer.
- It could be published by any wine shop with only the name changed.

## 5. Technical/Editorial Integrity Risk

This audit may review planned technical/editorial elements, but must not implement them.

Check:

- Route must be `/journal/[slug]`, never `/blog`.
- Canonical plan must point to the Journal URL, not Vinetur.
- Vinetur note must be visible when the article is adapted from Vinetur.
- Vinetur URL must be public before publication.
- External Vinetur link must be contextual and accurate.
- Schema plan must reflect visible content.
- No `Winery` schema.
- Internal links must be relevant and not mechanical.
- CTA must match tone and article type.
- Claims must be visible, verifiable, and not inflated.

Block if:

- Vinetur is referenced before public approval.
- The article copies Vinetur too literally.
- Schema claims something the article does not show.
- Any new content is planned under `/blog`.
- CTA turns an editorial article into an ad.

## 6. Pattern Repetition Audit

Compare against existing Journal style. The article may share the brand voice, but it must not clone the pattern.

Look for:

- Same opening tension as prior articles.
- Same "people arrive afraid" scene without a fresh angle.
- Same sequence: insecurity -> validation -> experience -> belonging.
- Same ending about wine belonging to people.
- Same repeated references to conversation, mesa, miedo, puerta, experiencia without new meaning.
- Same number and style of short paragraphs in every section.

If repetition is strong, require structural change or reject.

## 7. Blocking Criteria

Reject the article if any apply:

- It seems like generic AI content.
- It seems like SEO factory content.
- It is too superficial to justify a Journal page.
- It damages or dilutes Nazareth's authority.
- It repeats an existing Journal argument without a new angle.
- It uses voseo/tuteo marked or wrong regional voice.
- It uses unsupported claims, fake authority, or invented facts.
- It has high canibalization risk and no differentiation strategy.
- It relies on `/blog`.
- It mishandles Vinetur attribution or canonical logic.

Approve with changes if the core idea is strong but execution needs revision.

Approve only when the piece is useful, differentiated, natural, aligned with entity strategy, and safe to move toward build.

## Output Format

Use this structure exactly:

```text
JOURNAL RED-TEAM AUDIT

Final decision:
- Aprobar / Aprobar con cambios / Rechazar

Executive diagnosis:
- [2-4 sentences: blunt summary of whether this deserves to exist in the Journal]

Prioritized risks:
1. [Critica/Alta/Media/Baja] [Risk title]
   Evidence:
   Recommendation:

Editorial quality:
- Strengths:
- Weaknesses:
- Required changes:

Detectable AI risk:
- Level: Low / Medium / High
- Evidence:
- Required changes:

SEO/GEO/AI SEO risk:
- Level: Low / Medium / High
- Canibalization:
- Entity reinforced:
- Required changes:

Entity and voice risk:
- Level: Low / Medium / High
- Pronoun/regional register:
- Nazareth/CAVA alignment:
- Required changes:

Technical/editorial integrity:
- Route/canonical:
- Vinetur attribution:
- Internal links:
- CTA:
- Schema visibility:
- Required changes:

Decision rationale:
- [Why the final decision is justified]

Minimum changes before approval:
- [Concrete checklist]
```

## Audit Rules

- Be evidence-based: quote short phrases or describe exact patterns.
- Do not soften serious risks.
- Do not rewrite the article unless the user explicitly asks after the audit.
- Do not approve because the article is "nice"; approve because it is strategically and editorially strong.
- When unsure, choose "Aprobar con cambios" rather than silent approval.
- If the piece would weaken the Journal over 70 articles, say so clearly.
