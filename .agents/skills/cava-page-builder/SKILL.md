---
name: cava-page-builder
description: Use this skill when building or editing any HTML/CSS page for cavagourmet.com. Applies CAVA's visual consistency, editorial voice, SEO/GEO standards and production safety rules. Complements the CAVA Luxury Audit Skill defined in the root SKILL.md.
---

# CAVA Page Builder Skill

Use this skill when asked to create, edit, audit or optimize any page
for the CAVA Gourmet website.

This skill is distinct from the root `SKILL.md` (CAVA Luxury Audit Skill),
which focuses on auditing `index.html` and performance hardening.
This skill focuses on **building new pages and content** with semantic,
editorial and conversion architecture.

**Production is live on GitHub Pages. Preserve first. Improve second.**

---

## Relationship with other skills and agents

| Tool | Focus |
|---|---|
| Root `SKILL.md` | Audit index.html, Core Web Vitals, Lighthouse |
| This skill | Build new pages, semantic architecture, editorial copy |
| Red-Team Auditor | Find risks, break things defensively |
| Implementation Engineer | Execute code fixes, debug, performance tuning |
| cava-seo-geo-strategist | SEO/GEO strategy and entity architecture |

When a task touches both performance and new content, coordinate:
use this skill for content/SEO, flag performance concerns for the
Implementation Engineer.

---

## Goal

Build pages that achieve all of:
- Visual consistency with existing cavagourmet.com pages
- SEO / GEO / AI SEO / Entity SEO
- Local SEO for Pérez Zeledón and Zona Sur
- Lighthouse 90+ safe (no added performance debt)
- Human emotional copy in CAVA's editorial voice
- Clear conversion path to WhatsApp or reservation
- Brand moat contribution — something hard to replicate

---

## Step 1 · Inspect before touching anything

This step is mandatory. Do not skip.

```
1.  Read the target file completely
2.  Read index.html fully — it's the visual and code reference
3.  Read at least 2 sibling pages (e.g. nazareth.html, blog.html)
4.  List every CSS class used — reuse before creating new ones
5.  Verify all asset paths with exact casing (Assets/ not assets/)
6.  Copy nav HTML pattern exactly — do not paraphrase or simplify
7.  Copy footer HTML pattern exactly — do not paraphrase or simplify
8.  Note existing schema JSON-LD if present
9.  Note existing internal links
10. Note any JS behavior (scroll effects, lazy load, modals)
11. Check robots.txt — confirm the new URL will be indexable
12. Check sitemap.xml — note if new page needs to be added
```

After inspection, write a brief summary:
- What visual patterns did you find?
- What CSS classes are available?
- What schema is already in use?
- What risks exist for this specific edit?

---

## Step 2 · Define strategy before writing copy

Answer every question before writing a single word of copy:

```
Page purpose:          [one sentence — what does this page do strategically?]
Primary keyword:       [exact phrase the page targets]
Secondary keywords:    [3–5 supporting phrases]
Dominant intent:       [aspirational / anxious / romantic / social /
                        professional / educational / local /
                        transactional / conversational AI]
Emotional tension:     [what does the user fear, want or need?]
CAVA answer:           [how does CAVA specifically resolve that tension?]
Local anchor:          [how does this page connect to Pérez Zeledón/Zona Sur?]
Entity reinforced:     [CAVA / Nazareth / Pérez Zeledón / wine culture CR]
Brand moat:            [what makes this page hard to replicate or outrank?]
Nazareth signal:       [where does her expertise add trust?]
AI query:              [how would someone ask ChatGPT for this page?]
CTA destination:       [WhatsApp link or internal reservation page]
```

---

## Step 3 · Page structure

Use this order for new pages. Adapt and simplify for edits.

```
<head>
  title, meta description, canonical, OG tags, schema JSON-LD

<body>
  Nav            — identical HTML to existing pages
  Hero           — H1 + emotional hook + primary keyword visible
  Entity/Credibility — who is CAVA, where is it, why trust it
                       include Nazareth signal when relevant
  Experience     — what happens, what to expect, what it feels like
  Human/Emotional — why this matters to this specific person
  Educational    — when beginner or learning intent is present
  FAQ            — minimum 4 Q&A, visible, conversational
  CTA            — warm, clear, matched to page intent
  Footer         — identical HTML to existing pages
```

Not every page needs every block.
Remove blocks that don't serve the page intent.
Never add blocks just to fill space.

---

## Step 4 · Copy rules

### Voice

Write copy that feels:
- Elegant and warm — not cold, not corporate
- Editorial — has a point of view
- Sensory — what will the person feel, smell, hear?
- Local — Pérez Zeledón, Zona Sur, Costa Rica, not generic "Costa Rica tourism"
- Premium but approachable — never snob, never exclusionary

