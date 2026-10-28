// Study 1 - belief revision task, web version.
// Port of Study1_PsychoPy/study1_task.py: same procedure, screens, texts
// (config.js) and data columns. See the PsychoPy script for the procedure;
// comments here only cover what is specific to the web version.
'use strict';

// ---------------------------------------------------------------------------
// Stage and layout helpers. Positions and sizes are given in PsychoPy
// 'height' units (origin in the middle, y up; 1 unit = 1024 px).
// ---------------------------------------------------------------------------
const W = 1366, H = 1024, HALF_W = W / H / 2;
const PX = 1 / H;
const stage = document.getElementById('stage');
const X = x => W / 2 + x * H;
const Y = y => H / 2 - y * H;
const U = v => v * H;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
// A step that may never answer (e.g. inside claude.ai) gives up after ms.
const withTimeout = (promise, ms, fallback) =>
  Promise.race([Promise.resolve(promise).catch(() => fallback), sleep(ms).then(() => fallback)]);

// Errors are shown on the screen (red, top), so they can be reported.
function showError(message) {
  let box = document.getElementById('error');
  if (!box) {
    box = document.createElement('div');
    box.id = 'error';
    Object.assign(box.style, {position: 'fixed', left: '8px', right: '8px', top: '8px', zIndex: 99,
                              color: '#c00000', font: '14px Arial, sans-serif', whiteSpace: 'pre-wrap',
                              pointerEvents: 'none'});
    document.body.appendChild(box);
  }
  box.textContent += `${message}\n`;
}
window.addEventListener('error', event => showError(`Error: ${event.message}`));
window.addEventListener('unhandledrejection', event =>
  showError(`Error: ${event.reason && event.reason.message || event.reason}`));
const fmt = (s, values = {}) => s.replace(/\{(\w+)\}/g, (m, k) => (k in values ? values[k] : m));
const round = (v, digits) => Math.round(v * 10 ** digits) / 10 ** digits;
const pick = list => list[Math.floor(Math.random() * list.length)];
const shuffle = list => {
  for (let i = list.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [list[i], list[j]] = [list[j], list[i]];
  }
  return list;
};

function fit() {
  const scale = Math.min(window.innerWidth / W, window.innerHeight / H);
  stage.style.transform = `scale(${scale})`;
}
window.addEventListener('resize', fit);
fit();

function clear() {
  stage.innerHTML = '';
}
function add(tag, cls, parent = stage) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  parent.appendChild(e);
  return e;
}
function place(e, x, y, anchor) {
  e.style.left = `${X(x)}px`;
  e.style.top = `${Y(y)}px`;
  e.classList.add('at');
  if (anchor) e.classList.add(anchor);
  return e;
}
function text(str, x, y, {size = 0.03, color, bold, italic, width, anchor, cls = ''} = {}) {
  const e = add('div', `txt ${cls}`);
  e.textContent = str;
  e.style.fontSize = `${U(size)}px`;
  if (color) e.style.color = color;
  if (bold) e.style.fontWeight = 'bold';
  if (italic) e.style.fontStyle = 'italic';
  e.style.width = width ? `${U(width)}px` : 'max-content';
  return place(e, x, y, anchor);
}
function expText(str, x, y, opts = {}) {
  return text(str, x, y, Object.assign({color: CFG.EXP_COLOR, italic: true}, opts));
}
function sayText(str, x, y, opts = {}) {
  if (!str) return null;
  return expText(str, x, y, Object.assign({size: 0.026, anchor: 'top', width: 2 * HALF_W * 0.9,
                                           cls: 'say'}, opts));
}

// Images are preloaded, so their natural size is known: image() scales
// them to fit max_size (as load_image in the PsychoPy version).
const IMAGES = {};
function preloadImages(paths) {
  return Promise.all(paths.map(path => new Promise(resolve => {
    const img = new Image();
    img.onload = img.onerror = () => resolve();
    img.src = path;
    IMAGES[path] = img;
  })));
}
function image(path, x, y, maxSize, cls = '') {
  const known = IMAGES[path];
  if (known && !known.naturalWidth) {  // missing file
    return text(`[${path.split('/').pop()}]`, x, y, {size: maxSize * 0.2});
  }
  const e = add('img', `img ${cls}`);
  e.src = path;
  let w = maxSize, h = maxSize;
  if (known && known.naturalWidth) {
    const scale = maxSize / Math.max(known.naturalWidth, known.naturalHeight);
    w = known.naturalWidth * scale;
    h = known.naturalHeight * scale;
  }
  e.style.width = `${U(w)}px`;
  e.style.height = `${U(h)}px`;
  return place(e, x, y);
}
const media = {
  animal: a => `media/animals/${a}.png`,
  group: t => `media/groups/${t}.png`,
  team: t => `media/teams/${t}.png`,
  member: (t, g) => `media/members/${t}_${g}.png`,
};

function button(label, x, y, {color = '#111111', width} = {}) {
  const e = add('div', 'btn');
  e.textContent = label;
  e.dataset.color = color;
  e.style.background = color;
  if (width) {
    e.style.width = `${U(width)}px`;
    e.style.padding = '0';
  }
  return place(e, x, y);
}
function setColor(b, color) {
  b.dataset.color = color;
  b.style.background = color;
}
function setEnabled(b, on) {
  b.classList.toggle('disabled', !on);
}

// Taps: as in the PsychoPy version, a press counts; every screen first waits
// until the finger of the previous tap is lifted (wait_release).
let pointerDown = false;
let releaseWaiters = [];
document.addEventListener('pointerdown', () => { pointerDown = true; }, true);
const lifted = () => {
  pointerDown = false;
  releaseWaiters.forEach(resolve => resolve());
  releaseWaiters = [];
};
document.addEventListener('pointerup', lifted, true);
document.addEventListener('pointercancel', lifted, true);
async function released() {
  if (pointerDown) await new Promise(resolve => releaseWaiters.push(resolve));
  await sleep(60);  // let the click of that tap pass
}
function onTap(e, fn) {
  e.addEventListener('pointerdown', event => {
    event.preventDefault();
    event.stopPropagation();
    fn(event);
  });
}

// (i) icon: shows/hides what the experimenter can say (the 'say' texts).
let helpOn = CFG.SHOW_HELP;
stage.classList.toggle('help-on', helpOn);
function helpIcon() {
  const e = add('div');
  e.id = 'help';
  e.textContent = 'i';
  place(e, -HALF_W + 0.04, 0.46);
  onTap(e, () => {
    helpOn = !helpOn;
    stage.classList.toggle('help-on', helpOn);
  });
  return e;
}

// SVG layer for the boxes, arrows and ticks
const NS = 'http://www.w3.org/2000/svg';
function svgLayer(parent = stage) {
  const s = document.createElementNS(NS, 'svg');
  s.setAttribute('class', 'layer');
  s.setAttribute('viewBox', `0 0 ${W} ${H}`);
  parent.appendChild(s);
  return s;
}
function svgAdd(parent, tag, attrs) {
  const e = document.createElementNS(NS, tag);
  Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  parent.appendChild(e);
  return e;
}
function svgRect(parent, x, y, w, h, fill, {stroke = 'none', lineWidth = 0, ori = 0} = {}) {
  const attrs = {x: X(x) - U(w) / 2, y: Y(y) - U(h) / 2, width: U(w), height: U(h), fill,
                 stroke, 'stroke-width': lineWidth};
  if (ori) attrs.transform = `rotate(${ori} ${X(x)} ${Y(y)})`;
  return svgAdd(parent, 'rect', attrs);
}
function svgPolygon(parent, points, fill) {
  return svgAdd(parent, 'polygon', {points: points.map(([x, y]) => `${X(x)},${Y(y)}`).join(' '), fill});
}

