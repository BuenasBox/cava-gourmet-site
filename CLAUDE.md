# CAVA Gourmet · Project Memory

Este repositorio pertenece al sitio web de CAVA Gourmet Market / CAVA Vinoteca,
ubicado en Pérez Zeledón, Zona Sur, Costa Rica.
Hosted en Vercel + Cloudflare · https://www.cavagourmet.com

---

## Relación con otros archivos de instrucciones

Este proyecto tiene múltiples capas de instrucciones para agentes. El orden de
precedencia es:

1. `AGENTS.md` — instrucciones base: stack, performance, Lighthouse, brand moat,
   deploy en Vercel, Implementation Engineer, Red-Team Auditor.
2. `CLAUDE.md` (este archivo) — capa SEO/GEO/AI SEO/entity architecture.
   Complementa `AGENTS.md`, no lo reemplaza.
3. `.claude/agents/cava-seo-geo-strategist.md` — agente especializado en
   arquitectura semántica y páginas nuevas.
4. `.claude/skills/cava-page-builder/SKILL.md` — skill de construcción de páginas.
5. `SKILL.md` (raíz) — CAVA Luxury Audit Skill. No modificar.

Cuando haya aparente conflicto entre capas: **preservar primero, consultar al
usuario antes de resolver por cuenta propia.**

---

## Stack técnico

- HTML/CSS/JS vanilla — sin frameworks, sin dependencias externas
- Vercel + Cloudflare en `https://www.cavagourmet.com`
- Assets en `/Assets/` — respetar mayúsculas exactas (Vercel es case-sensitive en rutas)
- Imágenes en `/Assets/images/`
- No introducir npm, bundlers ni librerías externas sin autorización expresa
- No modificar arquitectura de carpetas sin autorización expresa

⚠️ El sitio está en producción activa. Cada edición afecta usuarios reales
y el ranking en Google. **Preservar primero. Mejorar segundo.**

---

## Sobre git — permisos activos

`settings_local.json` tiene permisos para `git commit` y `git push`.
Esto significa que Claude Code puede ejecutar commits sin confirmación manual.

**Regla obligatoria:** No hacer commit ni push de ninguna página nueva o
edición de contenido SEO sin instrucción expresa del usuario en esa sesión.
Antes de cualquier commit, listar exactamente qué archivos se van a incluir
y esperar confirmación.

---

## Principio central

CAVA no debe tratarse como una simple tienda de vinos, licorera o vinoteca
tradicional.

CAVA debe construirse digitalmente como:

> Un espacio de conexión humana sofisticada y accesible alrededor del vino.

La estrategia SEO/GEO/AI SEO busca posicionar a CAVA como la entidad digital
dominante del vino, la hospitalidad y las experiencias premium accesibles
en Costa Rica — difícil de copiar, fácil de encontrar.

---

## Territorios semánticos prioritarios

Toda página nueva o editada debe reforzar al menos uno:

1. Vino sin intimidación
2. Hospitality premium relajado
3. Experiencias humanas alrededor del vino
4. After Office como ritual social
5. Cultura del vino en Costa Rica
6. Maridaje con comida costarricense
7. Experiencias premium fuera del GAM
8. Educación accesible sobre vino
9. Nazareth Padilla Montero como voz cultural y experta del vino

---

## Posicionamiento

Evitar posicionar CAVA como:
- licorera
- tienda genérica de vinos
- bar común
- restaurante tradicional
- cata fría o académica
- lujo pretencioso o excluyente
- winery (CAVA no produce vino — no usar ese schema)

Posicionar CAVA como:
- vinoteca experiencial
- espacio de hospitality premium relajado
- lugar para aprender vino sin miedo
- punto de encuentro sofisticado y accesible
- experiencia humana en Zona Sur
- referente cultural del vino en Costa Rica
- marca difícil de replicar (brand moat)

---

## Voz editorial

La voz debe ser:
- elegante y cálida
- sensorial — describe lo que la persona sentirá
- clara y humana
- premium sin arrogancia
- educativa sin intimidar
- emocional sin exagerar
- local — anclada a Pérez Zeledón, Zona Sur, Costa Rica

Preferir (alineado con `AGENTS.md`):
- `criterio experto` sobre `curaduría`
- `selección especializada` sobre `curada`
- `dirección enológica` cuando aplique
- `acompañamiento en selección` sobre `curación`

