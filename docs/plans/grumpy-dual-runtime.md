# Grumpy 1.4.0: shared Claude and Codex support

Adapt Grumpy within its existing marketplace entry: shared skills, separate runtime hooks, and a local structural plan check for Codex.

## 1. Non-negotiables

- Scope: **Grumpy only**, plus the marketplace validation and documentation needed to support it.
- Preserve Claude commands, prompt hooks, workflow rules, and stored context/ADR/plan formats.
- Preserve explicit user approval before implementation or ADR writes. Passing a hook never constitutes approval.
- Use local scripts without model calls, credentials, network access, or persistent hook state.
- Respect Codex hook review; installation cannot automatically trust hooks. [Hook documentation](https://learn.chatgpt.com/docs/hooks)

## 2. Decisions

- Keep one marketplace entry and plugin directory. Add a `.codex-plugin/plugin.json` pointing to shared skills and a separate Codex hook configuration. This compatibility layout supports explicit hook paths. [Plugin packaging documentation](https://developers.openai.com/plugins/build/plugins)
- Release **1.4.0**, with matching names and versions in both runtime manifests.
- Codex gets two SessionStart readers, a UserPromptSubmit planning reminder, and a Stop structural check. Claude retains its existing configuration.
- Use Python 3’s standard library for Codex hook parsing and tests; retain Bash for shared startup readers.
- Keep Claude slash commands. Document Codex skill selection and natural-language invocation instead of relying on Claude command loading.

## 3. Models

- No changes to persisted data.
- The Codex dispatcher reads event JSON from stdin and writes event-appropriate JSON to stdout.
- The Stop check reads `last_assistant_message` and `stop_hook_active`. It neither reads transcripts nor searches for plan files.
- Completed Codex plans use one `<proposed_plan>` envelope containing the ten canonical sections. Clarification replies remain ordinary messages.

## 4. Functions

**Codex hooks**

- UserPromptSubmit adds a brief conditional reminder: for planning work, establish context and scope, use the planning skill, include ten sections, and await approval.
- Stop checks only messages consisting entirely of one complete plan envelope.
- Require each canonical section exactly once, in order, with content. Accept case differences, optional numbering, and bold heading text.
- Ignore headings inside fenced code; nonempty diagrams and file trees count as section content.
- Reject empty sections and standalone placeholders such as `TODO`, `TBD`, or unexplained `None`; accept an explained absence.
- Return a correction request naming structural failures. If `stop_hook_active` is true, return immediately to prevent repeated continuations.
- Missing messages, unrelated replies, and malformed input fail open; malformed input produces a short diagnostic without echoing its contents.

**Shared startup readers**

- Resolve the project from `CLAUDE_PROJECT_DIR`, otherwise the Git root of the working directory, otherwise the working directory.
- Keep missing or unreadable indexes nonblocking.
- Count plain and linked four-digit ADR identifiers without changing the index format.

**Shared skills**

- Replace runtime-specific tool requirements with the available question/approval mechanism, retaining Claude-specific guidance where appropriate.
- Support applicable `AGENTS.md` and `CLAUDE.md` instructions while preserving target-subtree scope and excluding siblings.
- Recognize actual conversational approval independently of plan formatting.
- Preserve saving exceptions, ADR approval boundaries, and targeted testing rules.
- When a referenced companion skill is unavailable, disclose that limitation and follow applicable repository guidance without claiming the companion was consulted.

## 5. Diagram

```text
Existing marketplace entry
          |
    Shared Grumpy package
          |
    +-----+---------------------+
    |                           |
Claude manifest             Codex manifest
    |                           |
Existing commands/hooks     Startup readers
    |                       Planning reminder
    |                       Structural Stop check
    +-------------+-------------+
                  |
          Four shared skills
                  |
         User reviews the plan
```

## 6. File tree

```text
plugins/grumpy-senior-engineer-workflow/
  .codex-plugin/plugin.json       new
  hooks.codex.json               new
  hooks/codex-plan.py             new
  tests/test_codex_hooks.py       new
  existing manifests, readers, skills, commands and README updated

schemas/codex-plugin.schema.json  new
scripts/validate.sh               runtime-aware validation
docs/plugins/grumpy-senior-engineer-workflow/
  codex.md                       new compatibility/setup guide
  existing topic guides          updated
adr/                             dual-runtime decision and index update
```

Also update the marketplace description, changelog, and concise repository documentation pointers.

## 7. Tests

- Exercise real hook subprocesses with valid plans, missing/duplicate/reordered sections, empty bodies, placeholders, explained absences, fenced headings, diagrams, and file trees.
- Verify clarification replies, quoted examples, missing messages, malformed JSON, and continuation-loop prevention.
- Exercise startup readers with missing, empty, header-only, populated, linked-ID, and unreadable indexes; include nested working directories and paths containing spaces.
- Validate runtime-specific manifests, matching identity/version, referenced paths, and command-only Codex hooks. Preserve Claude hook configuration.
- Run `./scripts/validate.sh` with schema validation and shellcheck available; integrate the new tests into that command and replace its macOS-incompatible path formatting.
- Perform a native Codex smoke test using an isolated local marketplace installation: verify four skills, correct hook discovery, startup context, ordinary replies, and one invalid-plan correction. Report automated checks and native runtime results separately.
- Recheck ADR draft/approval scenarios and context deduplication against both instruction-file conventions.

## 8. Size check

Target approximately **700–1,000 changed lines**, including tests and documentation. Reuse existing readers and skills; avoid a generic hook framework. Keep user-facing guides below 150 lines.

## 9. ADR check

Record the shared-package/separate-hooks decision using this repository’s existing `adr/` convention. Explain why Codex uses structural checks and why they do not establish semantic completeness or user approval.

## 10. Documentation check

Document installation, Python/Bash requirements, hook review, restart/update steps, invocation differences, and runtime capabilities.

State the Codex limitations explicitly: structural validation cannot judge plan quality; Stop requests a continuation and may run after output is visible; unwrapped or file-only plans are outside the check. [Stop hook behavior](https://learn.chatgpt.com/docs/hooks)

Update claims that every runtime prevents incomplete plans from reaching the user. Keep update-manager and the general plugin template outside this release.

## Approved implementation amendment — native Plan Mode preflight

Native testing on Codex 0.162.0 showed structured Plan Mode output reaches Stop
with `last_assistant_message: null`. The user approved adding a local preflight
command on 2026-10-09: reuse the same parser through `codex-plan.py --check-plan`,
reading the exact complete plan envelope from stdin before presenting it.
Reject malformed envelopes and structural defects with a nonzero exit; require
the Codex planning skill to correct failures and rerun after edits. No plan file
is written before approval. Keep Stop as a backstop for available final text.
Document that preflight is agent-invoked, not automatic runtime enforcement,
and test the CLI contract plus an independent planning-skill exercise.
