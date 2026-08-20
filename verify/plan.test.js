// plan.test.js — StudyBuddy verification (canonical: npm test)
// Extracts the REAL inline JS from ../index.html and runs it against a stubbed DOM
// plus an in-memory fake of the serve.py REST API (register/login/state/answers/snapshot/plan),
// mirroring the PostgreSQL semantics (per-user answers/snapshot/plan, bearer tokens).
// Run: npm test  (root)  →  npm --prefix verify install && npm --prefix verify test
const fs = require('fs'), vm = require('vm'), path = require('path');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

// ---------- fake server (mirrors serve.py /api/* over Postgres) ----------
const server = {
  users: new Map(),            // username -> { password, id }
  tokens: new Map(),           // token -> username
  data: new Map(),             // username -> { answers:{}, snapshot:null, plan:null }
  nextId: 1,
};
function fakeFetch(url, opt) {
  opt = opt || {};
  const method = opt.method || 'GET';
  const path = url.split('?')[0];
  const send = (status, obj) => Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(obj) });
  let body = {};
  try { body = opt.body ? JSON.parse(opt.body) : {}; } catch (e) {}
  const user = () => { const h = opt.headers || {}; const t = (h.Authorization || '').replace('Bearer ', ''); return server.tokens.get(t) || null; };
  if (method === 'POST' && path === '/api/register') {
    if (server.users.has(body.username)) return send(409, { error: 'dup' });
    server.users.set(body.username, { password: body.password, id: server.nextId++ });
    server.data.set(body.username, { answers: {}, snapshot: null, plan: null });
    const tok = 'tok_' + body.username; server.tokens.set(tok, body.username);
    return send(201, { token: tok, username: body.username });
  }
  if (method === 'POST' && path === '/api/login') {
    const u = server.users.get(body.username);
    if (!u || u.password !== body.password) return send(401, { error: 'bad credentials' });
    const tok = 'tok_' + body.username; server.tokens.set(tok, body.username);
    return send(200, { token: tok, username: body.username });
  }
  if (method === 'POST' && path === '/api/logout') return send(200, { ok: true });
  if (method === 'GET' && path === '/api/state') {
    const u = user(); if (!u) return send(401, { error: 'unauthorized' });
    const d = server.data.get(u);
    return send(200, { answers: d.answers, snapshot: d.snapshot, plan: d.plan });
  }
  if (method === 'PUT' && path === '/api/answers') {
    const u = user(); if (!u) return send(401, {});
    Object.assign(server.data.get(u).answers, body.answers || {});
    return send(200, { ok: true });
  }
  if (method === 'PUT' && path === '/api/snapshot') {
    const u = user(); if (!u) return send(401, {});
    server.data.get(u).snapshot = body.snapshot; return send(200, { ok: true });
  }
  if (method === 'PUT' && path === '/api/plan') {
    const u = user(); if (!u) return send(401, {});
    server.data.get(u).plan = { plan: body.plan, schedule: body.schedule || {} };
    return send(200, { ok: true });
  }
  if (method === 'POST' && path === '/api/generate-plan') {
    const u = user(); if (!u) return send(401, {});
    const weak = (body.phys && body.phys.weak) || [];
    const freq = Math.max(2, Math.min(6, ((body.dosage && body.dosage.frequency_per_week) || 3)));
    const weeks = [1, 2, 3, 4].map(w => ({
      week: w,
      focus: (w === 1 && weak.length) ? '主題（針對薄弱項：' + weak.join('、') + '）' : (w === 4 ? '綜合複習＋升級預覽' : '主題' + w),
      lessons: Array.from({ length: freq }, (_, i) => ({ day: 'Day ' + (i + 1), pillar: ['Hear', 'Read', 'Spell'][i % 3], activity: '活動' + i, how: '做法（每次 15 分）', words: 'dog、cat', goal: '目標' }))
    }));
    return send(200, { plan: { generated_at: '2026-08-19', level: body.level, weeks }, source: 'deepseek', model: 'fake' });
  }
  return send(404, { error: 'not found' });
}

