// ATLANTECH Progress Tracker — Cloudflare Worker API.
// Static page is served from ./public; this worker only handles /api/*.
//
//   GET  /api/state                public  -> { state: {cur, t, h, x, cm} }
//   GET  /api/log?task=ID&limit=N  public  -> { log: [...] }, newest first (every change, with time and editor)
//   GET  /api/me                   editor  -> { name }
//   POST /api/op                   editor  -> body {op, ...}; returns the new state
//
// Editors are set with the EDITORS secret: "Name1:key1,Name2:key2".

const STATUSES = ['todo', 'progress', 'review', 'done', 'blocked'];
const ID_RE = /^[A-Za-z0-9-]{1,24}$/;
const CHK_RE = /^\d{1,2}-\d{1,3}$/;
const MAX_NOTE = 2000;

const SCHEMA = [
  // cs = the shared "current sprint" at the moment of the change (used to spot work finished late)
  'CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, s TEXT NOT NULL, at TEXT, by TEXT, cs INTEGER)',
  'CREATE TABLE IF NOT EXISTS notes (n INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, d TEXT NOT NULL, x TEXT NOT NULL, by TEXT)',
  'CREATE INDEX IF NOT EXISTS notes_task ON notes(task)',
  'CREATE TABLE IF NOT EXISTS checks (k TEXT PRIMARY KEY, v INTEGER NOT NULL, at TEXT, by TEXT)', // k = "h:1-0" or "x:1-0"
  'CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT)',
  // Append-only history: one row per change. op = status | note | check | cur
  'CREATE TABLE IF NOT EXISTS log (n INTEGER PRIMARY KEY AUTOINCREMENT, d TEXT NOT NULL, by TEXT, op TEXT NOT NULL, target TEXT NOT NULL, old TEXT, new TEXT, cs INTEGER)',
  'CREATE INDEX IF NOT EXISTS log_target ON log(target)',
];
// Columns added after the first release; ALTER fails harmlessly when the column already exists.
const MIGRATIONS = [
  'ALTER TABLE tasks ADD COLUMN cs INTEGER',
  'ALTER TABLE checks ADD COLUMN at TEXT',
  'ALTER TABLE checks ADD COLUMN by TEXT',
];
let schemaReady = false;
async function ensureSchema(db) {
  if (schemaReady) return;
  await db.batch(SCHEMA.map(q => db.prepare(q)));
  for (const q of MIGRATIONS) { try { await db.prepare(q).run(); } catch {} }
  schemaReady = true;
}

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
  });

function editors(env) {
  const m = new Map();
  for (const pair of String(env.EDITORS || '').split(',')) {
    const i = pair.indexOf(':');
    if (i < 1) continue;
    const name = pair.slice(0, i).trim(), key = pair.slice(i + 1).trim();
    if (name && key.length >= 8) m.set(key, name);
  }
  return m;
}

function editorName(req, env) {
  const h = req.headers.get('authorization') || '';
  const key = h.startsWith('Bearer ') ? h.slice(7).trim() : '';
  return key ? editors(env).get(key) || null : null;
}

async function readState(db) {
  const [tasks, notes, checks, meta] = await db.batch([
    db.prepare('SELECT id, s, at, by, cs FROM tasks'),
    db.prepare('SELECT task, d, x, by FROM notes ORDER BY n'),
    db.prepare('SELECT k, v, at, by FROM checks'),
    db.prepare("SELECT v FROM meta WHERE k = 'cur'"),
  ]);
  const S = { cur: 1, t: {}, h: {}, x: {}, cm: {} };
  for (const r of tasks.results) S.t[r.id] = { s: r.s, at: r.at, by: r.by, cs: r.cs };
  for (const r of notes.results) {
    const t = (S.t[r.task] = S.t[r.task] || {});
    (t.n = t.n || []).push({ d: r.d, x: r.x, by: r.by });
  }
  for (const r of checks.results) {
    S[r.k[0]][r.k.slice(2)] = !!r.v;
    if (r.at) S.cm[r.k] = { at: r.at, by: r.by };
  }
  if (meta.results[0]) S.cur = +meta.results[0].v || 1;
  return S;
}

