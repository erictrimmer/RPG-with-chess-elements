/* ===== Puzzle Harvester: drill batches ===== */
const $ = id => document.getElementById(id);

const VAL = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
const TNAME = { p: 'pawn', n: 'knight', b: 'bishop', r: 'rook', q: 'queen', k: 'king' };
const cap1 = s => s.charAt(0).toUpperCase() + s.slice(1);

/* ---- the batch list (order = drill order) ---- */
const GROUPS = { 1: 'Mate in 1', 2: 'Winning material', 3: 'Mate in 2', 4: 'Sacrifice material', 5: 'Win a pinned piece' };
const PIECES4 = [['q', 'queen'], ['r', 'rook'], ['b', 'bishop'], ['n', 'knight']];
const BATCHES = [];
const addBatch = (id, key, title, o) => BATCHES.push(Object.assign({ id, key, title, group: +id[0], order: BATCHES.length + 1 }, o));

[['a', 'rook'], ['b', 'bishop'], ['c', 'knight'], ['d', 'pawn']].forEach(([l, p]) =>
  addBatch('1' + l, `1${l}_mate_in_1_${p}`, `Mate in 1: ${p} checkmates`, {
    kind: 'm1', m1: true, bucket: 'm1:' + p,
    task: `Checkmate in one move with your ${p}!`, hint: `Find the ${p} move that gives check where the king cannot escape.`,
    win: `Checkmate! The ${p} delivers mate.` }));
addBatch('1e', '1e_mate_in_1_mixed', 'Mate in 1: mixed', { kind: 'm1', m1: true, mixed: true,
  task: 'Checkmate in one move!', hint: 'Find the check where the king has no escape and nothing can block or capture.', win: 'Checkmate!' });

[['a', 'r', 'rook'], ['b', 'n', 'knight'], ['c', 'b', 'bishop'], ['d', 'q', 'queen']].forEach(([l, t, p]) =>
  addBatch('2' + l, `2${l}_win_a_${p}`, `Winning material: gain a ${p}`, { kind: 'gain', gainType: t, bucket: '2' + l,
    task: `Win a ${p}!`, hint: `Look for a fork, a loose piece or a pin that wins a ${p}.`, win: `You won a ${p}!` }));
addBatch('2e', '2e_draw', 'Winning material: save the draw', { kind: 'draw', bucket: '2e',
  task: 'You are in trouble. Find a way to draw!', hint: 'Look for a perpetual check or a stalemate trick.', win: 'Draw! You saved the game.' });

addBatch('3a', '3a_mate_in_2_double_check', 'Mate in 2: double check', { kind: 'm2', bucket: '3a',
  task: 'Checkmate in two moves. Look for a double check!', hint: 'A double check can only be answered by moving the king.', win: 'Checkmate in two!' });
[['b', 'queen'], ['c', 'rook'], ['d', 'knight'], ['e', 'bishop'], ['f', 'pawn']].forEach(([l, p]) =>
  addBatch('3' + l, `3${l}_mate_in_2_${p}`, `Mate in 2: ${p} checkmates`, { kind: 'm2', m2cat: p, bucket: '3' + l,
    task: `Checkmate in two moves. Your ${p} delivers the mate!`, hint: 'Look for a forcing first move: the king must have no good reply.', win: `Checkmate in two! The ${p} delivers mate.` }));

[['a', 'queen'], ['b', 'rook'], ['c', 'bishop'], ['d', 'knight']].forEach(([l, p]) =>
  addBatch('4' + l, `4${l}_sacrifice_${p}`, `Sacrifice material: ${p} sacrifice`, { kind: 'sac', sacType: PIECES4.find(x => x[1] === p)[0], bucket: '4' + l,
    task: `Sacrifice your ${p} to win!`, hint: `Give up the ${p}: what does the capture open up?`, win: `Brilliant! The ${p} sacrifice works.` }));

[['a', 'r', 'rook'], ['b', 'n', 'knight'], ['c', 'b', 'bishop'], ['d', 'q', 'queen']].forEach(([l, t, p]) =>
  addBatch('5' + l, `5${l}_pinned_${p}`, `Pinned pieces: win the pinned ${p}`, { kind: 'pin', pinType: t, bucket: '5' + l,
    task: `A ${p} is pinned to its king. Attack it with another piece to win it!`, hint: 'A pinned piece cannot move away. Attack it again.', win: `You won the pinned ${p}!` }));

