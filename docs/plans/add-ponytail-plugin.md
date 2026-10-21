# Add the custom Ponytail plugin to olivier-vault

## 1. Non-negotiables

Deliver validated local working-tree changes on `feat/add-ponytail-plugin`. The marketplace stores plugins under `plugins/`, registers explicit relative paths, and uses `scripts/validate.sh` as its validation authority.

Base the adaptation on Dietrich Gebert’s [Ponytail 5.3.2, commit 09c434ab73ca43761c5d8b0c5d341926c2fba710](https://github.com/DietrichGebert/ponytail/tree/09c434ab73ca43761c5d8b0c5d341926c2fba710). Preserve its [MIT license and copyright notice](https://github.com/DietrichGebert/ponytail/blob/09c434ab73ca43761c5d8b0c5d341926c2fba710/LICENSE), prominently name the original author, and distinguish Olivier Morel’s adaptation from upstream.

Success means five usable skills, working conversation-specific mode hooks for Claude Code and Codex, a documented safety assessment of the shipped package, and passing validation. This assessment must state its coverage and limitations; it must not certify the entire upstream repository.

## 2. Decisions

The following choices are settled:

| Area | Decision |
|---|---|
| Contents | Coding, review, audit, debt, and help skills with a focused mode adapter. |
| Exclusions | Board, metrics, webhook, transcript imports, source mapper, status-line setup, benchmark scoreboard, and other assistant integrations. |
| Runtime | Node.js, using built-in modules without npm dependencies. |
| Platforms | macOS and Linux; Windows support is outside this release. |
| Activation | Full mode after installation and the host’s required hook review. |
| Persistence | Independent conversations; resume and compaction retain their mode. An explicit command changes future defaults. |
| Delivery | Local changes only, as one larger change with the agreed size exception. |

Implementation defaults: plugin name `ponytail`, custom package version `1.0.0`, and Node.js 24 or a newer supported release. Node 24 is the CI baseline. [Node release status](https://nodejs.org/en/about/previous-releases)

## 3. Models

- **Plugin package:** matching Claude/Codex names and versions, shared `./skills/`, separate hook manifests, MIT license, Dietrich Gebert as original author, and this marketplace as the adaptation’s repository. Marketplace source is `./plugins/ponytail`; its entry has no version.
- **Mode:** `off | lite | full | ultra`. Review, audit, debt, and help are one-shot operations, never modes.
- **Session state:** only the selected mode, stored under the host-provided plugin data directory using a SHA-256 filename derived from the session ID. Working-directory changes do not change conversation identity.
- **Default preference:** `defaultMode`, initially `full`, stored separately in the same private data area. It applies to new conversations in that host; existing conversations remain unchanged.
- **Safety record:** reviewed upstream revision and files, retained and excluded behavior, custom changes, test evidence, findings, and remaining limitations.

No upstream configuration or mode files are migrated. Retained session files enable resume; removing the plugin’s data resets stored preferences and modes.

## 4. Functions

**Skill adaptation**

Adapt the five entrypoints using skill-creator. Keep normal skill discovery, concise descriptions, and original-author attribution. Remove unsupported frontmatter and references to excluded features.

Preserve the user’s requested scope, established architecture, validation, security, accessibility, and meaningful tests. Ultra mode may suggest alternatives but must respect settled decisions. Review/audit report findings without editing; debt writes a report only when requested and treats custom markers as literal search input. A shortcut comment never excuses a security or correctness defect.

The latest hook mode governs the persona. An implicitly selected skill must not reactivate an off conversation. Without working hooks, explicitly requested skills provide task-local guidance without claiming persistent activation.

**Mode adapter**

- `parseCommand(prompt)`: recognize standalone `/ponytail`, `/ponytail:ponytail`, and their dollar-prefixed equivalents, optionally followed by a mode or `default <mode>`. Recognize standalone “stop ponytail” and “normal mode.” Mentions, quoted examples, report commands, and unknown arguments never change state.
- `loadState/saveState` and `loadDefault/saveDefault`: read and atomically write validated mode values. Use private directories/files, reject symlinks and nonregular state files, and keep writes within plugin data. Missing host data paths disable persistence without a fallback into user settings or the project.
- `handleSessionStart`: initialize startup, clear, and fork from the default; restore saved state on resume and compact, falling back to the default when no valid state exists.
- `handleUserPromptSubmit`: switch modes; a bare command reports an active mode or enables the default, using full if that default is off. `default <mode>` changes only future defaults. Ordinary prompts produce no output.
- `handleSubagentStart`: inject the parent conversation’s saved mode without changing it; absent state produces no injection.
- `renderContext(mode)`: read the packaged core skill and identify the active mode. Off emits a short instruction retiring earlier Ponytail guidance. Never include raw prompts, repository content, or transcript content in hook output.

Use one shared CommonJS adapter and state module. Both hook manifests register SessionStart, UserPromptSubmit, and SubagentStart with five-second timeouts. Limit stdin to 1 MiB and one second; malformed input or I/O failures return harmless output with a generic diagnostic, never blocking the user.

Claude uses direct executable arguments. Codex uses a fixed Node loader that reads the plugin root from its environment, avoiding path or prompt interpolation into shell source. Return one hook-specific JSON context object. Preserve normal host trust review. [Claude hook contract](https://code.claude.com/docs/en/hooks) · [Codex hook contract](https://learn.chatgpt.com/docs/hooks)

**Repository integration**

Review the shipped source and its dependencies before executing imported code; do not run upstream installers. Record the final safety assessment before declaring the package ready.

Register the package, update discovery documentation, and add its Node tests to the blocking validator. Configure Node 24 through `actions/setup-node@v7` with package caching disabled. Refresh the workflow’s dependency inventory hash and corresponding Renovate provenance marker, preserving update policies. [setup-node release](https://github.com/actions/setup-node/releases/tag/v7.1.0)

## 5. Diagram

```text
olivier-vault catalog
        |
        v
plugins/ponytail
  |-- shared skills -----------> coding guidance / read-only reports
  |
  |-- Claude hook manifest --+
  |-- Codex hook manifest ---+--> trusted host launches Node adapter
                                      |
                         validate event and exact command
                                      |
                     +----------------+----------------+
                     |                                 |
              private plugin data               packaged core skill
              default + session mode                   |
                     +----------------+----------------+
                                      |
                          mode context back to host
                          and inherited by subagents
```

## 6. File tree

```text
plugins/ponytail/
  .claude-plugin/plugin.json          # Claude package identity and paths
  .codex-plugin/plugin.json           # Matching Codex compatibility manifest
  hooks.json                         # Claude event registrations and launcher
  hooks.codex.json                   # Codex event registrations and launcher
  hooks/ponytail.cjs                  # Bounded input, command dispatch, context output
  hooks/state.cjs                     # Isolated defaults and atomic session state
  skills/ponytail/SKILL.md            # Core guidance, modes, and attribution
  skills/ponytail-review/SKILL.md     # Review a requested change
  skills/ponytail-audit/SKILL.md      # Audit a requested repository scope
  skills/ponytail-debt/SKILL.md       # Report deliberate shortcuts
  skills/ponytail-help/SKILL.md       # Custom edition’s supported commands
  tests/hooks.test.cjs                # Behavioral and filesystem regression tests
  tests/skill-scenarios.md            # Reproducible behavioral evaluation prompts
  README.md                          # Installation, operation, differences, credits
  CHANGELOG.md                       # Independent 1.0.0 release history
  LICENSE                            # Unmodified upstream MIT notice
docs/plugins/ponytail/security-review.md # Scoped safety evidence and limitations
.claude-plugin/marketplace.json       # Register package and update description
README.md                            # Plugin listing, runtime support, attribution
CLAUDE.md                            # Node prerequisite and validation guidance
CONTRIBUTING.md                       # Contributor Node prerequisite
scripts/validate.sh                  # Run Ponytail tests as a blocking check
.github/workflows/validate.yml        # Establish Node 24 for validation
inventory.md                         # Workflow hash and setup-node dependency
renovate.json5                       # Refresh inventory provenance marker
adr/0006-ponytail-mode-hooks.md        # Record focused adapter and state isolation
adr/README.md                        # Index the new decision
docs/plans/add-ponytail-plugin.md     # Save this plan after approval
```

## 7. Tests

- **Lifecycle:** fresh conversations start full; all four modes work; resume/compact preserve off and other selections; clear/fork use defaults; default changes leave active conversations untouched.
- **Isolation:** simultaneous conversations in the same project and different hosts cannot change each other’s modes; subagents inherit only their parent’s mode.
- **Command safety:** exercise both runtime namespaces, bare activation, default changes, and deactivation. Embedded commands, code fences, shell metacharacters, report invocations, and invalid values do not mutate state.
- **Filesystem safety:** test hostile session IDs, symlinks, corrupt/oversized state, unwritable directories, and concurrent writes. Writes remain confined and complete; failures do not block sessions.
- **Process contract:** run the actual manifest launchers from paths containing spaces and shell metacharacters. Empty, malformed, oversized, or stalled input exits promptly; output never leaks supplied secrets or prompts.
- **Skill behavior:** use skill-creator’s independent forward-test in temporary fixtures. Check that requested functionality survives simplification, off remains off, read-only reports make no edits, and marked shortcuts do not hide genuine defects.
- **Packaging:** validate every skill with skill-creator’s `quick_validate.py`, both manifests and referenced paths, source attribution, and the retained license.
- **Repository:** run Node’s test runner through `./scripts/validate.sh`, plus workflow linting. Make `ajv`, `ajv-formats`, and `shellcheck` available so the current skipped checks actually run. Existing tests must remain green.

Provide a native installation/trust smoke checklist for both assistants without modifying the user’s active installations. Record which native checks were actually run; local delivery must not claim unperformed integration tests or a remote CI result.

## 8. Size check

Estimate **1,100–1,500 changed lines**, including skills, hooks, tests, documentation, and the saved plan. The user explicitly chose one larger change despite the repository’s 1,000-line soft cap. Keep this exception documented and exclude unrelated cleanup.

## 9. ADR check

This introduces a meaningful choice: maintaining a focused adapter with conversation-isolated state instead of importing upstream’s broader runtime.

Record it through the ADR skill in `adr/0006-ponytail-mode-hooks.md`, following the existing repository template and index. Include the Node dependency, reduced feature set, and independent maintenance obligation. Do not draft the ADR during planning.

## 10. Documentation check

Document local installation, Node/platform prerequisites, hook trust, command examples for each assistant, mode/default persistence, data locations, reset behavior, and coexistence with Grumpy.

Name **Dietrich Gebert (DietrichGebert)** as the original author in the plugin README and skill attribution; link upstream and the pinned revision. Identify Olivier Morel as the custom edition’s maintainer. Explain independent versioning and require fresh review of future upstream imports.

Keep individual documentation files below approximately 150 lines. The final implementation handoff must identify actual checks, unresolved limitations, and that publication remains pending because delivery is local only.

Per [Grumpy’s plan skill](/Users/omorel/.codex/plugins/cache/olivier-vault/grumpy-senior-engineer-workflow/1.4.1/skills/plan/SKILL.md): “Present the complete plan and await explicit user approval before saving or implementing it.”