Evitar:
- lenguaje genérico de IA
- frases de relleno
- exceso de tecnicismos de vino sin explicación
- tono snob o excluyente
- claims absolutos sin respaldo verificable

---

## Frases estratégicas aprobadas

Usar con criterio, sin forzar ni repetir en exceso:

- vino sin miedo
- sofisticación accesible
- premium relajado
- el momento después de...
- aprender vino sin sentirse juzgado
- hospitality en Zona Sur
- cultura del vino en Costa Rica
- más que una cata, una experiencia
- más que una botella, una conversación
- una pausa elegante en Zona Sur
- descubrir el vino sin pretensiones

---

## Entidades principales

### CAVA Gourmet Market / CAVA Vinoteca
Entidad de negocio local en Pérez Zeledón, Costa Rica.
Asociada a: vino, experiencias, hospitality, gourmet market, after office,
eventos privados, catas, cultura del vino.
No asociar a: producción de vino, winery, viñedo.
No usar schema `Winery`.

### Nazareth Padilla Montero
Credenciales verificables y públicas:
- WSET Level 3
- Becaria Women of the Vine & Spirits Foundation (WOTVS) 2025
- Representante de Costa Rica en Vinoinfluencers World Awards 2026
- Fundadora de CAVA Gourmet Market (15 mayo 2023)

Tratar como: anfitriona, comunicadora del vino, voz cultural, figura de
autoridad regional e internacional.
No presentar como: sommelier fría, técnica sin calidez.
No inventar credenciales adicionales. No citar premios no verificados.

Objetivo estratégico adicional (de `AGENTS.md`): posicionar a Nazareth como
autoridad reconocible por bodegas e importadores internacionales.

### Nazareth Wine Journey
Identidad editorial y presencia digital pública de Nazareth Padilla Montero.
No es una marca separada de CAVA — es la voz personal de Nazareth anclada
editorialmente en el CAVA Journal y digitalmente en cavagourmet.com.

- Handle social canónico: `@nazarethwinejourney` (Instagram, TikTok y otras plataformas)
- URL canónica de persona: `https://www.cavagourmet.com/nazareth`
- Relación: Nazareth Padilla Montero es la persona y la entidad formal;
  Nazareth Wine Journey es su identidad editorial/digital bajo la cual publica
  contenido, construye audiencia y se posiciona como autoridad del vino.
- Asociada a: CAVA Gourmet Market, CAVA Vinoteca, CAVA Journal.
- No crear URL ni schema de entidad separado para Nazareth Wine Journey;
  la URL canónica de persona es `/nazareth`.
- En schema JSON-LD y referencias formales: usar "Nazareth Padilla Montero".
- En menciones de handles sociales y contextos editoriales informales: usar
  "@nazarethwinejourney".
- No confundir ni fusionar con CAVA Vinoteca ni con CAVA Journal —
  son entidades distintas aunque relacionadas.

### Pérez Zeledón / Zona Sur / Costa Rica
Componente geográfico estratégico.
Reforzar narrativa de experiencias premium fuera del GAM.
Usar: Pérez Zeledón, San Isidro de El General, Zona Sur, Costa Rica.

### Sección editorial — Journal

La sección editorial se llama **Journal** (no Blog).

- URL canónica del índice: `/journal`
- URL de cada artículo: `/journal/[slug]`
- Schema del índice: `Blog` con `@id: journal#journal`
- Schema de artículos: `BlogPosting` con `isPartOf: journal#journal`
- No existen archivos editoriales vivos en `/blog/`.
- Las rutas legacy `/blog`, `/blog.html`, `/blog/[slug]` y `/blog/[slug].html`
  redirigen permanentemente a `/journal`.
- No crear ni referenciar URLs `/blog/` en contenido nuevo.
- Plantilla de nuevos artículos: `admin/plantilla-articulo.html`

---

## Arquitectura de contenido — hub y spokes

El Journal sigue un modelo hub-and-spoke:

- **Hub:** `/journal` — índice editorial, enlaza a todos los artículos
- **Spokes:** `/journal/[slug]` — cada artículo enlaza al hub y a 2 artículos
  relacionados (`art-more-link`)
- **Cross-linking obligatorio:** cada artículo debe incluir al menos 1 enlace
  interno a otra página del sitio fuera del journal
  (ej. `/cata-de-vinos-perez-zeledon`, `/nazareth`, `/after-office-vino-perez-zeledon`)