/* The order batches claim puzzles: the scarcest first, so common puzzles never steal from rare batches. */
const CLAIM_ORDER = ['5a', '5b', '5c', '5d', '4a', '4b', '4c', '4d', '2e', '2d', '2a', '2c', '2b',
  '3a', '3b', '3c', '3d', '3e', '3f', '1a', '1b', '1c', '1d', '1e'];
const MIXED_CATS = ['queen', 'discovered', 'double_check', 'promotion', 'king', 'rook', 'bishop', 'knight', 'pawn', 'castling'];

const GAIN_THEMES = ['hangingPiece', 'fork', 'skewer', 'discoveredAttack', 'trappedPiece', 'capturingDefender', 'attraction',
  'deflection', 'xRayAttack'];     // not 'advantage'/'crushing': half the database, and far too slow to analyse

/* ---- chess helpers ---- */
const uciMove = u => ({ from: u.slice(0, 2), to: u.slice(2, 4), promotion: u.length > 4 ? u[4].toLowerCase() : undefined });
const uciOf = m => m.from + m.to + (m.promotion || '');
const countPieces = fen => { let n = 0; for (const ch of fen.split(' ')[0]) if (/[a-zA-Z]/.test(ch)) n++; return n; };
const FILES = 'abcdefgh';
const sqName = (f, r) => FILES[f] + (r + 1);

function counts(g) {
  const c = { w: { p: 0, n: 0, b: 0, r: 0, q: 0 }, b: { p: 0, n: 0, b: 0, r: 0, q: 0 } };
  for (const rank of g.board()) for (const s of rank) if (s && s.type !== 'k') c[s.color][s.type]++;
  return c;
}
const material = c => c.p + 3 * c.n + 3 * c.b + 5 * c.r + 9 * c.q;
function kingSq(g, color) {
  for (const rank of g.board()) for (const s of rank) if (s && s.type === 'k' && s.color === color) return s.square;
  return null;
}

/* Plays a solution line and records what happened. sol[0] is the first move of the side to move. */
function analyzeLine(fen, sol) {
  const g = new Chess(fen);
  const me = g.turn(), op = me === 'w' ? 'b' : 'w';
  const a = { me, op, start: counts(g), plies: [] };
  for (let i = 0; i < sol.length; i++) {
    const by = i % 2 === 0 ? me : op;
    let m;
    try { m = g.move(uciMove(sol[i])); } catch (e) { return null; }
    if (!m || m.color !== by) return null;
    const ply = { uci: sol[i], by: i % 2 === 0 ? 'me' : 'op', piece: m.piece, captured: m.captured || null, from: m.from, to: m.to,
      promotion: m.promotion || null, flags: m.flags, san: m.san, checkers: 0, giver: [] };
    if (g.isCheck()) {
      const att = g.attackers(kingSq(g, by === 'w' ? 'b' : 'w'), by);
      ply.giver = att; ply.checkers = att.length;
    }
    a.plies.push(ply);
  }
  a.end = counts(g);
  a.mate = g.isCheckmate(); a.stalemate = g.isStalemate(); a.drawn = g.isDraw();
  a.netMe = (material(a.end[me]) - material(a.end[op])) - (material(a.start[me]) - material(a.start[op]));
  a.hasPromo = a.plies.some(p => p.promotion);
  return a;
}

/* What kind of mate did this move deliver? (p = a ply record whose move gave checkmate) */
function mateCat(p) {
  if (p.promotion) return 'promotion';
  if (p.checkers >= 2) return 'double_check';
  if (p.checkers === 1 && p.giver[0] !== p.to) return 'discovered';
  if (p.flags.includes('k') || p.flags.includes('q')) return 'castling';
  return TNAME[p.piece];
}

/* Moves that give checkmate. The SAN of each verbose move already ends in '#', which chess.js works out
   cheaply; playing every move just to test it would be far slower. */
const mateMoves = g => g.moves({ verbose: true }).filter(m => m.san.endsWith('#'));
function countMates(fen, limit) { return Math.min(limit, mateMoves(new Chess(fen)).length); }

