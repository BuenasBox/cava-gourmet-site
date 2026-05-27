---
name: content-gap-planner
description: Use this skill to identify which Journal articles or landing pages to build next. Cross-references the keyword cluster registry and the canonical entity roadmap against existing published content, planned pages, and data/pages.json to surface the highest-priority gaps. Outputs a ranked recommendation list with gap type, cluster, intent, canonical slug, and readiness notes. Does not build pages or write copy.
---

# Content Gap Planner

Use this skill to decide what to build next for cavagourmet.com. It does not write articles, generate HTML, or modify site files. Its only output is a ranked content gap report.

---

## Load context first

Before any analysis, read these four sources in order. If any cannot be read, note the failure and proceed with the remaining sources.

**1. Keyword cluster registry:**
```
admin/KeywordResearch_NazarethWineJourney_CAVA_v1.md
```
Extract: all clusters, their primary keywords, KD, intent type, priority flags, and any notes about planned vs. live status.

**2. Canonical entity and execution roadmap:**
```
admin/arquitectura-semantica-canonica.md
```
Extract: the content execution roadmap (phases, priorities, URL patterns), entity targets per phase, and any explicit content gaps named in the document.

**3. Planned page registry:**
```
data/pages.json
```
Extract: every slug, its status (live / planned / draft), and its assigned cluster or topic.

**4. Live Journal index — scan for published slugs:**
```
journal.html
```
Extract: every article slug currently listed as published.

---

## Gap classification

After loading context, classify every cluster entry and roadmap item into one of:

| Gap type | Definition |
|---|---|
| `ausente` | No live page and no entry in data/pages.json. Highest priority to fill. |
| `planificado` | Entry exists in data/pages.json but page is not yet built or published. Needs builder. |
| `borrador` | Draft exists but has not been published. Needs review or completion. |
| `cubierto` | A live, published page covers this cluster adequately. No action needed. |
| `riesgo-canibalizacion` | Two or more planned or live pages target the same query. Needs consolidation before building more. |
| `cluster-sin-hub` | A cluster has spokes (articles) but no hub landing page, or a hub without spokes. Needs structural fix. |

---

## Scoring criteria

Rank uncovered gaps by combining:

1. **Priority flag** from keyword research (P0 → P3, where P0 = highest).
2. **Entity reinforcement value**: does filling this gap strengthen Nazareth, CAVA, or Pérez Zeledón in search and LLMs?
3. **Brand moat contribution**: is this topic hyperlocal, hard to replicate, or tied to verified credentials?
4. **Intent completeness**: is an entire intent type (e.g., anxious beginner, after office professional) without coverage?
5. **Roadmap phase**: Phase 1 gaps outrank Phase 2, which outrank Phase 3.
6. **LLM citation potential**: can an AI model answer a common question by citing this page? If yes, prioritize.

Do not rank by keyword volume alone. A low-volume hyperlocal page that CAVA can own completely ranks above a high-volume generic term CAVA cannot compete for.

---

## Input — optional

The user may optionally provide:

- A cluster name to focus on (e.g., `experiencias`, `nazareth`, `maridaje`).
- A specific intent type to fill (e.g., "anxious beginner", "after office professional").
- A phase from the roadmap to review (e.g., "Phase 1 only").
- A constraint (e.g., "Journal articles only, no landing pages").

If no input is given, analyze all clusters and output the top 5 gaps across the full site.

---

## Cannibalization check

Before recommending any new page, verify:

1. No existing published article or planned page covers the same primary keyword with the same dominant intent.
2. The recommended slug does not conflict with any entry in `data/pages.json`.
3. If two existing planned items target the same query, flag both as `riesgo-canibalizacion` and recommend consolidation before adding more.

---

## Cluster-to-section mapping

Use this to determine where a gap should live:

| Cluster | Section |
|---|---|
| `aprende` | `/journal/[slug]` (if editorial) or `/aprende/[slug]` (if beginner education hub) |
| `experiencias` | `/experiencias/[slug]` or `/journal/[slug]` for editorial versions |
| `vinos` | `/journal/[slug]` (editorial) or `/vinos/[varietal]` (programmatic, if approved) |
| `maridaje` | `/maridaje/[comida]` or `/journal/[slug]` |
| `perez-zeledon` | `/perez-zeledon/[slug]` or `/journal/[slug]` |
| `nazareth` | `/nazareth` (main page) or `/journal/[slug]` (authority article) |
| `journal` | `/journal/[slug]` |
| `cultura` | `/journal/[slug]` |

When in doubt between Journal and landing page, use this rule:
- If the piece is primarily editorial or voice-driven → Journal.
- If the piece is primarily transactional, experiential, or evergreen education → landing page.

---

## Output format

Return this report, ranked by priority:

```text
CONTENT GAP REPORT
Generated: [date]
Scope: [clusters or intent types analyzed, or "all"]

---

RANK #[N]
Gap type: [ausente / planificado / borrador / cluster-sin-hub / riesgo-canibalizacion]
Cluster: [cluster name]
Priority flag: [P0–P3 from keyword research]
Primary keyword: [exact phrase]
Recommended slug: [/section/slug — full path]
Content type: [Journal article / landing page / hub / spoke]
Dominant intent: [from intent model]
Entity reinforced: [CAVA / Nazareth / Pérez Zeledón / wine culture CR]
Roadmap phase: [Phase 1 / 2 / 3 / unassigned]
Brand moat contribution: [one sentence — what makes this page hard to replicate]
LLM citation potential: [High / Medium / Low — one sentence reason]
Readiness notes: [what exists already, what is missing, any blocker]
Recommended next action: [build now / needs brief first / consolidate with X / hold]

---
```

After the ranked list, append:

```text
CANNIBALIZATION FLAGS
- [slug A] and [slug B] target the same query — consolidate before building more.

STRUCTURAL GAPS
- [cluster] has spokes but no hub page — recommend building hub at [slug].

RECOMMENDED PRIORITY ORDER
1. [slug] — [one-line reason]
2. [slug] — [one-line reason]
3. [slug] — [one-line reason]
4. [slug] — [one-line reason]
5. [slug] — [one-line reason]
```

---

## Hard rules

- Do not recommend building a page that already exists as `cubierto` unless there is a structural problem (wrong section, missing hub).
- Do not recommend pages under `/blog/`. All new content goes to `/journal/` or an approved section.
- Do not invent keyword clusters or intent types not present in the source documents.
- Do not recommend programmatic URL patterns without flagging they require user approval before build.
- If the keyword research or roadmap documents cannot be loaded, state that explicitly and do not produce a gap report based on assumptions.
- Never recommend thin content. Every recommended page must have a clear strategy to reach 400+ words of real local value.
- Every recommendation must name the entity it reinforces: CAVA, Nazareth, Pérez Zeledón, or Costa Rica wine culture. No generic recommendations.