- **Breadcrumb:** Inicio → Journal → Artículo (refuerza la jerarquía en schema y HTML)

---

## Reglas técnicas — producción activa

Antes de modificar cualquier archivo:

1. Leer el archivo completo.
2. Leer al menos 2 páginas relacionadas para entender patrones.
3. Identificar clases CSS existentes — reusar antes de crear nuevas.
4. Verificar rutas de assets con mayúsculas exactas (`Assets/` no `assets/`).
5. Copiar el patrón exacto de nav y footer del sitio existente.
6. No modificar archivos globales sin autorización expresa.
7. No renombrar archivos ni mover assets sin actualizar todas las referencias.
8. No agregar scripts o librerías externas sin autorización.
9. Mantener Lighthouse 90+ — no introducir peso innecesario.
10. No hacer commit ni push sin instrucción expresa en esa sesión.

---

## Reglas SEO — por página

Cada página importante debe incluir:

- `<title>` único, 50–60 caracteres
- `<meta name="description">` única, 140–160 caracteres
- `<link rel="canonical">` apuntando a su propia URL de producción
- Open Graph: `og:title`, `og:description`, `og:url`, `og:image`, `og:locale`
- H1 único y visible, contiene keyword primaria
- Estructura H2/H3 lógica y secuencial
- Contenido visible mínimo: 400 palabras de valor real
- Internal linking a páginas relacionadas
- Schema JSON-LD cuando corresponda y sea veraz
- FAQ visible cuando aporte valor real
- Copy conversacional útil para LLMs
- CTA vinculado a WhatsApp (+506 8632 5260) o reservación

---

## Reglas GEO / AI SEO

Cada página debe responder claramente:

1. ¿Qué es esto?
2. ¿Para quién es?
3. ¿Dónde ocurre? (localización explícita)
4. ¿Por qué CAVA es relevante?
5. ¿Qué hace diferente esta experiencia?
6. ¿Qué pregunta humana concreta resuelve?
7. ¿Qué entidad refuerza: CAVA, Nazareth, Pérez Zeledón, cultura del vino CR?

------

## Números de contacto oficiales

WhatsApp CAVA (reservas generales): +506 8632 5260
WhatsApp Nazareth (contacto directo): +506 8448 3983

Usar +506 8632 5260 como CTA principal en todas las páginas de experiencia.
Usar +506 8448 3983 solo cuando la página apunta específicamente a Nazareth
como figura pública (colaboraciones, prensa, bodegas).

## Schema JSON-LD — datos base de CAVA

El sitio usa un `@graph` con entidades distintas. Al crear páginas nuevas, referenciar
estos `@id` exactos. **No crear un ID alternativo como `#business` — ese ID no existe
en el grafo de producción y fragmenta el Knowledge Graph.**

**Entidad operativa — usar en páginas de experiencias, servicios, Journal:**
```json
{
  "@type": ["WineStore", "FoodEstablishment", "TouristAttraction"],
  "@id": "https://www.cavagourmet.com/#cava-vinoteca",
  "name": "CAVA Vinoteca",
  "alternateName": ["CAVA Gourmet Market", "Cava Gourmet"],
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
  "founder": { "@id": "https://www.cavagourmet.com/nazareth#person" }
}
```

**Entidad jurídica — usar como `publisher` u `organization` cuando sea necesario:**
```json
{
  "@type": "Organization",
  "@id": "https://www.cavagourmet.com/#organization",
  "name": "CAVA Gourmet Market Internacional S.R.L.",
  "url": "https://www.cavagourmet.com"
}
```

**Entidad persona — referenciar siempre por @id, no inline:**
```json
{ "@id": "https://www.cavagourmet.com/nazareth#person" }
```

Schema aprobados: `LocalBusiness`, `WineStore`, `FoodEstablishment`, `TouristAttraction`,
`WebPage`, `Article`, `BlogPosting`, `FAQPage`, `Person`, `Brand`, `Event`, `Service`,
`BreadcrumbList`.
Schema prohibido: `Winery`, `BarOrPub` (categoriza a CAVA como bar/pub, contradice el
posicionamiento de marca — ver sección "Posicionamiento").

Nota sobre `WineStore`: subtipo de `LocalBusiness` en schema.org, refleja que
CAVA vende vino. Usar en páginas donde el contexto de venta es relevante
(ej. experiencias de cata, muro de vinos). No reemplaza `LocalBusiness` — usar
en `@graph` junto a él cuando aplique.