/* Pieces of `color` that are pinned to their own king (absolute pins). */
const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]];
function pinnedPieces(g, color) {
  const k = kingSq(g, color); if (!k) return [];
  const kf = FILES.indexOf(k[0]), kr = parseInt(k[1], 10) - 1, res = [];
  for (const [df, dr] of DIRS) {
    let f = kf + df, r = kr + dr, cand = null;
    while (f >= 0 && f < 8 && r >= 0 && r < 8) {
      const p = g.get(sqName(f, r));
      if (p) {
        if (!cand) { if (p.color === color) cand = { sq: sqName(f, r), type: p.type }; else break; }
        else {
          if (p.color !== color && (p.type === 'q' || (df !== 0 && dr !== 0 ? p.type === 'b' : p.type === 'r')))
            res.push({ sq: cand.sq, type: cand.type, pinner: sqName(f, r) });
          break;
        }
      }
      f += df; r += dr;
    }
  }
  return res;
}

/* Section 5: an enemy piece is pinned to its king; move 1 adds a new attacker on it; the line wins it. */
function pinWinInfo(fen, a) {
  const g = new Chess(fen);
  const pins = pinnedPieces(g, a.op).filter(p => 'nbrq'.includes(p.type));
  if (!pins.length) return null;
  const first = a.plies[0];
  const g2 = new Chess(fen); g2.move(uciMove(first.uci));
  for (const pin of pins) {
    if (first.to === pin.sq) continue;                        // grabbing it at once is not a threat
    const before = g.attackers(pin.sq, a.me).filter(s => s !== pin.pinner).length;
    const after = g2.attackers(pin.sq, a.me).filter(s => s !== pin.pinner).length;
    if (after <= before) continue;                            // move 1 must bring a new attacker
    const won = a.plies.findIndex((p, i) => i > 0 && p.by === 'me' && p.to === pin.sq && p.captured === pin.type);
    if (won < 0) continue;
    return { type: pin.type, sq: pin.sq };
  }
  return null;
}

/* Section 4: a piece worth 3+ is given up (the opponent captures it on the square it moved to) for real. */
function sacInfo(a) {
  for (let i = 0; i + 1 < a.plies.length; i++) {
    const m = a.plies[i], r = a.plies[i + 1];
    if (m.by !== 'me' || r.by !== 'op' || !r.captured || r.to !== m.to) continue;
    const given = VAL[m.piece], got = m.captured ? VAL[m.captured] : 0;
    if (given >= 3 && given - got >= 2 && !m.promotion) return { type: m.piece };
  }
  return null;
}

/* Section 2: winning a piece cleanly. prize = the most valuable enemy piece type that is lost. */
function gainInfo(a) {
  let prize = null;
  for (const t of ['q', 'r', 'b', 'n']) if (a.start[a.op][t] > a.end[a.op][t]) { prize = t; break; }
  if (!prize) return null;
  const need = { q: 8, r: 4, b: 2, n: 2 }[prize];
  if (a.netMe < need) return null;
  return { type: prize };
}

/* Mate in 2 must be a real drill: no mate in 1, exactly one first move forces mate on the next move. */
function verifyMate2(fen, first) {
  const g = new Chess(fen), all = g.moves({ verbose: true }), forcing = [];
  if (all.some(m => m.san.endsWith('#'))) return { ok: false, why: 'a mate in 1 exists' };
  for (const m of all) {
    g.move({ from: m.from, to: m.to, promotion: m.promotion });
    if (!g.isGameOver()) {
      const replies = g.moves({ verbose: true });
      let every = replies.length > 0;
      for (const rp of replies) {
        g.move({ from: rp.from, to: rp.to, promotion: rp.promotion });
        const found = mateMoves(g).length > 0;
        g.undo();
        if (!found) { every = false; break; }
      }
      if (every) forcing.push(uciOf(m));
    }
    g.undo();
    if (forcing.length > 1) break;
  }
  return { ok: forcing.length === 1 && forcing[0] === first, why: forcing.length === 1 ? 'different first move' : 'first move not unique' };
}

/* ---- candidates ---- */
let buckets = new Map();      // bucket key -> {items:[{score, placement, build}], seen:Set, minScore}
let finalBatches = [];        // [{def, items:[{puzzle, off}], found}]
let scanning = false, cancelFlag = false, lastFile = null;

