# Ponytail 1.0.0 — scoped safety assessment

Review date: 2026-10-21. This record covers the **shipped custom package** and
its marketplace integration, not a security certification of upstream Ponytail.
Original author: **Dietrich Gebert (DietrichGebert)**; adaptation: **Olivier Morel**.

## Source and review boundary

Base: [upstream 5.3.2 at 09c434ab73ca43761c5d8b0c5d341926c2fba710](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710).
Reviewed before running custom code: the upstream tree, README, LICENSE,
package.json, Claude/Codex manifests, all six upstream skill entrypoints,
`hooks/claude-codex-hooks.json`, and `hooks/ponytail-{config,runtime,instructions,
map,subagent,activate,mode-tracker}.js`. Upstream installers were not executed.
Excluded packages and integrations were not exhaustively audited.

Reviewed custom dependency closure: both plugin manifests, both hook manifests,
`hooks/ponytail.cjs`, `hooks/state.cjs`, all five skills, license, documentation,
and regression tests. Runtime imports are only local `state.cjs` and Node's
`fs`, `path`, and `crypto`; there is no npm runtime dependency, network client,
process spawning, installer, transcript reader, or repository scanner.
The test harness uses child processes to exercise the real manifest launchers.

## Findings and retained behavior

Upstream includes broader source discovery, status-line/configuration setup,
shared mode handling, and board/metrics/webhook paths. Those behaviors exceed
this edition's scope and were excluded, not declared vulnerabilities in upstream.
Only five rewritten skill entrypoints and a focused mode adapter are shipped.
The upstream MIT notice is retained byte-for-byte and every skill credits its author.

The shipped runtime has the following boundaries:

- Only exact standalone allowlisted commands can change modes/defaults. Prose,
  quoted commands, reports, unknown arguments, and shell punctuation are inert.
- Hooks read bounded JSON from stdin (1 MiB, one-second deadline) and return at
  most one event-specific context object. Errors exit zero with a generic message.
  Output consists of validated modes and packaged guidance, never raw input.
- Claude launches Node with direct arguments. Codex runs a fixed loader reading
  `PLUGIN_ROOT` from its environment; paths/prompts are not inserted into shell code.
- Persistence uses only host-provided plugin data with separate host directories.
  Session IDs become SHA-256 filenames; files contain one validated mode value.
  Private directories/files, ownership checks, symlink/nonregular-file rejection,
  exclusive temporary files, and atomic rename limit accidental redirection and
  partial records. Concurrent commands for one conversation use last-write-wins.
- Full is the initial default. Off persists across resume/compaction and cannot
  be reactivated by implicit selection. Startup/clear/fork use defaults; changing
  defaults leaves existing sessions alone. Subagents read parent state only.
- Skills preserve scope, settled architecture, meaningful validation, security,
  and accessibility. Reports are read-only unless saving debt was requested;
  custom markers are literal search input. Shortcut comments never waive defects.

No release-blocking issue was identified in this scoped manual review. This is
evidence about the inspected paths and exercised cases, not a guarantee of safety.

## Evidence

The [hook suite](../../../plugins/ponytail/tests/hooks.test.cjs) exercises both
manifest launchers, lifecycle/defaults, host/session isolation, subagents, hostile
paths/IDs, symlinks, malformed/oversized state/input, private permissions,
unwritable/missing storage, stalled input, concurrent writes, and output privacy.
The oversized-input test allows the expected writer-side EPIPE after early exit;
it still requires successful hook exit, no context output, and a generic diagnostic.

Two independent skill-creator forward-test agents used temporary fixtures and
the [reproducible scenarios](../../../plugins/ponytail/tests/skill-scenarios.md):

| Scenario | Observed result |
|---|---|
| Full-mode search simplification | Case-insensitive substring behavior and order retained; six assertions passed. |
| Off-mode explanation and help | No mode/config changes; accurate host commands and task-local reporting. |
| Review and audit of tenant authorization | Both reported a cross-tenant support bypass despite its shortcut marker; no edits. |
| Debt and literal shell-like marker | Correct deferrals, missing trigger flagged, no report/file writes or marker execution. |

The evaluator initially inspected an ignored fixture file while inventorying;
actual debt searches and output excluded it. Only the requested search function
changed across the fixture runs. These are sampled behavioral observations.

Local results on macOS arm64:

- `./scripts/validate.sh` passed on **Node 24.0.0**: 17 Ponytail tests, 9 package
  validator tests, and 16 Grumpy tests; schemas, YAML, and ShellCheck all ran.
  The earlier 16-test hook suite also passed on Node 26.12.0; the added loader
  failure check and both hostile-path launchers passed there after the final change.
- All five skills passed skill-creator's `quick_validate.py` (PyYAML 6.0.3).
- actionlint 1.7.12 passed the changed workflow; ShellCheck 0.11.0 was available.
- Claude 2.1.303 validated Ponytail and the marketplace. The marketplace retained
  its existing nonblocking Humanizer missing-author warning. Codex 0.163.0 CLI
  help and the repository's compatibility/path validator were checked.
- The license matched the pinned source byte-for-byte (SHA-256
  `fb1bc6909ac3ef82d5c22106e32ef682b0cff66788fa915fb9b53b15c9d2f3ab`).
  Workflow inventory hashes, Renovate provenance, and local document links matched.

## Remaining limitations and native smoke status

Native Claude/Codex installation, trust prompts, event ordering, session-ID
propagation, and real assistant compliance were **not** exercised. Use the
[native smoke checklist](../../../plugins/ponytail/README.md#differences-and-verification)
before publication. CLI help/manifest checks do not establish native compatibility.
No remote CI run or publication is claimed; user profiles were not changed.

The host, Node executable/PATH, package files, and host-provided environment are
trusted. These checks do not isolate malicious processes running as the same OS
user or defend against all concurrent ancestor-directory replacement races.
The one-second limit bounds stdin acquisition, not a hung synchronous filesystem;
the host's five-second timeout remains the outer bound. Atomic replacement is not
a promise of crash durability across filesystem or power failures.

Guidance influences an assistant; it is not a security sandbox or enforcement
layer. Off cannot erase old context. Session files accumulate to support resume.
Windows is unsupported, and future upstream imports or host contract changes
need renewed review and tests. No upstream defaults or config are migrated.
