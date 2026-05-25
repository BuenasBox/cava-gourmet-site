---
name: journal-article-builder
description: Use this skill to convert approved CAVA/Nazareth Journal content into a draft journal/[slug].html page for final review, following the existing Journal HTML pattern. It assumes voice, SEO/GEO brief, and initial editorial audit are already approved; it must not invent strategy, publish, update indexes, commit, or push.
---

# Journal Article Builder

## Purpose

Convert an already approved Journal article for CAVA/Nazareth into a review-ready HTML draft at:

```text
journal/[slug].html
```

This skill is a builder, not a strategist. It translates approved editorial and SEO inputs into the existing CAVA Journal page format.

It must preserve the site's current architecture, visual pattern, metadata discipline, schema logic, internal-linking rules, and GitHub Pages stability.

## Boundaries

This skill may produce:

- A complete HTML draft for `journal/[slug].html`.
- A publication checklist.
- A list of files that should be updated after approval.
- A list of risks or blockers detected during build preparation.

This skill must not:

- Redefine the article's voice.
- Invent SEO strategy, keywords, metadata, schema, CTA, or internal links.
- Rewrite the article from scratch.
- Publish automatically.
- Modify `journal.html`.
- Modify `sitemap.xml`.
- Modify `data/pages.json`.
- Modify `llms.txt`.
- Modify any other file unless the user explicitly asks for the article HTML file to be created.
- Commit.
- Push.
- Deploy.

If required inputs are missing, stop and report the missing items instead of filling gaps with generic assumptions.

## Required Inputs

Before building HTML, confirm that these inputs exist:

- Persisted approved brief at `admin/briefs/[slug].md`.
- Approved final or near-final article text.
- Approved slug from `journal-seo-geo`.
- Approved title tag.
- Approved meta description.
- Approved H1.
- Article type.
- Publication date and, if applicable, modified date.
- Author attribution.
- Approved CTA.
- Approved internal links.
- Approved related articles.
- Approved schema plan.
- Image path and alt text, with asset existence verified against `admin/journal-image-inventory.md`.
- Image choice documented in the persisted article brief.
- Initial editorial audit result from `journal-red-team-auditor`.

For Vinetur adaptations, also require:

- Public Vinetur URL.
- Confirmation that the Journal version is adapted and not a literal copy.
- Approved visible note text.
- Approved contextual link placement.
- Approved schema relationship, if any: `citation`, `subjectOf`, or `isBasedOn`.

If the Vinetur article is still pending approval or no public URL exists, do not build the Vinetur-specific final version. Produce only a blocked status or a temporary internal draft note if the user explicitly asks.

## Source Patterns To Follow

Use the existing project pattern, in this priority:

1. `admin/plantilla-articulo.html` as the structural template.
2. `journal/el-miedo-silencioso-de-no-saber-de-vino.html` for Vinetur adaptation pattern, visible origin note, article schema, author entity, breadcrumbs, related articles, and CTA integration.
3. `journal/vino-menos-elitismo-mas-experiencia.html` for standard Journal article structure and internal-linking rhythm.
4. Other `journal/*.html` files only to confirm consistency.
5. `CLAUDE.md` for canonical Journal rules, schema rules, `/blog` restrictions, and hub/spoke requirements.

Preserve the established page system:

- Existing navigation pattern.
- Existing article layout classes.
- Existing author block pattern.
- Existing breadcrumb pattern.
- Existing related article pattern.
- Existing CTA style.
- Existing footer pattern.
- Existing WhatsApp contact pattern where already present in Journal articles.
- Existing script pattern only when it is already part of the article template.

Do not add new dependencies, new tracking scripts, unnecessary JavaScript, or new design systems.

## Mandatory Journal Image Selection And Optimization Gate

This gate is mandatory before building or finalizing any HTML for the Journal. It cannot be skipped, deferred, or assumed complete based on prior conversations.

### Step 1 — Survey available images

Review the following sources in full:

```text
admin/journal-image-inventory.md
Assets/images/
Assets/images/Nazareth/
Assets/images/Erick/
```

Also review any other relevant subcarpetas within `Assets/images/` that may contain suitable editorial images. Do not invent paths — traverse only paths that exist.

### Step 2 — Select the best image

Choose the best available image based on these criteria, in order of priority:

- Editorial relationship with the article topic.
- Not already used as the primary editorial image in another Journal article or site page.
- Coherence with Nazareth / CAVA / Journal visual identity.
- Low risk of overuse or visual repetition across the site.
- Potential for OG crop at 1200×630 without losing the primary subject (face, glass, bottle, element).
- File weight and orientation appropriate for responsive web use.