const enabledIds = () => new Set([...document.querySelectorAll('#batchBoxes input:checked')].map(c => c.dataset.id));
const getOpts = () => withFlags({ enabled: enabledIds(),
  m1Max: +$('m1Max').value, maxRating: +$('maxRating').value, size: +$('size').value,
  minPop: +$('minPop').value, minPlays: +$('minPlays').value, maxPieces1: +$('maxPieces1').value, maxPieces: +$('maxPieces').value,
});
function withFlags(o) { o.anyM1 = [...o.enabled].some(i => i[0] === '1'); o.anyOther = [...o.enabled].some(i => i[0] !== '1');
  const has = p => [...o.enabled].some(i => i.startsWith(p)), th = new Set();
  if (has('3')) th.add('mateIn2');
  if (has('4')) th.add('sacrifice');
  if (has('5')) th.add('pin');
  if (o.enabled.has('2e')) th.add('equality');
  o.gain = ['2a', '2b', '2c', '2d'].some(i => o.enabled.has(i));
  if (o.gain) GAIN_THEMES.forEach(t => th.add(t));
  o.wantThemes = th; return o; }

function offer(o, key, score, placement, build) {
  const cap = o.size * 4;
  let b = buckets.get(key);
  if (!b) { b = { items: [], seen: new Set(), minScore: -Infinity }; buckets.set(key, b); }
  if (b.seen.has(placement)) return;
  if (b.items.length >= cap && score <= b.minScore) return;
  b.items.push({ score, placement, build }); b.seen.add(placement);
  if (b.items.length > cap * 2) trimBucket(b, cap);
}
function trimBucket(b, cap) {
  b.items.sort((x, y) => y.score - x.score);
  b.items.length = Math.min(b.items.length, cap);
  b.seen = new Set(b.items.map(i => i.placement));
  b.minScore = b.items.length >= cap ? b.items[b.items.length - 1].score : -Infinity;
}

function buildPuzzle(def, row, fen, solution, rating) {
  const side = fen.split(' ')[1] === 'w' ? 'White' : 'Black';
  const tags = [def.key.replace(/^\d[a-z]_/, ''), 'batch_' + def.id, rating < 800 ? 'elementary' : 'beginner'];
  return { id: row.PuzzleId, name: `${def.title} #${row.PuzzleId}`, batch: def.id, batch_title: def.title, order: def.order,
    elo_min: Math.max(100, rating - 150), elo_max: rating + 250, theme: def.key,
    difficulty: rating < 800 ? 'easy' : (rating < 1200 ? 'medium' : 'hard'),
    fen, side: side.toLowerCase(), objective_move: solution[0], solution,
    instruction: `${side} to move. ${def.task}`, success_text: def.win, hint: def.hint, tags,
    rating, source: 'lichess puzzle database (CC0)' };
}
const BY_ID = Object.fromEntries(BATCHES.map(b => [b.id, b]));
const GAIN_ID = { r: '2a', n: '2b', b: '2c', q: '2d' }, SAC_ID = { q: '4a', r: '4b', b: '4c', n: '4d' };
const PIN_ID = { r: '5a', n: '5b', b: '5c', q: '5d' };
const M2_ID = { queen: '3b', rook: '3c', knight: '3d', bishop: '3e', pawn: '3f' };

