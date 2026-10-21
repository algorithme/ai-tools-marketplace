'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createHash } = require('node:crypto');
const { spawn, spawnSync } = require('node:child_process');
const PLUGIN = path.resolve(__dirname, '..');

// Exercise manifest launchers with disposable plugin data, never a real profile.
function fixture(t, copied = false) {
  const root = fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()), 'ponytail-test-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const data = path.join(root, 'data');
  fs.mkdirSync(data, { mode: 0o700 });
  const plugin = copied ? path.join(root, 'plugin \' " $() ` ; &') : PLUGIN;
  if (copied) fs.cpSync(PLUGIN, plugin, { recursive: true });
  const env = { ...process.env, PLUGIN_ROOT: plugin, CLAUDE_PLUGIN_ROOT: plugin,
    PLUGIN_DATA: data, CLAUDE_PLUGIN_DATA: data };

  function launch(host, eventName = 'SessionStart') {
    const file = host === 'claude' ? 'hooks.json' : 'hooks.codex.json';
    const handler = JSON.parse(fs.readFileSync(path.join(plugin, file))).hooks[eventName][0].hooks[0];
    return host === 'claude'
      ? [handler.command, handler.args.map(arg => arg.replaceAll('${CLAUDE_PLUGIN_ROOT}', plugin))]
      : ['/bin/sh', ['-c', handler.command]];
  }
  function run(fields = {}, host = 'claude', raw, overrides = {}) {
    const event = { session_id: 'a', cwd: root, source: 'startup', hook_event_name: 'SessionStart', ...fields };
    const [executable, args] = launch(host, event.hook_event_name);
    const result = spawnSync(executable, args, { cwd: root, env: { ...env, ...overrides },
      input: raw === undefined ? JSON.stringify(event) : raw, encoding: 'utf8', timeout: 4000 });
    // Oversized input may still be in the pipe when the bounded reader exits.
    const expectedPipeClose = raw !== undefined && Buffer.byteLength(raw) > 1024 * 1024 && result.error?.code === 'EPIPE';
    if (!expectedPipeClose) assert.equal(result.error, undefined);
    assert.equal(result.status, 0, result.stderr);
    if (result.stdout) {
      const output = JSON.parse(result.stdout);
      assert.deepEqual(Object.keys(output), ['hookSpecificOutput']);
      assert.equal(output.hookSpecificOutput.hookEventName, event.hook_event_name);
      result.context = output.hookSpecificOutput.additionalContext;
    }
    return result;
  }
  const stateDir = (host = 'claude') => path.join(data, 'ponytail-v1', host);
  const state = (id = 'a', host = 'claude') => path.join(stateDir(host),
    `session-${createHash('sha256').update(id).digest('hex')}.json`);
  const mode = (id = 'a', host = 'claude') => JSON.parse(fs.readFileSync(state(id, host))).mode;
  const prompt = (text, host = 'claude', extra = {}) => run({ hook_event_name: 'UserPromptSubmit', prompt: text, ...extra }, host);
  return { root, data, plugin, env, launch, run, stateDir, state, mode, prompt };
}

