// Mood explorer: the national-mood slider, live counts, the municipal map and a field of
// 1,785 dots (one per voting district) that slide and turn red as turnout falls.
// All maths mirrors dashboard/data.py (district_turnout, municipality_turnout, expected_ballots).
// Runs in the browser, so the dots animate instead of the page reloading.
export default function (component) {
  const { data, parentElement, setStateValue, setTriggerValue } = component;
  if (!data) return;
  if (parentElement.__mood) { parentElement.__mood.refresh(data); return; }

  const SVGNS = 'http://www.w3.org/2000/svg';
  const C = { bg: '#141413', panel: '#1f1f1d', ink: '#ffffff', ink2: '#c3c2b7', muted: '#8f8d86', grid: '#34332f',
              blue: '#3987e5', blueSoft: '#86b6ef', red: '#e66767', redHot: '#ff6b6b', mid: '#4a4944', orange: '#f07a4a' };
  const root = parentElement.querySelector('.mx');
  const $ = (sel) => root.querySelector(sel);
  const el = (tag, attrs = {}, parent) => {
    const e = document.createElementNS(SVGNS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    if (parent) parent.appendChild(e);
    return e;
  };
  const fmt = (n) => Math.round(n).toLocaleString('en-US');
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------------- data ----------------
  const D = data;
  const munis = D.munis;                                    // sorted: lowest local position first
  const muniIndex = Object.fromEntries(munis.map((m, i) => [m.code, i]));
  const vds = D.vds.map((r, i) => ({ code: r[0], m: r[1], local: r[2], beta: r[3], reg: r[4], venue: r[5], t21: r[6],
                                     pLow: r[7], p10: r[8], p90: r[9], i }));
  const regTotal = vds.reduce((s, v) => s + v.reg, 0);
  let level = D.level, threshold = D.threshold, mapMode = 'risk', hoverMuni = null;

  function chanceAtOrBelow(P) {                      // share of simulations with turnout <= P
    const q = D.quantiles; if (P <= q[0]) return 0; if (P >= q[q.length - 1]) return 1;
    let lo = 0, hi = q.length - 1;
    while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (q[mid] <= P) lo = mid; else hi = mid; }
    return (lo + (P - q[lo]) / (q[hi] - q[lo])) / (q.length - 1);
  }
  const districtTurnout = (v, P) => Math.min(100, Math.max(0, P + v.local + (v.beta - 1) * (P - D.central)));

  function compute(P, thr) {
    const sumT = new Float64Array(munis.length), sumW = new Float64Array(munis.length);
    const belowN = new Int32Array(munis.length), belowW = new Float64Array(munis.length);
    let n = 0, voters = 0;
    for (const v of vds) {
      v.t = districtTurnout(v, P);
      sumT[v.m] += v.t * v.reg; sumW[v.m] += v.reg;
      v.below = v.t < thr;
      if (v.below) { n += 1; voters += v.reg; belowN[v.m] += 1; belowW[v.m] += v.reg; }
    }
    let ballots = 0;
    const muniT = munis.map((m, i) => { const t = sumT[i] / sumW[i]; ballots += m.reg2026 * t / 100; return t; });
    return { n, voters, ballots, muniT, belowN, belowShare: munis.map((m, i) => belowW[i] / sumW[i]) };
  }

  // ---------------- controls ----------------
  const range = $('#mx-range'), thrRange = $('#mx-thr');
  range.min = 30; range.max = 50; range.step = 0.5; range.value = level;
  thrRange.min = 10; thrRange.max = 40; thrRange.step = 1; thrRange.value = threshold;
  const marks = $('.mx-marks');
  const pos = (v) => ((v - 30) / 20) * 100;
  let lastV = -99, lastRow = 0;
  D.marks.map((m) => [m[0], m[1]])
    .sort((a, b) => a[1] - b[1]).forEach(([label, v]) => {
    const b = document.createElement('button');
    const row = v - lastV < 7 ? 1 - lastRow : 0;          // stagger labels that would collide
    lastV = v; lastRow = row;
    b.className = 'mx-mark' + (row ? ' row2' : ''); b.style.left = pos(v) + '%';
    b.innerHTML = `<span class="tick"></span><span class="mlabel">${label}<br><b>${v.toFixed(1)}%</b></span>`;
    b.onclick = () => { range.value = Math.round(v * 2) / 2; onLevel(true); };
    marks.appendChild(b);
  });
  range.addEventListener('input', () => onLevel(false));
  range.addEventListener('change', () => onLevel(true));
  thrRange.addEventListener('input', () => onThreshold(false));
  thrRange.addEventListener('change', () => onThreshold(true));
  root.querySelectorAll('.mx-toggle button').forEach((b) => b.addEventListener('click', () => {
    mapMode = b.dataset.mode;
    root.querySelectorAll('.mx-toggle button').forEach((x) => x.classList.toggle('on', x === b));
    render(true);
  }));

  function onLevel(commit) {
    level = parseFloat(range.value);
    render(true);
    if (commit) setStateValue('level', level);
  }
  function onThreshold(commit) {
    threshold = parseInt(thrRange.value, 10);
    render(true);
    if (commit) setStateValue('threshold', threshold);
  }

  // ---------------- map ----------------
  const map = $('#mx-map');
  const lons = [], lats = [];
  D.geo.forEach((g) => g.rings.forEach((r) => r.forEach(([x, y]) => { lons.push(x); lats.push(y); })));
  const minLon = Math.min(...lons), maxLon = Math.max(...lons), minLat = Math.min(...lats), maxLat = Math.max(...lats);
  const kx = Math.cos((((minLat + maxLat) / 2) * Math.PI) / 180);
  const MW = 520, pad = 12;
  const scale = (MW - 2 * pad) / ((maxLon - minLon) * kx);
  const MH = Math.round((maxLat - minLat) * scale + 2 * pad);
  map.setAttribute('viewBox', `0 0 ${MW} ${MH}`);
  const px = (lon) => pad + (lon - minLon) * kx * scale;
  const py = (lat) => pad + (maxLat - lat) * scale;
  const shapes = {};
  const gShapes = el('g', {}, map), gLabels = el('g', { class: 'labels' }, map);
  D.geo.forEach((g) => {
    const d = g.rings.map((r) => 'M' + r.map(([x, y]) => `${px(x).toFixed(1)},${py(y).toFixed(1)}`).join('L') + 'Z').join('');
    const p = el('path', { d, class: 'muni', 'data-code': g.code }, gShapes);
    p.addEventListener('mouseenter', () => setHover(g.code));
    p.addEventListener('mouseleave', () => setHover(null));
    p.addEventListener('click', () => setTriggerValue('open', g.code));
    shapes[g.code] = p;
  });
  const labelEls = {};
  D.labels.forEach((l) => {
    const t = el('text', { x: px(l.lon).toFixed(1), y: py(l.lat).toFixed(1), class: 'mlab' }, gLabels);
    t.textContent = munis[muniIndex[l.code]].name;
    const c = el('text', { x: px(l.lon).toFixed(1), y: (py(l.lat) + 13).toFixed(1), class: 'mcount' }, gLabels);
    labelEls[l.code] = c;
  });

  function mix(a, b, t) {
    const pa = a.match(/\w\w/g).map((h) => parseInt(h, 16)), pb = b.match(/\w\w/g).map((h) => parseInt(h, 16));
    return '#' + pa.map((x, i) => Math.round(x + (pb[i] - x) * t).toString(16).padStart(2, '0')).join('');
  }
  function mapColour(i, r) {
    if (mapMode === 'risk') {                     // share of the municipality's voters in low-turnout districts
      const s = Math.min(1, r.belowShare[i] / 0.35);
      return s === 0 ? '#2b2b28' : mix('#4a2f2e', C.redHot, Math.sqrt(s));
    }
    if (mapMode === 'chance') {                   // simulated chance of falling below its own 2021 turnout
      const s = Math.max(0, Math.min(1, (munis[i].pBelow2021 - 0.5) / 0.5));
      return mix('#2b2b28', C.redHot, s);
    }
    const rel = Math.max(-3, Math.min(3, r.muniT[i] - level)) / 3;    // above / below province
    return rel < 0 ? mix('#3a3936', C.red, -rel) : mix('#3a3936', C.blue, rel);
  }

  // ---------------- dot field ----------------
  const field = $('#mx-field');
  const FW = 760, rowH = 29, top = 24, left = 150, right = 70;
  const FH = top + rowH * munis.length + 44;
  field.setAttribute('viewBox', `0 0 ${FW} ${FH}`);
  const X0 = 0, X1 = 80;
  const fx = (t) => left + ((Math.min(X1, t) - X0) / (X1 - X0)) * (FW - left - right);
  const gGrid = el('g', {}, field), gRows = el('g', {}, field), gDots = el('g', {}, field), gTop = el('g', {}, field);
  for (let t = 0; t <= 80; t += 10) {
    el('line', { x1: fx(t), x2: fx(t), y1: top - 6, y2: FH - 40, class: 'grid' }, gGrid);
    const lab = el('text', { x: fx(t), y: FH - 6, class: 'axis' }, gGrid); lab.textContent = t + '%';
  }
  const rowEls = munis.map((m, i) => {
    const y = top + i * rowH + rowH / 2;
    const band = el('rect', { x: 0, y: y - rowH / 2, width: FW, height: rowH, class: 'band' }, gRows);
    const name = el('text', { x: left - 12, y: y + 4, class: 'rowname' }, gRows); name.textContent = m.name;
    const cnt = el('text', { x: FW - 4, y: y + 4, class: 'rowcount' }, gRows);
    [band, name].forEach((e) => {
      e.addEventListener('mouseenter', () => setHover(m.code)); e.addEventListener('mouseleave', () => setHover(null));
      e.addEventListener('click', () => setTriggerValue('open', m.code));
    });
    return { band, name, cnt, y };
  });
  const maxReg = Math.max(...vds.map((v) => v.reg));
  const hash = (s) => { let h = 2166136261; for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; };
  vds.forEach((v) => {
    v.r = 1.6 + 3.4 * Math.sqrt(v.reg / maxReg);
    v.jy = (hash(v.code) - 0.5) * (rowH - 9);
    v.el = el('circle', { r: v.r.toFixed(2), class: 'dot' }, gDots);
    v.el.style.transitionDelay = reduced ? '0ms' : Math.round(hash(v.code + 'd') * 160) + 'ms';
    v.el.addEventListener('mouseenter', (e) => showTip(e, v));
    v.el.addEventListener('mouseleave', hideTip);
  });
  const thrLine = el('line', { y1: top - 10, y2: FH - 40, class: 'thr' }, gTop);
  const thrLab = el('text', { y: top - 12, class: 'thrlab' }, gTop);
  const provLine = el('line', { y1: top - 10, y2: FH - 34, class: 'prov' }, gTop);
  const provLab = el('text', { y: FH - 24, class: 'provlab' }, gTop);

  // draggable threshold line
  let dragging = false;
  const toT = (evt) => {
    const pt = field.createSVGPoint(); pt.x = evt.clientX; pt.y = evt.clientY;
    const p = pt.matrixTransform(field.getScreenCTM().inverse());
    return Math.round(X0 + ((p.x - left) / (FW - left - right)) * (X1 - X0));
  };
  thrLine.addEventListener('pointerdown', (e) => { dragging = true; thrLine.setPointerCapture(e.pointerId); });
  thrLine.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    thrRange.value = Math.max(10, Math.min(40, toT(e))); onThreshold(false);
  });
  thrLine.addEventListener('pointerup', () => { if (dragging) { dragging = false; onThreshold(true); } });

  // ---------------- tooltip ----------------
  const tip = $('.mx-tip');
  function showTip(e, v) {
    const m = munis[v.m];
    tip.innerHTML = `<b>Voting district ${v.code}</b><br>${m.name} · ${v.venue || 'venue unknown'}<br>` +
      `${fmt(v.reg)} registered voters<br>Turnout at ${level.toFixed(1)}%: <b>${v.t.toFixed(1)}%</b>` +
      (v.t21 != null ? `<br>2021 turnout: ${v.t21.toFixed(1)}%` : '') +
      `<br><span style="color:#b83b3b">Chance below 25% on 4 Nov: <b>${Math.round(100 * v.pLow)}%</b></span>` +
      `<br>80% range (simulated): ${v.p10.toFixed(0)}–${v.p90.toFixed(0)}%`;
    const box = root.getBoundingClientRect();
    tip.style.left = Math.min(box.width - 230, e.clientX - box.left + 14) + 'px';
    tip.style.top = (e.clientY - box.top + 14) + 'px';
    tip.classList.add('show');
  }
  function hideTip() { tip.classList.remove('show'); }

  function setHover(code) {
    hoverMuni = code;
    root.classList.toggle('hovering', !!code);
    munis.forEach((m, i) => {
      const on = m.code === code;
      rowEls[i].band.classList.toggle('on', on); rowEls[i].name.classList.toggle('on', on);
      shapes[m.code].classList.toggle('on', on);
    });
    vds.forEach((v) => v.el.classList.toggle('dim', !!code && munis[v.m].code !== code));
  }

  // ---------------- counters ----------------
  const counters = {};
  function tween(id, to, fmtFn) {
    const node = $(id); const from = counters[id] ?? to; counters[id] = to;
    if (reduced || from === to) { node.textContent = fmtFn(to); return; }
    const t0 = performance.now(), dur = 450;
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      node.textContent = fmtFn(from + (to - from) * e);
      if (k < 1 && counters[id] === to) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  // ---------------- render ----------------
  function render() {
    const r = compute(level, threshold);
    $('#mx-level').textContent = level.toFixed(1);
    range.style.setProperty('--fill', pos(level) + '%');
    tween('#mx-n', r.n, fmt);
    tween('#mx-voters', r.voters, fmt);
    tween('#mx-ballots', r.ballots, fmt);
    const diff = r.ballots - D.ballots2021;
    $('#mx-ballots-ctx').textContent = `${fmt(D.reg2026Total - r.ballots)} registered voters stay home`;
    const ch = chanceAtOrBelow(level);
    $('#mx-chance').innerHTML = `<b>${Math.round(100 * ch)}%</b> chance turnout is this low or lower`;
    $('#mx-thr-val').textContent = threshold;
    root.querySelectorAll('.thr-now').forEach((e) => { e.textContent = threshold; });
    const mood = level < D.central - 0.25 ? 'weaker than forecast'
      : level <= D.central + 0.25 ? 'our forecast'
      : level < D.actual2021 ? 'better than forecast'
      : 'above the 2021 record low';
    $('#mx-sentence').innerHTML = `<span class="tag">${level.toFixed(1)}% \u00b7 ${mood}</span>` +
      `<span class="arrow">\u2192</span><b class="hot">${fmt(r.n)}</b>&nbsp;districts under ${threshold}%` +
      `<span class="sep">\u00b7</span><b>${fmt(r.voters)}</b>&nbsp;voters in them` +
      `<span class="sep">\u00b7</span><b>${fmt(D.reg2026Total - r.ballots)}</b>&nbsp;stay home`;
    munis.forEach((m, i) => {
      shapes[m.code].style.fill = mapColour(i, r);
      rowEls[i].cnt.textContent = r.belowN[i] ? `${r.belowN[i]} below` : '';
      labelEls[m.code].textContent = r.belowN[i] ? `${r.belowN[i]} below` : '';
    });
    vds.forEach((v) => {
      const y = rowEls[v.m].y + v.jy;
      v.el.style.transform = `translate(${fx(v.t).toFixed(1)}px, ${y.toFixed(1)}px)`;
      v.el.classList.toggle('below', v.below);
    });
    thrLine.setAttribute('x1', fx(threshold)); thrLine.setAttribute('x2', fx(threshold));
    thrLab.setAttribute('x', fx(threshold)); thrLab.textContent = `Very low turnout: under ${threshold}% · drag`;
    provLine.setAttribute('x1', fx(level)); provLine.setAttribute('x2', fx(level));
    provLab.setAttribute('x', fx(level)); provLab.textContent = `Mpumalanga ${level.toFixed(1)}%`;
    $('.mx-legend-map').innerHTML = mapMode === 'risk'
      ? '<span class="sw" style="background:linear-gradient(90deg,#2b2b28,#ff6b6b)"></span>Redder = more voters below the line'
      : mapMode === 'chance' ? '<span class="sw" style="background:linear-gradient(90deg,#2b2b28,#ff6b6b)"></span>Redder = likelier to drop below 2021'
      : '<span class="sw" style="background:linear-gradient(90deg,#e66767,#3a3936,#3987e5)"></span>Red = below Mpumalanga \u00b7 Blue = above';
  }

  parentElement.__mood = { refresh: () => {} };             // state lives here; later reruns keep it
  render();
}