function processRow(line, cols, o, stats) {
  const f = line.split(',');
  const rating = parseInt(f[cols.Rating], 10);
  if (!(rating <= o.maxRating || rating <= o.m1Max)) return;
  if (!(parseInt(f[cols.Popularity], 10) >= o.minPop && parseInt(f[cols.NbPlays], 10) >= o.minPlays)) return;
  const themes = (f[cols.Themes] || '').split(' ');
  const wantM1 = rating <= o.m1Max && themes.includes('mateIn1') && o.anyM1;
  const wantOther = rating <= o.maxRating && o.anyOther && themes.some(t => o.wantThemes.has(t));
  if (!wantM1 && !wantOther) return;
  const fen0 = f[cols.FEN], seq = f[cols.Moves].trim().split(/\s+/);
  const limit = Math.max(wantM1 ? o.maxPieces1 : 0, wantOther ? o.maxPieces : 0);
  if (seq.length < 2 || countPieces(fen0) > limit + 1) return;        // cheap check before any chess work
  let g;
  try { g = new Chess(fen0); g.move(uciMove(seq[0])); } catch (e) { return; }   // the opponent's move comes first
  const fen = g.fen(), solution = seq.slice(1), pieces = countPieces(fen);
  const placement = fen.split(' ').slice(0, 2).join(' ');
  const row = { PuzzleId: f[cols.PuzzleId] }, pop = parseInt(f[cols.Popularity], 10);
  const score = pop - 3 * pieces - rating / 100;
  const build = def => buildPuzzle(def, row, fen, solution, rating);

  if (wantM1 && solution.length === 1 && pieces <= o.maxPieces1) {
    const a = analyzeLine(fen, solution);
    if (a && a.mate && countMates(fen, 2) === 1) {            // a drill needs exactly one answer
      const cat = mateCat(a.plies[0]);
      stats.kept++;
      offer(o, 'm1:' + cat, score, placement, build);
    }
  }
  if (!wantOther || pieces > o.maxPieces) return;
  const a = analyzeLine(fen, solution);
  if (!a) return;
  let used = false;
  const put = (id, bonus) => { if (!o.enabled.has(id)) return; offer(o, BY_ID[id].bucket, score + (bonus || 0), placement, build); used = true; };

  if (themes.includes('mateIn2') && solution.length === 3 && a.mate) {
    const cat = mateCat(a.plies[2]);
    if (a.plies[0].checkers >= 2 || cat === 'double_check') put('3a');
    else if (M2_ID[cat]) put(M2_ID[cat]);
  }
  const sac = themes.includes('sacrifice') && o.enabled.size ? sacInfo(a) : null;
  if (sac) put(SAC_ID[sac.type]);
  const pin = themes.includes('pin') ? pinWinInfo(fen, a) : null;
  if (pin) put(PIN_ID[pin.type]);
  if (themes.includes('equality') && !a.mate && a.netMe <= 2) put('2e', a.stalemate || a.drawn ? 10 : 0);
  if (o.gain && !sac && !pin && !a.mate && !a.hasPromo && themes.some(t => GAIN_THEMES.includes(t))) {
    const gain = gainInfo(a);
    if (gain) put(GAIN_ID[gain.type]);
  }
  if (used) stats.kept++;
}

async function scanFile(file, o, onProgress) {
  buckets = new Map();
  const stats = { rows: 0, kept: 0 };
  const reader = file.stream().getReader(), dec = new TextDecoder('utf-8');
  let buf = '', bytes = 0, cols = null, last = performance.now();
  const handle = line => {
    if (line.endsWith('\r')) line = line.slice(0, -1);
    if (!line) return;
    if (!cols) { cols = {}; line.split(',').forEach((n, i) => cols[n.trim()] = i); return; }
    stats.rows++;
    try { processRow(line, cols, o, stats); } catch (e) { /* skip a bad row */ }
  };
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    bytes += value.length;
    buf += dec.decode(value, { stream: true });
    let start = 0, idx;
    while ((idx = buf.indexOf('\n', start)) !== -1) { handle(buf.slice(start, idx)); start = idx + 1; }
    buf = buf.slice(start);
    if (performance.now() - last > 40) {
      onProgress(bytes / file.size, stats);
      await new Promise(r => setTimeout(r, 0));
      last = performance.now();
      if (cancelFlag) { await reader.cancel(); break; }
    }
  }
  if (buf && !cancelFlag) handle(buf);
  onProgress(1, stats);
  return stats;
}

