# SOP — Pipeline Editorial CAVA Journal

Procedimiento operativo estándar para crear y publicar artículos del Journal
usando el editor admin y Claude Code.

Archivo interno — no enlazado desde el sitio público.

---

## Antes de empezar

- VS Code abierto con el proyecto CAVA
- Claude Code activo en la terminal de VS Code
- Texto del artículo de Nazareth en mano (borrador o versión final)

---

## Paso 1 — Abrir el editor

Abre `admin/editor-articulo-cava.html` directamente en el navegador.

Desde VS Code: clic derecho sobre el archivo → **Open with Live Server**
(o clic en `Go Live` en la barra inferior de VS Code).

---

## Paso 2 — Llenar los campos del panel izquierdo

Completa los campos en orden. Los marcados con `*` son obligatorios.

| Campo | Qué poner |
|---|---|
| **Título `*`** | El título del artículo de Nazareth |
| **Categoría `*`** | La que corresponda (Cultura del vino, Educación, etc.) |
| **Fecha `*`** | La fecha de publicación deseada |
| Slug | Se genera automático — revisa que sea correcto |
| Título SEO | El título para Google (máx. 60 caracteres) |
| Meta descripción | Resumen para buscadores (máx. 155 caracteres) |
| Keywords | 4–6 palabras clave separadas por comas |
| Extracto | Una frase que invite a leer |
| Alt de imagen | Descripción breve de la foto de portada |
| Artículo relacionado 1 y 2 | Seleccionar dos artículos del Journal |

---

## Paso 3 — Pegar el texto de Nazareth en el editor

En el área grande de la derecha, pega el artículo completo tal como lo escribió Nazareth.

Usa la barra de formato del editor para estructurar párrafos, títulos o listas si es necesario.

---

## Paso 4 — Abrir el Pipeline

Haz clic en el botón morado **"Publicar con Claude"** en la barra superior derecha.

Se abre el modal **Pipeline Editorial · CAVA Journal** con el indicador de 3 pasos.

---

## Paso 5 — Paso 1: Start Pipeline

El modal muestra el **Paso 1 — Start Pipeline**.

1. Revisa que el prompt generado incluya el título y el contenido del artículo
2. (Opcional) Activa **Modo seguro** si quieres que Claude explique qué va a tocar antes de ejecutar
3. Haz clic en **Copiar prompt** (botón dorado)

---

## Paso 6 — Enviar el prompt a Claude Code

Ve a la terminal de VS Code con Claude Code activo.

Pega el prompt copiado y presiona Enter.

Claude propondrá y generará archivos según el prompt, ejecutando el pipeline en este orden:

1. `/nazareth-editorial-voice` — adapta la voz editorial
2. `/journal-seo-geo` — construye el brief SEO + verifica Vinetur (anti-duplicación)
3. `/journal-red-team-auditor` — audita el brief
4. `/journal-article-builder` — genera el HTML final

Al terminar, Claude reportará el archivo creado, las imágenes necesarias y el resultado
del Vinetur Gate. Revisa todo antes de continuar.

---

## Paso 7 — Revisar el artículo generado

Abre `journal/[slug].html` en el navegador para revisar visualmente.

Si algo no está bien, corrígelo directamente o pídele a Claude que lo ajuste antes de continuar.

---

## Paso 8 — Subir las imágenes de portada

**Antes de ejecutar el Publication Gate**, sube las imágenes a `/Assets/images/Nazareth/`.
El Gate las auditará — si no están presentes, reportará bloqueadores que no corresponden.

| Archivo | Dimensiones |
|---|---|
| `[slug]-480.webp` | 480 px ancho |
| `[slug]-800.webp` | 800 px ancho |
| `[slug]-1280.webp` | 1280 px ancho |
| `[slug]-og-1200x630.jpg` | 1200 × 630 px |

---

## Paso 9 — Paso 2: Publication Gate

En el modal, haz clic en **Siguiente →** para ir al **Paso 2 — Publication Gate**.

1. Haz clic en **Copiar prompt**
2. Pega en Claude Code y presiona Enter

Claude auditará el artículo contra el checklist completo (SEO, schema, voz, Vinetur, imágenes).

- **PASS** → continúa al Paso 10
- **Bloqueadores** → corrígelos y vuelve a ejecutar el Gate antes de continuar

---

## Paso 10 — Paso 3: Publicar

Con el gate en PASS, haz clic en **Siguiente →** para el **Paso 3 — Publicar**.

1. Haz clic en **Copiar prompt**
2. Pega en Claude Code y presiona Enter

Claude modificará los archivos de indexación según el prompt:
`journal/journal.html`, `sitemap.xml`, `data/pages.json`, `llms.txt`, `JOURNAL-REGISTRY.md`.

No hace commit automático — listará los archivos modificados para revisión.

---

## Paso 11 — Confirmar el commit

Cuando Claude liste los archivos modificados, verifica que sean exactamente los esperados
y usa este mensaje:

```
Confirma primero el listado exacto de archivos que vas a commitear. No incluyas
.agents/, skills-lock.json, .claude/skills/find-skills/ ni archivos no relacionados.
Si todo coincide, prepara el commit y espera mi confirmación final antes del push.
```

---

## Paso 12 — Enviar a Nazareth por WhatsApp

Una vez publicado y el sitio actualizado en GitHub Pages, copia la URL:

```
https://www.cavagourmet.com/journal/[slug]
```

Envíasela a Nazareth al **+506 8448 3983**:

> "Nazareth, el artículo ya está publicado en el Journal.
> Revísalo aquí: https://www.cavagourmet.com/journal/[slug]
> Cualquier ajuste me avisas."

---

**Tiempo estimado total:** 20–35 minutos según la longitud del artículo y los ajustes del Gate.

---

## Archivos relacionados

| Archivo | Propósito |
|---|---|
| `admin/editor-articulo-cava.html` | Editor y launcher del pipeline |
| `admin/plantilla-articulo.html` | Plantilla base de artículos |
| `admin/briefs/` | Briefs persistidos por artículo |
| `data/pages.json` | Registro de páginas y estado de publicación |
| `JOURNAL-REGISTRY.md` | Tabla de artículos publicados |
| `CLAUDE.md` | Instrucciones base para Claude Code |
| `AGENTS.md` | Stack técnico y reglas de producción |
