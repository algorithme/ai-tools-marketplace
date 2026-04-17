# 0003 — Validation authority — `scripts/validate.sh` + best-effort CI

**Status**: Accepted

## Context

Two tools can validate Claude Code plugins:

1. **`claude plugin validate`** — the official CLI command. Checks `plugin.json` shape, skill/agent/command frontmatter, and `hooks/hooks.json`. Authoritative but requires the Claude Code CLI.
2. **`jq` / `ajv` / `yq` / `shellcheck`** — standard Unix tools. Cover JSON syntax, JSON Schema, YAML frontmatter, and shell script safety. Available everywhere.

The problem: `claude plugin validate` is not reliably installable in GitHub Actions. The npm package name (`@anthropic-ai/claude-code`) may not be stable, and installing it in every CI run adds latency and an external dependency.

## Decision

**`scripts/validate.sh` is the single source of truth for validation.**

The script runs:
1. `jq` — JSON syntax check on all `*.json` files.
2. `ajv` — JSON Schema validation against `schemas/marketplace.schema.json` and `schemas/plugin.schema.json`.
3. `yq` — YAML frontmatter validation on `SKILL.md`, agent, and command files.
4. `shellcheck` — shell safety lint on `scripts/**/*.sh` and plugin `bin/` executables.
5. Kebab-case filename lint for plugin directories.
6. `claude plugin validate .` — **best-effort, non-blocking**.

CI (`.github/workflows/validate.yml`) calls `scripts/validate.sh`. The `claude plugin validate` step uses `continue-on-error: true`.

**Devs run `./scripts/validate.sh` locally before opening a PR.** The PR template checklist includes this step.

## Consequences

### Positive
- CI is reliable and fast — no dependency on external CLI availability.
- Local and CI environments are identical (same script).
- `claude plugin validate` still runs in CI when the CLI is available; it just does not gate the merge.
- When the Claude Code CLI becomes reliably installable as a GitHub Action, we can promote it to blocking by removing `continue-on-error: true`.

### Negative / trade-offs
- Schema in `schemas/plugin.schema.json` may drift from the canonical Claude Code spec if the spec evolves. Maintainer must update the schema manually.
- `ajv`-based schema validation may accept files that `claude plugin validate` rejects, or vice versa.

### Neutral
- `shellcheck` and `yq` must be installed on contributor machines. Installation is documented in `CONTRIBUTING.md` and `docs/troubleshooting.md`.