/* ---- choosing the final batches ---- */
async function finalize(o, onProgress) {
  const usedIds = new Set(), usedPlacements = new Set(), res = {};
  const sorted = key => { const b = buckets.get(key); return b ? b.items.slice().sort((x, y) => y.score - x.score) : []; };
  let last = performance.now(), done = 0;
  const tick = async (msg) => {
    if (performance.now() - last > 40) { onProgress(done / Math.max(1, o.enabled.size), msg); await new Promise(r => setTimeout(r, 0)); last = performance.now(); }
  };
  for (const id of CLAIM_ORDER) {
    if (!o.enabled.has(id)) continue;
    const def = BY_ID[id], chosen = [], notes = {};
    const take = async c => {
      const p = c.build(def);
      if (usedIds.has(p.id) || usedPlacements.has(c.placement)) return false;
      if (def.kind === 'm2') {
        const v = verifyMate2(p.fen, p.objective_move);
        await tick(`Checking mate-in-2 puzzles for batch ${id}...`);
        if (!v.ok) { notes[v.why] = (notes[v.why] || 0) + 1; return false; }
      }
      usedIds.add(p.id); usedPlacements.add(c.placement); chosen.push({ puzzle: p, score: c.score }); return true;
    };
    if (def.mixed) {
      const lists = MIXED_CATS.map(cat => sorted('m1:' + cat));
      const idx = lists.map(() => 0);
      let progress = true;
      while (chosen.length < o.size && progress) {
        progress = false;
        for (let k = 0; k < lists.length && chosen.length < o.size; k++) {
          while (idx[k] < lists[k].length) {
            const ok = await take(lists[k][idx[k]++]);
            if (ok) { progress = true; break; }
          }
        }
      }
    } else if (def.kind === 'm1') {
      for (const c of sorted(def.bucket)) { if (chosen.length >= o.size) break; await take(c); }
    } else {
      for (const c of sorted(def.bucket)) { if (chosen.length >= o.size) break; await take(c); }
    }
    chosen.sort((x, y) => x.puzzle.rating - y.puzzle.rating || y.score - x.score);   // easiest first
    const pool = def.mixed ? MIXED_CATS.reduce((s, c) => s + (buckets.get('m1:' + c)?.items.length || 0), 0) : (buckets.get(def.bucket)?.items.length || 0);
    res[id] = { def, items: chosen.map(c => ({ puzzle: c.puzzle, off: false })), pool, notes, selected: chosen.length > 0 };
    done++; await tick(`Batch ${id} chosen.`);
  }
  finalBatches = BATCHES.filter(b => res[b.id]).map(b => res[b.id]);
  onProgress(1, 'Done.');
  return finalBatches;
}

/* ---- output ---- */
function buildFiles() {
  const files = [];
  for (const b of finalBatches) {
    if (!b.selected) continue;
    const puzzles = b.items.filter(i => !i.off).map(i => i.puzzle);
    if (!puzzles.length) continue;
    const text = JSON.stringify({ pack: b.def.key, batch: b.def.id, title: b.def.title, order: b.def.order,
      source: 'Lichess puzzle database (CC0)', puzzles }, null, 1);
    files.push({ name: b.def.key + '.json', text, count: puzzles.length });
  }
  return files;
}
const log = (msg, cls) => { const d = document.createElement('div'); if (cls) d.className = cls; d.textContent = msg; $('log').appendChild(d); $('log').scrollTop = 1e9; };

async function writeToFolder() {
  const files = buildFiles();
  if (!files.length) return log('Nothing selected to write.', 'bad');
  if (!window.showDirectoryPicker) return log('This browser cannot write to a folder directly. Use "Download as a .zip" (or open this page in Chrome or Edge).', 'bad');
  let dir;
  try { dir = await window.showDirectoryPicker({ mode: 'readwrite' }); } catch (e) { return log('No folder chosen.'); }
  for (const f of files) {
    const h = await dir.getFileHandle(f.name, { create: true });
    const w = await h.createWritable(); await w.write(f.text); await w.close();
    log(`Wrote ${f.name} (${f.count} puzzles)`, 'ok');
  }
  log(`Done: ${files.length} file(s) written to "${dir.name}".`, 'ok');
}

/* tiny ZIP writer (stored, no compression) */
const CRC = (() => { const t = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; } return t; })();
const crc32 = b => { let c = 0xFFFFFFFF; for (let i = 0; i < b.length; i++) c = CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; };
function makeZip(files) {
  const enc = new TextEncoder(), parts = [], central = []; let offset = 0;
  const u16 = v => [v & 255, (v >> 8) & 255], u32 = v => [v & 255, (v >> 8) & 255, (v >> 16) & 255, (v >>> 24) & 255];
  for (const f of files) {
    const name = enc.encode(f.name), data = enc.encode(f.text), crc = crc32(data);
    const head = new Uint8Array([0x50, 0x4b, 3, 4, ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0)]);
    parts.push(head, name, data);
    central.push(new Uint8Array([0x50, 0x4b, 1, 2, ...u16(20), ...u16(20), ...u16(0x0800), ...u16(0), ...u16(0), ...u16(0x21), ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0), ...u16(0), ...u16(0), ...u16(0), ...u32(0), ...u32(offset)]), name);
    offset += head.length + name.length + data.length;
  }
  const cdSize = central.reduce((s, p) => s + p.length, 0);
  parts.push(...central, new Uint8Array([0x50, 0x4b, 5, 6, 0, 0, 0, 0, ...u16(files.length), ...u16(files.length), ...u32(cdSize), ...u32(offset), 0, 0]));
  return new Blob(parts, { type: 'application/zip' });
}
function downloadZip() {
  const files = buildFiles();
  if (!files.length) return log('Nothing selected to write.', 'bad');
  const url = URL.createObjectURL(makeZip(files));
  const a = document.createElement('a'); a.href = url; a.download = 'PuzzlePacks.zip'; a.click();
  log(`Downloaded PuzzlePacks.zip with ${files.length} file(s). Unzip into Data/PuzzlePacks.`, 'ok');
}