// ---------- DOM stub (mirrors real element existence) ----------
const values = {};
const elements = {};
const opts = [];
function makeClassList() { const s = new Set(); return { add(c) { s.add(c); }, remove(c) { s.delete(c); }, toggle(c, f) { f === true ? s.add(c) : f === false ? s.delete(c) : s.has(c) ? s.delete(c) : s.add(c); }, contains(c) { return s.has(c); } }; }
function makeOpt(name, multi, vs) { const chips = vs.map(v => ({ dataset: { v }, classList: makeClassList() })); opts.push({ dataset: { name, multi: multi ? '1' : undefined }, querySelectorAll(sel) { return sel === '.chip' ? chips : []; }, chips }); return chips; }
function el(id) {
  if (elements[id]) return elements[id];
  const m = sandbox.S ? sandbox.S.months : 36;
  if (/^EA\d$/.test(id) && m >= 36) return null;
  if (/^EB\d$/.test(id) && m < 36) return null;
  const o = { innerHTML: '', textContent: '', scrollTop: 0, style: {}, dataset: {}, classList: makeClassList(), addEventListener() {}, querySelectorAll() { return []; } };
  Object.defineProperty(o, 'value', { get: () => values[id] || '', set: v => { values[id] = v; } });
  elements[id] = o;
  return o;
}
const storage = new Map();
const sandbox = {
  console, setTimeout, Date, Math, JSON, parseInt, isNaN, alert() {},
  fetch: fakeFetch,
  localStorage: { getItem: k => storage.has(k) ? storage.get(k) : null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) },
  document: { getElementById: el, querySelectorAll: sel => sel === '.opt' ? opts : [], addEventListener() {}, createElement: el },
  location: { href: '' },
};
sandbox.window = sandbox;
vm.createContext(sandbox);