// A row of n boxes in the box colour (as box_row in the PsychoPy version).
function boxRow(color, {n = CFG.N_BOXES, y = -0.2, nOpen = 1, arrow = true, width = null,
                        x0 = 0, parent = null} = {}) {
  const layer = parent || svgLayer();
  const g = svgAdd(layer, 'g', {});
  if (width === null) width = Math.min(n * 0.1 + (n - 1) * 0.02, 2 * HALF_W * 0.92);
  const w = width / (n + (n - 1) * 0.2);
  const gap = 0.2 * w;
  const h = w * 0.62;
  const line = w > 0.06 ? 1.5 : 1;
  for (let i = 0; i < n; i++) {
    const x = x0 + (i - (n - 1) / 2) * (w + gap);
    svgRect(g, x, y - h * 0.1, w, h, color, {stroke: '#333333', lineWidth: line});
    if (i < nOpen) {
      // open: dark opening, lid swung up around its right back corner
      svgRect(g, x, y + h * 0.33, w * 0.94, h * 0.1, '#1a1a1a');
      const angle = -40 * Math.PI / 180;
      const hinge = [x + w * 0.52, y + h * 0.4];
      const [dx, dy] = [-w * 0.52, h * 0.125];
      svgRect(g, hinge[0] + dx * Math.cos(angle) - dy * Math.sin(angle),
              hinge[1] + dx * Math.sin(angle) + dy * Math.cos(angle),
              w * 1.04, h * 0.25, color, {stroke: '#333333', lineWidth: line, ori: 40});
    }
    if (i === 0 && arrow) {
      const top = y + h * 3.1, tip = y + h * 2.0;
      svgPolygon(g, [[x - w * 0.08, top], [x + w * 0.08, top], [x + w * 0.08, tip + w * 0.18],
                     [x + w * 0.22, tip + w * 0.18], [x, tip], [x - w * 0.22, tip + w * 0.18],
                     [x - w * 0.08, tip + w * 0.18]], '#555555');
    }
    if (i >= nOpen) {
      svgRect(g, x, y + h * 0.4, w * 1.04, h * 0.25, color, {stroke: '#333333', lineWidth: line});
    }
    for (const side of [-1, 1]) {
      svgRect(g, x + side * w * 0.3, y + h * 0.2, w * 0.12, h * 0.14, '#c9a227');
    }
  }
  return g;
}

// Texts that only the web version needs
const WEB_TEXT = {
  en: {download: 'Download data (CSV)', again: 'New session', device: 'on this device',
       db_ok: 'All data are saved in the database of this page.',
       db_waiting: '{n} row(s) not saved in the database yet (no internet?). They are saved '
                   + 'automatically when this page is open with internet.',
       device_only: 'Data are kept on this device only: please download them (CSV).'},
  nl: {download: 'Download data (CSV)', again: 'Nieuwe sessie', device: 'op dit apparaat',
       db_ok: 'Alle data zijn opgeslagen in de database van deze pagina.',
       db_waiting: '{n} rij(en) nog niet opgeslagen in de database (geen internet?). Ze worden '
                   + 'automatisch opgeslagen zodra deze pagina met internet open is.',
       device_only: 'De data staan alleen op dit apparaat: download ze (CSV).'},
};

// ---------------------------------------------------------------------------
// Sounds (Web Audio; unlocked by the tap on Start)
// ---------------------------------------------------------------------------
// Sounds are played with Web Audio when it runs; otherwise (a downloaded
// copy opened as file://, or a frame that does not let Web Audio start, as
// on claude.ai) with <audio> elements, which are always prepared as well.
const Sound = {
  NAMES: ['team_chosen', 'wrong', 'correct'],
  ctx: null,
  buffers: {},
  elements: {},
  async init() {
    // <audio> elements first, unlocked by this tap (iOS)
    this.NAMES.forEach(name => {
      const audio = new Audio(`media/sounds/${name}.mp3`);
      audio.preload = 'auto';
      audio.muted = true;
      const p = audio.play();
      if (p) p.then(() => { audio.pause(); audio.currentTime = 0; audio.muted = false; })
        .catch(() => { audio.muted = false; });
      else audio.muted = false;
      this.elements[name] = audio;
    });
    if (location.protocol === 'file:') return;  // fetch is blocked there
    try {
      this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      this.ctx.resume().catch(() => {});
      await Promise.all(this.NAMES.map(async name => {
        const data = await (await fetch(`media/sounds/${name}.mp3`)).arrayBuffer();
        this.buffers[name] = await this.ctx.decodeAudioData(data);
      }));
    } catch (e) { /* the <audio> elements are used */ }
  },
  play(name) {
    if (this.ctx && this.ctx.state === 'running' && this.buffers[name]) {
      const source = this.ctx.createBufferSource();
      source.buffer = this.buffers[name];
      source.connect(this.ctx.destination);
      source.start();
    } else if (this.elements[name]) {
      const audio = this.elements[name];
      audio.muted = false;
      audio.currentTime = 0;
      const p = audio.play();
      if (p) p.catch(() => {});
    }
  },
};

// ---------------------------------------------------------------------------
// Session info, counterbalancing and texts
// ---------------------------------------------------------------------------
let info, lang, reasonSet, TXT, EXP, trials, swapSides;