/* ---- UI ---- */
const GLYPH = { K: '♔', Q: '♕', R: '♖', B: '♗', N: '♘', P: '♙', k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟' };
function boardHtml(fen, uci) {
  const from = uci.slice(0, 2), to = uci.slice(2, 4); let html = '<div class="board">', rank = 8;
  for (const row of fen.split(' ')[0].split('/')) {
    let file = 0;
    const cell = ch => {
      const sq = FILES[file] + rank, light = (file + rank) % 2 === 1;
      const cls = [light ? 'l' : 'd', ch ? (ch === ch.toUpperCase() ? 'w' : 'b') : '', sq === from ? 'f' : '', sq === to ? 't' : ''].join(' ');
      html += `<div class="${cls}">${ch ? GLYPH[ch] : ''}</div>`; file++;
    };
    for (const ch of row) { if (/\d/.test(ch)) for (let i = 0; i < +ch; i++) cell(''); else cell(ch); }
    rank--;
  }
  return html + '</div>';
}
function sanOf(p) { try { return new Chess(p.fen).move(uciMove(p.objective_move)).san; } catch (e) { return p.objective_move; } }

function renderResults() {
  const t = $('packs'), size = +$('size').value;
  t.innerHTML = '<tr><th></th><th>Batch</th><th style="text-align:right">Puzzles</th><th style="text-align:right">Ratings</th><th>Notes</th></tr>';
  let lastGroup = 0;
  for (const b of finalBatches) {
    if (b.def.group !== lastGroup) {
      lastGroup = b.def.group;
      const gr = document.createElement('tr'); gr.className = 'group';
      gr.innerHTML = `<td colspan="5">${lastGroup}. ${GROUPS[lastGroup]}</td>`; t.appendChild(gr);
    }
    const kept = b.items.filter(i => !i.off), rs = kept.map(i => i.puzzle.rating);
    const range = rs.length ? `${Math.min(...rs)}-${Math.max(...rs)}` : '-';
    let note = '';
    if (!b.items.length) note = `<span class="warn">none found (${b.pool} candidates)</span>`;
    else if (b.items.length < size) note = `<span class="warn">only ${b.items.length} of ${size} (${b.pool} candidates)</span>`;
    const skipped = Object.entries(b.notes).map(([k, v]) => `${v} rejected: ${k}`).join('; ');
    if (skipped) note += ` <span class="hint">${skipped}</span>`;
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><input type="checkbox" data-k="${b.def.id}" ${b.selected ? 'checked' : ''}></td><td><a href="#" data-pv="${b.def.id}" style="color:var(--text)">${b.def.id.toUpperCase()}  ${b.def.title}</a> <span class="hint">${b.def.key}.json</span></td><td class="num">${kept.length}${kept.length !== b.items.length ? ' / ' + b.items.length : ''}</td><td class="num">${range}</td><td>${note}</td>`;
    t.appendChild(tr);
  }
  t.querySelectorAll('input[data-k]').forEach(c => c.onchange = () => { finalBatches.find(b => b.def.id === c.dataset.k).selected = c.checked; });
  t.querySelectorAll('a[data-pv]').forEach(a => a.onclick = e => { e.preventDefault(); openPreview(a.dataset.pv); });
}
let pvId = null;
function openPreview(id) {
  pvId = id; const b = finalBatches.find(x => x.def.id === id);
  $('preview').style.display = 'block'; $('pvTitle').textContent = `Preview: ${b.def.title} (${b.items.length} puzzles, easiest first)`;
  const grid = $('pvGrid'); grid.innerHTML = '';
  b.items.forEach(it => {
    const p = it.puzzle, d = document.createElement('div'); d.className = 'pv' + (it.off ? ' off' : '');
    d.innerHTML = boardHtml(p.fen, p.objective_move) + `<label class="check"><input type="checkbox" ${it.off ? '' : 'checked'}> keep</label><div><b>${sanOf(p)}</b> &middot; rating ${p.rating} &middot; ${p.side} to move</div><div class="hint">#${p.id}${p.solution.length > 1 ? ' &middot; ' + p.solution.length + ' moves' : ''}</div>`;
    d.querySelector('input').onchange = e => { it.off = !e.target.checked; d.classList.toggle('off', it.off); renderResults(); };
    grid.appendChild(d);
  });
  $('preview').scrollIntoView({ behavior: 'smooth' });
}
$('pvClose').onclick = () => { $('preview').style.display = 'none'; };
$('pvAll').onclick = () => { if (pvId) { finalBatches.find(b => b.def.id === pvId).items.forEach(i => i.off = false); openPreview(pvId); renderResults(); } };
$('pvNone').onclick = () => { if (pvId) { finalBatches.find(b => b.def.id === pvId).items.forEach(i => i.off = true); openPreview(pvId); renderResults(); } };
$('selAll').onclick = () => { finalBatches.forEach(b => b.selected = b.items.length > 0); renderResults(); };
$('selNone').onclick = () => { finalBatches.forEach(b => b.selected = false); renderResults(); };

