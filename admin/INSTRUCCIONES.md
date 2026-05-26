# Cómo publicar un nuevo artículo en el blog de CavaGourmet

Este documento explica, paso a paso, cómo agregar un nuevo artículo al blog sin necesidad de saber programación. Solo necesitas seguir el orden.

---

## Lo que necesitas antes de empezar

1. El texto del artículo listo y revisado.
2. Una imagen de portada en formato `.webp` con tres tamaños: 480px, 800px y 1280px de ancho. (El desarrollador puede ayudarte a generar estos tamaños desde una sola imagen.)
3. Acceso al repositorio del sitio (si lo administras tú) o acceso para enviar los archivos al desarrollador.

---

## Paso 1 — Prepara los datos del artículo

Antes de tocar el código, define estos datos. Los necesitarás para llenar la plantilla:

| Campo | Ejemplo |
|---|---|
| **TITLE** | Por qué el vino necesita menos elitismo |
| **SLUG** | vino-menos-elitismo (sin tildes, sin espacios, con guiones) |
| **CATEGORY** | Educación y experiencia |
| **DATE** | Junio 2026 |
| **SEO TITLE** | Por qué el vino necesita menos elitismo \| CavaGourmet |
| **META DESCRIPTION** | Máximo 155 caracteres. Describe de qué trata el artículo. |
| **KEYWORDS** | palabras clave separadas por coma |
| **EXCERPT** | Una o dos frases cortas. Aparece en la tarjeta del blog. |
| **OG TITLE** | Igual al título o una variación para redes sociales |
| **OG DESCRIPTION** | Una frase llamativa para compartir en redes |
| **IMAGEN** | Nombre base de la imagen, sin tamaño ni extensión (ej: `07-cava-nueva-imagen`) |

**Nota sobre el SLUG:** debe ser en minúsculas, sin tildes, sin espacios. Los espacios se reemplazan con guiones. Ejemplo: "Cómo elegir un vino" → `como-elegir-un-vino`

---

## Paso 2 — Copia la plantilla

1. Ve a la carpeta `admin/` del sitio.
2. Copia el archivo `plantilla-articulo.html`.
3. Renombra la copia con el SLUG del artículo: `[SLUG].html`
   - Ejemplo: `como-elegir-un-vino.html`
4. Abre el archivo copiado en un editor de texto (Notepad, VS Code, o similar).

---

## Paso 3 — Llena los datos del encabezado (head)

Al inicio del archivo verás bloques con `[CORCHETES]`. Reemplaza cada uno:

- `[SEO TITLE]` → El título SEO que definiste
- `[META DESCRIPTION — máximo 155 caracteres]` → Tu descripción
- `[KEYWORDS separados por coma]` → Tus palabras clave
- `[SLUG]` → El slug del artículo (aparece varias veces — cámbialos todos)
- `[IMAGEN]` → El nombre base de la imagen (sin tamaño ni extensión)
- `[OG TITLE]` → Título para redes sociales
- `[OG DESCRIPTION]` → Descripción para redes
- `[FECHA en formato YYYY-MM-DD]` → Ejemplo: `2026-06-15`
- `[CATEGORY]` → La categoría del artículo
- `[TITLE]` → El título completo del artículo

---

## Paso 4 — Llena el contenido visible del artículo

Busca la sección marcada con el comentario:
```
<!-- ENCABEZADO DEL ARTÍCULO -->
```

Ahí reemplaza:
- `[CATEGORÍA — ej: Cultura del vino]` → Tu categoría
- `[TÍTULO DEL ARTÍCULO]` → El título completo
- `[MES AÑO — ej: Mayo 2026]` → La fecha de publicación

Luego busca:
```
<!-- IMAGEN DE PORTADA -->
```

Reemplaza `[IMAGEN]` con el nombre base de tu imagen (en los tres lugares donde aparece).
Reemplaza `[Descripción de la imagen para lectores de pantalla]` con una descripción breve de la foto.

---

## Paso 5 — Escribe el contenido del artículo

Busca la sección marcada con:
```
<!-- CUERPO DEL ARTÍCULO -->
```

Aquí es donde va el texto. Usa estas reglas:

**Párrafo normal:**
```html
<p>Texto del párrafo aquí.</p>
```

**Subtítulo de sección:**
```html
<h2>Título de la sección</h2>
```

**Frase destacada (cita o frase impactante):**
```html
<p class="art-quote">"La frase que quieres resaltar."</p>
```

Agrega todos los párrafos que necesites. Cada pensamiento separado va en su propio `<p>`.

---

## Paso 6 — Actualiza "Más artículos" al final

Busca la sección:
```
<!-- NAVEGACIÓN ENTRE ARTÍCULOS -->
```

Reemplaza los dos artículos relacionados con los más relevantes del Journal. Cambia el `href` (la ruta) y el texto visible.

Ejemplo:
```html
<a href="/journal/como-se-construye-cultura-del-vino" class="art-more-link">
  Cómo se construye cultura del vino en un país sin tradición vitivinícola
</a>
```

---

## Paso 7 — Agrega la imagen a la carpeta

Sube tus tres archivos de imagen a la carpeta `Assets/images/`:
- `[IMAGEN]-480.webp`
- `[IMAGEN]-800.webp`
- `[IMAGEN]-1280.webp`

---

## Paso 8 — Agrega la tarjeta en `journal.html`

Abre el archivo `journal.html` en la raíz del sitio.

Busca la última tarjeta de artículo (`<!-- Card 3 -->` o similar) y agrega una nueva tarjeta copiando el patrón. Actualiza la imagen, la categoría, el título, el excerpt, la fecha y los enlaces.

---

## Paso 9 — Actualiza el sitemap

Abre `sitemap.xml` y agrega una nueva entrada:

```xml
<url>
  <loc>https://www.cavagourmet.com/journal/[SLUG]</loc>
  <lastmod>[FECHA YYYY-MM-DD]</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.7</priority>
</url>
```

---

## Paso 10 — Guarda y sube los cambios

Una vez que hayas revisado que todo está bien:

1. Guarda todos los archivos modificados.
2. Súbelos al repositorio o envíaselos al desarrollador para que los publique.
3. Verifica que la URL del artículo funcione correctamente en el sitio.

---

## Nombres de imágenes disponibles actualmente

| Nombre | Descripción |
|---|---|
| `01-cava-vinoteca-wine-wall-hero` | Muro de vinos — toma frontal |
| `02-cava-vinoteca-private-tasting-table` | Mesa de cata privada |
| `03-cava-vinoteca-charcuterie-experience` | Experiencia charcutería |
| `04-cava-vinoteca-after-office-lounge` | Ambiente After Office |
| `05-cava-vinoteca-artisan-wine-detail` | Detalle artesanal de vino |
| `06-nazareth-wine-journey-wset-cava-vinoteca` | Nazareth en CAVA |

---

## Categorías que puedes usar

- Cultura del vino
- Educación y experiencia
- Marketing del vino
- Experiencias en CAVA
- Maridaje y gastronomía

---

## ¿Tienes dudas?

Escríbele al desarrollador del sitio con el texto del artículo y los datos del Paso 1. Él puede crear el archivo HTML por ti y tú solo necesitas revisar y aprobar antes de publicar.
