const nav = document.querySelector('#nav');
const toggle = document.querySelector('#navToggle');
const menu = document.querySelector('#mobileMenu');
const game = document.querySelector('#main');
const context = document.querySelector('#cava-context');
let previousFocus = null;

function setMenu(open) {
  menu.classList.toggle('open', open);
  menu.inert = !open;
  toggle.classList.toggle('open', open);
  toggle.setAttribute('aria-expanded', String(open));
  toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
  game.inert = open;
  document.querySelector('.topbar').inert = open;
  context.inert = open;
  document.querySelector('footer').inert = open;
  document.body.classList.toggle('menu-open', open);
  if (open) { previousFocus = document.activeElement; menu.querySelector('a').focus(); }
  else if (previousFocus) { previousFocus.focus(); previousFocus = null; }
  document.dispatchEvent(new CustomEvent('cava-menu', { detail: { open } }));
}
toggle.addEventListener('click', () => setMenu(toggle.getAttribute('aria-expanded') !== 'true'));
menu.addEventListener('click', e => { if (e.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', e => {
  if (toggle.getAttribute('aria-expanded') !== 'true') return;
  if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); setMenu(false); }
  if (e.key !== 'Tab') return;
  const items = [toggle, ...menu.querySelectorAll('a')];
  const first = items[0], last = items[items.length - 1];
  if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
}, true);
window.matchMedia('(min-width:961px)').addEventListener('change', e => {
  if (e.matches && toggle.getAttribute('aria-expanded') === 'true') setMenu(false);
});
let queued = false;
window.addEventListener('scroll', () => {
  if (queued) return;
  queued = true;
  requestAnimationFrame(() => { nav.classList.toggle('scrolled', window.scrollY > 40); queued = false; });
}, { passive: true });
function syncContext() {
  const playing = Boolean(game.querySelector('.game'));
  if (playing !== context.hidden) {
    context.hidden = playing;
    game.scrollIntoView({ block: 'start', behavior: 'instant' });
  }
}
new MutationObserver(syncContext).observe(game, { childList: true });
syncContext();
