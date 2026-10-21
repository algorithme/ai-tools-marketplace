# Ponytail — olivier-vault edition

Five skills for simpler, complete software and conversation-specific coding modes
in Claude Code and Codex. **Original author: Dietrich Gebert (DietrichGebert)**.
**Custom edition maintainer: Olivier Morel**.

Derived from [Ponytail 5.3.2](https://github.com/DietrichGebert/ponytail) at
[09c434ab73ca43761c5d8b0c5d341926c2fba710](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710).
The [upstream MIT license and copyright notice](./LICENSE) are preserved unchanged.
Version **1.0.0** belongs to this adaptation; it is not an upstream release.

## Install and review hooks

Requires **Node.js 24 or a newer supported release** on the assistant's `PATH`,
macOS or Linux, and a host supporting plugin data directories and the three
registered hook events. Windows is outside this release. There are no npm
runtime dependencies or installation scripts. CI uses Node 24.

From this marketplace checkout, choose your host:

```bash
# Claude Code
claude plugin marketplace add ./
claude plugin install ponytail@olivier-vault

# Codex
codex plugin marketplace add ./
codex plugin add ponytail@olivier-vault
```

These commands modify the selected host's installation. Review the selected
hook manifest and `hooks/*.cjs` first. Use the host's normal hook review/trust
flow (`/hooks`), then start a new conversation. Do not copy trust settings or
disable host review. Updated hooks require review again. See the official
[Claude hook contract](https://code.claude.com/docs/en/hooks) and
[Codex hook contract](https://learn.chatgpt.com/docs/hooks).
Full mode is the initial default once the hooks run successfully.

## Commands and skills

Send mode commands as a **standalone message**; commands quoted in prose or
code fences do not change settings. The hook also recognizes short `/ponytail`
and `$ponytail` forms when the host delivers them as user text.

| Purpose | Claude Code | Codex |
|---|---|---|
| Status; enable when off | `/ponytail:ponytail` | `$ponytail:ponytail` |
| Light guidance | `/ponytail:ponytail lite` | `$ponytail:ponytail lite` |
| Smallest complete change | `/ponytail:ponytail full` | `$ponytail:ponytail full` |
| Challenge unnecessary work | `/ponytail:ponytail ultra` | `$ponytail:ponytail ultra` |
| Turn off in this conversation | `/ponytail:ponytail off` | `$ponytail:ponytail off` |
| Change future default | `/ponytail:ponytail default lite` | `$ponytail:ponytail default lite` |
| Review a change | `/ponytail:ponytail-review` | `$ponytail:ponytail-review` |
| Audit a repository scope | `/ponytail:ponytail-audit` | `$ponytail:ponytail-audit` |
| List deliberate shortcuts | `/ponytail:ponytail-debt` | `$ponytail:ponytail-debt` |
| Help | `/ponytail:ponytail-help` | `$ponytail:ponytail-help` |

`default` accepts one of `off`, `lite`, `full`, or `ultra`. “Stop ponytail” and
“normal mode” also turn off the persona when sent alone. A bare command keeps
an active mode; when off, it enables the default (full if the default is off).
Review, audit, debt, and help are one-shot operations available even while off.
Review/audit do not edit code; debt saves a report only when explicitly requested.

## State and coexistence

Each host and conversation has independent state. Resume and compaction restore
the mode; startup, clear, and fork use the saved default. Changing directories
does not change identity. Subagents inherit the parent's saved mode without
changing it. A default change does not alter any existing conversation.

Claude stores records under `$CLAUDE_PLUGIN_DATA/ponytail-v1/claude/`; Codex uses
`$PLUGIN_DATA/ponytail-v1/codex/`. These variables are supplied to the hook by
the host. Private files contain only `mode` or `defaultMode`; session filenames
use SHA-256 hashes of host session IDs. No prompts or transcripts are saved.
The adapter requires a canonical, owned data path and rejects symlinks and
nonregular files. Missing/unsafe storage disables persistence with a generic
diagnostic; it never falls back to project files or user settings.

Retained session files enable resume and are not automatically pruned. To reset,
close the host's conversations and remove only this plugin's `ponytail-v1/<host>/`
directory from the actual host-provided data location. A later resume then uses
the default, initially full. No upstream mode files or configuration are migrated.

The latest hook mode governs the persona; implicit skill selection cannot turn
off back on. Without working hooks, explicitly requested skills supply task-local
guidance and cannot claim persistent activation. Off retires earlier guidance;
it does not erase conversation history. Use one Ponytail edition at a time.
Grumpy retains its planning, approval, and validation workflows. Ponytail does
not override those, the user's scope, settled architecture, security, or accessibility.

## Differences and verification

This edition excludes upstream board, metrics, webhook, transcript imports,
source mapper, status-line setup, scoreboard, and other assistant integrations.
The small Node adapter is maintained independently; future upstream imports
require a fresh source and safety review. See [CHANGELOG](./CHANGELOG.md) and the
[scoped safety assessment](../../docs/plugins/ponytail/security-review.md).

Run `./scripts/validate.sh` from the marketplace root. Native smoke checks remain
separate: in a disposable profile for **each host**, install and inspect hooks;
confirm full on startup, off after its command and after resume/compact, a changed
default only in a new/cleared/forked conversation, isolation between two sessions,
and parent mode in a subagent. Confirm ordinary prompts have no hook output and
reports work while off. Record host versions and observed trust behavior.
This local delivery ran launcher tests, not those native installation/trust checks;
no active assistant installations were changed and publication remains pending.