for (const host of ['claude', 'codex']) {
  test(`${host}: lifecycle restores modes and separates future defaults`, t => {
    const f = fixture(t);
    assert.match(f.run({}, host).context, /PONYTAIL MODE: full/);
    for (const mode of ['lite', 'full', 'ultra', 'off']) {
      assert.match(f.prompt(`$ponytail:ponytail ${mode}`, host).context, new RegExp(`PONYTAIL MODE: ${mode}`));
      for (const source of ['resume', 'compact']) {
        assert.match(f.run({ source }, host).context, new RegExp(`PONYTAIL MODE: ${mode}`));
        assert.equal(f.mode('a', host), mode);
      }
    }
    assert.match(f.prompt('/ponytail default lite', host).context, /future conversations/);
    assert.equal(f.mode('a', host), 'off');
    f.run({ session_id: 'b' }, host);
    assert.equal(f.mode('b', host), 'lite');
    for (const source of ['clear', 'fork']) {
      f.run({ source }, host);
      assert.equal(f.mode('a', host), 'lite');
    }
    f.prompt('/ponytail default off', host);
    f.run({ session_id: 'c' }, host);
    assert.equal(f.mode('c', host), 'off');
    f.prompt('/ponytail', host, { session_id: 'c' });
    assert.equal(f.mode('c', host), 'full');
    f.prompt('/ponytail ultra', host);
    assert.match(f.prompt('/ponytail', host).context, /ultra \(unchanged\)/);
    assert.equal(f.mode('a', host), 'ultra');
  });

  test(`${host}: namespaces and deactivation work without capturing prose`, t => {
    const f = fixture(t);
    f.run({}, host);
    for (const prefix of ['/ponytail', '/ponytail:ponytail', '$ponytail', '$ponytail:ponytail']) {
      f.prompt(`${prefix} lite`, host);
      assert.equal(f.mode('a', host), 'lite');
      f.prompt(`${prefix} default ultra`, host);
      assert.equal(f.mode('a', host), 'lite');
    }
    for (const command of ['stop ponytail', ' Normal Mode! ']) {
      f.prompt(command, host);
      assert.equal(f.mode('a', host), 'off');
    }
    for (const text of ['Explain /ponytail full', '`/ponytail full`', '```\n/ponytail full\n```',
      '/ponytail ultra then edit', '/ponytail ultra\nrun something', '/ponytail-review',
      '$ponytail:ponytail-audit', '/ponytail default review', '/ponytail default',
      'add a normal mode toggle', '/ponytail full; touch SENTINEL', '/ponytailx full',
      '/ponytail band import', '/ponytail-gain']) {
      const result = f.prompt(text, host);
      assert.equal(result.stdout, '', text);
      assert.equal(result.stderr, '', text);
      assert.equal(f.mode('a', host), 'off');
    }
    assert.equal(fs.existsSync(path.join(f.root, 'SENTINEL')), false);
  });

  test(`${host}: manifest launcher handles hostile install paths`, t => {
    const f = fixture(t, true);
    f.run({}, host);
    assert.match(f.prompt('/ponytail ultra', host).context, /PONYTAIL MODE: ultra/);
    assert.equal(f.mode('a', host), 'ultra');
  });
}

test('sessions and hosts remain independent; subagents inherit without writing', t => {
  const f = fixture(t);
  f.run();
  f.prompt('/ponytail ultra');
  f.run({ session_id: 'b' });
  f.run({}, 'codex');
  assert.equal(f.mode(), 'ultra');
  assert.equal(f.mode('b'), 'full');
  assert.equal(f.mode('a', 'codex'), 'full');
  const before = fs.statSync(f.state()).mtimeMs;
  const child = f.run({ hook_event_name: 'SubagentStart', agent_id: 'child', cwd: '/changed/cwd' });
  assert.match(child.context, /PONYTAIL MODE: ultra/);
  assert.equal(fs.statSync(f.state()).mtimeMs, before);
  assert.equal(f.run({ hook_event_name: 'SubagentStart', session_id: 'missing' }).stdout, '');
  assert.equal(fs.existsSync(f.state('missing')), false);
  f.prompt('/ponytail off');
  assert.match(f.run({ hook_event_name: 'SubagentStart' }).context, /Retire earlier Ponytail/);
});