(async () => {
  vm.runInContext(scripts, sandbox, { filename: 'index.html-inline.js' });
  sandbox.PATHWAYS.forEach(p => p.questions.forEach(q => makeOpt(q[0], false, ['0', '1', '2', '3'])));
  for (const [n, m, vs] of [['tier', false, ['1線', '2線', '3線', '4線', '5線', '香港']], ['freq', false, ['每天 10 分鐘', '每週 3-4 次', '每週 1-2 次', '不確定']], ['screen', false, ['完全接受', '適度使用', '盡量減少', '不接受']], ['E2', true, ['英文兒歌', '英文繪本', '以上皆無']]]) makeOpt(n, m, vs);

  let pass = 0, fail = 0;
  const check = (n, c) => { c ? pass++ : fail++; console.log((c ? 'PASS' : 'FAIL') + '  ' + n); };
  const view = v => !sandbox.document.getElementById('view-' + v).classList.contains('hidden');
  const tick = () => new Promise(r => setTimeout(r, 0));
  const reg = async (u, p) => { const r = await sandbox.apiRegister(u, p); sandbox.API.token = r.j.token; sandbox.API.user = u; };
  const login = async (u, p) => { const r = await sandbox.apiLogin(u, p); sandbox.API.token = r.j.token; sandbox.API.user = u; };
  const store = u => server.data.get(u);

  const WEAK_ANSWERS = { inParent: '陳太', inBaby: '小宇', inBirth: '2022-08-01', inNote: '好動坐不住', E1: '15–30 分鐘', E3: '有時', E4: '每週數次' };
  const setPhys = (strong = true) => {
    ['V1','V2','V3','V4','V5','A1','A2','A3','A4'].forEach(k => { sandbox.S[k] = 3; }); // 1–4 階段達成
    sandbox.S.V6 = 3;
    sandbox.S.A5 = strong ? 3 : 1;   // 弱聽覺：A5 未達（落後 ≥2 階段）→ 薄弱項
    sandbox.S.A6 = strong ? 3 : 1;
    sandbox.S.R1 = 3; sandbox.S.R2 = 3; sandbox.S.R3 = 2; sandbox.S.R4 = 1;  // 閱讀階梯 3 → L2（0–3 分制，≥2 才算達成）
    sandbox.S.SP1 = 3; sandbox.S.SP2 = 3; sandbox.S.SP3 = 1;                  // 拼寫階梯 2（不升等）
  };

  // ---- flow 1: register + fill + submit => levels/mistakes/progress/chat derived; persisted server-side ----
  await reg('t1', 'test123456');
  sandbox.S.user = 't1';
  sandbox.S.months = 48; sandbox.S.tier = '香港'; sandbox.S.freq = '每週 3-4 次'; sandbox.S.screen = '適度使用'; sandbox.S.physWindow = [5, 7];
  Object.assign(values, WEAK_ANSWERS); setPhys(false);
  await sandbox.submitAssessment();   // async: DeepSeek(fake) plan → render → save
  await tick();
  check('1: weak answers => L2', sandbox.S.level === 'L2');
  check('1: mistakes EMPTY (no lessons yet)', sandbox.S.mistakes.length === 0);
  check('1: phys weak detected', sandbox.S.phys.weak.length > 0);
  check('1: chat script derived for level', sandbox.S.script.length >= 3);
  check('1: plan has 4 weeks', sandbox.S.teachingPlan.weeks.length === 4);
  check('1: week1 focus mentions weak area, no baked 第N週 prefix', !/^第\s*\d+\s*週/.test(sandbox.S.teachingPlan.weeks[0].focus) && sandbox.S.teachingPlan.weeks[0].focus.indexOf('薄弱項') >= 0);
  check('1: answers + plan persisted to server store', Object.keys(store('t1').answers).length >= 20 && store('t1').plan !== null);
  const genAt = sandbox.S.teachingPlan.generated_at;

  // ---- regression: stage=Σ(level×score)/4; weak = lowest 2 dimensions ----
  {
    const bak = Object.assign({}, sandbox.S);
    sandbox.S.months = 48;
    ['V1','V2','V3','V4','V5','V6','V7','A1','A2','A3','A4','A5','A6','A7','R1','R2','R3','R4','R5','R6','R7','SP1','SP2','SP3','SP4','SP5','SP6','SP7'].forEach(k => delete sandbox.S[k]);
    // 四維度完全均衡（1–5 階段 3 分、第 6 階段 1 分）→ 無薄弱
    ['V1','V2','V3','V4','V5','A1','A2','A3','A4','A5','R1','R2','R3','R4','R5','SP1','SP2','SP3','SP4','SP5'].forEach(k => { sandbox.S[k] = 3; });
    ['V6','A6','R6','SP6'].forEach(k => { sandbox.S[k] = 1; });
    const r1 = sandbox.physAssessment();
    check('R: equal-high 4 dims => no weak', r1.weak.length === 0 && r1.strong.length === 0);
    // 用戶案例：視覺4 聽覺5 閱讀6 拼寫4 → 薄弱＝視覺＋拼寫
    ['V1','V2','V3','V4','V5','V6','V7','A1','A2','A3','A4','A5','A6','A7','R1','R2','R3','R4','R5','R6','R7','SP1','SP2','SP3','SP4','SP5','SP6','SP7'].forEach(k => delete sandbox.S[k]);
    ['V1','V2','V3','V4','A1','A2','A3','A4','R1','R2','R3','R4','R5','R6','SP1','SP2','SP3'].forEach(k => { sandbox.S[k] = 3; });
    sandbox.S.V5 = 1; sandbox.S.A5 = 1; sandbox.S.A6 = 1; sandbox.S.SP4 = 1;
    const r2 = sandbox.physAssessment();
    check('R: lowest-2 rule picks Vision+Spelling',
      JSON.stringify(r2.weak.slice().sort()) === JSON.stringify(['拼寫','視覺']) &&
      JSON.stringify(r2.strong.slice().sort()) === JSON.stringify(['聽覺','閱讀']));
    Object.assign(sandbox.S, bak);
  }

  // ---- flow 2: complete lesson => schedule advances + persisted server-side ----
  vm.runInContext('completeLesson();', sandbox);
  await tick();
  check('2: schedule advanced + persisted', sandbox.S.schedule.current_lesson === 1 && sandbox.S.schedule.completed.length === 1 && store('t1').plan.schedule.current_lesson === 1);

  // ---- flow 3: re-login => skip questionnaire, plan NOT regenerated ----
  sandbox.S = {};
  await login('t1', 'test123456');
  await sandbox.afterLogin('t1');
  check('3: returning user lands on dashboard (questionnaire skipped)', view('dash') && !view('questionnaire'));
  check('3: plan preserved, not regenerated', sandbox.S.teachingPlan.generated_at === genAt && sandbox.S.schedule.current_lesson === 1);
  check('3: level recomputed from answers', sandbox.S.level === 'L2');

  // ---- flow 4: old-format plan migration (第N週 prefix stripped on load) ----
  await reg('m1', 'test123456');
  const oldPlan = { generated_at: '2026-08-01', level: 'L4', weeks: [1, 2, 3, 4].map(w => ({ week: w, focus: '第 ' + w + ' 週：主題', lessons: [{ day: 'Day 1', pillar: 'Hear', activity: 'a', how: 'h', words: '—', goal: 'g' }] })) };
  store('m1').answers = { inBirth: '2022-08-01', EB1: '能說一兩個字' };
  store('m1').plan = { plan: oldPlan, schedule: {} };
  sandbox.S = {};
  await sandbox.afterLogin('m1');
  check('4: baked 第N週 prefix stripped on load', sandbox.S.teachingPlan.weeks.every(w => !/^第\s*\d+\s*週/.test(w.focus)));
  check('4: generated_at preserved', sandbox.S.teachingPlan.generated_at === '2026-08-01');

  // ---- flow 5: brand-new account => questionnaire ----
  await reg('t2', 'test123456');
  sandbox.S = {};
  await sandbox.afterLogin('t2');
  check('5: new account goes to questionnaire', view('questionnaire') && !view('dash'));

  // ---- flow 6: legacy UI removed from markup; new lesson screen present ----
  check('6: avatarKV/physKV/routingNote gone', html.indexOf('id="avatarKV"') < 0 && html.indexOf('id="physKV"') < 0 && html.indexOf('id="routingNote"') < 0);
  check('6: todayCard + weekPlan present', html.indexOf('id="todayCard"') >= 0 && html.indexOf('id="weekPlan"') >= 0);

  // ---- whiteboard: transition speech must NOT resurrect the old word ----
  {
    const wbLines = sandbox.document.getElementById('wbLines');
    wbLines.appendChild = function (c) { this.innerHTML += (c.textContent || ''); };
    sandbox.S.teachingPlan = { generated_at: 'x', weeks: [{ week: 1, focus: 'f', lessons: [{ day: 'Day 1', pillar: 'Vision', activity: '圖詞配對', how: 'h', words: 'dog、park', goal: 'g' }] }] };
    sandbox.S.schedule = { current_week: 0, current_lesson: 0, completed: [] };
    sandbox.drawOnWhiteboard({ clear: true });
    check('W: board starts empty', sandbox.boardLines === 0 && sandbox.boardWords.length === 0);
    sandbox.drawOnWhiteboard({ text: 'dog' });
    check('W: tool draw dog => 1 line', sandbox.boardLines === 1 && JSON.stringify(sandbox.boardWords) === JSON.stringify(['dog']));
    sandbox.maybeShowPicture('We learned dog, now let us learn park!');
    check('W: transition speech draws park (not blocked by dog)', JSON.stringify(sandbox.boardWords) === JSON.stringify(['dog', 'park']));
    sandbox.maybeShowPicture('Great! Dog and park!');
    check('W: repeat mention does not duplicate lines', sandbox.boardLines === 2 && sandbox.boardWords.length === 2);
    sandbox.drawOnWhiteboard({ text: 'park', clear: true });   // agent 開新單字：清板＋畫 park
    sandbox.maybeShowPicture('We learned dog, now let us learn park!');
    check('W: after clear, transition speech does NOT resurrect dog', JSON.stringify(sandbox.boardWords) === JSON.stringify(['park']));
    sandbox.drawOnWhiteboard({ text: 'park', clear: true });
    sandbox.maybeShowPicture('Repeat after me: dog!');
    check('W: explicit single-word mention still draws when absent', JSON.stringify(sandbox.boardWords) === JSON.stringify(['park', 'dog']));
  }

  // ---- lesson stats: echo judging (right/wrong counts) ----
  {
    sandbox.S.user = 't1';
    sandbox.lessonStats = { right: 0, wrong: 0, attempts: [] };
    sandbox.curWord = 'dog';
    sandbox.recordChildAnswer('park');
    check('S: wrong word counted wrong', sandbox.lessonStats.wrong === 1 && sandbox.lessonStats.right === 0 && sandbox.lessonStats.attempts[0].ok === false);
    sandbox.recordChildAnswer('dog');
    check('S: correct word counted right', sandbox.lessonStats.right === 1 && sandbox.lessonStats.wrong === 1);
    sandbox.recordChildAnswer('Dog!');
    check('S: case/punctuation normalized', sandbox.lessonStats.right === 2);
    sandbox.recordChildAnswer('doh');
    check('S: near-miss babble accepted as right', sandbox.lessonStats.right === 3);
    sandbox.recordChildAnswer('a very long sentence about the park today');
    check('S: long sentence not counted', sandbox.lessonStats.attempts.length === 4);
    sandbox.curWord = null;
    sandbox.recordChildAnswer('dog');
    check('S: no current word => not counted', sandbox.lessonStats.attempts.length === 4);
    sandbox.drawOnWhiteboard({ text: 'park', clear: true });
    check('S: drawing a word sets current word', sandbox.curWord === 'park');
  }

  // ---- lesson stats: agent record_answer tool path (authoritative) ----
  {
    sandbox.agentToolMode = false;
    sandbox.lessonStats = { right: 0, wrong: 0, attempts: [] };
    sandbox.recordAgentAnswer(true, 'dog', 'dog');
    check('T: agent tool correct => right + tool mode on', sandbox.lessonStats.right === 1 && sandbox.lessonStats.wrong === 0 && sandbox.lessonStats.attempts[0].ok === true && sandbox.agentToolMode === true);
    sandbox.recordAgentAnswer(false, 'dog', 'park');
    check('T: agent tool wrong => wrong counted', sandbox.lessonStats.wrong === 1 && sandbox.lessonStats.right === 1 && sandbox.lessonStats.attempts[1].ok === false);
    sandbox.recordAgentAnswer(true, 'park', 'park');
    check('T: second word counted too', sandbox.lessonStats.right === 2 && sandbox.lessonStats.attempts.length === 3);
  }

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(2); });
