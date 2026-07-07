// Sprint 11 — gate + lazy-load del signature moment de Home.
// Vanilla, sin dependencias: decide SI cargar three.js, nunca lo precarga.

(function () {
  var el = document.querySelector('[data-signature-moment]');
  if (!el) return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!('IntersectionObserver' in window) || !('ResizeObserver' in window)) return;

  var webglOK = false;
  try {
    var testCanvas = document.createElement('canvas');
    webglOK = !!(testCanvas.getContext('webgl2') || testCanvas.getContext('webgl'));
  } catch (e) {
    webglOK = false;
  }
  if (!webglOK) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        io.disconnect();
        import('./signature-glass.js')
          .then(function (mod) { return mod.initSignatureGlass(el); })
          .catch(function (err) { console.warn('[signature-moment] no se pudo cargar', err); });
      }
    });
  }, { rootMargin: '400px 0px', threshold: 0 });

  io.observe(el);
})();