function dateStr(d = new Date()) {  // as PsychoPy's data.getDateStr()
  const p = (v, n = 2) => String(v).padStart(n, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}_${p(d.getHours())}h` +
         `${p(d.getMinutes())}.${p(d.getSeconds())}.${p(d.getMilliseconds(), 3)}`;
}

async function assignList(age) {
  // Least used condition order (A-D) at this age and, within that order, the
  // least used list; ties at random. Completed sessions: 4 trials, IDs not
  // starting with "test".
  const {sessions} = await withTimeout(Data.completedSessions(), 5000,
                                       {source: 'none', sessions: []});
  const done = sessions
    .filter(s => Number(s.n) === CFG.CONDITIONS.length && String(s.age) === String(age)
                 && !String(s.participant).toLowerCase().startsWith('test'))
    .map(s => Number(s.cb_list));
  const usage = cb => [done.filter(d => (d - 1) % 4 === (cb - 1) % 4).length,
                       done.filter(d => d === cb).length, Math.random()];
  let best = null, bestUsage = null;
  for (let cb = 1; cb <= CFG.N_LISTS; cb++) {
    const u = usage(cb);
    if (!best || u[0] < bestUsage[0] || (u[0] === bestUsage[0] && (u[1] < bestUsage[1]
        || (u[1] === bestUsage[1] && u[2] < bestUsage[2])))) {
      best = cb;
      bestUsage = u;
    }
  }
  return best;
}

function makeTrials(cbList) {
  const idx = cbList - 1;
  const conditionOrder = CFG.LATIN[idx % 4].map(i => CFG.CONDITIONS[i]);
  const boxOrder = CFG.LATIN[Math.floor(idx / 4) % 4].map(i => CFG.BOX_ORDER[i]);
  swapSides = idx >= 16;
  return conditionOrder.map((cond, i) => {
    const box = boxOrder[i];
    const pair = CFG.BOXES[box];
    const [left, right] = swapSides ? [pair[1], pair[0]] : pair;
    const [group, quality] = cond.split('_');
    return {trial: i + 1, condition: cond, group_type: group, reason_quality: quality,
            box_color: box, animal_left: left, animal_right: right};
  });
}

const cap = s => s.charAt(0).toUpperCase() + s.slice(1);
const animalName = a => cap(lang === 'nl' ? CFG.DUTCH[a] : a);
function theAnimal(a) {
  const name = animalName(a).toLowerCase();
  if (lang === 'nl') return (CFG.NEUTER_NL.includes(a) ? 'het ' : 'de ') + name;
  return `the ${name}`;
}
function withArticle(a) {
  const name = animalName(a).toLowerCase();
  if (lang === 'nl') return `een ${name}`;
  return ('aeiou'.includes(name[0]) ? 'an ' : 'a ') + name;
}
function videoName(box, team, quality, claimed) {
  const row = CFG.BOX_ORDER.indexOf(box) * 8 + CFG.TEAMS.indexOf(team) * 4
            + CFG.BOXES[box].indexOf(claimed) * 2 + CFG.QUALITIES.indexOf(quality) + 1;
  const version = {numeric: 1, quality: 3}[reasonSet] + (lang === 'nl' ? 1 : 0);
  const words = [box, team, claimed, quality].map(w => cap(lang === 'nl' ? CFG.DUTCH[w] : w));
  return `${row}.${version}-${words.join('-')}`;
}

// ---------------------------------------------------------------------------
// Start form (the dialog of the PsychoPy version)
// ---------------------------------------------------------------------------
function startForm() {
  return new Promise(resolve => {
    clear();
    const page = add('div', 'form-page', document.body);
    const form = add('div', 'form', page);
    form.innerHTML = `
      <h1>Study 1</h1>
      <label>language <select id="f-lang"><option value="nl">Nederlands</option>
        <option value="en">English</option></select></label>
      <label>reasons (video version) <select id="f-reasons"><option>numeric</option>
        <option>quality</option></select></label>
      <label>participant <input id="f-participant" autocomplete="off"></label>
      <label>age <select id="f-age"><option value="" selected disabled>choose</option>
        ${CFG.AGES.map(a => `<option>${a}</option>`).join('')}</select></label>
      <label>gender <select id="f-gender"><option value=""></option><option>female</option>
        <option>male</option><option>other</option></select></label>
      <div class="btn start disabled" id="f-start">OK</div>
      <div class="note" id="f-note"></div>`;
    const $ = id => form.querySelector(`#${id}`);
    const start = $('f-start');
    $('f-age').addEventListener('change', () => setEnabled(start, $('f-age').value !== ''));

    const rows = Data.allRows();
    const note = $('f-note');
    const destination = Data.destination();
    note.textContent = destination === 'db'
      ? `Data are saved in this page's database (only you and editors can read them) and on `
        + `this device. ${Data.waiting() ? `${Data.waiting()} row(s) waiting to be saved. ` : ''}`
      : destination === 'sheets'
        ? `Google Sheets: ${Data.waiting()} row(s) waiting to be sent. `
        : 'Data are kept on this device only: download them at the end of each session. ';
    const downloadLink = (label, getRows, name) => {
      const link = add('a', '', note);
      link.href = '#';
      link.textContent = label;
      link.style.display = 'block';
      link.addEventListener('click', async event => {
        event.preventDefault();
        Data.download(name, await getRows());
      });
    };
    if (Data.db) {
      downloadLink('Download all data in the database (CSV)', () => Data.allDbRows(),
                   `study1_database_${dateStr()}.csv`);
    }
    if (rows.length) {
      downloadLink(`Download all data on this device (${rows.length} rows)`, () => rows,
                   `study1_all_data_${dateStr()}.csv`);
    }

    start.addEventListener('click', async () => {
      setEnabled(start, false);
      start.textContent = '...';
      const root = document.documentElement;
      const fullscreen = root.requestFullscreen || root.webkitRequestFullscreen;
      try {
        const p = fullscreen && fullscreen.call(root);
        if (p && p.catch) p.catch(() => {});
      } catch (e) { /* fullscreen is optional */ }
      await withTimeout(Sound.init(), 3000);
      const answers = {language: $('f-lang').value, reason_set: $('f-reasons').value,
                       participant: $('f-participant').value.trim(), age: $('f-age').value,
                       gender: $('f-gender').value};
      page.remove();
      // phones held upright: ask to turn sideways during the task
      const rotate = add('div', '', document.body);
      rotate.id = 'rotate';
      rotate.textContent = 'Draai het scherm een kwartslag (liggend).\n'
                         + 'Please turn the screen sideways (landscape).';
      rotate.style.whiteSpace = 'pre-line';
      document.body.classList.add('running');
      resolve(answers);
    });
  });
}

// ---------------------------------------------------------------------------
// Screens
// ---------------------------------------------------------------------------
async function experimenterScreen(str, color = null, say = null) {
  clear();
  helpIcon();
  expText(str, 0, 0.4, {size: 0.034, anchor: 'top', width: 2 * HALF_W * 0.85});
  sayText(say, 0, 0.16);
  expText(EXP.tap, 0, -0.44, {size: 0.026});
  if (color) boxRow(color, {y: -0.33});
  await released();
  await new Promise(resolve => stage.addEventListener('pointerdown', function handler(event) {
    if (event.target.id === 'help') return;
    stage.removeEventListener('pointerdown', handler);
    resolve();
  }));
}

// Happy sound while an area blinks (gold/green frame, with `glow` a gold glow
// behind it) and `pulse` grows and shrinks; `fade` is dimmed.
async function celebrate({x, y, w, h, fade = [], pulse = null, glow = true, dur = 1800}) {
  let glowBox = null;
  if (glow) {
    glowBox = add('div');
    Object.assign(glowBox.style, {width: `${U(w + 0.12)}px`, height: `${U(h + 0.12)}px`,
                                  background: '#ffd54f', borderRadius: `${U(0.04)}px`});
    place(glowBox, x, y);
    stage.prepend(glowBox);
  }
  const frame = add('div');
  Object.assign(frame.style, {width: `${U(w + 0.04)}px`, height: `${U(h + 0.04)}px`,
                              border: '12px solid #f5b700', pointerEvents: 'none'});
  place(frame, x, y);
  fade.forEach(e => { e.style.opacity = 0.25; });
  Sound.play('team_chosen');
  const t0 = performance.now();
  await new Promise(resolve => {
    const step = () => {
      const t = (performance.now() - t0) / 1000;
      const on = Math.floor(t / 0.15) % 2 === 0;
      if (glowBox) glowBox.style.opacity = on ? 0.7 : 0.15;
      frame.style.borderColor = on ? '#f5b700' : '#2e7d32';
      if (pulse) {  // transform (not the newer `scale` property): older iPads
        const f = 1 + 0.08 * Math.abs(Math.sin(t * Math.PI / 0.3));
        pulse.style.transform = `translate(-50%, -50%) scale(${f})`;
      }
      if (t * 1000 < dur) requestAnimationFrame(step);
      else resolve();
    };
    requestAnimationFrame(step);
  });
}

async function chooseGroup() {
  clear();
  const sides = Math.random() < 0.5 ? [...CFG.TEAMS] : [...CFG.TEAMS].reverse();
  const xs = [-HALF_W * 0.5, HALF_W * 0.5];
  const options = {};
  sides.forEach((team, i) => {
    const pic = image(media.group(team), xs[i], 0, 0.45);
    const frame = add('div', 'hit');
    Object.assign(frame.style, {width: `${U(0.5)}px`, height: `${U(0.5)}px`,
                                border: '4px solid grey'});
    place(frame, xs[i], 0);
    options[team] = {pic, frame, x: xs[i]};
  });
  await released();
  const t0 = performance.now();
  const team = await new Promise(resolve => {
    Object.entries(options).forEach(([t, o]) => onTap(o.frame, () => resolve(t)));
  });
  const rt = (performance.now() - t0) / 1000;
  stage.style.pointerEvents = 'none';
  const other = Object.entries(options).filter(([t]) => t !== team)
    .flatMap(([, o]) => [o.pic, o.frame]);
  options[team].frame.style.borderColor = 'transparent';
  await celebrate({x: options[team].x, y: 0, w: 0.5, h: 0.5, fade: other,
                   pulse: options[team].pic});
  stage.style.pointerEvents = '';
  return {team, left: sides[0], rt};
}