### Vocabulary (aligned with AGENTS.md)

Use:
- `criterio experto` (not `curaduría`)
- `selección especializada`
- `dirección enológica` when applicable
- `acompañamiento en selección`

Never use:
- `curaduría` or `curado`
- Generic AI filler ("En el mundo del vino...")
- Unverifiable superlatives ("la mejor", "la única", "inigualable")
- Wine jargon without immediate plain-language explanation
- Paragraphs duplicated from other pages
- Invented statistics, awards or credentials

### Copy calibration

❌ Generic — never write like this:
"Ofrecemos una experiencia única de vino para todos los públicos
en Costa Rica."

✅ CAVA voice — write like this:
"En CAVA, nadie llega sabiendo todo. Llegan curiosos, y eso es suficiente.
Una copa, una conversación y una forma más cercana de descubrir el vino
en el sur de Costa Rica."

### Approved strategic phrases

Use naturally, never force, never repeat more than once per page:
- vino sin miedo
- aprender vino sin sentirse juzgado
- una experiencia alrededor del vino
- hospitality premium relajado
- sofisticación accesible
- el momento después del trabajo
- una pausa elegante en Zona Sur
- más que una botella, una conversación
- descubrir el vino sin pretensiones
- en el sur de Costa Rica

---

## Step 5 · SEO / GEO implementation

### Required in every page `<head>`

```html
<!-- Core SEO -->
<title>[Unique · 50–60 chars · Primary keyword + CAVA Vinoteca]</title>
<meta name="description"
  content="[Unique · 140–160 chars · Intent-driven · No generic filler]">
<link rel="canonical" href="https://www.cavagourmet.com/[slug]/">

<!-- Open Graph -->
<meta property="og:title"
  content="[Same as title or natural variant]">
<meta property="og:description"
  content="[Same as meta description or natural variant]">
<meta property="og:url"
  content="https://www.cavagourmet.com/[slug]/">
<meta property="og:image"
  content="https://www.cavagourmet.com/Assets/images/[relevant-image]">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CR">
<meta property="og:site_name" content="CAVA Vinoteca">
```

### Heading rules

```
H1 — one only, visible, contains primary keyword in natural phrasing
H2 — major sections (2–6 per page)
H3 — subsections within H2
Never skip levels (H1 → H3 without H2 is invalid)
Never use heading tags for visual styling only
```

### Content minimum

400 words of visible, useful content per page.
If a page cannot justify 400 words of real value, it should not be a
separate page — consider adding it as a section to an existing page instead.

---

## Step 6 · Schema JSON-LD rules

Place inside `<script type="application/ld+json">` in `<head>`.
Schema must reflect content visible on the page — never invent data.

### Approved schema types

| Type | When |
|---|---|
| `LocalBusiness` | Main pages, experience pages |
| `WebPage` | General content pages |
| `Article` / `BlogPosting` | Blog posts |
| `FAQPage` | Any page with visible FAQ |
| `Person` | Nazareth pages |
| `Event` | Event announcement pages |
| `Service` | Cata, after office, corporate experience |
| `BreadcrumbList` | All pages below home |

### Prohibited

`Winery` — CAVA does not produce wine. Never use this type.

### CAVA base LocalBusiness data

Use consistently. Do not alter core fields:

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://www.cavagourmet.com/#business",
  "name": "CAVA Gourmet Market",
  "alternateName": "CAVA Vinoteca",
  "url": "https://www.cavagourmet.com",
  "telephone": "+50686325260",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "Pérez Zeledón",
    "addressRegion": "San José",
    "addressCountry": "CR"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 9.3676,
    "longitude": -83.6823
  },
  "description": "Vinoteca experiencial en Pérez Zeledón, Costa Rica. Catas privadas, after office, experiencias sensoriales de vino y hospitalidad premium en Zona Sur.",
  "foundingDate": "2023-05-15",
  "founder": {
    "@type": "Person",
    "name": "Nazareth Padilla Montero"
  }
}
```

### FAQPage schema rule

FAQPage schema must match questions visible on the page exactly.
If a question is in schema but not visible to the user, remove it.
If a question is visible but not in schema, add it.

---

## Step 7 · FAQ construction

FAQs must be:
- Visible to users on the page (never hidden in schema only)
- Written in natural conversational language
- Answerable by ChatGPT or Gemini if someone asks the same question
- Accompanied by FAQPage schema that mirrors them exactly
- Minimum 4 questions per page

**Good FAQ examples:**

Q: ¿Necesito saber de vino para venir a CAVA?
A: No. CAVA está diseñada exactamente para quienes no saben de vino y quieren
descubrirlo sin presión. Nazareth y Erick te acompañan desde el principio,
sin tecnicismos ni juicios.

Q: ¿Qué diferencia hay entre una cata tradicional y una experiencia en CAVA?
A: En una cata tradicional el foco es la técnica. En CAVA, el foco es la
conversación. El vino es la excusa para conectar, no el examen que tienes
que pasar.

---

## Step 8 · CTA rules

Every page needs at least one clear, warm call to action.

### WhatsApp CTA — primary

```html
<a href="https://wa.me/50686325260?text=Hola%20CAVA%2C%20quiero%20reservar"
   target="_blank"
   rel="noopener noreferrer">
  [CTA text matched to page intent]
