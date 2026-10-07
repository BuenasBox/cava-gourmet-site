// Design study only. Decisions are scripted here to test play, not the historical evaluator.
import { campaign } from './cases.js';
import { icon, adornIcons } from './icons.js';
const main = document.querySelector('main');
const settingsDialog = document.querySelector('#settings');
const pauseDialog = document.querySelector('#pause');
const reduceMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const say = text => { document.querySelector('#announcer').textContent = text; };
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const presets = { rookie: { difficulty:'rookie', seconds:180, budget:9 }, detective:{ difficulty:'detective', seconds:120, budget:6 }, expert:{ difficulty:'expert', seconds:75, budget:4 } };
let config = { ...presets.detective, timed:true, music:true, volume:25 };
let state = null;
let run = 0;
let lastTick = performance.now();
const levelName = {rookie:'Explorador',detective:'Detective',expert:'Experto'};
// Editorial game score, 0-100 per mission. Not a validated learning measure and unrelated to the preserved evaluator.
const POINTS = { pick:40, evidence:30, twist:20, transfer:10 };
// Hotspot rectangles over the 160x360 bottle artwork / label card art, as percentages of the art box.
// Generic a/b zone keys so every case (see cases.js) can point its two inspectable zones at whatever
// evidence its source item documents; the rectangle geometry itself is shared by every case within a
// track, since it is a property of the artwork, not of any one case. 'back' has no rect: it is read by
// flipping the object.
const zoneRects = { bottle:{ a:{top:3,left:25,width:50,height:26}, b:{top:45,left:16,width:22,height:46} }, label:{ a:{top:47,left:24,width:52,height:24}, b:{top:71,left:24,width:52,height:13} } };
// Session-only completion tracking (not persisted): which case ids in each track have been finished,
// used only to label mission cards on the home screen and to pick the next case after 'complete'.
let progress = { bottle: new Set(), label: new Set() };
function currentCase(){ return campaign[state.mode][state.caseIndex]; }
// Advance within the same track first (next case by rank); once a track is exhausted, offer the first
// not-yet-completed case of the other track; once both tracks are fully completed, there is no next case.
function nextCase(){
  const track=campaign[state.mode];
  if(state.caseIndex+1<track.length)return{mode:state.mode,index:state.caseIndex+1};
  const other=state.mode==='bottle'?'label':'bottle';
  const otherTrack=campaign[other];
  const firstPending=otherTrack.findIndex(c=>!progress[other].has(c.id));
  if(firstPending!==-1)return{mode:other,index:firstPending};
  return null;
}

// Inline original vector art, local and dependency-free.
function bottleSVG(object, uid='preview', largeLabel=false){
  const lines = object.front.split(' / ');
  const wire = object.style==='wire';
  const screw = object.style==='screw';
  return `<svg viewBox="0 0 160 360" aria-hidden="true" focusable="false"><defs><linearGradient id="glass-${uid}" x1="0" x2="1"><stop offset="0" stop-color="#0a1a19"/><stop offset=".26" stop-color="${object.color}"/><stop offset=".6" stop-color="${object.color}"/><stop offset="1" stop-color="#0a1a19"/></linearGradient><linearGradient id="foil-${uid}"><stop stop-color="${object.foil}"/><stop offset=".5" stop-color="#d0c69a"/><stop offset="1" stop-color="${object.foil}"/></linearGradient></defs><ellipse cx="80" cy="346" rx="52" ry="7" fill="#000" opacity=".28"/><path d="M65 29 Q80 22 95 29 L95 115 Q97 137 114 151 Q125 162 125 183 L125 325 Q125 339 112 341 L48 341 Q35 339 35 325 L35 183 Q35 162 46 151 Q63 137 65 115Z" fill="url(#glass-${uid})" stroke="#57736c" stroke-opacity=".45"/><path d="M48 184L48 317" stroke="#e4f2d5" stroke-opacity=".13" stroke-width="5" stroke-linecap="round"/><path d="M65 30Q80 24 95 30L96 87Q80 94 64 87Z" fill="url(#foil-${uid})"/><ellipse cx="80" cy="29" rx="15" ry="4" fill="${object.foil}"/>${wire?'<path d="M62 48Q80 60 98 48M62 71Q80 84 98 71M66 33L62 83M94 33L98 83M66 83Q80 90 94 83" stroke="#bac7c7" stroke-width="2.3" fill="none"/><circle cx="97" cy="76" r="5" stroke="#bac7c7" fill="none"/>':''}${screw?'<path d="M64 42L96 42M64 51L96 51M64 60L96 60" stroke="#112330" stroke-width="2"/>':''}<rect x="${largeLabel?40:42}" y="${largeLabel?170:195}" width="${largeLabel?80:76}" height="${largeLabel?130:98}" rx="2" fill="#eee6d5"/><rect x="47" y="${largeLabel?178:203}" width="66" height="${largeLabel?114:82}" rx="1" fill="none" stroke="#b7a579" stroke-width=".7"/><path d="M70 ${largeLabel?195:216}L80 ${largeLabel?186:207}L90 ${largeLabel?195:216}L80 ${largeLabel?203:224}Z" fill="${object.foil}"/><text x="80" y="${largeLabel?225:240}" font-size="${largeLabel?12:10}" text-anchor="middle" font-family="Georgia" fill="#343c35">${esc(lines[0])}</text><text x="80" y="${largeLabel?247:257}" font-size="${largeLabel?12:10}" text-anchor="middle" font-family="Georgia" fill="#343c35">${esc(lines[1])}</text>${largeLabel?`<text x="80" y="268" text-anchor="middle" font-size="7" font-family="sans-serif" fill="#6d715f">${esc(object.country)}</text>`:''}<path d="M65 324Q80 313 95 324" fill="none" stroke="#071815" stroke-width="6" opacity=".7"/></svg>`;
}