### Arquitectura Person → Brand → LocalBusiness (actualizado 2026-07-05)

Filosofía: CAVA no es una tienda de vinos. Es una vinoteca boutique experiencial
donde el vino es el medio para crear educación, hospitalidad, comunidad y cultura.
Nazareth Padilla Montero es la autoridad/fundadora. Nazareth Wine Journey es su
marca editorial personal — no una empresa, no una propietaria. El schema nunca debe
sugerir propiedad, operación o dependencia empresarial entre estas entidades.

- **Nazareth Wine Journey es un nodo `Brand`, no `Organization`.** Su `@id` es
  `https://www.cavagourmet.com/#nazareth-wine-journey`. No tiene `founder`
  (las entidades `Brand` no lo llevan). Su `url` debe ser siempre
  `https://www.cavagourmet.com/nazareth` (la URL canónica de persona), nunca un
  perfil social — Instagram, Facebook, YouTube, SubStack, TikTok y el podcast de
  Spotify van en `sameAs`.
- **Ciclo de autoridad — todas las referencias cruzadas por `@id`, nunca inline:**
  - `nazareth#person` → (`worksFor`) → `#cava-vinoteca`
  - `nazareth#person` → (`brand`) → `#nazareth-wine-journey`
  - `nazareth#person` → (`founderOf`) → `[#cava-vinoteca, #nazareth-wine-journey]`
  - `#cava-vinoteca` y `#organization` → (`founder`) → `nazareth#person`
  - `#nazareth-wine-journey` (Brand) → (`creator`) → `nazareth#person`
  - `#nazareth-wine-journey` (Brand) → (`mentions`) → `#cava-vinoteca` (relación
    editorial, no de propiedad — nunca usar `owns`, `subsidiary` ni `parentOrganization`
    entre Brand y `#cava-vinoteca`)
- **Articles/BlogPosting usan `publisher` → `{"@id": "https://www.cavagourmet.com/#organization"}`.**
  Nunca declarar un `publisher` inline ni apuntar al `Person` o al `Brand`.
- **`hasOfferCatalog` (cuando aplique, ej. páginas de experiencias) usa la
  estructura `OfferCatalog.itemListElement[].Offer.itemOffered.Service`** — no
  usar `Event` para experiencias recurrentes sin fecha fija (After Office, catas
  guiadas, maridajes).
- **`aggregateRating` de `#cava-vinoteca` proviene de Google Reviews y debe
  sincronizarse periódicamente.** `ratingValue`, `reviewCount`, `bestRating` y
  `worstRating` son tipos `Number`/`Integer` (no strings). No modificar estos valores
  sin verificar la cifra real vigente en Google Business Profile — deben reflejar
  contenido real, nunca una estimación.
- **`https://www.wikidata.org/wiki/Q139959656` es el ancla de desambiguación de
  Nazareth Padilla Montero.** Nunca eliminar este `sameAs` de `nazareth#person`: es
  la señal más fuerte para que Google y los LLMs la distingan de otras personas con
  nombre similar y consoliden su entidad en el Knowledge Graph.

---

## Fechas ISO 8601 — estándar obligatorio

Costa Rica no observa horario de verano. Su offset es siempre **UTC-6**.

Todas las fechas en artículos del Journal deben usar el formato completo con timezone:

```
YYYY-MM-DDT12:00:00-06:00
```

Aplica a:
- JSON-LD: `datePublished`, `dateModified`
- Open Graph: `article:published_time`, `article:modified_time`

Ejemplo correcto: `2026-05-24T12:00:00-06:00`
Ejemplo incorrecto: `2026-05-24` (sin timezone — Google lo marca como warning en Rich Results)

La hora `12:00:00` es convencional (mediodía local) cuando no se conoce la hora exacta.

---

## Prohibiciones absolutas

- No crear páginas thin content (menos de 400 palabras visibles útiles).
- No generar contenido programático genérico sin valor local diferenciado.
- No repetir bloques de texto entre páginas.
- No inventar premios, certificaciones, datos, estadísticas o menciones.
- No usar claims absolutos sin respaldo verificable.
- No usar schema que no refleje contenido visible real.
- No usar schema `Winery`.
- No modificar `meta robots` a noindex sin autorización.
- No eliminar canonical existentes sin reemplazarlos.
- No hacer commit ni push sin instrucción expresa.