async function showTeams(own) {
  clear();
  helpIcon();
  const order = Math.random() < 0.5 ? [...CFG.TEAMS] : [...CFG.TEAMS].reverse();
  const other = CFG.TEAMS.find(t => t !== own);
  const names = {own: CFG.TEAM_NAMES[lang][own], other: CFG.TEAM_NAMES[lang][other]};
  const icon = 0.13;
  const w = Math.min(0.72, 2 * HALF_W - icon - 0.2);
  const h = w / 2.6;
  const rowW = icon + 0.03 + w;
  const leftEdge = -rowW / 2;
  text(fmt(TXT.teams, {first: CFG.TEAM_NAMES[lang][order[0]], second: CFG.TEAM_NAMES[lang][order[1]]}),
       0, 0.45, {size: 34 * PX, bold: true, width: 2 * HALF_W * 0.9});
  expText(fmt(EXP.chosen, {TEAM: names.own.toUpperCase()}), 0, 0.385,
          {size: 0.024, width: 2 * HALF_W * 0.85});
  sayText(`${fmt(EXP.chosen_say, {team: names.own})}\n${fmt(EXP.show_teams_say, names)}\n` +
          EXP.tap_team_say, -0.08, -0.3, {size: 0.021});
  const rows = {};
  order.forEach((team, i) => {
    const y = [0.19, -0.13][i];
    const box = add('div', 'hit');
    Object.assign(box.style, {width: `${U(rowW + 0.04)}px`, height: `${U(h + 0.04)}px`});
    place(box, 0, y);
    const iconImg = image(media.group(team), leftEdge + icon / 2, y, icon);
    const photo = image(media.team(team), leftEdge + icon + 0.03 + w / 2, y, w, 'rounded');
    rows[team] = {box, iconImg, photo, y};
  });
  const skip = button(TXT.continue, HALF_W - 0.13, -0.45, {color: CFG.EXP_BUTTON_COLOR});
  const result = {team_tap_first: '', team_tap_n_wrong: 0, team_tap_rt: ''};
  await released();
  const t0 = performance.now();
  await new Promise(resolve => {
    let busy = false;
    onTap(skip, () => resolve());
    Object.entries(rows).forEach(([team, row]) => onTap(row.box, async () => {
      if (busy) return;
      if (!result.team_tap_first) result.team_tap_first = team === own ? 'own' : 'other';
      if (team === own) {
        busy = true;
        result.team_tap_rt = round((performance.now() - t0) / 1000, 3);
        stage.style.pointerEvents = 'none';
        await celebrate({x: 0, y: row.y, w: rowW, h, glow: false, pulse: row.iconImg,
                         fade: [rows[other].iconImg, rows[other].photo]});
        stage.style.pointerEvents = '';
        resolve();
      } else {  // wrong team: 'oops' sound and a little shake
        result.team_tap_n_wrong++;
        Sound.play('wrong');
        [row.iconImg, row.photo].forEach(e => {
          e.classList.remove('shake');
          void e.offsetWidth;
          e.classList.add('shake');
        });
      }
    }));
  });
  return {top: order[0], tap: result};
}

async function stickerTask(memberGender) {
  clear();
  const sides = Math.random() < 0.5 ? [...CFG.TEAMS] : [...CFG.TEAMS].reverse();
  const photo = Math.min(0.42, HALF_W * 0.62);
  const x = Math.min(0.3, HALF_W * 0.45);
  const yPhoto = 0.07, yDots = 0.07 - photo / 2 - 0.06;
  const spacing = 0.075, radius = 0.026;
  text(TXT.stickers, 0, 0.4, {size: 42 * PX, bold: true, width: 2 * HALF_W * 0.9});
  const total = text('', 0, yDots - 0.07, {size: 18 * PX, color: '#777777'});
  const done = button(TXT.continue, 0, -0.38);
  const count = {moon: 0, sun: 0};
  const dots = {};
  sides.forEach((team, i) => {
    const xpos = [-x, x][i];
    image(media.member(team, memberGender), xpos, yPhoto, photo, 'rounded');
    dots[team] = [];
    for (let k = 0; k < CFG.N_STICKERS; k++) {
      const dot = add('div', 'hit');
      Object.assign(dot.style, {width: `${U(2 * radius)}px`, height: `${U(2 * radius)}px`,
                                borderRadius: '50%', border: '3px solid #777777', background: '#ffffff'});
      place(dot, xpos + (k - (CFG.N_STICKERS - 1) / 2) * spacing, yDots);
      dots[team].push(dot);
    }
  });
  const draw = () => {
    CFG.TEAMS.forEach(team => dots[team].forEach((dot, k) => {
      const filled = k + 1 <= count[team];
      dot.style.background = filled ? '#f5b800' : '#ffffff';
      dot.style.borderColor = filled ? '#111111' : '#777777';
    }));
    total.textContent = `${count.moon + count.sun} / ${CFG.N_STICKERS}`;
  };
  draw();
  await released();
  const t0 = performance.now();
  CFG.TEAMS.forEach(team => dots[team].forEach((dot, i) => onTap(dot, () => {
    const k = i + 1;
    const value = count[team] === k ? k - 1 : k;
    if (value + count.moon + count.sun - count[team] <= CFG.N_STICKERS) count[team] = value;
    draw();
  })));
  await new Promise(resolve => onTap(done, resolve));
  return {count, left: sides[0], rt: (performance.now() - t0) / 1000};
}

// Thinking child with a thought bubble (as ThoughtBubble in the PsychoPy version)
class ThoughtBubble {
  constructor(left, right) {
    const width = 0.25, pos = [0.05, 0.185];
    const inside = [pos[0] + 0.03 * width, pos[1] + 0.07 * width];
    this.left = left;
    this.right = right;
    image('media/thinking/bubble.png', pos[0], pos[1], width);
    image('media/thinking/child.png', -0.105, 0.065, 0.11);
    this.animals = {};
    [left, right].forEach(a => {
      this.animals[a] = image(media.animal(a), inside[0], inside[1], 0.1);
    });
    this.unsure = text('?', inside[0], inside[1], {size: 0.1, color: '#555555', bold: true});
    this.show(null);
  }
  show(thought, strength = 1) {
    Object.values(this.animals).forEach(e => { e.style.display = 'none'; });
    this.unsure.style.display = thought === 'dont_know' ? '' : 'none';
    if (thought && thought !== 'dont_know') {
      const e = this.animals[thought];
      e.style.display = '';
      e.style.transform = `translate(-50%, -50%) scale(${0.25 + 0.75 * strength})`;
      e.style.opacity = 0.15 + 0.85 * strength;  // fades toward the middle
    }
  }
  follow(pos, placed) {
    if (!placed) this.show(null);
    else if (pos === 0) this.show('dont_know');
    else this.show(pos < 0 ? this.left : this.right, Math.abs(pos));
  }
}

