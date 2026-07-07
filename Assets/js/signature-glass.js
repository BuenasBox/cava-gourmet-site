// Sprint 11 — "La Copa que Captura la Luz" (signature moment, exclusivo de Home)
// Cargado dinámicamente solo cuando el contenedor entra en viewport. Ver signature-moment-loader.js.

let threeModulePromise;
function loadThree() {
  if (!threeModulePromise) {
    threeModulePromise = import('./vendor/three.module.min.js');
  }
  return threeModulePromise;
}

export async function initSignatureGlass(container) {
  let THREE;
  try {
    THREE = await loadThree();
  } catch (err) {
    console.warn('[signature-moment] three.js no disponible, se conserva la imagen', err);
    return;
  }

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reducedMotion.matches) return;

  const canvas = document.createElement('canvas');
  canvas.className = 'signature-glass-canvas';
  canvas.setAttribute('aria-hidden', 'true');

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'low-power' });
  } catch (err) {
    console.warn('[signature-moment] no se pudo crear el contexto WebGL, se conserva la imagen', err);
    return;
  }

  container.appendChild(canvas);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 10);
  camera.position.set(0, 0, 3.4);

  // Perfil de la copa (pie -> tallo -> cuenco), revolucionado con LatheGeometry.
  // Geometría procedural: cero peso de asset 3D adicional.
  const profile = [
    [0.55, 0.00], [0.50, 0.03], [0.16, 0.05], [0.05, 0.09],
    [0.05, 0.62], [0.10, 0.66], [0.30, 0.80], [0.46, 1.05],
    [0.50, 1.35], [0.46, 1.62], [0.34, 1.82], [0.16, 1.93], [0.00, 1.96]
  ].map(([x, y]) => new THREE.Vector2(x, y));
  const glassGeo = new THREE.LatheGeometry(profile, 64);
  glassGeo.translate(0, -1.0, 0);

  // Transparencia + clearcoat en vez de transmission real: la transmission de
  // Three.js exige un render-pass extra por frame (costoso/inestable en Safari
  // iOS). El brillo cálido que recorre el borde al hacer scroll basta para
  // leer "vidrio que atrapa la luz" sin ese riesgo de rendimiento.
  const glassMat = new THREE.MeshPhysicalMaterial({
    color: 0xf6efe3,
    metalness: 0,
    roughness: 0.05,
    transparent: true,
    opacity: 0.22,
    clearcoat: 1,
    clearcoatRoughness: 0.08,
    side: THREE.DoubleSide,
    depthWrite: false
  });
  const glass = new THREE.Mesh(glassGeo, glassMat);
  scene.add(glass);

  const ambient = new THREE.AmbientLight(0x2a2018, 0.7);
  scene.add(ambient);

  // Color del punto de luz cálido: mismo tono que --gold-soft del sistema de tokens.
  const warmLight = new THREE.PointLight(0xd7b879, 1.6, 8);
  warmLight.position.set(1.6, 0.6, 1.8);
  scene.add(warmLight);

  function resize() {
    const rect = container.getBoundingClientRect();
    const w = Math.max(1, rect.width);
    const h = Math.max(1, rect.height);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h, false);
  }
  resize();

  const ro = new ResizeObserver(resize);
  ro.observe(container);

  // Aproximación de var(--ease) (cubic-bezier(.22,.61,.36,1)) via smoothstep:
  // mismo espíritu "lento-lento" sin resolver la curva de Bézier en JS.
  function ease(t) {
    return t * t * (3 - 2 * t);
  }

  let raf = null;
  let running = false;
  let intersecting = false;
  const frameTimes = [];

  function frame() {
    raf = requestAnimationFrame(frame);

    const now = performance.now();
    frameTimes.push(now);
    if (frameTimes.length > 30) frameTimes.shift();
    if (frameTimes.length === 30) {
      const avgDelta = (frameTimes[29] - frameTimes[0]) / 29;
      // Vigilante de rendimiento: si el frame-time sostenido cae por debajo de
      // ~24fps, el dispositivo no puede con esto — se descarta en vivo y se
      // revela la imagen de respaldo, sin esperar a un reporte de Lighthouse.
      if (avgDelta > 42) {
        teardown();
        return;
      }
    }

    const rect = container.getBoundingClientRect();
    const vh = window.innerHeight || document.documentElement.clientHeight;
    const raw = 1 - (rect.top + rect.height / 2) / (vh + rect.height);
    const progress = Math.min(1, Math.max(0, raw));
    const t = ease(progress);

    glass.rotation.y = -0.35 + t * 0.7;
    warmLight.position.x = 1.6 - t * 3.2;
    warmLight.position.y = 0.6 + Math.sin(t * Math.PI) * 0.8;
    warmLight.intensity = 1.4 + Math.sin(t * Math.PI) * 1.3;

    renderer.render(scene, camera);
  }

  function start() {
    if (running) return;
    running = true;
    frameTimes.length = 0;
    frame();
  }

  function stop() {
    if (raf) cancelAnimationFrame(raf);
    raf = null;
    running = false;
  }

  function onVisibilityChange() {
    if (document.hidden) stop();
    else if (intersecting) start();
  }
  document.addEventListener('visibilitychange', onVisibilityChange);

  function onReducedMotionChange(e) {
    if (e.matches) teardown();
  }
  reducedMotion.addEventListener('change', onReducedMotionChange);

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      intersecting = entry.isIntersecting;
      if (intersecting && !document.hidden) start();
      else stop();
    });
  }, { threshold: 0 });
  io.observe(container);

  function teardown() {
    stop();
    ro.disconnect();
    io.disconnect();
    document.removeEventListener('visibilitychange', onVisibilityChange);
    reducedMotion.removeEventListener('change', onReducedMotionChange);
    renderer.dispose();
    glassGeo.dispose();
    glassMat.dispose();
    canvas.remove();
  }
}
