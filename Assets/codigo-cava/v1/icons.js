// Original lightweight interface vectors; no icon font or external runtime.
const paths={
 search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 check:'<path d="m5 12 4 4L19 6"/>',
 arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 diagonal:'<path d="M5 19 19 5M7 5h12v12"/>',
 rotate:'<path d="M20 7v5h-5M4 17v-5h5"/><path d="M6 7a7 7 0 0 1 12-2l2 2M18 17a7 7 0 0 1-12 2l-2-2"/>',
 pause:'<path d="M8 5v14M16 5v14"/>',
 music:'<path d="M9 18V5l11-2v13M9 8l11-2"/><ellipse cx="6" cy="18" rx="3" ry="2"/><ellipse cx="17" cy="16" rx="3" ry="2"/>',
 muted:'<path d="M9 18V5l11-2v13M3 3l18 18"/><ellipse cx="6" cy="18" rx="3" ry="2"/>',
 pin:'<path d="m8 3 8 0-1 6 4 4H5l4-4-1-6M12 13v8"/>',
 down:'<path d="m6 9 6 6 6-6"/>',
 clock:'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
 question:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 4 2c-1 .6-1.5 1-1.5 2M12 17h.01"/>',
 alert:'<path d="m12 3 10 18H2L12 3ZM12 9v5M12 17h.01"/>',
 scope:'<path d="M4 12h16M8 8l-4 4 4 4M16 8l4 4-4 4"/>',
 ring:'<circle cx="12" cy="12" r="8"/>',
 partial:'<circle cx="12" cy="12" r="8"/><path d="M12 4v16"/>',
 diamond:'<path d="m12 3 9 9-9 9-9-9 9-9Z"/>',
 dot:'<circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>',
 minus:'<path d="M5 12h14"/>',
 close:'<path d="m6 6 12 12M18 6 6 18"/>',
 equal:'<path d="M5 8h14M5 16h14"/>'
};
export function icon(name){return '<svg class="ui-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'+(paths[name]||paths.search)+'</svg>';}
const symbols={'⌕':'search','✓':'check','→':'arrow','↗':'diagonal','↻':'rotate','↺':'rotate','Ⅱ':'pause','♪':'music','⚑':'pin','▾':'down','◷':'clock','↔':'scope','○':'ring','◐':'partial','◇':'diamond','◎':'ring','●':'dot','×':'close'};
export function adornIcons(markup){
 return markup.split(/(<[^>]*>)/g).map(piece=>{
  if(piece.startsWith('<'))return piece;
  if(['?','!','=','–'].includes(piece.trim()))return icon({'?':'question','!':'alert','=':'equal','–':'minus'}[piece.trim()]);
  return piece.replace(/[⌕✓→↗↻↺Ⅱ♪⚑▾◷↔○◐◇◎●×]/g,s=>icon(symbols[s]));
 }).join('');
}