// Belief scale (as rating_scale in the PsychoPy version)
async function ratingScale(left, right, header, buttonText,
                           {first = null, binary = false, question = null, say = null,
                            thought = null, check = null, follow = false} = {}) {
  clear();
  helpIcon();
  const taskW = Math.min(1100 * PX, 0.92 * 2 * HALF_W);
  const halfLen = 1.05 * taskW / 2;
  const barH = 40 * PX, imgSize = 0.16;
  const yHead = 0.44, yQuestion = 0.35, yAnimal = 0.14, yName = 0.035, y = -0.07, yButton = -0.25;
  const animalX = taskW / 2 - imgSize / 2;

  expText(header, 0, yHead, {size: 16 * PX, width: 2 * HALF_W * 0.8});
  expText(info.participant, HALF_W - 16 * PX, 0.5 - 18 * PX, {size: 12 * PX, anchor: 'right'});
  const q = text(question === null ? TXT.question : question, 0, yQuestion,
                 {size: 42 * PX, bold: true, width: 2 * HALF_W * 0.9});
  const bubble = thought || follow ? new ThoughtBubble(left, right) : null;
  const imgL = image(media.animal(left), -animalX, yAnimal, imgSize);
  const imgR = image(media.animal(right), animalX, yAnimal, imgSize);
  const nameL = text(animalName(left), -animalX, yName, {size: 24 * PX, color: '#333333'});
  const nameR = text(animalName(right), animalX, yName, {size: 24 * PX, color: '#333333'});

  const scaleParts = [];
  const bar = add('div');
  Object.assign(bar.style, {
    width: `${U(2 * halfLen)}px`, height: `${U(barH)}px`, border: '2px solid #555555',
    borderRadius: '12px',
    background: `linear-gradient(to right, ${CFG.ANIMAL_COLORS[left]}, #ffffff 50%, ` +
                `${CFG.ANIMAL_COLORS[right]})`});
  place(bar, 0, y);
  scaleParts.push(bar);
  let veil = null;
  let firstLabel = null;
  if (first !== null) {
    const marker = add('div');
    Object.assign(marker.style, {width: '3px', height: '52px', background: '#777777'});
    place(marker, first * halfLen, y);
    firstLabel = text(TXT.first_answer, first * halfLen, y - (first === 0 ? 95 : 40) * PX,
                      {size: 14 * PX, color: '#777777'});
  }
  const middleMark = text('?', 0, y - 58 * PX, {size: 36 * PX, color: CFG.EXP_COLOR, bold: true});
  const handle = add('div');
  Object.assign(handle.style, {width: '45px', height: '45px', borderRadius: '50%',
                               border: '5px solid #111111', background: '#ffffff',
                               boxShadow: '0 2px 3px rgba(0, 0, 0, 0.12)', pointerEvents: 'none'});
  place(handle, 0, y);
  const done = button(buttonText, 0, yButton);
  scaleParts.push(done);
  let script = sayText(say, 0, yButton - 0.06);
  const skip = button(EXP.skip, HALF_W - 0.12, -0.45, {color: CFG.EXP_BUTTON_COLOR});
  skip.style.display = 'none';
  const zone = add('div', 'hit');
  Object.assign(zone.style, {width: `${U(2 * halfLen)}px`, height: '150px'});
  place(zone, 0, y);

  const result = {};
  let side = 0;
  if (binary) {
    // Binary belief: tap an animal (picture or name); the scale appears after
    scaleParts.forEach(e => { e.style.display = 'none'; });
    handle.style.display = middleMark.style.display = zone.style.display = 'none';
    await released();
    const t0 = performance.now();
    const choice = await new Promise(resolve => {
      [[left, -animalX], [right, animalX]].forEach(([animal, x]) => {
        const hit = add('div', 'hit');
        const top = yAnimal + imgSize / 2, bottom = yName - 0.04;
        Object.assign(hit.style, {width: `${U(imgSize + 0.04)}px`, height: `${U(top - bottom)}px`});
        place(hit, x, (top + bottom) / 2);
        onTap(hit, () => resolve(animal));
      });
    });
    stage.querySelectorAll('.hit').forEach(e => { if (e !== zone) e.remove(); });
    result.choice = choice;
    result.choice_rt = (performance.now() - t0) / 1000;
    q.textContent = TXT.sure;
    if (script) script.remove();
    script = sayText(fmt(EXP.ask_sure_say, {pl: CFG.PLURALS[lang][choice]}), 0, yButton - 0.06);
    // only the chosen half of the scale (up to the middle) can be used
    side = choice === left ? -1 : 1;
    (side < 0 ? [imgR, nameR] : [imgL, nameL]).forEach(e => { e.style.opacity = CFG.UNCHOSEN_OPACITY; });
    veil = add('div');
    Object.assign(veil.style, {width: `${U(halfLen) + 4}px`, height: `${U(barH) + 4}px`,
                               background: '#ffffff', opacity: 1 - CFG.UNCHOSEN_OPACITY,
                               pointerEvents: 'none'});
    place(veil, -side * (halfLen + 4 * PX) / 2, y);
    bar.after(veil);
    scaleParts.forEach(e => { e.style.display = ''; });
    zone.style.display = '';
  }

  let placed = first !== null;
  let pos = placed ? first : 0;
  let nTouches = 0, firstTouchRt = null, attempts = 0, busy = false;
  const draw = (ring = '#111111') => {
    handle.style.display = placed ? '' : 'none';
    handle.style.left = `${X(pos * halfLen)}px`;
    handle.style.borderColor = ring;
    middleMark.style.display = placed && pos === 0 ? '' : 'none';
    if (firstLabel) firstLabel.style.display = nTouches === 0 ? '' : 'none';
    if (bubble && follow) bubble.follow(pos, placed);
    else if (bubble) bubble.show(thought);
    setEnabled(done, placed);
    skip.style.display = check && attempts >= CFG.PRACTICE_SKIP_AFTER ? '' : 'none';
  };
  draw();
  await released();
  const t0 = performance.now();
  const setFrom = event => {
    const r = zone.getBoundingClientRect();
    pos = Math.max(-1, Math.min(1, ((event.clientX - r.left) / r.width) * 2 - 1));
    if (Math.abs(pos) < CFG.MIDDLE_SNAP || pos * side < 0) pos = 0;
    draw();
  };
  zone.addEventListener('pointerdown', event => {
    if (busy) return;
    const r = zone.getBoundingClientRect();
    const p = ((event.clientX - r.left) / r.width) * 2 - 1;
    if (side && p * side < -CFG.MIDDLE_SNAP) return;  // touch on the faded half
    event.preventDefault();
    zone.setPointerCapture(event.pointerId);
    nTouches++;
    if (firstTouchRt === null) firstTouchRt = (performance.now() - t0) / 1000;
    placed = true;
    setFrom(event);
  });
  zone.addEventListener('pointermove', event => {
    if (zone.hasPointerCapture(event.pointerId)) setFrom(event);
  });

  await new Promise(resolve => {
    const finish = extra => {
      Object.assign(result, {pos, rt: (performance.now() - t0) / 1000,
                             first_touch_rt: firstTouchRt, n_touches: nTouches}, extra);
      resolve();
    };
    onTap(skip, () => finish({attempts, correct: false}));
    onTap(done, async () => {
      if (busy) return;
      if (!check) return finish({});
      // practice: chime and green marker, or 'oops' and a red shaking marker
      busy = true;
      attempts++;
      if (attempts === 1) result.first_pos = pos;
      const right = check(pos);
      Sound.play(right ? 'correct' : 'wrong');
      draw(right ? '#2e9d4a' : '#d93025');
      if (!right) handle.classList.add('shake');
      await sleep(800);
      handle.classList.remove('shake');
      busy = false;
      if (right) return finish({attempts, correct: true});
      placed = false;
      draw();
    });
  });
  return result;
}

async function sliderTraining(left, right, names) {
  await ratingScale(left, right, EXP.train_demo, TXT.continue,
                    {question: TXT.practice_show, say: fmt(EXP.train_demo_say, names), follow: true});
  const result = {};
  const items = [['train_left', 'practice_really_left', left, p => p <= -CFG.REALLY],
                 ['train_right', 'practice_really_right', right, p => p >= CFG.REALLY],
                 ['train_middle', 'practice_dont_know', 'dont_know',
                  p => Math.abs(p) <= CFG.PRACTICE_MIDDLE]];
  for (const [key, column, thought, check] of items) {
    const answer = await ratingScale(left, right, fmt(EXP[key], names), TXT.continue,
                                     {question: '', say: fmt(EXP[`${key}_say`], names), thought, check});
    result[column] = round(answer.pos * 100, 1);
    result[`${column}_first`] = round(answer.first_pos * 100, 1);
    result[`${column}_attempts`] = answer.attempts;
    result[`${column}_correct`] = answer.correct;
  }
  return result;
}