// The object's back face: a fixed generic card (name + redacted lines + a lot-code block). The same
// shape is used for every case and both tracks -- only ever shown as the flipped face, never cropped
// to a clue zone (the engine only ever calls this with no zone argument; see render()'s face-back markup).
function inspectionArt(object){
  return `<svg viewBox="0 0 150 140" aria-hidden="true"><rect x="22" y="12" width="106" height="117" rx="5" fill="#eee6d5"/><text x="75" y="32" text-anchor="middle" font-family="Georgia" font-size="9" fill="#343c35">${esc(object.name)}</text><path d="M37 45H113M37 54H113M37 63H103M37 72H113" stroke="#8d927d" stroke-width="2"/><rect x="36" y="85" width="78" height="26" fill="#d7d0bc"/><path d="M40 89V106M45 89V106M49 89V106M55 89V106M61 89V106M64 89V106M71 89V106M76 89V106M80 89V106M84 89V106M91 89V106M99 89V106M103 89V106M109 89V106" stroke="#526151" stroke-width="2"/></svg>`;
}

class TensionMusic {
  constructor(){this.context=null;this.master=null;this.interval=null;this.enabled=false;this.step=0;this.next=0;this.suspended=false;}
  async enable(){
    try {
      if(!this.context){const Audio = window.AudioContext||window.webkitAudioContext;if(!Audio)return false;this.context=new Audio();this.master=this.context.createGain();this.master.gain.value=config.volume/100*.22;this.master.connect(this.context.destination);}
      await this.context.resume();this.enabled=true;this.suspended=Boolean(state?.paused)||document.hidden;this.next=this.context.currentTime+.04;
      if(!this.interval)this.interval=setInterval(()=>this.schedule(),80);
      this.updateButton();return true;
    }catch{this.enabled=false;this.updateButton();say('Este navegador no pudo activar el audio. Puedes jugar sin música.');return false;}
  }
  disable(){this.enabled=false;this.master?.gain.setTargetAtTime(0,this.context.currentTime,.03);this.updateButton();}
  setVolume(){if(this.context)this.master.gain.setTargetAtTime(this.enabled&&!this.suspended?config.volume/100*.22:0,this.context.currentTime,.04);}
  suspend(){this.suspended=true;if(this.context)this.master.gain.setTargetAtTime(0,this.context.currentTime,.03);}
  resume(){this.suspended=false;this.next=this.context?.currentTime+.04;this.setVolume();}
  updateButton(){const b=document.querySelector('#sound');b.innerHTML=icon(this.enabled?'music':'muted')+` Música: ${this.enabled?'encendida':'apagada'}`;b.setAttribute('aria-pressed',String(this.enabled));this.setVolume();}
  note(frequency,start,duration,type='sine',gain=.5){const osc=this.context.createOscillator(),amp=this.context.createGain();osc.type=type;osc.frequency.setValueAtTime(frequency,start);amp.gain.setValueAtTime(0,start);amp.gain.linearRampToValueAtTime(gain,start+.015);amp.gain.exponentialRampToValueAtTime(.001,start+duration);osc.connect(amp);amp.connect(this.master);osc.start(start);osc.stop(start+duration+.03);osc.onended=()=>{osc.disconnect();amp.disconnect();};}
  schedule(){
    if(!this.enabled||this.suspended||!state||!['play','twist','transfer'].includes(state.phase))return;
    const urgency=state.settings.timed?1-state.remaining/state.settings.seconds:.3;
    const beat=60/(68+urgency*54)/2;
    while(this.next<this.context.currentTime+.18){
      if(this.next<this.context.currentTime)this.next=this.context.currentTime+.03;
      const notes=[146.83,220,174.61,220,146.83,207.65,174.61,164.81];
      this.note(notes[this.step%8],this.next,beat*.75,'triangle',.2);
      if(this.step%4===0)this.note(73.42,this.next,beat*2,'sine',.4);
      if(urgency>.55)this.note(this.step%2?440:466.16,this.next,.045,'sine',.065);
      this.step++;this.next+=beat;
    }
  }
}
const music=new TensionMusic();

// Wrap a DOM-mutating function in a View Transition when the browser supports it and motion is allowed.
// This gives the phase-to-phase swaps (investigate → verdict → twist → close) a smooth cross-fade for free,
// with zero effect on the final DOM: the mutation itself still happens synchronously inside the callback.
// `after` runs once the new DOM is actually live and connected. During an active view transition the engine can
// silently drop a focus() call made from inside the update callback itself (the new tree isn't settled yet), so
// anything that depends on the post-mutation DOM — focus, measuring layout — must wait for `ready` instead of
// running synchronously after startViewTransition() is invoked.
function withTransition(mutate,after){
  if(main.hasAttribute("data-prerender")||!main.childElementCount||reduceMotion()||!document.startViewTransition){mutate();main.removeAttribute("data-prerender");after&&after();return;}
  const transition=document.startViewTransition(mutate);
  transition.ready.then(after||(()=>{})).catch(()=>{after&&after();});
}

