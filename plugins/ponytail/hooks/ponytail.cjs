#!/usr/bin/env node
// Focused mode adapter, inspired by Ponytail by Dietrich Gebert. See ../LICENSE.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createStore } = require('./state.cjs');

// Only entire user commands change state; prose and skill reports are inert.
function parseCommand(prompt) {
  if (typeof prompt !== 'string') return null;
  const text = prompt.trim();
  if (/^(stop ponytail|normal mode)[.!?]*$/i.test(text)) return { kind: 'mode', mode: 'off' };
  const match = text.match(/^[/$]ponytail(?::ponytail)?(?:[ \t]+(?:(off|lite|full|ultra)|default[ \t]+(off|lite|full|ultra)))?$/i);
  if (!match) return null;
  if (match[2]) return { kind: 'default', mode: match[2].toLowerCase() };
  return match[1] ? { kind: 'mode', mode: match[1].toLowerCase() } : { kind: 'status' };
}

// Context comes only from the packaged skill and a validated mode.
function renderContext(mode) {
  if (mode === 'off') return 'PONYTAIL MODE: off. Retire earlier Ponytail persona guidance. ' +
    'Do not reactivate it through implicit skill selection. Follow the user and project instructions; ' +
    'explicitly requested reviews and other task-local skills remain available.';
  const text = fs.readFileSync(path.join(__dirname, '../skills/ponytail/SKILL.md'), 'utf8');
  const body = text.replace(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/, '');
  if (body === text || !body.trim() || body.length > 65536) throw new Error('Invalid packaged skill');
  return `PONYTAIL MODE: ${mode}. This is the latest mode; it supersedes earlier Ponytail mode context.\n\n${body}`;
}

function handleSessionStart(event, store) {
  if (!['startup', 'clear', 'fork', 'resume', 'compact'].includes(event.source)) return '';
  const restore = event.source === 'resume' || event.source === 'compact';
  const mode = (restore && store.loadState()) || store.loadDefault();
  const context = renderContext(mode);
  store.saveState(mode);
  return context;
}

function handleUserPromptSubmit(event, store) {
  const command = parseCommand(event.prompt);
  if (!command) return '';
  if (command.kind === 'default') {
    store.saveDefault(command.mode);
    return `PONYTAIL DEFAULT: ${command.mode}. Only future conversations change; this conversation's mode is unchanged.`;
  }
  let mode = command.mode;
  if (command.kind === 'status') {
    const current = store.loadState();
    if (current && current !== 'off') return `PONYTAIL MODE: ${current} (unchanged).`;
    const defaultMode = store.loadDefault();
    mode = defaultMode === 'off' ? 'full' : defaultMode;
  }
  const context = renderContext(mode);
  store.saveState(mode);
  return context;
}

function handleSubagentStart(_event, store) {
  const mode = store.loadState();
  return mode ? renderContext(mode) : '';
}

// Dispatch known events only; ordinary prompts do not even open the data store.
function dispatch(event, host) {
  if (!event || typeof event !== 'object' || Array.isArray(event)) throw new Error('Invalid event');
  const handlers = { SessionStart: handleSessionStart, UserPromptSubmit: handleUserPromptSubmit,
    SubagentStart: handleSubagentStart };
  if (!Object.hasOwn(handlers, event.hook_event_name)) return '';
  if (event.hook_event_name === 'UserPromptSubmit') {
    if (typeof event.prompt !== 'string') throw new Error('Invalid prompt');
    if (!parseCommand(event.prompt)) return '';
  }
  return handlers[event.hook_event_name](event, createStore(host, event.session_id));
}

// Read one bounded JSON event, emit one JSON response, and always release the host.
function run(host = process.argv[2]) {
  let finished = false;
  let bytes = 0;
  const chunks = [];
  const timer = setTimeout(() => finish(true), 1000);
  function finish(failed = false) {
    if (finished) return;
    finished = true;
    clearTimeout(timer);
    try {
      if (failed || process.platform === 'win32' || Number(process.versions.node.split('.')[0]) < 24) {
        throw new Error('Unsupported input or runtime');
      }
      const event = JSON.parse(Buffer.concat(chunks).toString('utf8').replace(/^\uFEFF/, ''));
      const context = dispatch(event, host);
      if (context) fs.writeSync(1, JSON.stringify({ hookSpecificOutput: {
        hookEventName: event.hook_event_name, additionalContext: context,
      } }) + '\n');
    } catch {
      try { fs.writeSync(2, 'Ponytail: hook skipped; input, runtime, or private state is unavailable.\n'); }
      catch { /* The host may already have closed its output pipes. */ }
    }
    process.exit(0);
  }
  process.stdin.on('data', chunk => {
    bytes += chunk.length;
    if (bytes > 1024 * 1024) finish(true);
    else chunks.push(chunk);
  });
  process.stdin.on('end', () => finish());
  process.stdin.on('error', () => finish(true));
}

module.exports = { parseCommand, renderContext, handleSessionStart, handleUserPromptSubmit,
  handleSubagentStart, dispatch, run };
if (require.main === module) run();