// Video screen: tap the video to start it; afterwards Replay or Continue.
// Returns {plays, missing}.
async function playVideo(name) {
  clear();
  const vidW = Math.min(1.15, 0.92 * 2 * HALF_W), vidH = vidW * 9 / 16, vidY = 0.02;
  text(TXT.watch, 0, 0.42, {size: 42 * PX, bold: true});
  const box = add('div', 'video-box');
  Object.assign(box.style, {width: `${U(vidW)}px`, height: `${U(vidH)}px`});
  place(box, 0, vidY);
  const poster = add('img', '', box);
  poster.src = `media/posters/${name}.jpg`;
  const video = add('video', '', box);
  video.src = `media/videos/${name}.mp4`;
  video.preload = 'auto';
  video.playsInline = true;
  video.setAttribute('playsinline', '');
  video.style.display = 'none';
  const play = add('div', 'play', box);
  const yButtons = vidY - vidH / 2 - 66 * PX;
  const replay = button(TXT.replay, -0.11, yButtons, {color: '#616161'});
  const cont = button(TXT.continue, 0.11, yButtons);
  replay.style.display = cont.style.display = 'none';
  let plays = 0, missing = false, playing = false;

  const ended = () => {
    playing = false;
    replay.style.display = cont.style.display = '';
  };
  const start = () => {
    plays++;
    playing = true;
    play.style.display = 'none';
    replay.style.display = cont.style.display = 'none';
    poster.style.display = 'none';
    video.style.display = '';
    video.currentTime = 0;
    const p = video.play();
    if (p) p.catch(() => {});
  };
  video.addEventListener('ended', ended);
  const failed = () => {
    missing = true;
    playing = false;
    box.innerHTML = '';
    text(`${EXP.video_missing}\n${name}.mp4`, 0, vidY, {size: 0.035, color: 'red'});
    replay.style.display = cont.style.display = '';
  };
  video.addEventListener('error', failed);
  const skipKey = event => {
    if (event.key === 's' && playing) {
      video.pause();
      ended();
    }
  };
  document.addEventListener('keydown', skipKey);
  await released();
  // click (not pointerdown): browsers only start a video with sound after a click
  box.addEventListener('click', () => {
    if (!playing && plays === 0 && !missing) start();
  });
  await new Promise(resolve => {
    onTap(replay, () => {
      if (missing) plays++;
      else start();
    });
    onTap(cont, resolve);
  });
  document.removeEventListener('keydown', skipKey);
  video.pause();
  return {plays: Math.max(plays, missing ? 1 : 0), missing};
}

// Check questions after the video, on one screen, one step at a time
// (as check_screen in the PsychoPy version).
async function checkScreen(team, whose, left, right, claimed, box, quality, attempt) {
  clear();
  helpIcon();
  const c = CFG.PLURALS[lang][claimed];
  let rightReason, reasonLabel, ifRight, questionReason;
  if (reasonSet === 'numeric') {
    const nOpen = CFG.BOXES_OPENED[quality];
    rightReason = `${nOpen}_boxes`;
    reasonLabel = fmt(EXP.n_boxes, {n: nOpen});
    ifRight = fmt(EXP.if_right_number_say, {n: CFG.NUMBER_WORDS[lang][nOpen], c});
    questionReason = TXT.check_reason_numeric;
  } else {
    rightReason = quality === 'strong' ? 'looked' : 'told';
    reasonLabel = EXP[`reason_${rightReason}`];
    ifRight = EXP.if_right_reason_say;
    questionReason = TXT.check_reason;
  }
  const line = (s, y, size = 0.024) => expText(s, 0, y, {size, width: 2 * HALF_W * 0.92});
  line(`${fmt(EXP.check_head, {k: attempt, m: CFG.MAX_CHECKS})}   ${fmt(EXP.correct, {c: `${c} · ${reasonLabel}`})}`,
       0.465, 0.021);
  image(media.group(team), -0.25, 0.35, 0.1);
  const photo = image(media.team(team), 0.06, 0.35, 0.42);
  photo.style.borderRadius = '8px';
  const askBelief = line(fmt(EXP.ask, {q: fmt(TXT.check_belief, {whose, a: CFG.PLURALS[lang][left],
                                                                 b: CFG.PLURALS[lang][right]})}), 0.235);
  const askReason = line(fmt(EXP.ask, {q: questionReason}), 0.0);

  // answer options: question -> value -> {elements, hit area}
  const yB = 0.12, yR = -0.12;
  const sections = {belief: [askBelief], reason: [askReason], end: []};
  const options = {belief: {}, reason: {}};
  const option = (q, value, x, y, hw, hh, elements) => {
    const hl = add('div');
    Object.assign(hl.style, {width: `${U(2 * hw + 0.02)}px`, height: `${U(2 * hh + 0.02)}px`,
                             background: CFG.SELECTED_COLOR, borderRadius: `${U(0.02)}px`});
    place(hl, x, y);
    stage.prepend(hl);
    const hit = add('div', 'hit');
    Object.assign(hit.style, {width: `${U(2 * hw)}px`, height: `${U(2 * hh)}px`});
    place(hit, x, y);
    options[q][value] = {hl, hit};
    sections[q].push(...elements);
  };
  [[left, -0.22], [right, 0.22]].forEach(([animal, x]) =>
    option('belief', animal, x, yB, 0.1, 0.09, [image(media.animal(animal), x, yB, 0.14)]));
  if (reasonSet === 'numeric') {
    const layer = svgLayer();
    [[2, -0.25], [4, 0.25]].forEach(([n, x]) => {
      const g = svgAdd(layer, 'g', {});
      boxRow(CFG.BOX_DISPLAY[box], {y: yR - 0.01, nOpen: n, arrow: false, width: 0.42, x0: x, parent: g});
      option('reason', `${n}_boxes`, x, yR, 0.23, 0.07, [g]);
    });
  } else {
    [['looked', -0.22], ['told', 0.22]].forEach(([value, x]) =>
      option('reason', value, x, yR, 0.1, 0.08, [image(`media/reasons/${value}.png`, x, yR, 0.12)]));
  }
  const dontKnow = {
    belief: button(EXP.dont_know, 0, yB, {color: CFG.EXP_BUTTON_COLOR}),
    reason: button(EXP.dont_know, 0, yR - 0.105, {color: CFG.EXP_BUTTON_COLOR}),
  };
  sections.belief.push(dontKnow.belief);
  sections.reason.push(dontKnow.reason);
  const prompted = {self: button(EXP.said_self, -0.17, -0.31, {color: CFG.EXP_BUTTON_COLOR}),
                    prompted: button(EXP.said_prompted, 0.17, -0.31, {color: CFG.EXP_BUTTON_COLOR})};
  sections.end.push(...Object.values(prompted));
  const done = button(TXT.continue, 0, -0.42);
  sayText(`${fmt(EXP.if_right_belief_say, {whose, c})}\n${ifRight}`, 0, -0.455, {size: 0.019});

  const answer = {belief: null, reason: null, prompted: ''};
  const step = () => (answer.belief === null ? 'belief' : answer.reason === null ? 'reason' : 'end');
  const draw = () => {
    const now = step();
    Object.entries(sections).forEach(([name, elements]) => elements.forEach(e => {
      e.style.opacity = name === now ? 1 : CFG.CHECK_FADED_OPACITY;
    }));
    ['belief', 'reason'].forEach(q => {
      Object.entries(options[q]).forEach(([value, o]) => {
        o.hl.style.display = answer[q] === value ? '' : 'none';
        o.hl.style.opacity = (q === now ? 1 : CFG.CHECK_FADED_OPACITY) * 0.35;
      });
      setColor(dontKnow[q], answer[q] === 'dont_know' ? CFG.SELECTED_COLOR : CFG.EXP_BUTTON_COLOR);
    });
    Object.entries(prompted).forEach(([value, b]) =>
      setColor(b, answer.prompted === value ? CFG.SELECTED_COLOR : CFG.EXP_BUTTON_COLOR));
    setEnabled(done, now === 'end');
  };
  draw();
  await released();
  const t0 = performance.now();
  // questions not reached yet can't be tapped; answered ones can be changed
  const choose = (q, value) => {
    if (q !== step() && answer[q] === null) return;
    answer[q] = value;
    draw();
  };
  ['belief', 'reason'].forEach(q => {
    Object.entries(options[q]).forEach(([value, o]) => onTap(o.hit, () => choose(q, value)));
    onTap(dontKnow[q], () => choose(q, 'dont_know'));
  });
  Object.entries(prompted).forEach(([value, b]) => onTap(b, () => {
    if (step() !== 'end') return;
    answer.prompted = answer.prompted === value ? '' : value;
    draw();
  }));
  await new Promise(resolve => onTap(done, resolve));
  const rt = (performance.now() - t0) / 1000;
  const beliefCorrect = answer.belief === claimed;
  const reasonCorrect = answer.reason === rightReason;
  return {belief: answer.belief, belief_correct: beliefCorrect, reason: answer.reason,
          reason_correct: reasonCorrect, reason_prompted: answer.prompted,
          passed: beliefCorrect && reasonCorrect, rt: round(rt, 3)};
}

