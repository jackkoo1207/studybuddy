// plan.test.js — StudyBuddy prototype verification (ad-hoc, not a canonical test suite).
// Extracts the REAL inline JS from ../index.html, runs it against REAL sql.js (npm)
// in a stubbed DOM that mirrors real element existence (EA-block <36mo, EB-block >=36mo).
// Run: cd verify && npm i && npm test
const fs = require('fs'), vm = require('vm'), path = require('path');
const sqlInit = require('sql.js');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');

// ---------- DOM stub ----------
const values = {};            // id -> current .value
const elements = {};
const opts = [];              // .opt registry (chips per question)
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
  btoa: b => Buffer.from(b, 'binary').toString('base64'), atob: b => Buffer.from(b, 'base64').toString('binary'),
  localStorage: { getItem: k => storage.has(k) ? storage.get(k) : null, setItem: (k, v) => storage.set(k, v), removeItem: k => storage.delete(k) },
  document: { getElementById: el, querySelectorAll: sel => sel === '.opt' ? opts : [], addEventListener() {}, createElement: el },
  location: { href: '' },
};
sandbox.window = sandbox;
vm.createContext(sandbox);
(async () => {
  sandbox.initSqlJs = () => sqlInit(); // real sql.js injected in place of the CDN global (initSqlJs(config) => Promise<SQL>)
  vm.runInContext(scripts, sandbox, { filename: 'index.html-inline.js' });
  sandbox.PATHWAYS.forEach(p => p.questions.forEach(q => makeOpt(q[0], false, ['0', '1', '2', '3'])));
  for (const [n, m, vs] of [['tier', false, ['1線', '2線', '3線', '4線', '5線', '香港']], ['freq', false, ['每天 10 分鐘', '每週 3-4 次', '每週 1-2 次', '不確定']], ['screen', false, ['完全接受', '適度使用', '盡量減少', '不接受']], ['E2', true, ['英文兒歌', '英文繪本', '以上皆無']]]) makeOpt(n, m, vs);

  let pass = 0, fail = 0;
  const check = (n, c) => { c ? pass++ : fail++; console.log((c ? 'PASS' : 'FAIL') + '  ' + n); };
  const view = v => !sandbox.document.getElementById('view-' + v).classList.contains('hidden');
  const WEAK_ANSWERS = { inParent: '陳太', inBaby: '小宇', inBirth: '2022-08-01', inNote: '好動坐不住', E1: '15–30 分鐘', E3: '有時', E4: '每週數次', EB1: '只會點頭或搖頭', EB2: '很少', EB3: '只會幾個字', EB5: '很少', EB6: '1–2 個', EB7: '很少' };
  const setPhys = (strong = true) => { for (const id of ['V5', 'V6', 'A5', 'A6', 'T5', 'T6', 'M5', 'M6', 'L5', 'L6']) sandbox.S[id] = 3; if (!strong) { sandbox.S.L7 = 1; sandbox.S.H5 = 1; sandbox.S.H6 = 1; } };

  // ---- flow 1: fill + submit => levels/mistakes/progress/chat derived from answers ----
  await sandbox.initSql();
  sandbox.S.user = 't1';
  sandbox.S.months = 48; sandbox.S.tier = '香港'; sandbox.S.freq = '每週 3-4 次'; sandbox.S.screen = '適度使用'; sandbox.S.physWindow = [5, 7];
  Object.assign(values, WEAK_ANSWERS); setPhys(false);
  sandbox.DB = sandbox.loadDb('t1');
  vm.runInContext('submitAssessment();', sandbox);
  check('1: weak answers => L2', sandbox.S.level === 'L2');
  check('1: mistakes EMPTY (no lessons yet)', sandbox.S.mistakes.length === 0);
  check('1: phys weak detected', sandbox.S.phys.weak.length > 0);
  check('1: chat script derived for level', sandbox.S.script.length >= 3);
  check('1: plan has 4 weeks', sandbox.S.teachingPlan.weeks.length === 4);
  check('1: week1 focus mentions weak area, no baked 第N週 prefix', !/^第\s*\d+\s*週/.test(sandbox.S.teachingPlan.weeks[0].focus) && sandbox.S.teachingPlan.weeks[0].focus.indexOf('薄弱項') >= 0);
  check('1: answers + plan persisted to SQLite', sandbox.DB.exec("SELECT COUNT(*) FROM answers")[0].values[0][0] >= 20 && sandbox.DB.exec("SELECT COUNT(*) FROM plan WHERE id=1")[0].values[0][0] === 1);
  const genAt = sandbox.S.teachingPlan.generated_at;

  // ---- flow 2: complete lesson => schedule advances + persisted ----
  vm.runInContext('completeLesson();', sandbox);
  check('2: schedule advanced + persisted', sandbox.S.schedule.current_lesson === 1 && sandbox.S.schedule.completed.length === 1 && sandbox.DB.exec("SELECT schedule_json FROM plan WHERE id=1")[0].values[0][0].indexOf('current_lesson":1') >= 0);

  // ---- flow 3: re-login => skip questionnaire, plan NOT regenerated ----
  sandbox.S = {}; sandbox.DB = null;
  await sandbox.afterLogin('t1');
  check('3: returning user lands on dashboard (questionnaire skipped)', view('dash') && !view('questionnaire'));
  check('3: plan preserved, not regenerated', sandbox.S.teachingPlan.generated_at === genAt && sandbox.S.schedule.current_lesson === 1);
  check('3: level recomputed from answers', sandbox.S.level === 'L2');

  // ---- flow 4: old-format plan migration ----
  sandbox.S = {}; sandbox.DB = null;
  await sandbox.afterLogin('m1'); // creates empty DB; seed old plan + answers
  sandbox.S.user = 'm1'; sandbox.S.months = 48; sandbox.S.tier = '香港'; sandbox.S.freq = '每週 3-4 次'; sandbox.S.screen = '適度使用'; sandbox.S.physWindow = [5, 7];
  Object.assign(values, { inBirth: '2022-08-01', EB1: '能說一兩個字' }); setPhys(true);
  sandbox.saveAnswers();
  sandbox.DB.run("INSERT OR REPLACE INTO plan(id,plan_json,schedule_json) VALUES(1,?,?)", [JSON.stringify({ generated_at: '2026-08-01', level: 'L4', weeks: [1, 2, 3, 4].map(w => ({ week: w, focus: '第 ' + w + ' 週：主題', lessons: [{ day: 'Day 1', pillar: 'Hear', activity: 'a', how: 'h', words: '—', goal: 'g' }] })) }), '{}']);
  sandbox.saveDb();
  const mig = sandbox.loadPlan();
  check('4: baked 第N週 prefix stripped on load', mig.plan.weeks.every(w => !/^第\s*\d+\s*週/.test(w.focus)));
  check('4: generated_at preserved', mig.plan.generated_at === '2026-08-01');

  // ---- flow 5: brand-new account => questionnaire ----
  sandbox.S = {}; sandbox.DB = null;
  await sandbox.afterLogin('t2');
  check('5: new account goes to questionnaire', view('questionnaire') && !view('dash'));

  // ---- flow 6: old AvatarPlan UI removed from markup ----
  check('6: avatarKV/physKV/routingNote gone', html.indexOf('id="avatarKV"') < 0 && html.indexOf('id="physKV"') < 0 && html.indexOf('id="routingNote"') < 0);
  check('6: todayCard + weekPlan present', html.indexOf('id="todayCard"') >= 0 && html.indexOf('id="weekPlan"') >= 0);

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('HARNESS ERROR:', e); process.exit(2); });