</a>
```

### CTA copy by intent

| Page intent | CTA copy |
|---|---|
| Romantic | Planear mi noche especial |
| Corporate / B2B | Consultar disponibilidad para mi equipo |
| Gift | Regalar esta experiencia |
| Beginner / Educational | Quiero conocer el vino sin miedo |
| After office | Reservar mi lugar en la mesa |
| Generic | Pedir un lugar en la mesa |

---

## Step 9 · Internal linking

Every page must link to at least 3 internal destinations.

| Destination | When to include |
|---|---|
| `/` | Always |
| `/nazareth/` | When expertise or trust is relevant |
| `/cata-de-vinos-perez-zeledon/` | When booking or experience intent exists |
| `/blog/` | When content is educational or cultural |
| Sibling experience pages | When related commercial intent exists |

Anchor text rules:
- Descriptive and keyword-relevant
- Never: "haz clic aquí", "ver más", "leer aquí"
- Yes: "conoce a Nazareth", "reserva tu cata privada",
  "aprende sobre el vino en CAVA"

---

## Step 10 · Technical validation checklist

Run every item before reporting the task as complete.

```
HTML STRUCTURE
[ ] No duplicate IDs in the page
[ ] No duplicate H1
[ ] Heading levels are sequential (H1 → H2 → H3, no skips)
[ ] All <img> have descriptive alt text
[ ] All <a> have descriptive anchor text (no "click here")
[ ] External links have rel="noopener noreferrer" if target="_blank"
[ ] No inline styles that break existing CSS cascade

GITHUB PAGES SAFETY
[ ] All asset paths use correct casing (Assets/ not assets/)
[ ] All internal links use relative paths
[ ] Canonical uses full production URL (https://www.cavagourmet.com/...)
[ ] New page slug is lowercase with hyphens only
[ ] No spaces or special characters in filenames

SEO
[ ] <title> unique, 50–60 characters
[ ] <meta description> unique, 140–160 characters
[ ] <link rel="canonical"> correct and present
[ ] H1 contains primary keyword
[ ] FAQ section is visible to users
[ ] Minimum 3 internal links present
[ ] Sitemap.xml needs update? (flag for user — do not auto-edit)

SCHEMA
[ ] JSON-LD is syntactically valid
[ ] Schema types match visible page content
[ ] No Winery schema used
[ ] FAQPage schema mirrors visible FAQ questions exactly
[ ] No invented data in schema

ASSETS AND PERFORMANCE
[ ] All image paths resolve correctly (case-sensitive check)
[ ] Hero image has fetchpriority="high" if LCP candidate
[ ] Non-hero images have loading="lazy"
[ ] No new external scripts or stylesheets added
[ ] No layout shifts introduced
[ ] No broken internal or external links

CONVERSION
[ ] CTA is visible without excessive scrolling
[ ] WhatsApp link uses +50686325260
[ ] CTA copy matches page emotional intent

PRODUCTION SAFETY
[ ] Nav HTML is identical to existing pages
[ ] Footer HTML is identical to existing pages
[ ] No global CSS or JS files modified
[ ] No files renamed or moved
[ ] robots.txt not modified
[ ] No commit or push executed
```

---

## Output format

Always produce in this exact order:

```
STRATEGY NOTE
─────────────
Page purpose:      [one sentence]
Primary intent:    [intent type]
Primary keyword:   [exact phrase]
Entity reinforced: [CAVA / Nazareth / Pérez Zeledón / wine culture CR]
Brand moat:        [what makes this page hard to replicate]
AI query answered: [how someone would ask ChatGPT for this]

IMPLEMENTATION
─────────────
[HTML with file path clearly marked]
[CSS additions clearly marked, if any]

POST-IMPLEMENTATION CHECKLIST
─────────────────────────────
[Completed checklist from Step 10 — every item marked]

RISKS AND ASSUMPTIONS
─────────────────────
[Everything uncertain that requires human review before going live]
[Flag if sitemap.xml needs updating]
[Flag any performance concerns for Implementation Engineer]
```

Do not report the task as complete until every section above is present
and the checklist is fully completed.