function tickMark(layer, x, y, r = 0.028) {
  svgAdd(layer, 'circle', {cx: X(x), cy: Y(y), r: U(r), fill: '#2e9d4a'});
  svgAdd(layer, 'polyline', {
    points: [[x - 0.45 * r, y], [x - 0.1 * r, y - 0.35 * r], [x + 0.5 * r, y + 0.4 * r]]
      .map(([px, py]) => `${X(px)},${Y(py)}`).join(' '),
    fill: 'none', stroke: '#ffffff', 'stroke-width': 5, 'stroke-linecap': 'round',
    'stroke-linejoin': 'round'});
}

// Solution at the end: the child's animal is in most boxes (always right).
async function solutionScreen(rounds) {
  clear();
  helpIcon();
  text(TXT.solution, 0, 0.45, {size: 34 * PX, bold: true, width: 2 * HALF_W * 0.9});
  expText(EXP.solution, 0, 0.395, {size: 0.022, width: 2 * HALF_W * 0.9});
  sayText(EXP.solution_say, 0, -0.465, {size: 0.019});
  const rowW = 0.8, rowX = -0.13, n = CFG.N_BOXES;
  const boxW = rowW / (n + (n - 1) * 0.2);
  const done = button(TXT.continue, 0, -0.4);
  done.style.display = 'none';
  const rows = rounds.map(([box, left, right, animal], i) => {
    const y = 0.27 - i * 0.17;
    const other = animal === left ? right : left;
    const contents = shuffle([...Array(CFG.SOLUTION_MAJORITY).fill(animal),
                              ...Array(n - CFG.SOLUTION_MAJORITY).fill(other)]);
    const closed = boxRow(CFG.BOX_DISPLAY[box], {y: y - 0.02, nOpen: 0, arrow: false, width: rowW, x0: rowX});
    const openLayer = svgLayer();
    boxRow(CFG.BOX_DISPLAY[box], {y: y - 0.02, nOpen: n, arrow: false, width: rowW, x0: rowX,
                                   parent: openLayer});
    const icons = contents.map((a, k) =>
      image(media.animal(a), rowX + (k - (n - 1) / 2) * 1.2 * boxW, y + 0.012, boxW * 0.95));
    const tick = svgLayer();
    tickMark(tick, 0.54, y + 0.04);
    image(media.animal(animal), 0.43, y, 0.11);
    [openLayer, tick, ...icons].forEach(e => { e.style.display = 'none'; });
    const hit = add('div', 'hit');
    Object.assign(hit.style, {width: `${U(1.2)}px`, height: `${U(0.16)}px`});
    place(hit, -0.01, y);
    return {hit, closed, opened: [openLayer, tick, ...icons], open: false};
  });
  await released();
  await new Promise(resolve => {
    rows.forEach(row => onTap(row.hit, () => {
      if (row.open) return;
      row.open = true;
      row.closed.style.display = 'none';
      row.opened.forEach(e => { e.style.display = ''; });
      const all = rows.every(r => r.open);
      Sound.play(all ? 'team_chosen' : 'correct');
      if (all) done.style.display = '';
    }));
    onTap(done, resolve);
  });
}