async function readLog(db, url) {
  const task = url.searchParams.get('task');
  const limit = Math.min(Math.max(Math.trunc(+url.searchParams.get('limit')) || 300, 1), 2000);
  const cols = 'SELECT d, by, op, target, old, new, cs FROM log';
  const q = task && ID_RE.test(task)
    ? db.prepare(cols + ' WHERE target = ? ORDER BY n DESC LIMIT ?').bind(task, limit)
    : db.prepare(cols + ' ORDER BY n DESC LIMIT ?').bind(limit);
  return (await q.all()).results;
}

async function applyOp(db, b, by) {
  const now = new Date().toISOString();
  const curRow = await db.prepare("SELECT v FROM meta WHERE k = 'cur'").first();
  const cs = curRow ? +curRow.v || 1 : 1;
  const log = (op, target, old, nw) =>
    db.prepare('INSERT INTO log (d, by, op, target, old, new, cs) VALUES (?, ?, ?, ?, ?, ?, ?)')
      .bind(now, by, op, target, old == null ? null : String(old), nw == null ? null : String(nw), cs);

  switch (b.op) {
    case 'status': {
      if (!ID_RE.test(b.id) || !STATUSES.includes(b.v)) return 'bad status';
      const old = (await db.prepare('SELECT s FROM tasks WHERE id = ?').bind(b.id).first())?.s || 'todo';
      if (old === b.v) return null;
      await db.batch([
        db.prepare('INSERT INTO tasks (id, s, at, by, cs) VALUES (?1, ?2, ?3, ?4, ?5) ON CONFLICT(id) DO UPDATE SET s = ?2, at = ?3, by = ?4, cs = ?5')
          .bind(b.id, b.v, now, by, cs),
        log('status', b.id, old, b.v),
      ]);
      return null;
    }
    case 'note': {
      const x = String(b.x || '').trim();
      if (!ID_RE.test(b.id) || !x || x.length > MAX_NOTE) return 'bad note';
      await db.batch([
        db.prepare('INSERT INTO notes (task, d, x, by) VALUES (?, ?, ?, ?)').bind(b.id, now, x, by),
        log('note', b.id, null, x),
      ]);
      return null;
    }
    case 'check': {
      if (!['h', 'x'].includes(b.kind) || !CHK_RE.test(b.k)) return 'bad check';
      const k = b.kind + ':' + b.k, v = b.v ? 1 : 0;
      const old = (await db.prepare('SELECT v FROM checks WHERE k = ?').bind(k).first())?.v || 0;
      if (old === v) return null;
      await db.batch([
        db.prepare('INSERT INTO checks (k, v, at, by) VALUES (?1, ?2, ?3, ?4) ON CONFLICT(k) DO UPDATE SET v = ?2, at = ?3, by = ?4')
          .bind(k, v, now, by),
        log('check', k, old, v),
      ]);
      return null;
    }
    case 'cur': {
      const v = Math.trunc(+b.v);
      if (!(v >= 1 && v <= 99)) return 'bad sprint';
      if (v === cs && curRow) return null;
      await db.batch([
        db.prepare("INSERT INTO meta (k, v) VALUES ('cur', ?1) ON CONFLICT(k) DO UPDATE SET v = ?1").bind(String(v)),
        log('cur', 'sprint', cs, v),
      ]);
      return null;
    }
  }
  return 'unknown op';
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (!url.pathname.startsWith('/api/')) return env.ASSETS.fetch(req);
    const db = env.DB;
    await ensureSchema(db);

    if (req.method === 'GET' && url.pathname === '/api/state') return json({ state: await readState(db) });
    if (req.method === 'GET' && url.pathname === '/api/log') return json({ log: await readLog(db, url) });

    const by = editorName(req, env);
    if (url.pathname === '/api/me' && req.method === 'GET')
      return by ? json({ name: by }) : json({ error: 'wrong key' }, 401);

    if (req.method === 'POST' && url.pathname === '/api/op') {
      if (!by) return json({ error: 'editors only' }, 401);
      let body;
      try { body = await req.json(); } catch { return json({ error: 'bad json' }, 400); }
      const err = await applyOp(db, body, by);
      if (err) return json({ error: err }, 400);
      return json({ state: await readState(db) });
    }
    return json({ error: 'not found' }, 404);
  },
};
