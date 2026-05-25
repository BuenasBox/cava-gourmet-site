# Journal Image Inventory

Fecha de auditoria: 2026-05-24  
Alcance: `Assets/images/`, `Assets/` y carpetas Nazareth detectadas  
Uso: control previo para construir articulos del Journal

## Regla operativa

Antes de construir o publicar un articulo del Journal:

- Revisar este inventario.
- Usar solo rutas reales y case-sensitive.
- No usar placeholders.
- Validar que la imagen exista localmente.
- Preferir WebP y versiones responsive cuando existan.
- Si no hay imagen validada, bloquear publicacion y mantener `noindex,nofollow`.
- Documentar la imagen elegida en el brief persistido del articulo.

## Carpetas auditadas

- `Assets/`
- `Assets/images/`
- `Assets/images/Nazareth/`
- `Assets/images/Nazareth y Erick/`
- `Assets/images/Vinoteca/`
- `Assets/images/Erick/`

Carpetas de archivo detectadas:

- `Assets/images/Nazareth/_Archivo/`
- `Assets/images/Nazareth y Erick/_Archivo/`
- `Assets/images/Erick/_Archivo/`

Las carpetas `_Archivo` contienen imagenes potencialmente utiles, pero por peso, nomenclatura o falta de seleccion editorial no deben usarse en Journal sin validacion manual.

## Imagenes recomendadas para Journal