async function endScreen(sheetsLine, sessionRows, filename) {
  clear();
  helpIcon();
  const web = WEB_TEXT[lang];
  expText(fmt(EXP.end, {n: trials.length, file: `${filename} (${web.device})`}) + sheetsLine,
          0, 0.4, {size: 0.034, anchor: 'top', width: 2 * HALF_W * 0.85});
  sayText(EXP.end_say, 0, -0.05);
  const download = button(web.download, -0.2, -0.35, {color: CFG.EXP_BUTTON_COLOR});
  const again = button(web.again, 0.2, -0.35, {color: CFG.EXP_BUTTON_COLOR});
  await released();
  onTap(download, () => Data.download(filename, sessionRows()));
  onTap(again, () => window.location.reload());
}

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------
async function main() {
  Data.initClaude();
  await Promise.race([Data.ready, sleep(2000)]);  // claude.ai database, if any
  Data.startRetrying();
  const images = [
    ...['elephant', 'lion', 'dog', 'cat', 'rhino', 'turtle', 'cow', 'pig'].map(media.animal),
    ...CFG.TEAMS.flatMap(t => [media.group(t), media.team(t), media.member(t, 'female'),
                               media.member(t, 'male')]),
    'media/thinking/bubble.png', 'media/thinking/child.png',
    'media/reasons/looked.png', 'media/reasons/told.png'];
  await preloadImages(images);

  info = await startForm();
  lang = info.language;
  reasonSet = info.reason_set;
  TXT = CFG.TEXT[lang];
  EXP = CFG.EXP_TEXT[lang];
  document.documentElement.lang = lang;
  const cbList = await assignList(info.age);
  info.order = CFG.ORDER_NAMES[(cbList - 1) % 4];
  info.cb_list = cbList;
  info.date = dateStr();
  info.app = 'web';
  trials = makeTrials(cbList);
  const filename = `${info.participant}_${info.date}.csv`;

  const sessionStart = performance.now();
  const minutes = () => round((performance.now() - sessionStart) / 60000, 2);
  await experimenterScreen(fmt(EXP.start, {p: info.participant, o: info.order}), null, EXP.start_say);
  const group = await chooseGroup();
  const childTeam = group.team;
  const otherTeam = CFG.TEAMS.find(t => t !== childTeam);
  const ownName = CFG.TEAM_NAMES[lang][childTeam];

  const teams = await showTeams(childTeam);

  const memberGender = ['female', 'male'].includes(info.gender) ? info.gender : pick(['female', 'male']);
  const [thisSg, pl] = CFG.MEMBER_WORDS[lang][memberGender];
  await experimenterScreen(fmt(EXP.sticker_intro, {n: CFG.N_STICKERS}), null,
                           fmt(EXP.sticker_intro_say, {pl, this_sg: thisSg}));
  const stickers = await stickerTask(memberGender);
  const session = {child_team: childTeam, team_pic_left: group.left,
                   team_choice_rt: round(group.rt, 3), teams_pic_top: teams.top, ...teams.tap,
                   sticker_member_gender: memberGender, sticker_pic_left: stickers.left,
                   stickers_to_sun_member: stickers.count.sun,
                   stickers_to_moon_member: stickers.count.moon,
                   sticker_rt: round(stickers.rt, 3)};
  ['really_left', 'really_right', 'dont_know'].forEach(item =>
    ['', '_first', '_attempts', '_correct'].forEach(suffix => { session[`practice_${item}${suffix}`] = ''; }));

  const solutions = [];
  for (const t of trials) {
    const left = t.animal_left, right = t.animal_right, box = t.box_color;
    const names = {pl_l: CFG.PLURALS[lang][left], pl_r: CFG.PLURALS[lang][right],
                   a_l: withArticle(left), a_r: withArticle(right),
                   l: animalName(left).toLowerCase(), r: animalName(right).toLowerCase(),
                   the_l: theAnimal(left), the_r: theAnimal(right)};
    const firstRound = t.trial === 1;
    const setup = firstRound ? 'setup_first' : 'setup';
    await experimenterScreen(
      fmt(EXP[setup], {t: t.trial, n: trials.length, k: CFG.N_BOXES,
                       color: lang === 'nl' ? CFG.COLOR_ADJ_NL[box] : box, ...names}),
      CFG.BOX_DISPLAY[box], fmt(EXP[`${setup}_say`], names));

    // Practice with the scale (first round only), then open the first box
    let openSay = EXP.open_box_say;
    if (firstRound) {
      Object.assign(session, await sliderTraining(left, right, names));
      openSay = `${EXP.train_end_say}\n${openSay}`;
    }
    await experimenterScreen(EXP.open_box, CFG.BOX_DISPLAY[box], openSay);

    const header = s => fmt(EXP.header, {t: t.trial, n: trials.length, s,
                                         color: cap(CFG.COLOR_NAMES[lang][box])});

    // Initial belief: binary choice, then how sure on the scale
    const rating1 = await ratingScale(left, right, header(1), TXT.continue,
                                      {binary: true, say: fmt(EXP.ask_binary_say, names),
                                       follow: CFG.BUBBLE_IN_TEST});
    const r1 = rating1.pos;
    const choice = rating1.choice;

    // Video: the team states the belief opposite to the child's choice
    const claimed = choice === left ? right : left;
    const videoTeam = t.group_type === 'ingroup' ? childTeam : otherTeam;
    const whose = EXP[videoTeam === childTeam ? 'your_team' : 'other_team'];
    const teamName = CFG.TEAM_NAMES[lang][videoTeam];
    const vid = videoName(box, videoTeam, t.reason_quality, claimed);
    await experimenterScreen(fmt(EXP.before_video, {team: teamName, whose}), null,
                             fmt(EXP.before_video_say, {team: teamName, whose, own: ownName, ...names}));
    let video = await playVideo(vid);
    let nPlays = video.plays;

    // Check questions; if the answer is wrong the video is shown again
    const nBoxes = reasonSet === 'numeric' ? CFG.BOXES_OPENED[t.reason_quality] : null;
    const c = CFG.PLURALS[lang][claimed];
    const why = nBoxes ? fmt(EXP.why_numeric, {n: CFG.NUMBER_WORDS[lang][nBoxes], c})
                       : fmt(EXP[`why_${t.reason_quality}`], {c});
    const checks = {};
    for (let k = 1; k <= CFG.MAX_CHECKS; k++) CFG.CHECK_FIELDS.forEach(f => { checks[`check${k}_${f}`] = ''; });
    let attempt, result;
    for (attempt = 1; attempt <= CFG.MAX_CHECKS; attempt++) {
      if (attempt > 1) {
        await experimenterScreen(EXP.repeat, null, EXP.repeat_say);
        video = await playVideo(vid);
        nPlays += video.plays;
      }
      result = await checkScreen(videoTeam, whose, left, right, claimed, box, t.reason_quality, attempt);
      CFG.CHECK_FIELDS.forEach(f => { checks[`check${attempt}_${f}`] = result[f]; });
      if (result.passed) break;
    }
    if (attempt > CFG.MAX_CHECKS) attempt = CFG.MAX_CHECKS;

    // Summary of the team's belief; the toy animal goes on the team logo
    await experimenterScreen(
      (result.passed ? '' : fmt(EXP.give_up, {m: CFG.MAX_CHECKS}))
        + fmt(EXP.summary, {animal: animalName(claimed).toLowerCase(), team: teamName}),
      null, fmt(EXP.summary_say, {whose, c, why}));

    // Second belief; the handle starts at the first answer
    let how, said;
    if (r1 === 0) {
      how = 'dont_know';
      said = choice;
    } else {
      how = Math.abs(r1) >= CFG.REALLY ? 'really' : 'kind_of';
      said = r1 < 0 ? left : right;
    }
    const last = t.trial === trials.length;
    const rating2 = await ratingScale(left, right, header(2), last ? TXT.finish : TXT.next,
                                      {first: r1, follow: CFG.BUBBLE_IN_TEST,
                                       say: fmt(EXP.ask_final_say, {how: EXP.how[how],
                                                                    pl: CFG.PLURALS[lang][said]})});
    const r2 = rating2.pos;
    const finalAnimal = r2 === 0 ? choice : (r2 < 0 ? left : right);  // middle: first choice
    solutions.push([box, left, right, finalAnimal]);

    const rt3 = v => (v === null || v === undefined ? null : round(v, 3));
    const sign = claimed === right ? 1 : -1;  // positive = toward claimed animal
    const row = {
      ...info, ...session, swap_sides: swapSides, ...t,
      belief1_choice: choice,
      belief1_choice_side: choice === left ? 'left' : 'right',
      belief1_choice_rt: round(rating1.choice_rt, 3),
      video_team: videoTeam, claimed_animal: claimed,
      video_file: `${vid}.mp4`, video_missing: video.missing, video_n_plays: nPlays,
      check_n_attempts: attempt, check_passed: result.passed,
      ...checks,
      rating1_raw: round(r1 * 100, 1),
      rating1_toward_claim: round(sign * r1 * 100, 1),
      rating1_on_chosen_side: sign * r1 < 0,
      rating1_rt: round(rating1.rt, 3),
      rating1_first_touch_rt: rt3(rating1.first_touch_rt),
      rating1_n_touches: rating1.n_touches,
      rating2_raw: round(r2 * 100, 1),
      rating2_toward_claim: round(sign * r2 * 100, 1),
      rating2_rt: round(rating2.rt, 3),
      rating2_first_touch_rt: rt3(rating2.first_touch_rt),
      rating2_n_touches: rating2.n_touches,
      change_toward_claim: round(sign * (r2 - r1) * 100, 1),
      solution_animal: finalAnimal,
      minutes_since_start: minutes(),
      session_duration_min: '',  // filled in at the end
    };
    Data.saveRow(row);
  }

  // Solution: the child's animal was always right
  await solutionScreen(solutions);

  // Duration from the first screen to the last (the end screen)
  Data.addSessionDuration(info, minutes());
  let sheetsLine = '';
  const destination = Data.destination();
  const waiting = destination ? await withTimeout(Data.send(5000), 6000, Data.waiting()) : 0;
  if (Data.destination() === 'db') {
    sheetsLine = `\n\n${waiting ? fmt(WEB_TEXT[lang].db_waiting, {n: waiting}) : WEB_TEXT[lang].db_ok}`;
  } else if (Data.destination() === 'sheets') {
    sheetsLine = `\n\n${waiting ? fmt(EXP.sheets_waiting, {n: waiting}) : EXP.sheets_ok}`;
  } else {
    sheetsLine = `\n\n${WEB_TEXT[lang].device_only}`;
  }
  await endScreen(sheetsLine, () => Data.sessionRows(info), filename);
}

main();
