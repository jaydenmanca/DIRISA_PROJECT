// 2026 hero: the forecast for 4 November 2026 told in three steps.
//   1. The roll:       2,170 dots = the 2026 voters' roll (1 dot = 1,000 registered voters).
//   2. The forecast:   lit dots = expected ballots; dark dots = registered voters expected to stay home.
//   3. The simulation: 10,000 simulated election days rain down as a histogram (1 dot = 10 simulations);
//                      red = turnout below the 2021 record low.
// Plays once when it scrolls into view; the step buttons replay any step.
export default function (component) {
  const { data, parentElement } = component;
  if (!data || parentElement.__hero) return;
  parentElement.__hero = true;

  const SVGNS = 'http://www.w3.org/2000/svg';
  const root = parentElement.querySelector('.sh');
  const $ = (s) => root.querySelector(s);
  const fmt = (n) => Math.round(n).toLocaleString('en-US');
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const D = data;
  const el = (tag, attrs, parent) => {
    const e = document.createElementNS(SVGNS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    parent.appendChild(e);
    return e;
  };

  // Countdown to election day (from the viewer's clock).
  const now = new Date();                                   // whole calendar days, local date
  const days = Math.round((Date.UTC(2026, 10, 4) - Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())) / 864e5);
  $('#sh-countdown').textContent = days > 1 ? `${days} days to go` : days === 1 ? '1 day to go'
    : days === 0 ? 'Election day' : 'Election held · compare with the results';

  // ---- the roll grid ------------------------------------------------------------------
  const nRoll = Math.round(D.reg2026 / 1000), nVote = Math.round(D.ballots2026 / 1000);
  const COLS = 62, GAP = 9.2, R = 3.1;
  const TOP = 26, SPLIT = 30;                    // room for the label above; gap between voters and stay-home
  const grid = $('#sh-grid');
  grid.setAttribute('viewBox', `0 0 ${COLS * GAP + 4} ${Math.ceil(nRoll / COLS) * GAP + TOP + SPLIT + 4}`);
  const dots = [];
  for (let i = 0; i < nRoll; i++) {
    dots.push(el('circle', { cx: (2 + GAP / 2 + (i % COLS) * GAP).toFixed(1),
                             cy: (TOP + GAP / 2 + Math.floor(i / COLS) * GAP).toFixed(1), r: R, class: 'd' }, grid));
  }
  // Labels written ON the grid, so nobody has to decode a legend
  const inTen = Math.round((10 * D.ballots2026) / D.reg2026);
  const labTop = el('text', { x: 4, y: 16, class: 'glab' }, grid);
  const labHome = el('text', { x: 4, y: (TOP + Math.floor(nVote / COLS) * GAP + SPLIT - 6).toFixed(1), class: 'glab home-lab' }, grid);
  labHome.textContent = `Expected to stay home · ${fmt(D.reg2026 - D.ballots2026)} · ${10 - inTen} in 10`;

  // ---- the simulation histogram (1 dot = 10 simulated elections) -------------------------
  const hist = $('#sh-hist');
  const HW = 640, HH = 330, base = 290, left = 10, right = 10;
  hist.setAttribute('viewBox', `0 0 ${HW} ${HH}`);
  const xs = D.bins.map((b) => b.x);
  const xMin = Math.min(...xs), xMax = Math.max(...xs) + D.binWidth;
  const hx = (v) => left + ((v - xMin) / (xMax - xMin)) * (HW - left - right);
  const step = (HW - left - right) / ((xMax - xMin) / D.binWidth);
  const maxN = Math.max(...D.bins.map((b) => b.n));
  const hgap = Math.min(step * 0.78, (base - 44) / maxN);            // tallest bin stays below the labels
  const hr = Math.max(1.4, Math.min(3.2, hgap / 2.15));
  const hdots = [];
  D.bins.forEach((b, bi) => {
    for (let k = 0; k < b.n; k++) {
      const c = el('circle', { cx: (hx(b.x) + step / 2).toFixed(1), cy: (base - hr - k * hgap).toFixed(1), r: hr.toFixed(2),
                               class: 'h' + (b.x + D.binWidth / 2 < D.recordLow ? ' red' : '') }, hist);
      c.style.transitionDelay = reduced ? '0ms' : Math.round(bi * 18 + k * 9) + 'ms';
      hdots.push(c);
    }
  });
  el('line', { x1: left, x2: HW - right, y1: base + 1, y2: base + 1, class: 'axisline' }, hist);
  for (let t = Math.ceil(xMin / 5) * 5; t <= xMax; t += 5) {
    const lab = el('text', { x: hx(t), y: base + 20, class: 'tick' }, hist); lab.textContent = t + '%';
  }
  const rx = hx(D.recordLow);
  el('line', { x1: rx, x2: rx, y1: 18, y2: base + 1, class: 'record' }, hist);
  const rl = el('text', { x: rx + 6, y: 30, class: 'recordlab' }, hist); rl.textContent = `2021 record low ${D.recordLow.toFixed(1)}%`;
  const hh = el('text', { x: 10, y: 14, class: 'histhead' }, hist);
  hh.textContent = 'Each dot = 10 simulated election days, placed at the turnout it produced';
  const rl2 = el('text', { x: rx - 6, y: 30, class: 'recordlab left' }, hist); rl2.textContent = '← new record low';

  const steps = [
    { key: 'roll', eyebrow: 'Registered for 4 November 2026', big: fmt(D.reg2026), unit: 'registered voters, a record',
      points: [`+${fmt(D.reg2026 - D.reg2021)} since 2021`, '1 dot = 1,000 voters'] },
    { key: 'votes', eyebrow: 'Our 2026 forecast', big: '\u2248 ' + fmt(D.ballots2026), unit: `expected to vote (${D.turnout2026.toFixed(1)}%)`,
      points: [`\u2248 ${fmt(D.reg2026 - D.ballots2026)} expected to stay home (dark dots)`,
               `Likely: ${fmt(D.ballotsLow)} \u2013 ${fmt(D.ballotsHigh)} votes`] },
    { key: 'sims', eyebrow: 'Election day, simulated 10,000 times', big: Math.round(100 * D.pRecord) + '%', unit: 'chance of a new record-low turnout',
      points: [`Record low: ${D.recordLow.toFixed(1)}% in 2021`, '1 dot = 10 simulations \u00b7 red = below the record',
               `Cautious estimate: ${Math.round(100 * D.pRecordCautious)}%`] },
  ];

  let timers = [];
  const clear = () => { timers.forEach(clearTimeout); timers = []; };
  const later = (ms, fn) => timers.push(setTimeout(fn, reduced ? 0 : ms));

  function show(i) {
    const s = steps[i];
    root.querySelectorAll('.sh-steps button:not(.replay)').forEach((b, j) => b.classList.toggle('on', j === i));
    const panel = $('.sh-text');
    panel.classList.remove('in'); void panel.offsetWidth; panel.classList.add('in');
    $('#sh-eyebrow').textContent = s.eyebrow;
    $('#sh-big').textContent = s.big;
    $('#sh-big').classList.toggle('hot', s.key === 'sims');
    $('#sh-unit').textContent = s.unit;
    $('#sh-body').innerHTML = s.points.map((t) => `<li>${t}</li>`).join('');
    root.classList.toggle('show-hist', s.key === 'sims');
    $('.sh-key.grid-key').style.display = s.key === 'sims' ? 'none' : '';
    $('.sh-key.hist-key').style.display = s.key === 'sims' ? '' : 'none';
    labTop.textContent = s.key === 'votes' ? `Expected to vote · ${fmt(D.ballots2026)} · ${inTen} in 10`
      : `${fmt(D.reg2026)} registered · each dot = 1,000 people`;
    labTop.classList.toggle('lit-lab', s.key === 'votes');
    labHome.classList.toggle('show', s.key === 'votes');
    dots.forEach((c, j) => {
      let cls = 'd on';
      if (s.key === 'votes') cls += j < nVote ? ' lit' : ' home';
      c.setAttribute('class', cls);
      c.style.transitionDelay = reduced ? '0ms' : Math.round(s.key === 'roll' ? j * 0.4 : (j % COLS) * 8 + Math.floor(j / COLS) * 5) + 'ms';
    });
    hdots.forEach((c) => c.classList.toggle('in', s.key === 'sims'));
  }

  function play() {
    clear();
    dots.forEach((c) => { c.style.transitionDelay = '0ms'; c.setAttribute('class', 'd'); });
    hdots.forEach((c) => c.classList.remove('in'));
    later(80, () => show(0));
    later(2600, () => show(1));
    later(5600, () => show(2));
  }
  root.querySelectorAll('.sh-steps button:not(.replay)').forEach((b, i) => b.addEventListener('click', () => { clear(); show(i); }));
  $('#sh-replay').addEventListener('click', play);

  const io = new IntersectionObserver((entries) => {
    if (entries.some((e) => e.isIntersecting)) { io.disconnect(); play(); }
  }, { threshold: 0.25 });
  io.observe(root);
  return () => { clear(); io.disconnect(); };
}