| Ruta exacta case-sensitive | Orientacion / dimensiones | WebP | Responsive | Uso sugerido | Riesgo de reutilizacion | Notas de performance |
| --- | --- | --- | --- | --- | --- | --- |
| `Assets/images/Nazareth/nazareth-padilla-catando-vino-tinto-cava.jpg` | Vertical 738x1108 | No | No | Articulos sobre cata, percepcion, cuerpo, tanino, evaluacion en copa | Medio: muy especifica para cata; puede repetirse en articulos educativos | Peso bajo aprox. 128 KB; buena para inline, debil para OG horizontal |
| `Assets/images/Nazareth/nazareth-padilla-analisis-copa-vino-blanco-cata.jpg` | Horizontal 4898x3266 | Sí: 480w (17.9 KB) · 800w (36.3 KB) · 1280w (77.7 KB) · OG 1200x630 (105.3 KB) | Sí | USADA — `/journal/que-significa-cuerpo-en-el-vino` como imagen principal | Alto: ya asignada como imagen primaria del artículo de cuerpo del vino — no reutilizar como imagen principal en otro artículo | Derivados WebP creados y validados. OG dentro de peso óptimo. Excelente candidata para este tema; no disponible para nuevo artículo |
| `Assets/images/Nazareth/nazareth-padilla-guia-cata-vinos-cava-gourmet.jpg` | Horizontal 6000x4000 | Si, fuera de subcarpeta Nazareth | Si: `Assets/images/nazareth-padilla-guia-cata-vinos-cava-gourmet-480.webp`, `-800.webp`, `-1280.webp`, `-1920.webp` | Catas guiadas, educacion sin intimidacion, articulos evergreen | Alto: ya es imagen transversal de catas y autoridad | Preferir variantes WebP en `Assets/images/` para LCP/OG |
| `Assets/images/nazareth-padilla-guia-cata-vinos-cava-gourmet-1280.webp` | Horizontal, variante 1280 | Si | Si | Imagen principal optimizada para articulos de cata/educacion | Alto si se usa en demasiados articulos | Buena candidata para Journal si coincide con el tema |
| `Assets/images/Nazareth/nazareth-padilla-editorial-vino-cava-costa-rica.jpg` | Vertical 1920x3200 | No | No | Articulos editoriales, voz Nazareth, reflexion cultural | Medio-alto: puede volverse imagen comodin de Journal | Peso moderado aprox. 543 KB; falta WebP/responsive |
| `Assets/images/Nazareth/nazareth-padilla-comunicadora-vino-costa-rica.jpg` | Vertical 1080x1350 | Si, fuera de subcarpeta Nazareth existe set de comunicadora | Si: `Assets/images/nazareth-padilla-montero-comunicadora-vino-cava-costa-rica-480.webp`, `-800.webp`, `-1205.webp` | Articulos de entidad Nazareth, autoridad, medios, cultura del vino | Alto para piezas de entidad; no usar en todos los evergreen | Preferir versiones WebP disponibles |
| `Assets/images/nazareth-padilla-montero-comunicadora-vino-cava-costa-rica-1205.webp` | Vertical, variante 1205 | Si | Si | Imagen optimizada para autoridad de Nazareth | Medio-alto | Buena para author/entity, no ideal como OG horizontal |
| `Assets/images/Nazareth/nazareth-padilla-cava-vinoteca-blog-vino.jpg` | Horizontal 6000x3376 | No | No | Journal, blog/editorial, vinoteca, conversacion alrededor del vino | Alto: nombre sugiere uso editorial generico | JPG pesado aprox. 8.4 MB; requiere optimizacion antes de uso |
| `Assets/images/Nazareth/nazareth-padilla-cava-gourmet-market-vino-tinto.jpg` | Horizontal 6000x3376 | No | No | Articulos sobre seleccion de vino tinto, cuerpo, experiencia en vinoteca | Medio | JPG muy pesado aprox. 9.8 MB; no usar sin version optimizada |
| `Assets/images/Nazareth/nazareth-padilla-botella-vino-tinto-vinoteca.jpg` | Vertical 3038x4160 | No | No | Articulos sobre vino tinto, cuerpo, seleccion de botella | Medio | Peso aprox. 719 KB; vertical, falta responsive |
| `Assets/images/Nazareth/nazareth-padilla-seleccion-vino-bodega-cava.jpg` | Vertical 2773x4160 | No | No | Articulos sobre como elegir vino, criterio experto, seleccion especializada | Medio | Peso aprox. 609 KB; falta WebP/responsive |
| `Assets/images/Nazareth/nazareth-padilla-muro-vinos-cava-vinoteca.jpg` | Vertical 2773x4160 | No | No | Articulos sobre elegir vino frente al muro, primeras decisiones | Medio | Peso aprox. 647 KB; falta WebP/responsive |
| `Assets/images/Nazareth/nazareth-padilla-copa-vino-tinto-cata-cava.jpg` | Vertical 2851x4160 | No | No | Articulos de vino tinto, cuerpo, textura, cata | Medio | Peso aprox. 711 KB; falta WebP/responsive |
| `Assets/images/Nazareth/nazareth-padilla-botella-vino-blanco-cava-gourmet.jpg` | Horizontal 4160x2773 | No | No | Articulos sobre vino blanco, frescura, acidez, decision de compra | Bajo-medio | Peso aprox. 1.9 MB; requiere optimizacion |
| `Assets/images/Nazareth/nazareth-padilla-cata-grupal-vinos-cava-gourmet.jpg` | Horizontal 6000x4000 | No | No | Articulos de hospitalidad, grupos, aprendizaje compartido | Medio | JPG pesado aprox. 2.9 MB; requiere WebP/responsive |
| `Assets/images/Nazareth/cava-gourmet-evento-cata-vinos-perez-zeledon.jpg` | Horizontal 6000x4000 | No | No | Articulos locales sobre catas, eventos, Perez Zeledon | Medio | JPG pesado aprox. 3.1 MB; optimizar antes de usar |
| `Assets/images/Nazareth/cava-gourmet-mesa-maridaje-copas-vino.jpg` | Horizontal 6000x4000 | No | No | Maridaje, mesa, hospitalidad, experiencia | Medio | JPG pesado aprox. 4.1 MB; optimizar antes de usar |
| `Assets/images/Nazareth/cava-gourmet-maridaje-quesos-vinos-perez-zeledon.jpg` | Horizontal 6000x4000 | No | No | Maridaje, quesos, cata, experiencia | Medio | JPG pesado aprox. 2.8 MB; optimizar antes de usar |
| `Assets/images/Nazareth/cava-gourmet-market-interior-vinoteca-perez-zeledon.jpg` | Horizontal 4898x3266 | No | No | Articulos locales sobre vinoteca, espacio, Perez Zeledon | Medio | JPG pesado aprox. 2.9 MB; optimizar antes de usar |
| `Assets/images/Vinoteca/Cava-Gourmer-Marker-Interior-de-tienda.jpg` | Horizontal 4898x3266 | No | No | Vinoteca, ambiente interior, articulos locales | Bajo-medio | Nombre contiene posible typo `Gourmer`; evitar si se busca pulcritud de URL |
| `Assets/images/Vinoteca/DSC_6831.jpg` | Horizontal 6000x4000 | No | No | Ambiente de vinoteca, articulos locales o de experiencia | Bajo-medio | Nombre generico; optimizar y renombrar solo si se crea derivado |
| `Assets/images/02-cava-vinoteca-private-tasting-table-1280.webp` | Horizontal, variante 1280 | Si | Si: 480/640/800/1280/1920 | Catas privadas, educacion, mesa de degustacion | Alto: probablemente ya se usa en paginas principales | Muy buena performance; verificar no saturar como imagen editorial |
| `Assets/images/05-cava-vinoteca-artisan-wine-detail-1280.webp` | Horizontal, variante 1280 | Si | Si: 480/800/1280/1920 | Detalle de vino, articulos evergreen o sensoriales sin retrato | Medio | Buena performance; util para evitar repetir retratos |
| `Assets/images/01-cava-vinoteca-wine-wall-hero-1280.webp` | Horizontal, variante 1280 | Si | Si: 320/480/640/800/1280/1920 | Articulos sobre eleccion de vino, muro de vinos, vinoteca | Alto: imagen hero del sitio; usar con moderacion | Buena performance, pero alto riesgo de sobreuso |
| `Assets/images/06-nazareth-wine-journey-wset-cava-vinoteca-1280.webp` | Horizontal, variante 1280 | Si | Si: 800/1280/1920 | Articulos de entidad Nazareth, WSET, Nazareth Wine Journey | Medio-alto | Buena performance; usar solo cuando el tema refuerce autoridad |

