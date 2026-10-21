// Local mode storage for the olivier-vault adaptation of Dietrich Gebert's Ponytail.
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createHash, randomBytes } = require('node:crypto');
const MODES = ['off', 'lite', 'full', 'ultra'];
const isMode = value => MODES.includes(value);

// Reject redirected or shared storage; the host owns the parent data directory.
function directory(dir, create, privateOnly) {
  try {
    if (create) {
      try { fs.mkdirSync(dir, { mode: 0o700 }); }
      catch (error) { if (error.code !== 'EEXIST') throw error; }
    }
    const stat = fs.lstatSync(dir);
    if (!stat.isDirectory() || fs.realpathSync(dir) !== dir ||
        stat.uid !== process.getuid() || (stat.mode & (privateOnly ? 0o077 : 0o022))) {
      throw new Error('Unsafe state directory');
    }
    return true;
  } catch (error) {
    if (!create && error.code === 'ENOENT') return false;
    throw error;
  }
}

// Create a host-specific store; session IDs never become path components.
function createStore(host, sessionId) {
  const variable = { claude: 'CLAUDE_PLUGIN_DATA', codex: 'PLUGIN_DATA' }[host];
  const supplied = variable && process.env[variable];
  if (!supplied || !path.isAbsolute(supplied) || typeof sessionId !== 'string' ||
      !sessionId.trim() || sessionId.length > 4096) throw new Error('Missing host context');
  const root = path.normalize(supplied).replace(/\/$/, '');
  if (!root || root === path.parse(root).root) throw new Error('Unsafe data root');
  const dirs = [root, path.join(root, 'ponytail-v1'), path.join(root, 'ponytail-v1', host)];
  const key = createHash('sha256').update(sessionId).digest('hex');
  const session = `session-${key}.json`;

  function prepare(create) {
    // Existing ancestor symlinks are rejected before any directory is created.
    const parent = path.dirname(root);
    if (fs.realpathSync(parent) !== parent) throw new Error('Redirected data root');
    return dirs.every((dir, index) => directory(dir, create, index > 0));
  }

  function checkedFile(file) {
    const stat = fs.lstatSync(file);
    if (!stat.isFile() || stat.uid !== process.getuid() || stat.nlink !== 1 ||
        (stat.mode & 0o077)) throw new Error('Unsafe state file');
    return stat;
  }

  // A missing or invalid value is absent state, never a new instruction.
  function read(name, field) {
    if (!prepare(false)) return null;
    const file = path.join(dirs[2], name);
    let fd;
    try {
      checkedFile(file);
      fd = fs.openSync(file, fs.constants.O_RDONLY | fs.constants.O_NOFOLLOW | fs.constants.O_NONBLOCK);
      const stat = fs.fstatSync(fd);
      if (!stat.isFile() || stat.size > 4096) return null;
      const buffer = Buffer.alloc(4097);
      const size = fs.readSync(fd, buffer, 0, buffer.length, 0);
      if (size > 4096) return null;
      let value;
      try { value = JSON.parse(buffer.subarray(0, size).toString('utf8')); }
      catch { return null; }
      return value && !Array.isArray(value) && Object.keys(value).length === 1 &&
        isMode(value[field]) ? value[field] : null;
    } catch (error) {
      if (error.code === 'ENOENT') return null;
      throw error;
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
    }
  }

  // Replace complete files atomically; never follow an existing target link.
  function write(name, field, mode) {
    if (!isMode(mode)) throw new Error('Invalid mode');
    prepare(true);
    const file = path.join(dirs[2], name);
    try { checkedFile(file); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    const temporary = path.join(dirs[2], `.tmp-${randomBytes(16).toString('hex')}`);
    let fd;
    try {
      fd = fs.openSync(temporary, 'wx', 0o600);
      fs.writeFileSync(fd, JSON.stringify({ [field]: mode }) + '\n');
      fs.fsyncSync(fd);
      fs.closeSync(fd);
      fd = undefined;
      fs.renameSync(temporary, file);
    } finally {
      if (fd !== undefined) fs.closeSync(fd);
      try { fs.unlinkSync(temporary); }
      catch (error) { if (error.code !== 'ENOENT') throw error; }
    }
  }

  return {
    loadState: () => read(session, 'mode'),
    saveState: mode => write(session, 'mode', mode),
    loadDefault: () => read('config.json', 'defaultMode') || 'full',
    saveDefault: mode => write('config.json', 'defaultMode', mode),
  };
}

module.exports = { createStore, isMode };