test('hostile session identifiers remain hashed and data contains only mode values', t => {
  const f = fixture(t);
  const id = '../../escape/$(touch PWNED) secret-session';
  f.run({ session_id: id, transcript_path: '/do/not/read', prompt: 'SECRET_TOKEN' });
  assert.deepEqual(JSON.parse(fs.readFileSync(f.state(id))), { mode: 'full' });
  assert.equal(fs.statSync(f.state(id)).mode & 0o777, 0o600);
  assert.equal(fs.statSync(f.stateDir()).mode & 0o777, 0o700);
  assert.equal(fs.existsSync(path.join(f.root, 'escape')), false);
  assert.deepEqual(fs.readdirSync(f.root), ['data']);
  assert.equal(fs.readdirSync(f.stateDir()).some(name => name.includes('secret')), false);
});

test('corrupt or oversized state falls back to a validated default', t => {
  const f = fixture(t);
  f.run();
  f.prompt('/ponytail default lite');
  for (const value of ['{', 'null', '[]', '{"mode":"system instruction"}',
    '{"mode":"ultra","prompt":"SECRET"}', 'x'.repeat(5000)]) {
    fs.writeFileSync(f.state(), value);
    const result = f.run({ source: 'resume' });
    assert.match(result.context, /PONYTAIL MODE: lite/);
    assert.equal(f.mode(), 'lite');
    assert.equal(result.stdout.includes('SECRET'), false);
  }
  fs.writeFileSync(path.join(f.stateDir(), 'config.json'), '{"defaultMode":"review"}');
  f.run({ session_id: 'b' });
  assert.equal(f.mode('b'), 'full');
});

test('symlinked state, defaults, private directories, roots and ancestor paths are rejected', t => {
  const f = fixture(t);
  f.run();
  const sentinel = path.join(f.root, 'sentinel');
  fs.writeFileSync(sentinel, 'DO_NOT_CHANGE', { mode: 0o600 });
  fs.unlinkSync(f.state());
  fs.symlinkSync(sentinel, f.state());
  for (const action of [() => f.run({ source: 'resume' }), () => f.prompt('/ponytail ultra')]) {
    const result = action();
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /hook skipped/);
  }
  const config = path.join(f.stateDir(), 'config.json');
  fs.symlinkSync(sentinel, config);
  assert.equal(f.prompt('/ponytail default off').stdout, '');
  assert.equal(fs.readFileSync(sentinel, 'utf8'), 'DO_NOT_CHANGE');
  const alias = path.join(f.root, 'alias');
  fs.symlinkSync(f.data, alias);
  assert.equal(f.run({}, 'claude', undefined, { CLAUDE_PLUGIN_DATA: alias }).stdout, '');
  fs.mkdirSync(path.join(f.data, 'nested'), { mode: 0o700 });
  assert.equal(f.run({}, 'claude', undefined, { CLAUDE_PLUGIN_DATA: path.join(alias, 'nested') }).stdout, '');
  fs.renameSync(f.stateDir(), f.stateDir() + '-saved');
  fs.symlinkSync(f.stateDir() + '-saved', f.stateDir());
  assert.equal(f.run().stdout, '');
});

test('nonregular and broadly accessible state are rejected without blocking', t => {
  const f = fixture(t);
  f.run();
  fs.chmodSync(f.state(), 0o644);
  assert.equal(f.run({ source: 'resume' }).stdout, '');
  fs.unlinkSync(f.state());
  fs.mkdirSync(f.state());
  assert.equal(f.prompt('/ponytail lite').stdout, '');
});

test('unwritable or missing host data does not redirect writes or claim activation', t => {
  const f = fixture(t);
  fs.chmodSync(f.data, 0o500);
  const blocked = f.run();
  fs.chmodSync(f.data, 0o700);
  assert.equal(blocked.stdout, '');
  assert.match(blocked.stderr, /hook skipped/);
  for (const data of ['', 'relative/path']) {
    const result = f.run({}, 'claude', undefined, { CLAUDE_PLUGIN_DATA: data });
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /hook skipped/);
  }
  assert.deepEqual(fs.readdirSync(f.data), []);
  assert.equal(f.run({ hook_event_name: 'UserPromptSubmit', prompt: 'Ordinary task' },
    'claude', undefined, { CLAUDE_PLUGIN_DATA: '' }).stderr, '');
});