## Imagenes detectadas pero no recomendadas como primera opcion

| Ruta | Motivo |
| --- | --- |
| `Assets/images/Logos/*.png` | Logos; no sirven como imagen principal de Journal. |
| `Assets/logo-cava-mark.jpg`, `Assets/logo-cava-mark.webp`, `Assets/Logo-Cava.png`, `Assets/logotipo-cava.png` | Marca/logotipo; no usar como imagen de articulo salvo fallback tecnico excepcional. |
| `Assets/images/*/_Archivo/*` | Archivo bruto o no seleccionado; pesos altos, nombres genericos, falta decision editorial. |
| `Assets/images/Erick/*` | Util para articulos donde Erick sea protagonista; no usar para voz Nazareth salvo contexto compartido. |
| `Assets/images/Nazareth y Erick/*` | Util para historia, anfitriones, experiencias compartidas; evitar en articulos donde la voz principal sea solo Nazareth. |

## Brechas detectadas

- Muchas imagenes JPG utiles para Journal no tienen version WebP ni responsive.
- Varias imagenes horizontales fuertes pesan entre 2 MB y 10 MB.
- La imagen de "Que significa que un vino tenga cuerpo" fue optimizada y publicada con derivados 480/800/1280 WebP y OG 1200x630 JPG. Brecha resuelta — 2026-05-24.
- Hay activos optimizados WebP suficientes para empezar, pero con riesgo de reutilizacion si se usan en demasiados articulos.
- Falta convencion formal para derivar imagenes editoriales del Journal con `-480`, `-800`, `-1280`, `-1920`.

## Recomendacion operativa

Para cada articulo nuevo del Journal, registrar en su brief:

- Imagen elegida.
- Alt text aprobado.
- Variante OG.
- Variante inline.
- Si existe WebP.
- Si existe `srcset`.
- Riesgo de reutilizacion.
- Accion pendiente si falta optimizacion.
