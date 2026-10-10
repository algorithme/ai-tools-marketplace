# Codex setup and compatibility

[Plugin overview](../../../plugins/grumpy-senior-engineer-workflow/README.md)

Grumpy 1.4.0 is one package with shared skills and separate runtime hooks.
Its `.codex-plugin/plugin.json` selects `hooks.codex.json`; Claude retains
its own manifest, commands, and prompt hooks. Other marketplace plugins
have not been adapted by this release.

## Install and update

Use a Codex version with plugins and hooks (CLI commands checked with 0.162.0).
The hooks require `bash` and `python3` on `PATH`. Git enables root discovery
when a session starts in a repository subdirectory.

```bash
codex plugin marketplace add omorel/ai-tools-marketplace
codex plugin add grumpy-senior-engineer-workflow@olivier-vault
```

For a local checkout, run `codex plugin marketplace add ./` from this
repository instead of adding the Git source. To update a Git marketplace:

```bash
codex plugin marketplace upgrade olivier-vault
codex plugin add grumpy-senior-engineer-workflow@olivier-vault
```

Open `/hooks`, inspect Grumpy's commands, and trust the configuration after
reviewing it. Installation does not grant hook trust. A changed configuration
requires review again. Restart the session after installation or update so
startup hooks run with the new package. See the official
[hook review documentation](https://learn.chatgpt.com/docs/hooks).

If `/hooks` still shows unsupported `prompt` hooks, check the installed
version and refresh it: those belong to the earlier Claude-only configuration.
Do not edit the installed cache; make durable changes in the source package.

## Use the shared skills

Select Grumpy's `context`, `adr`, `plan`, or `implement` skill, or ask naturally:

- “Update the project context: billing now uses Postgres.”
- “Record our decision to reuse the payments Redis cluster.”
- “Plan idempotent publishing for the billing service.”
- “Implement the plan I just approved.”

The `/grumpy-*` command files are Claude entry points. Codex uses the skills.
Both runtimes retain the same stored files, approval requirements, and plan
saving exception. Context deduplication includes applicable `AGENTS.md` and
`CLAUDE.md` instructions, excluding sibling subprojects.

## What each runtime checks

| Behavior | Claude Code | Codex |
|---|---|---|
| Startup context and ADR pointer | Bash readers | Same readers, after hook review |
| Context and scope before planning | Prompt gate on `EnterPlanMode` | Skill instructions and prompt reminder |
| Plan completeness | Prompt gate on `ExitPlanMode` | Agent-run structural preflight; `Stop` backstop when final text is available |
| Plan quality and approval | User review | User review |

The Codex planning skill runs `hooks/codex-plan.py --check-plan` before
presenting the completed plan, including in native Plan Mode. It supplies
the complete envelope on stdin without saving a file; exit 0 means the
structure passes, and exit 1 means the agent must correct it and check again.
This is an agent-run preflight, so it depends on the agent following the skill.

**Codex 0.162.0 limitation:** native Plan Mode emits a structured plan item
and supplies no final-message text to `Stop`. The automatic hook cannot check
that path; the preflight uses the same parser before presentation. Native
smoke tests verified the hook's missing-text behavior and normal-text path.

The shared parser checks one complete
`<proposed_plan>` envelope. It requires ten sections once, in order, with
content; explained absences and nonempty code fences are accepted.
When final-message text is available, `Stop` requests one correction and
skips further checks on the resulting continuation to prevent a loop.
Malformed hook input fails open with a diagnostic.

It cannot judge whether reasoning is sound or content is useful. Unwrapped
messages and file-only plans are outside the `Stop` check. A `Stop` correction is
a continuation, so the original output may already be visible; it is not
equivalent to Claude's pre-tool gate. Passing never authorizes implementation
or ADR writes. See official [Stop behavior](https://learn.chatgpt.com/docs/hooks).

## Package maintenance

Keep both manifests' names and versions aligned. Skills are shared;
runtime-specific behavior belongs in each hook configuration. Paths in the
Codex manifest are relative to the plugin root, using the supported
[compatibility manifest layout](https://developers.openai.com/plugins/build/plugins).
Run `./scripts/validate.sh` from the repository root to validate manifests,
paths, shell scripts, and hook regression tests. Native runtime smoke tests
remain separate from those automated checks.