(function buildBatchBoxes() {
  const host = $('batchBoxes');
  for (const g of Object.keys(GROUPS)) {
    const d = document.createElement('div'); d.className = 'bgroup';
    d.innerHTML = `<b>${g}. ${GROUPS[g]}</b><br>` + BATCHES.filter(b => b.group == g).map(b =>
      `<label><input type="checkbox" data-id="${b.id}" checked> ${b.id}  ${b.title.replace(/^[^:]*: /, '')}</label>`).join('');
    host.appendChild(d);
  }
  $('bAll').onclick = () => host.querySelectorAll('input').forEach(c => c.checked = true);
  $('bNone').onclick = () => host.querySelectorAll('input').forEach(c => c.checked = false);
})();

function setFile(f) {
  if (!f) return; lastFile = f;
  $('fileinfo').textContent = `${f.name}  (${(f.size / 1048576).toFixed(0)} MB)`;
  $('scan').disabled = false;
}
$('file').onchange = e => setFile(e.target.files[0]);
const drop = $('drop');
['dragover', 'dragenter'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add('over'); }));
['dragleave', 'drop'].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove('over'); }));
drop.addEventListener('drop', e => setFile(e.dataTransfer.files[0]));

$('cancel').onclick = () => { cancelFlag = true; };
$('scan').onclick = async () => {
  if (scanning || !lastFile) return;
  scanning = true; cancelFlag = false;
  $('scan').disabled = true; $('cancel').disabled = false; $('results').style.display = 'none'; $('output').style.display = 'none'; $('preview').style.display = 'none';
  const o = getOpts(), t0 = performance.now();
  if (!o.enabled.size) { scanning = false; $('scan').disabled = false; $('cancel').disabled = true; $('progress').textContent = 'Tick at least one batch.'; return; }
  const stats = await scanFile(lastFile, o, (frac, s) => {
    $('barfill').style.width = (frac * 100).toFixed(1) + '%';
    $('progress').textContent = `${(frac * 100).toFixed(1)}%  -  ${s.rows.toLocaleString()} puzzles read, ${s.kept.toLocaleString()} candidates so far`;
  });
  $('progress').textContent = 'Choosing the final puzzles for each batch...';
  await finalize(o, (frac, msg) => { $('barfill').style.width = (frac * 100).toFixed(1) + '%'; $('progress').textContent = msg; });
  const secs = ((performance.now() - t0) / 1000).toFixed(0);
  $('progress').textContent = (cancelFlag ? 'Cancelled early. ' : 'Finished. ') + `${stats.rows.toLocaleString()} puzzles read in ${secs}s.`;
  renderResults();
  $('results').style.display = 'block'; $('output').style.display = 'block';
  $('scan').disabled = false; $('cancel').disabled = true; scanning = false;
};
$('writeDir').onclick = () => writeToFolder().catch(e => log('Error: ' + e.message, 'bad'));
$('writeZip').onclick = downloadZip;

window.__harvester = { Chess, scanFile, finalize, getOpts, setFile, buildFiles, analyzeLine, pinnedPieces, pinWinInfo, sacInfo, gainInfo,
  verifyMate2, mateCat, countMates, BATCHES, finalBatches: () => finalBatches, buckets: () => buckets };