function home(){
  state=null;music.suspend();
  withTransition(()=>{
    const hero=campaign.bottle[0];
    const trackCards=mode=>campaign[mode].map((c,i)=>{
      const done=progress[mode].has(c.id);
      return `<button class="mission-card" data-action="start" data-mode="${mode}" data-case-index="${i}"><span class="number">${String(i+1).padStart(2,'0')}</span><span><span class="eyebrow">${done?'<span style="color:var(--mint)">✓ COMPLETADO</span>':esc(c.subtitle)}</span><h3>${esc(c.title)}</h3><p>${esc(c.brief)}</p></span><span class="arrow">↗</span></button>`;
    }).join('');
    main.innerHTML=adornIcons(`<section class="home"><div class="hero-grid"><div class="hero-copy"><span class="eyebrow">EL VINO TIENE SECRETOS. TÚ TIENES OJO.</span><h1>Código<br><em>Cava.</em><span class="game-descriptor">Juego de vino · Botellas y etiquetas</span></h1><p class="tagline">Una pista cambia todo.</p><p>Catorce casos. Dos investigaciones.<br>Observa, compara y decide.<br>El reloj es opcional.</p><div class="hero-actions"><button class="primary" data-action="start" data-mode="bottle" data-case-index="0">Entrar al misterio ↗</button><button class="quiet" data-action="settings">Ajustar reto</button></div></div><div class="scene-preview" aria-hidden="true"><div class="preview-bottles">${hero.objects.slice(0,3).map((o,i)=>bottleSVG(o,'hero'+i)).join('')}</div><div class="case-stamp">EXPEDIENTE<br><br>001 / SIN FICHA</div><div class="preview-clue"><b>⌕</b><span>La botella más elegante podría estar distrayéndote.</span></div></div></div><div class="mission-list"><h2 class="track-heading">Investigación de botella</h2>${trackCards('bottle')}<h2 class="track-heading">Investigación de etiqueta</h2>${trackCards('label')}</div><div class="home-footer"><span>Gratis · Sin registro · Sin conocimientos previos</span><span>${levelName[config.difficulty]} · ${config.timed?config.seconds+' s':'sin reloj'} · ${config.budget} inspecciones</span></div></section>`);
  });
}
function start(mode,caseIndex=0){
  const m=campaign[mode][caseIndex];
  const objects=m.objects.slice(0,config.difficulty==='expert'?4:3);
  // Rotate object order between attempts; the correct item never stays tied to a slot.
  const offset=run++%objects.length;const shuffled=objects.slice(offset).concat(objects.slice(0,offset));
  state={mode,caseIndex,phase:'play',settings:{...config},objects:shuffled,selected:null,clues:[],seen:new Set(),remaining:config.seconds,inspections:config.budget,confidence:'cautious',paused:false,expired:false,initial:null,revision:null,lastClue:null,viewBack:false,pinned:new Set(),finalEvidence:null,transferCorrect:null,notesOpen:false,howOpen:false,lastAction:'',scorePulse:false,score:{pick:0,evidence:0,twist:0,transfer:0}};
  lastTick=performance.now();if(config.music)music.enable();else music.disable();render();main.focus({preventScroll:true});say('Misión iniciada. Elige un objeto para inspeccionarlo.');
}
function total(){return Math.min(100,Object.values(state.score).reduce((sum,v)=>sum+v,0));}
function hud(){const m=currentCase();return `<div class="hud"><div class="hud-title"><span class="eyebrow">EXPEDIENTE ${state.mode==='bottle'?'BOTELLA':'ETIQUETA'} ${String(state.caseIndex+1).padStart(2,'0')} · ${levelName[state.settings.difficulty]}</span><h1>${m.title}</h1></div><div class="counter ${state.settings.timed&&state.remaining<=20?'danger':''}" id="clock"><small>TIEMPO</small><span>${clockText()}</span></div><div class="counter"><small>INSPECCIONES</small>${state.inspections}/${state.settings.budget}</div><div class="counter score ${state.scorePulse?'bump':''}" id="score" aria-label="Puntos: ${total()} de 100"><small>PUNTOS</small>${total()}<i>/100</i></div><button class="quiet pause-control" data-action="pause" aria-label="Pausar partida">Ⅱ Pausa</button><button class="quiet settings-control" data-action="settings">Ajustes</button></div>`;}
// Evidence is scored only for clues seen on the object this check targets, and only when that object is the mission's real target
// (scoring never leaks which object is correct). Called both at the first commit (for the verdict screen) and again after the twist
// resolves, against whichever object the player actually holds at close — see revise().
function evidenceFor(objectId){
  const m=currentCase(),correct=objectId===m.target;
  const found=correct?m.evidence.filter(e=>state.seen.has(objectId+':'+e.id)):[];
  const missing=correct?m.evidence.filter(e=>!found.includes(e)):m.evidence;
  const points=found.reduce((sum,e)=>sum+e.points,0);
  const sufficient=correct&&m.evidence.filter(e=>e.core).every(e=>found.includes(e));
  return {objectId,correct,found,missing,points,sufficient};
}
function finalObjectId(){return state.initial.correct?state.initial.objectId:(state.revision==='recover'?currentCase().target:state.initial.objectId);}
function evidenceNote(){
  const ev=state.finalEvidence||evidenceFor(state.initial.objectId);
  if(!ev.correct)return'Las pruebas cuentan sobre el objeto que sostienes al cerrar el expediente; esta vez no era el correcto.';
  if(!ev.missing.length)return'Reuniste todas las pruebas relevantes de tu elección.';
  const base=ev.sufficient?'Pruebas suficientes.':'Faltó comprobar '+ev.missing.filter(e=>e.core).map(e=>e.label).join(' y ')+'.';
  const extra=ev.sufficient?' Sin comprobar: '+ev.missing.map(e=>e.label).join(', ')+'.':'';
  const recovered=state.revision==='recover'&&ev.points>0?' Contó lo que ya habías investigado antes de rectificar.':'';
  return (base+extra+recovered).trim();
}
function twistWhy(){const m=currentCase(),r=state.revision;return r==='scope'?'Mantuviste tu elección y limitaste lo que afirmas.':r==='recover'?'Corregiste por una razón válida: la nueva observación sí identifica qué objeto cumple la misión.':r==='stubborn'?'Mantuviste tu primera elección sin atender la nueva observación.':m.twistWhy[r];}
function breakdown(){const i=state.initial,s=state.score;return [{label:'Elección inicial',pts:s.pick,max:POINTS.pick,note:i.correct?'Elegiste el objeto correcto.':'No era el objeto buscado.'},{label:'Pruebas reunidas',pts:s.evidence,max:POINTS.evidence,note:evidenceNote()},{label:'Resolución del giro',pts:s.twist,max:POINTS.twist,note:twistWhy()},{label:'Transferencia',pts:s.transfer,max:POINTS.transfer,note:state.transferCorrect?'Aplicaste la regla a un caso nuevo.':'La regla no se aplicó en el caso nuevo.'}];}
function clockText(){if(!state.settings.timed)return '∞';const s=Math.ceil(state.remaining);return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;}
function zoneDots(object){return Object.keys(object.clues).map(z=>`<i class="${state.seen.has(object.id+':'+z)?'seen':''}"></i>`).join('');}
function hotspotButtons(object,mode){
  const rects=zoneRects[mode],tools=currentCase().tools;
  return Object.entries(rects).map(([id,r])=>{
    const key=object.id+':'+id,found=state.seen.has(key),label=tools.find(t=>t[0]===id)[2];
    const disabled=!found&&state.inspections===0;
    return `<button class="zone-hotspot ${found?'found':''}" style="top:${r.top}%;left:${r.left}%;width:${r.width}%;height:${r.height}%" data-action="inspect" data-id="${id}" ${disabled?'disabled':''} aria-label="${esc(label)} de ${esc(object.name)}${found?' (ya visto)':''}"><span class="zone-dot" aria-hidden="true">${found?'✓':'⌕'}</span></button>`;
  }).join('');
}
function render(focus){
  if(!state)return home();
  const m=currentCase();
  let content='';
  if(state.phase==='play'){
    const chosen=state.objects.find(o=>o.id===state.selected);
    const tools=m.tools;
    const zones=chosen?Object.keys(chosen.clues):[],seenHere=zones.filter(z=>state.seen.has(chosen.id+':'+z)).length,cur=!chosen?1:state.clues.length?3:2,left=state.inspections;
    const backTool=tools.find(t=>t[0]==='back'),backFound=chosen&&state.seen.has(chosen.id+':back'),backDisabled=chosen&&!backFound&&state.inspections===0;
    const steps=['Selecciona un objeto','Inspecciona detalles','Confirma tu elección'];
    content=`<div class="mission-brief"><span class="brief-icon" aria-hidden="true">⌕</span><div><span class="eyebrow">OBJETIVO</span><p>${m.brief}</p><button class="howto-btn" data-action="howto" aria-expanded="${state.howOpen}">¿Cómo se puntúa?</button>${state.howOpen?`<p class="howto">Máximo 100 por misión: <b>40</b> elegir bien · <b>30</b> pruebas relevantes · <b>20</b> resolver el giro con una razón válida · <b>10</b> aplicar la regla a un caso nuevo. Mirarlo todo, ir rápido o declarar más seguridad no suma. Si rectificas en el giro, lo que ya habías investigado sobre el objeto correcto también cuenta.</p>`:''}</div></div><ol class="steps" aria-label="Cómo jugar">${steps.map((s,i)=>`<li class="${i+1<cur?'done':i+1===cur?'now':''}" ${i+1===cur?'aria-current="step"':''}><span aria-hidden="true">${i+1<cur?'✓':i+1}</span>${s}</li>`).join('')}</ol><div class="status-row"><span class="chip ${chosen?'sel':''}">${chosen?'✓ '+esc(chosen.name):'Elige un objeto de la mesa'}</span><span class="chip">${left} de ${state.settings.budget} inspecciones</span></div><div class="table-layout"><section class="table" aria-label="Mesa de investigación"><div class="table-top"><span>LA MESA</span><span>TÓCALA PARA EXAMINARLA</span></div><div class="bottles ${state.objects.length===4?'four':''} ${chosen?'has-selection':''}">${state.objects.map((o,i)=>{const isSel=state.selected===o.id;const showBack=isSel&&state.viewBack;return `<div class="bottle-slot ${isSel?'active':''}"><div class="bottle-art"><div class="flip-inner ${showBack?'flipped':''}"><div class="face face-front"><button class="bottle-select" data-action="select" data-id="${o.id}" aria-pressed="${isSel}" aria-label="${isSel?'Seleccionada: ':'Seleccionar '}${esc(o.name)}">${isSel?'<span class="sel-badge">✓ Seleccionada</span>':''}${bottleSVG(o,'obj'+i,state.mode==='label')}</button>${isSel?hotspotButtons(o,state.mode):''}</div><div class="face face-back">${inspectionArt(o)}</div></div></div>${isSel?`<button class="flip-btn" data-action="flip" ${backDisabled?'disabled':''} aria-pressed="${showBack}" aria-label="${showBack?'Volver al frente de '+esc(o.name):backTool[2]+' de '+esc(o.name)}"><span aria-hidden="true">${showBack?'↺':'↻'}</span> ${showBack?'Ver el frente':'Girar la botella'}</button>`:''}<div class="bottle-meta"><span class="object-id">OBJETO ${String(i+1).padStart(2,'0')}</span><strong>${o.name}</strong><span class="zone-dots" aria-label="${Object.keys(o.clues).filter(z=>state.seen.has(o.id+':'+z)).length} de ${Object.keys(o.clues).length} zonas vistas">${zoneDots(o)}</span></div></div>`;}).join('')}</div>${chosen&&seenHere===0?`<p class="stage-hint">Toca una zona de ${esc(chosen.name)} o gírala para ver el dorso.</p>`:''}${state.lastClue?`<div class="insight" role="status"><span class="eyebrow">PISTA · ${esc(state.lastClue.objectName)}</span><p>${esc(state.lastClue.text)}</p><small>${esc(state.lastClue.title)}</small></div>`:''}</section><aside class="notebook ${state.notesOpen?'notes-open':''}" aria-labelledby="notebook-title"><span class="eyebrow">TU INVESTIGACIÓN</span><h2 id="notebook-title">Lo que encontraste</h2><button class="notes-toggle" data-action="notes" aria-expanded="${state.notesOpen}">${state.clues.length} pistas · ${state.notesOpen?'Ocultar':'Ver cuaderno'} <span aria-hidden="true">▾</span></button>${state.clues.length?state.clues.map(c=>{const key=c.objectId+':'+c.id,pinned=state.pinned.has(key);return `<div class="clue-entry ${pinned?'pinned':''}"><button class="pin-btn" data-action="pin" data-key="${key}" aria-pressed="${pinned}" aria-label="${pinned?'Quitar como razón principal':'Fijar como mi razón'}">⚑</button><b><span class="dot">●</span> ${esc(c.objectName)}</b><span>${esc(c.text)}</span></div>`;}).join(''):'<div class="clue-empty">Aquí aparecerán tus hallazgos.<br>Observaciones, no respuestas: tú decides qué importa.</div>'}</aside></div><div class="decision-bar"><div class="decision-copy"><strong>${chosen?`Tu elección: ${chosen.name}`:'¿Cuál resuelve la misión?'}</strong>${chosen?'Puedes confirmar ahora o seguir investigando.':'Selecciona un objeto para poder confirmar.'}</div><div class="wager" role="group" aria-label="Seguridad en tu elección (no cambia tus puntos)"><button data-action="confidence" data-id="cautious" aria-pressed="${state.confidence==='cautious'}">Tengo dudas</button><button data-action="confidence" data-id="firm" aria-pressed="${state.confidence==='firm'}">Me la juego</button></div><button class="primary" data-action="commit" ${!chosen?'disabled':''}>Confirmar elección →</button></div>`;
  }else if(state.phase==='pick'){
    const sel=state.objects.find(o=>o.id===state.initial.objectId),ok=state.initial.correct,ini=state.initial;
    const evidenceBox=ok?`<div class="evidence-box"><b>${ini.sufficient?'Pruebas suficientes':'Faltaron pruebas'} · +${state.score.evidence}/${POINTS.evidence}</b><ul>${m.evidence.map(e=>`<li class="${ini.found.includes(e)?'yes':'no'}"><span aria-hidden="true">${ini.found.includes(e)?'✓':'○'}</span>${ini.found.includes(e)?'Comprobaste':'No comprobaste'} ${e.label} <small>${ini.found.includes(e)?'+'+e.points:'0/'+e.points}</small></li>`).join('')}</ul>${ini.sufficient?'':`<p>Acertaste el objeto, pero faltó comprobar ${ini.missing.filter(e=>e.core).map(e=>e.label).join(' y ')}. Sin esa prueba, el acierto podría ser suerte.</p>`}</div>`:`<div class="evidence-box"><b>Pruebas · +0/${POINTS.evidence}</b><p>Las pruebas puntúan sobre el objeto correcto. Si ya lo investigaste, no se pierde: contará si rectificas en el giro.</p></div>`;
    content=`<section class="pick ${ok?'win':'miss'}"><div class="burst" aria-hidden="true">${ok?'<i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i>':''}<div class="result-emblem pop">${ok?'✓':'?'}</div></div><span class="eyebrow">TU ELECCIÓN · ${esc(sel.name)}</span><h2>${ok?'¡Objeto correcto!':'Casi. Esa no era.'}</h2><p class="points-pop ${ok?'':'zero'}">${ok?'+'+POINTS.pick:'+0'} puntos por el objeto</p><p class="pick-text">${ok?m.hit:m.miss[sel.id]}</p>${evidenceBox}<p class="open-note">El expediente sigue abierto: todavía falta una decisión.</p><div class="result-actions"><button class="primary" data-action="after-pick">Continuar →</button></div></section>`;
  }else if(state.phase==='twist'){
    const selected=state.objects.find(o=>o.id===state.initial.objectId);
    const targetSelected=state.initial.objectId===m.target;
    content=`<section class="twist"><div class="twist-art" aria-hidden="true">${bottleSVG(selected,'twist',state.mode==='label')}<span class="twist-symbol">?</span></div><div class="twist-content"><span class="eyebrow">02 / ALGO ACABA DE CAMBIAR</span><h2>${targetSelected?m.twist:'Antes de cerrar el expediente…'}</h2><p>${targetSelected?m.twistDetail:m.wrongTwist}</p><div class="twist-options">${(targetSelected?m.choices:[{id:'recover',icon:'↻',title:`Cambio mi elección a ${state.objects.find(o=>o.id===m.target).name}.`,detail:'La nueva observación es más relevante para la misión.'},{id:'stubborn',icon:'=',title:'Mantengo mi primera elección.',detail:'Mi impresión inicial me sigue convenciendo.'}]).map(c=>`<button class="twist-option" data-action="revise" data-id="${c.id}"><span class="symbol">${c.icon}</span><span><b>${c.title}</b><small>${c.detail}</small></span></button>`).join('')}</div></div></section>`;
  }else if(state.phase==='result'){
    const good=state.score.twist>0;const supported=state.initial.correct&&state.initial.hasEvidence;const clean=good&&(supported||state.revision==='recover');
    const why=twistWhy(),gain=state.score.twist;
    const title=clean?(state.revision==='recover'?'Cambiaste con una buena razón.':'Viste más allá de la apariencia.'):good?'La elección encaja. Falta la prueba.':'Una pista te puso a prueba.';
    const evidenceBonus=state.revision==='recover'&&state.score.evidence>0?`<p class="points-why evidence-bonus">+${state.score.evidence} puntos de pruebas, por lo que ya habías investigado antes de rectificar.</p>`:'';
    content=`<section class="result"><span class="eyebrow">03 / EXPEDIENTE ${clean?'RESUELTO':'PARA REVISAR'}</span><div class="result-emblem ${good?'pop':''}" aria-hidden="true">${clean?'⌕':'↻'}</div><h2>${title}</h2><p class="points-pop ${gain?'':'zero'}">${gain?'+20 puntos · Giro resuelto con razón':'+0 puntos · El giro quedó sin resolver bien'}</p><p class="points-why">${why}</p>${evidenceBonus}<p>${clean?'La clave fue distinguir lo que observaste de lo que aún no podías afirmar.':good?'Acertar la botella no basta: en tu primera elección faltó inspeccionar la evidencia que la distingue.':'La apariencia o la primera impresión pesaron más que la evidencia disponible. Puedes intentarlo con otra estrategia.'}</p><div class="result-rule"><span class="eyebrow">LLÉVATE UNA IDEA</span><p>${m.rule}</p><small>${m.ruleNote}</small></div><div class="result-stats"><div class="stat"><b>${state.settings.budget-state.inspections}</b>inspecciones usadas</div><div class="stat"><b>${state.initial.confidence==='firm'?'Me la juego':'Tengo dudas'}</b>tu confianza inicial</div><div class="stat"><b>${state.expired?'Reloj agotado':state.settings.timed?Math.ceil(state.settings.seconds-state.remaining)+' s':'Sin reloj'}</b>${state.settings.timed?'tiempo usado':'modo libre'}</div></div><details><summary>Quiero entenderlo mejor</summary><p>${m.technical}</p>${m.sourceLink?`<a href="${m.sourceLink.url}" target="_blank" rel="noopener">${esc(m.sourceLink.label)}</a>`:''}<p>Esta es una maqueta jugable de diseño. El reconocimiento es guionizado y el marcador es una regla editorial del juego; no utiliza el evaluador educativo preservado ni mide aprendizaje.</p></details><div class="result-actions"><button class="primary" data-action="transfer">Un último giro (+10) →</button><button class="quiet" data-action="retry">Repetir misión</button></div></section>`;
  }else if(state.phase==='transfer'){
    content=`<section class="result"><span class="eyebrow">04 / ¿TE LLEVAS LA REGLA?</span><div class="result-emblem" aria-hidden="true">↗</div><h2>${m.transfer}</h2><p>Otra situación. La misma capacidad de observar.</p><div class="transfer-options">${m.transferOptions.map((t,i)=>`<button data-action="transfer-answer" data-id="${i}">${t}</button>`).join('')}</div></section>`;
  }else if(state.phase==='complete'){
    const rows=breakdown();const next=nextCase();
    const nextButton=next?`<button class="primary" data-action="start" data-mode="${next.mode}" data-case-index="${next.index}">Siguiente misión: ${esc(campaign[next.mode][next.index].title)} ↗</button>`:'';
    content=`<section class="result complete"><span class="eyebrow">MISIÓN COMPLETA</span><div class="result-emblem ${state.transferCorrect?'pop':''}" aria-hidden="true">${state.transferCorrect?'✓':'↻'}</div><h2>${state.transferCorrect?'Te llevas la regla.':'Ahora tienes otra pista.'}</h2><p class="points-pop ${state.transferCorrect?'':'zero'}">${state.transferCorrect?'+10 puntos · Aplicaste la regla a un caso nuevo.':'+0 puntos · La regla no se aplicó en el caso nuevo; ahora sabes qué vigilar.'}</p><div class="final-score" aria-label="Marcador final: ${total()} de 100 puntos"><b>${total()}</b><span>/ 100 puntos</span></div><ul class="breakdown">${rows.map(r=>`<li class="${r.pts===r.max?'full':r.pts>0?'part':'none'}"><span class="mark" aria-hidden="true">${r.pts===r.max?'✓':r.pts>0?'◐':'–'}</span><span class="what"><b>${r.label}</b><small>${r.note}</small></span><span class="pts"><b>${r.pts}</b>/${r.max}</span></li>`).join('')}</ul><div class="result-rule"><span class="eyebrow">LA REGLA</span><p>${m.rule}</p></div><div class="result-actions">${nextButton}<button class="quiet" data-action="retry">Repetir esta misión</button><button class="quiet" data-action="home">Ver misiones</button></div><p class="game-note">${next?'':'Completaste todas las misiones disponibles por ahora. '}Marcador de juego: no mide aprendizaje. Al repetir, el marcador empieza de cero y las posiciones cambian.<br>Campaña: ${campaign.bottle.length} casos de botella y ${campaign.label.length} de etiqueta.</p></section>`;
  }else if(state.phase==='timeout'){
    content=`<section class="result"><span class="eyebrow">EL RELOJ LLEGÓ A CERO</span><div class="result-emblem" aria-hidden="true">◷</div><h2>El misterio sigue ahí.</h2><p>Tus hallazgos se conservan. Puedes terminar sin reloj o probar una partida con más tiempo.</p><div class="result-actions"><button class="primary" data-action="continue">Seguir sin reloj →</button><button class="quiet" data-action="settings">Dar más tiempo al próximo intento</button><button class="quiet" data-action="retry">Volver a empezar</button></div></section>`;
  }
  // scorePulse must be reset inside the mutate callback itself, right after hud() has read it for this render
  // (outside the callback, code runs before the DOM actually updates whenever a real view transition is active).
  // focus is deferred to withTransition's `after` hook — set during an active transition's update callback, it
  // gets silently dropped by the engine; `ready` guarantees the new tree is live and connected first.
  const phaseChanged=main.querySelector('.game')?.dataset.phase!==state.phase;
  withTransition(()=>{
    main.innerHTML=adornIcons(`<div class="game" data-phase="${state.phase}">${hud()}${content}</div>`);
    state.scorePulse=false;
  },()=>{
    if(phaseChanged)main.scrollIntoView({block:'start',behavior:'instant'});
    if(focus){const target=main.querySelector(focus);target?.focus({preventScroll:true});}
  });
}
function inspect(id){
  if(state.phase!=='play'||!state.selected)return;
  const object=state.objects.find(o=>o.id===state.selected),key=object.id+':'+id,clue=object.clues[id];
  if(!clue)return;
  const label=currentCase().tools.find(t=>t[0]===id)[2];
  if(!state.seen.has(key)){
    if(state.inspections===0)return;
    state.inspections--;state.seen.add(key);state.clues.push({...clue,objectName:object.name,objectId:object.id});
    state.lastAction=`Anotado en tu cuaderno: «${label}» de ${object.name}. Te quedan ${state.inspections} de ${state.settings.budget} inspecciones.`;
  }else state.lastAction=`Releíste «${label}» de ${object.name}. Releer no gasta inspección.`;
  state.lastClue={...clue,objectName:object.name,object,objectId:object.id,id};render(id==='back'?'[data-action="flip"]':`[data-action="inspect"][data-id="${id}"]`);say(`${state.lastAction} ${clue.text}`);
}
// Scoring is editorial (see DESIGN-HANDOFF.md). Evidence counts only for the committed object and only when it is the target,
// each clue once (state.seen is a Set), so repeating actions or inspecting everything cannot add points.
function commit(){
  if(state.phase!=='play'||!state.selected)return;
  const m=currentCase(),correct=state.selected===m.target;
  const ev=evidenceFor(state.selected);
  state.initial={objectId:state.selected,confidence:state.confidence,correct,hasEvidence:ev.sufficient,found:ev.found,missing:ev.missing,evidence:ev.points,sufficient:ev.sufficient};
  state.score.pick=correct?POINTS.pick:0;state.score.evidence=Math.min(ev.points,POINTS.evidence);state.scorePulse=correct||ev.points>0;
  state.phase='pick';render('[data-action="after-pick"]');
  say(correct?`¡Objeto correcto! Más ${POINTS.pick} puntos. Pruebas: ${state.score.evidence} de ${POINTS.evidence}.`:'Esa no era. Cero puntos por el objeto.');
}
// Revising re-scores "pruebas" against whichever object the player actually holds once the twist is settled, not just
// the first guess. A correct first pick is unaffected (same object, same seen-set). A well-founded recovery can now
// recoup evidence credit for clues the player already gathered on the real target before committing — see DESIGN-HANDOFF.md.
function revise(id){
  const valid=state.initial.correct?id==='scope':id==='recover';
  state.revision=id;
  const prevEvidence=state.score.evidence;
  const ev=evidenceFor(finalObjectId());
  state.finalEvidence=ev;
  state.score.evidence=Math.min(ev.points,POINTS.evidence);
  state.score.twist=valid?POINTS.twist:0;
  state.scorePulse=valid||state.score.evidence>prevEvidence;
  state.phase='result';music.suspend();render();main.focus();
  const bonus=state.score.evidence>prevEvidence?` También sumaste ${state.score.evidence-prevEvidence} puntos de pruebas que ya tenías.`:'';
  say(valid?`Más ${POINTS.twist} puntos por resolver el giro con una razón válida.${bonus}`:'Esta vez no hay puntos por el giro. Revisa por qué.');
}
function pause(){if(!state||state.paused)return;state.paused=true;music.suspend();pauseDialog.showModal();}
function resume(){if(!state)return;state.paused=false;lastTick=performance.now();pauseDialog.close();if(music.enabled)music.resume();}
function openSettings(){if(state){state.paused=true;music.suspend();}writeControls();settingsDialog.showModal();}
function writeControls(){for(const [id,value]of Object.entries(config)){const el=document.getElementById(id);if(!el)continue;if(el.type==='checkbox')el.checked=value;else el.value=value;}document.querySelector('#seconds-label').textContent=config.seconds+' segundos';document.querySelector('#budget-label').textContent=config.budget;}
function readControls(){config={difficulty:document.querySelector('#difficulty').value,timed:document.querySelector('#timed').checked,seconds:Number(document.querySelector('#seconds').value),budget:Number(document.querySelector('#budget').value),music:document.querySelector('#music').checked,volume:Number(document.querySelector('#volume').value)};music.setVolume();}
document.querySelector('#sound').addEventListener('click',()=>{if(music.enabled){music.disable();config.music=false;}else{config.music=true;music.enable();}});
let menuPaused = false;
document.addEventListener('cava-menu',e=>{
  if(e.detail.open&&state&&!state.paused){state.paused=true;music.suspend();menuPaused=true;}
  else if(!e.detail.open&&menuPaused){menuPaused=false;if(state&&!settingsDialog.open&&!pauseDialog.open){state.paused=false;lastTick=performance.now();if(music.enabled)music.resume();}}
});
settingsDialog.addEventListener('close',()=>{if(state){state.paused=false;lastTick=performance.now();if(music.enabled)music.resume();}else home();});
settingsDialog.addEventListener('input',()=>{document.querySelector('#seconds-label').textContent=document.querySelector('#seconds').value+' segundos';document.querySelector('#budget-label').textContent=document.querySelector('#budget').value;config.volume=Number(document.querySelector('#volume').value);music.setVolume();});
settingsDialog.addEventListener('click',e=>{const button=e.target.closest('[data-preset]');if(button){config={...config,...presets[button.dataset.preset]};writeControls();}});
document.querySelector('#save-settings').addEventListener('click',()=>{readControls();if(!config.music)music.disable();say('Ajustes guardados para la próxima misión.');});
document.querySelector('#resume').addEventListener('click',resume);
document.querySelector('#abandon').addEventListener('click',()=>{pauseDialog.close();home();});
pauseDialog.addEventListener('cancel',e=>{e.preventDefault();resume();});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&state&&!state.paused&&['play','pick','twist','transfer'].includes(state.phase))pause();});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&state&&!settingsDialog.open&&!pauseDialog.open&&['play','pick','twist','transfer'].includes(state.phase))pause();});
main.addEventListener('click',e=>{
  const button=e.target.closest('[data-action]');if(!button||button.disabled)return;const {action,id,mode,key,caseIndex}=button.dataset;
  if(action==='start')return start(mode,caseIndex!==undefined?Number(caseIndex):0);
  if(action==='home')return home();
  if(action==='settings')return openSettings();
  if(!state)return;
  if(action==='pause')return pause();
  if(action==='notes'){state.notesOpen=!state.notesOpen;return render('[data-action="notes"]');}
  if(action==='retry')return start(state.mode,state.caseIndex);
  if(action==='select'&&state.phase==='play'){const o=state.objects.find(x=>x.id===id);state.selected=id;state.lastClue=null;state.viewBack=false;state.lastAction=`Seleccionaste ${o.name}.`;say(state.lastAction);return render(`[data-action="select"][data-id="${id}"]`);}
  if(action==='inspect')return inspect(id);
  if(action==='flip'&&state.phase==='play'&&state.selected){state.viewBack=!state.viewBack;return inspect('back');}
  if(action==='pin'){state.pinned.has(key)?state.pinned.delete(key):state.pinned.add(key);return render(`[data-action="pin"][data-key="${key.replace(/"/g,'')}"]`);}
  if(action==='confidence'&&state.phase==='play'){state.confidence=id;return render(`[data-action="confidence"][data-id="${id}"]`);}
  if(action==='commit')return commit();
  if(action==='revise'&&state.phase==='twist')return revise(id);
  if(action==='transfer'&&state.phase==='result'){state.phase='transfer';music.suspend();render('[data-action="transfer-answer"]');return;}
  if(action==='transfer-answer'&&state.phase==='transfer'){const right=id==='0';state.transferCorrect=right;state.score.transfer=right?POINTS.transfer:0;state.scorePulse=right;progress[state.mode].add(currentCase().id);state.phase='complete';music.suspend();render();main.focus();say(right?`Más 10 puntos. Aplicaste la regla a un caso nuevo. Total: ${total()} de 100.`:`Esta vez 0 de 10 puntos en transferencia. Total: ${total()} de 100.`);return;}
  if(action==='after-pick'&&state.phase==='pick'){state.phase='twist';render('[data-action="revise"]');say('Nueva información. Puedes reconsiderar tu decisión.');return;}
  if(action==='howto'){state.howOpen=!state.howOpen;return render('[data-action="howto"]');}
  if(action==='continue'&&state.phase==='timeout'){state.settings.timed=false;state.phase=state.beforeTimeout;lastTick=performance.now();music.resume();render();main.focus();}
});
setInterval(()=>{
  const now=performance.now(),delta=(now-lastTick)/1000;lastTick=now;
  if(!state||state.paused||!state.settings.timed||!['play','twist'].includes(state.phase))return;
  state.remaining=Math.max(0,state.remaining-delta);
  const clock=document.querySelector('#clock');if(clock){clock.querySelector('span').textContent=clockText();clock.classList.toggle('danger',state.remaining<=20);}
  if(state.remaining===0){state.beforeTimeout=state.phase;state.phase='timeout';state.expired=true;music.suspend();render('[data-action="continue"]');say('Tiempo agotado. Puedes continuar sin reloj, conservando tus pistas.');}
},200);
music.updateButton();
home();
