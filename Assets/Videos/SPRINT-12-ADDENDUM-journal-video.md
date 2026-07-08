FABLE5 — SPRINT 12 — ADDENDUM
JOURNAL: "THE JOURNAL BREATHES" (living painting)

Este addendum se procesa bajo la REGLA DE TECNOLOGÍA NUEVA definida en
el Sprint 12 principal. No implementar sin tu aprobación explícita de
esta propuesta.

======================================================================
1. QUÉ ES
======================================================================

Un video ambiental en loop ("The Journal Breathes", generado en Runway
Gen-4.5, sin rostros, concepto "living painting") como fondo atmosférico
en el HERO de la página Journal (listado), por encima del cual va el
título y la intro editorial — no dentro de las tarjetas de artículo,
no repetido en cada página individual.

Esto NO reemplaza el momento WOW ya aprobado para Journal (transición
lista→artículo). Son dos capas distintas: el video es ambiente pasivo
al cargar la página; la transición es interacción activa al hacer
clic. Coexisten sin competir.

======================================================================
2. POR QUÉ LA CAJA DE HERRAMIENTAS NATIVA NO ALCANZA
======================================================================

Esto es contenido generativo específico (un "living painting" real,
hecho a medida para CAVA), no un efecto que CSS pueda simular. No hay
alternativa nativa razonable — es la única categoría de este sprint
que requiere un asset pesado real.

======================================================================
3. ESTADO DE LOS ASSETS (verificado con ffprobe, no asumido)
======================================================================

Encontré un bug real en tu pipeline: `journal-breathes-seamless.mp4`
estaba codificado en `mpeg4` (MPEG-4 Part 2, tag `mp4v`) — no h264.
Ese codec no es confiablemente reproducible en `<video>` en Chrome,
Firefox ni Safari. Muy probablemente `cv2.VideoWriter` de OpenCV
escribiendo su fourcc por defecto en vez de h264 real.

Ya corregido y optimizado (entregado en esta conversación):

- `journal-breathes-h264-web.mp4` — h264 real (avc1), faststart,
  1280x720, 24fps, sin audio. 1.42MB (antes: 4.9MB con el codec roto).
- `journal-breathes-hevc-web.mp4` — hevc (tag hvc1, correcto para
  Safari), faststart, sin audio. 3.98MB.
- `journal-breathes-poster.jpg` — frame fijo extraído del propio loop
  (evitando la costura del crossfade), para usar como poster/fallback.

Peso total agregado a la página Journal: ~1.4-4MB según navegador
(el navegador solo descarga UNA fuente, la que soporte), más el
poster de ~100KB que sirve de LCP inmediato.

======================================================================
4. IMPLEMENTACIÓN PROPUESTA
======================================================================

```html
<div class="journal-hero" data-video-hero>
  <video
    class="journal-hero__video"
    poster="/assets/video/journal-breathes-poster.jpg"
    muted
    loop
    playsinline
    preload="none"
    aria-hidden="true"
  >
    <source src="/assets/video/journal-breathes-hevc-web.mp4" type="video/mp4; codecs=hvc1.1.6.L93.B0">
    <source src="/assets/video/journal-breathes-h264-web.mp4" type="video/mp4; codecs=avc1.640020">
  </video>
  <div class="journal-hero__content">
    <!-- título e intro editorial existentes, sin cambios -->
  </div>
</div>
```

```css
.journal-hero { position: relative; }
.journal-hero__video {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
}
.journal-hero__content { position: relative; z-index: 1; }

@media (prefers-reduced-motion: reduce) {
  .journal-hero__video { display: none; }
  /* el poster, como fondo estático del contenedor, cubre este caso */
}
```

```js
// Vanilla JS, sin librería. Carga el video solo si:
// - el usuario no pidió reduced motion
// - no está en modo ahorro de datos
// - el hero está por entrar en viewport
(function () {
  const hero = document.querySelector('[data-video-hero]');
  if (!hero) return;

  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const saveData = navigator.connection && navigator.connection.saveData;
  if (reducedMotion || saveData) return; // se queda en el poster, nada más carga

  const video = hero.querySelector('video');

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        video.preload = 'auto';
        video.load();
        video.play().catch(() => {}); // autoplay puede fallar en algunos casos, se queda en poster
        io.disconnect();
      }
    });
  }, { rootMargin: '200px' });

  io.observe(hero);
})();
```

Puntos no negociables de esta implementación:
- `preload="none"` por defecto — el video NUNCA se descarga hasta que
  el IntersectionObserver confirma que el hero está por entrar en
  viewport. Esto protege LCP.
- El poster es una imagen real optimizada, no un placeholder gris —
  ES el contenido para reduced-motion, save-data, y el instante antes
  de que el video cargue.
- `aria-hidden="true"` en el video — es decorativo/ambiental, no
  transmite información que un lector de pantalla necesite.
- Reservar el espacio del contenedor (`aspect-ratio` o altura fija en
  CSS) para que la aparición del video no cause CLS.

======================================================================
5. VALIDACIÓN Y MEDICIÓN REQUERIDA
======================================================================

- Lighthouse en Journal antes/después, desktop y mobile real.
- Confirmar que el poster satisface LCP (el video no debe ser el
  elemento LCP — si lo es, algo está mal configurado).
- Confirmar comportamiento en `prefers-reduced-motion` y `Save-Data`:
  debe verse el poster, nunca un video roto ni un hueco vacío.
- Probar en Safari real que la fuente HEVC se selecciona y reproduce
  (no solo que "no rompe").
- Confirmar que el CLS no empeora al insertar el hero.

======================================================================
6. LO QUE NECESITO DE VOS ANTES DE QUE ESTO PASE A SPRINT 12
======================================================================

1. ✅ / ❌ Aprobar esta propuesta tal como está.
2. Confirmar: ¿"The Journal Breathes" es la pieza final, o querés que
   también prepare "The Journal Never Sleeps" como alternativa antes
   de decidir?
3. Confirmar la ruta real donde van los assets en tu repo (asumí
   `/assets/video/` — ajustá si tu estructura es otra).
4. Si apruebas, esto se agrega como un momento adicional dentro de la
   Fase 2 de Journal en el prompt de Sprint 12, con su propio commit
   separado y su propia validación Lighthouse — no se mezcla con el
   commit de la transición lista→artículo.