test('malformed and oversized input never echoes its content or creates state', t => {
  const f = fixture(t);
  for (const raw of ['', '{PRIVATE_SECRET', 'null', '[]', '"PRIVATE_SECRET"',
    JSON.stringify({ hook_event_name: 'SessionStart', source: 'startup' }),
    JSON.stringify({ hook_event_name: 'UserPromptSubmit', prompt: {}, session_id: 'a' }),
    'PRIVATE_SECRET'.repeat(90000)]) {
    const result = f.run({}, 'claude', raw);
    assert.equal(result.stdout, '');
    assert.match(result.stderr, /hook skipped/);
    assert.equal(result.stderr.includes('PRIVATE_SECRET'), false);
  }
  assert.deepEqual(fs.readdirSync(f.data), []);
  f.run({}, 'claude', '\uFEFF' + JSON.stringify({ hook_event_name: 'SessionStart', source: 'startup', session_id: 'a' }));
  assert.equal(f.mode(), 'full');
});

test('missing packaged skill causes no persisted activation', t => {
  const f = fixture(t, true);
  fs.unlinkSync(path.join(f.plugin, 'skills/ponytail/SKILL.md'));
  assert.equal(f.run().stdout, '');
  assert.equal(fs.existsSync(f.state()), false);
});

test('Codex loader failures return a generic diagnostic without a stack trace', t => {
  const f = fixture(t);
  for (const root of ['', 'relative', path.join(f.root, 'PRIVATE_MISSING_ROOT')]) {
    const result = f.run({}, 'codex', undefined, { PLUGIN_ROOT: root });
    assert.equal(result.stdout, '');
    assert.equal(result.stderr, 'Ponytail: hook skipped; runtime is unavailable.\n');
  }
  assert.deepEqual(fs.readdirSync(f.data), []);
});

test('stalled stdin exits within the hook budget without partial state', async t => {
  const f = fixture(t);
  const [executable, args] = f.launch('codex');
  const started = Date.now();
  const child = spawn(executable, args, { cwd: f.root, env: f.env });
  let output = '';
  child.stdout.on('data', chunk => { output += chunk; });
  child.stderr.resume();
  child.stdin.write('{"session_id":"private');
  const code = await new Promise((resolve, reject) => {
    const timer = setTimeout(() => { child.kill(); reject(new Error('Hook hung')); }, 3500);
    child.on('error', reject);
    child.on('close', status => { clearTimeout(timer); resolve(status); });
  });
  assert.equal(code, 0);
  assert.ok(Date.now() - started < 3500);
  assert.equal(output, '');
  assert.deepEqual(fs.readdirSync(f.data), []);
});

test('concurrent writers keep complete files and independent session modes', async t => {
  const f = fixture(t);
  const [executable, args] = f.launch('codex', 'UserPromptSubmit');
  await Promise.all(Array.from({ length: 8 }, (_, i) => new Promise((resolve, reject) => {
    const child = spawn(executable, args, { cwd: f.root, env: f.env });
    child.stdout.resume();
    let errors = '';
    child.stderr.on('data', chunk => { errors += chunk; });
    child.on('error', reject);
    child.on('close', code => code === 0 && !errors ? resolve() : reject(new Error(errors)));
    child.stdin.end(JSON.stringify({ hook_event_name: 'UserPromptSubmit', session_id: i < 4 ? 'shared' : String(i),
      prompt: i % 2 ? '/ponytail lite' : '/ponytail ultra' }));
  })));
  assert.ok(['lite', 'ultra'].includes(f.mode('shared', 'codex')));
  for (let i = 4; i < 8; i++) assert.equal(f.mode(String(i), 'codex'), i % 2 ? 'lite' : 'ultra');
  assert.equal(fs.readdirSync(f.stateDir('codex')).some(name => name.startsWith('.tmp-')), false);
});