Do not use image placeholders. Do not invent image paths from naming patterns. Do not use remote images unless explicitly approved in the brief.

### Step 3 — Verify current usage

Before finalizing selection, search the candidate image path in:

```text
index.html
nazareth.html
journal.html
journal/*.html
sitemap.xml
llms.txt
```

If the image appears in a high-prominence position (hero, OG, featured card) in more than one existing page, flag it as overused and select an alternative. Report the conflict if no alternative is available.

### Step 4 — Create optimized derivatives if missing

If the selected image does not have all required derivatives, create them before proceeding.

Required derivatives:

| Variant | Format | Dimensions | Target weight |
|---------|--------|------------|---------------|
| 480w    | WebP   | 480px wide | < 70 KB       |
| 800w    | WebP   | 800px wide | < 140 KB      |
| 1280w   | WebP   | 1280px wide | < 260 KB     |
| OG      | JPG    | 1200×630   | < 350 KB      |

Recommended encoding parameters:

- WebP quality: 72–78
- JPG OG quality: 78–82
- Preserve the primary subject (face, glass, bottle, editorial element) visible and unclipped in all crops and at all widths.
- File naming must follow exact case-sensitive conventions of the existing `Assets/images/[subfolder]/` directory.

If derivatives cannot be created in the current session, document the gap, report a performance risk, and keep the article at `noindex,nofollow` until resolved.

### Step 5 — Document the image

After selection and optimization, record in both locations before proceeding to HTML:

- `admin/journal-image-inventory.md`: image path, dimensions, all derivative paths, weight per variant, usage status, OG suitability, and assigned article slug.
- `admin/briefs/[slug].md`: selected image path, alt text, OG image path, all derivative paths, and optimization status.

### Step 6 — Block conditions

Stop and report a blocker if any of these conditions are met:

- The image file does not exist at the exact case-sensitive path.
- The image path is a placeholder or was invented from a naming pattern.
- No OG derivative exists and cannot be created in the current session.
- WebP derivatives are missing and no performance risk note is documented.
- The image is already used as the primary editorial image in another Journal article or in the `index.html` hero or OG position.
- The image is not documented in `admin/journal-image-inventory.md`.
- The image is not documented in `admin/briefs/[slug].md`.
- Image paths were not verified for GitHub Pages case-sensitivity.

Do not build publishable HTML when any block condition is active. Keep `noindex,nofollow` and list the unresolved blockers in the build output.

### Step 7 — Integrate into draft HTML

The builder may modify the draft HTML to integrate the optimized image:

- Use a `<picture>` element with `srcset` pointing to the WebP derivatives when all variants are available.
- Use `<img>` with correct `src`, `alt`, `width`, `height`, and `loading="lazy"` (or `eager` for the article hero image).
- Set `og:image` to the OG derivative path.

The builder must not — as part of this gate or at any other point during the build phase — take any of these publication actions without an explicit user-approved publication phase:

- Change `meta robots` from `noindex` to `index`.
- Modify `journal.html`.
- Modify `sitemap.xml`.
- Modify `data/pages.json`.
- Modify `llms.txt`.

If the inventory is missing, stale, or does not include a suitable image, stop and report a blocker instead of building publishable HTML.

## Article Type Handling

### Journal Original

Use when the article was created first for CAVA/Nazareth.

Rules:

- Canonical points to `https://www.cavagourmet.com/journal/[slug]`.
- No Vinetur origin note.
- Schema uses `BlogPosting` or the approved equivalent from the SEO/GEO brief.
- Strengthen the Journal hub through `isPartOf` when consistent with the existing pattern.
- Include internal links recommended by the brief.

### Vinetur Adaptation

Use when the article was originally published in Vinetur and later adapted for the CAVA Journal.

Rules:

- Canonical must still point to the CAVA Journal URL:

```text
https://www.cavagourmet.com/journal/[slug]
```

- Include a visible note:

```text
Publicado originalmente en Vinetur
```

- Include a contextual link to the public Vinetur URL.
- Do not point canonical to Vinetur.
- Do not paste a literal duplicate if the brief requires adaptation.
- Reflect the Vinetur relationship only when visible and approved.
- Use `citation`, `subjectOf`, or `isBasedOn` only if the schema plan calls for it and the visible article supports it.
- If there is no public Vinetur URL, block the final Vinetur build.

### Evergreen Article

Use for practical or educational search-driven articles.

Rules:

- Keep the structure clear and useful.
- Do not overbuild HTML just because the article targets SEO.
- Include FAQ schema only if the questions and answers are visible in the article and approved in the brief.
- Internal links should feel contextual, not forced.
- CTA should be helpful and aligned with reader intent.

### Nazareth Entity Article

Use when the article reinforces Nazareth Padilla Montero as a named authority.

Rules:

- Make entity references visible in the page content or author block.
- Use Person/entity schema only when consistent with the approved schema plan and existing site pattern.
- Do not invent credentials, publications, awards, roles, or external references.
- Avoid corporate self-promotion; preserve editorial authority.

### Local Costa Rica / Perez Zeledon Article

Use when local relevance is part of the article strategy.

Rules:

- Local references must appear naturally in visible content.
- Do not stuff "Costa Rica", "Perez Zeledon", or related terms.
- Use local internal links only when they help the reader.
- Keep the local signal precise, not decorative.

## Required HTML Integrations

The HTML draft must integrate, when approved in the brief:

- `<title>`.
- Meta description.
- Robots meta decision.
- Canonical URL.
- Open Graph tags.
- Twitter/X card tags.
- Article date metadata.
- Author metadata.
- Breadcrumbs.
- H1.
- Article category.
- Main article body.
- Verified image asset and alt text.
- Contextual internal links.
- Approved CTA.
- Related articles.
- JSON-LD schema.

All metadata must describe the visible article. If title, description, OG, schema, H1, and visible content drift apart, stop and report a blocker.

## Robots Handling

For a review draft, do not silently make the article indexable.

Use one of these paths:

- If the user asks only for an internal draft, keep `noindex,nofollow` and flag it in the publication checklist.
- If the user asks for a publication-ready HTML draft and the article has final approval, use the approved robots value from the brief.
- If robots status is unclear, stop and ask for confirmation or mark it as a risk.

Before publication, the checklist must explicitly confirm whether robots should be changed to `index,follow`.

## Canonical Rules

Canonical must be:

```text
https://www.cavagourmet.com/journal/[slug]
```

Block the build if:

- Canonical points to `/blog`.
- Canonical points to Vinetur.
- Canonical uses a different slug than the file path.
- Canonical uses a non-production domain.
- Canonical conflicts with `og:url`.

## Open Graph And Image Rules

OG tags must match the approved article:

- `og:title` aligns with title/H1 strategy.
- `og:description` aligns with meta description.
- `og:url` matches canonical.
- `og:image` uses an existing image asset validated in `admin/journal-image-inventory.md`.
- Image path case must be valid for GitHub Pages.

Block or flag if:

- The image file does not exist.
- The image path uses wrong case.
- The OG image is unrelated to the article.
- The article depends on a remote image that is not approved.

## Schema Rules

Schema must reflect visible content only.

Allowed schema should follow the approved `journal-seo-geo` plan and existing Journal patterns, typically:

- `BlogPosting`.
- `BreadcrumbList`.
- `WebPage`, if present in the existing pattern.
- `Person`, when Nazareth is visibly part of the article/author entity.
- `Organization`, when consistent with existing site pattern.
- `FAQPage`, only if visible FAQ content exists.

Never use:

- `Winery`.
- Schema that describes content not visible on the page.
- Vinetur relationships not visible or not approved.
- Fabricated credentials, awards, ratings, or publication claims.

For Vinetur adaptations, `citation`, `subjectOf`, or `isBasedOn` may be used only when:

- The Vinetur URL is public.
- The visible article includes the origin note or contextual reference.
- The SEO/GEO brief approves that relationship.

## Internal Links And Related Articles

Use only approved links from the SEO/GEO brief, unless the user explicitly asks for suggestions.

Minimum pattern to preserve:

- Link back to `/journal`.
- Include two related Journal links when available.
- Include at least one relevant non-Journal internal link when the brief supports it, such as:
  - `/cata-de-vinos-perez-zeledon`
  - `/nazareth`
  - `/after-office-vino-perez-zeledon`

Do not force links that interrupt the article or feel promotional.

Never create or reference `/blog` routes.

## CTA Rules

The CTA must match the article's intent and tone.

Use the approved CTA from the SEO/GEO brief. Do not invent a new conversion angle.

The CTA may point to:

- Wine tasting experiences.
- Nazareth authority/profile page.
- Journal hub.
- Relevant CAVA service page.
- WhatsApp contact, if consistent with the existing article pattern.

Avoid CTAs that sound generic, urgent, loud, or unrelated to the article.

## Blockers

Stop and report blockers if any of these appear:

- Missing approved SEO/GEO brief.
- Missing persisted brief at `admin/briefs/[slug].md`.
- Missing final article text.
- Missing approved slug.
- Missing title tag or meta description.
- Image Selection And Optimization Gate not completed.
- Missing or unverified image asset (file does not exist at the exact case-sensitive path).
- Image path is a placeholder or was invented from a naming pattern.
- `Assets/images/` and relevant subcarpetas were not surveyed.
- Image usage was not verified in index.html, nazareth.html, journal.html, journal/*.html, sitemap.xml, llms.txt.
- Image is overused across existing pages.
- OG image (1200×630 JPG) does not exist and cannot be created.
- WebP derivatives are missing and performance risk is not documented.
- Selected image is not documented in `admin/journal-image-inventory.md`.
- Selected image is not documented in the article brief.
- Image paths not verified for GitHub Pages case-sensitivity.
- Missing public Vinetur URL for a Vinetur adaptation.
- Article is a literal duplicate of Vinetur when adaptation is required.
- Canonical does not match `/journal/[slug]`.
- Any `/blog` route appears.
- Metadata contradicts visible content.
- Schema describes invisible content.
- `Winery` schema appears.
- OG image is broken or unverified.
- HTML adds unnecessary complexity.
- New JavaScript is introduced without a clear existing pattern.
- New dependency is introduced.
- Article has not passed initial editorial audit.

## Build Checklist

Before producing the final HTML draft, verify:

- File path is `journal/[slug].html`.
- Slug matches canonical and `og:url`.
- Title, H1, meta description, and OG title are consistent.
- Robots status is intentional.
- Breadcrumbs follow Inicio -> Journal -> Article.
- Article date and modified date are correct.
- Author attribution is correct.
- Image Selection And Optimization Gate completed (all 7 steps).
- `Assets/images/` and relevant subcarpetas were surveyed.
- Image usage was verified in index.html, nazareth.html, journal.html, journal/*.html, sitemap.xml, llms.txt.
- `admin/journal-image-inventory.md` has been reviewed and updated.
- Image asset exists, uses exact case-sensitive path, and alt text is useful.
- All required WebP derivatives exist (480w, 800w, 1280w) or performance risk is documented.
- OG image (1200×630 JPG) exists and is under 350 KB.
- Image choice and all derivative paths are documented in `admin/briefs/[slug].md`.
- JSON-LD is valid JSON.
- Schema claims are visible on page.
- No `/blog` references exist.
- No `Winery` schema exists.
- Internal links are approved and valid.
- Related articles exist.
- CTA is contextual.
- Vinetur note appears when required.
- Vinetur link appears when required.
- No final index files are modified automatically.

## Output Format

When using this skill, respond in this structure:

````text
JOURNAL ARTICLE BUILD

File to create:
- journal/[slug].html

Status:
- Draft for review | Ready for final editorial audit | Blocked

Image gate summary:
- Image selected: [path]
- Derivatives: 480w [status] | 800w [status] | 1280w [status] | OG [status]
- Usage verified in: index.html, nazareth.html, journal.html, journal/*.html, sitemap.xml, llms.txt
- Inventory updated: admin/journal-image-inventory.md [yes/no/blocker]
- Brief updated: admin/briefs/[slug].md [yes/no/blocker]
- Image gate: PASSED | BLOCKED — [reason]

HTML draft:
```html
...
```

Publication checklist:
- [ ] Confirm robots value before publication
- [ ] Validate canonical and og:url
- [ ] Validate schema JSON-LD
- [ ] Confirm all image derivatives exist at documented paths (case-sensitive)
- [ ] Confirm OG image exists and is under 350 KB
- [ ] Confirm selected image is documented in admin/journal-image-inventory.md
- [ ] Confirm selected image is documented in admin/briefs/[slug].md
- [ ] Confirm internal links
- [ ] Run final red-team editorial audit

Files that should be updated manually after approval:
- journal.html: add article card and Journal hub reference
- sitemap.xml: add article URL, lastmod, and image if applicable
- data/pages.json: add or update page registry entry
- llms.txt: add only if the article strengthens entity/authority value

Risks detected:
- ...

Assumptions:
- ...
````

If the user asks to create the HTML file, create only `journal/[slug].html` unless they explicitly authorize additional files.

## Final Reminder

This skill exists to protect the pipeline:

```text
nazareth-editorial-voice -> journal-seo-geo -> journal-red-team-auditor -> journal-article-builder -> final review -> manual publication updates
```

Do not collapse these steps. The builder is the conversion layer, not the editorial brain, SEO strategist, publisher, or deployment agent.
