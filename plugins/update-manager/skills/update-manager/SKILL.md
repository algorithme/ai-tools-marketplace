---
description: Tier-by-tier dependency updater for Rust, Python, Node, Docker, and GitHub Actions — discover, apply, gate, PR.
---

# update-manager

Orchestrates dependency updates across one or more ecosystems in a host project. Discovers
manifests, computes candidate bumps for a chosen tier, applies them, runs the project's own
quality gate, and opens a reviewable PR. Project-specific values (paths, commands, exclusions)
live in the host project's `inventory.md`, generated and refreshed by this skill.

## Invocation

```
/update-manager                          # all ecosystems, all tiers in sequence
/update-manager refresh                  # re-scan host project → regenerate inventory.md
/update-manager <ecosystem>              # rust | python | node | dockerfile | docker-compose | github-actions | all
/update-manager <ecosystem> <tier>       # tier = security | patch | minor | major | all
/update-manager --dry-run                # show plan, no edits
/update-manager --no-pr                  # commit on branch, skip gh pr create
```

Argument parsing:
- First positional arg: `refresh` OR an ecosystem (`rust`, `python`, `node`, `dockerfile`, `docker-compose`, `github-actions`, `all`).
- Second positional arg: a tier (`security`, `patch`, `minor`, `major`, `all`).
- Flags: `--dry-run`, `--no-pr`.
- Missing tier → all tiers. Missing ecosystem → all ecosystems.

## Playbook loading

For each ecosystem in scope, read the matching playbook:

```
${CLAUDE_PLUGIN_ROOT}/skills/update-manager/playbooks/<ecosystem>.md
```

If `CLAUDE_PLUGIN_ROOT` is not set in the runtime environment, resolve playbook paths relative
to this `SKILL.md` file (i.e. `./playbooks/<ecosystem>.md`). Do not silently skip playbook
loading — playbooks are required for tier mappings.

Playbooks define discovery rules, tier-to-command mappings, and ecosystem-specific notes. They
are advisory — actual commands run come from the host project's `inventory.md`.

## Inventory

Read and write `inventory.md` in the **host project root** (the `cwd` when the skill runs), not
in the plugin. The reference schema is in `inventory.template.md` next to this file.

## Workflow

### Phase 1 — Preflight

- Run `git status --porcelain`. Must return empty, or ask the user before stashing.
- Read `inventory.md`. If it does not exist, abort and tell the user to run
  `/update-manager refresh`.
- Read `update-manager.constraints.yml` if present in the host project root. If absent, treat
  as an empty constraints list (do not create the file at Preflight — only create it when the
  user first chooses to record a constraint).
- For each manifest listed in any in-scope subproject, compute its current SHA-256 and compare
  against the `manifest_hashes[<file>]` entry recorded in `inventory.md`. On any mismatch,
  abort with a refresh hint. (See `inventory.template.md` for the `manifest_hashes` field.)
- For each `prerequisites` command listed for the in-scope subprojects, verify it is reachable
  (run a healthcheck or the command itself). If a prerequisite is down, offer to run it and
  block until it succeeds.
- Determine branch name: `deps/<ecosystem>-<tier>-<YYYY-MM-DD>`. For multi-ecosystem runs use
  `deps/multi-<YYYY-MM-DD>`. If the branch already exists, append `-2`, `-3`, … until unused.
  Skip branch creation for `refresh` or `--dry-run` invocations; otherwise create and check it
  out.

For `refresh`: walk the working tree, run each playbook's discovery, then
write/merge `inventory.md`. Merge semantics: new subprojects appended; existing entries' paths
and commands updated; `excluded`, `manual-only`, `notes`, `format`, and `prerequisites` fields
preserved verbatim. Recompute and write `manifest_hashes` for every subproject on every refresh.

### Phase 2 — Plan

For each in-scope `(ecosystem, tier)`:
1. Use the playbook's discovery + listing command to compute candidate bumps.
2. Filter against the subproject's `excluded` list (silent skip; collected for end-of-run report).
3. Filter against `update-manager.constraints.yml`: if a candidate's target version exceeds
   a matching constraint's `max_version`, mark it `[blocked by constraint: <reason>]` and skip
   it — **except** for security-tier bumps that fix a CVE, which always bypass constraints and
   prompt the user directly.
4. For each candidate matching `manual-only`, fire `AskUserQuestion` with the package name and
   reason; only include if the user confirms.
5. For Docker/Compose minor-tier candidates (not blocked by constraint, not manual-only), fire
   `AskUserQuestion` per image: show `<image>:<old-tag>` → `<image>:<new-tag>` and ask the user
   to confirm. On decline, ask: "Record `<image>` max version as `<old-tag>` in
   `update-manager.constraints.yml`?" — if yes, append the entry and save the file immediately.
6. Print a table: `package | old | new | tier | status` where status is one of: `pending`,
   `blocked by constraint`, `manual-only (pending confirmation)`, `skipped (excluded)`.
   For uv-managed subprojects, annotate the tier column as `minor (uv: patch≡minor)` when
   `patch` was requested.
7. If `--dry-run`, stop here.

### Phase 3 — Apply

For each `(subproject, tier)` in scope:
1. `cd` into `inventory.working_directory`.
2. Check whether the playbook prescribes a per-advisory loop for this `(ecosystem, tier)`
   combination (currently: bun security; pnpm security when the resolved version is < 9;
   dockerfile security per FROM line; docker-compose security per service; github-actions security
   per advisory). When
   it does, run the scan command, parse its output, and apply a targeted package-level update
   per advisory instead of running `inventory.update_commands[tier]`.
3. Otherwise, run `inventory.update_commands[tier]`.
4. **Do not commit yet.** Files modified at this point: manifests + lockfile.

### Phase 4 — Fix

Run the playbook's typecheck/build command from `working_directory`. On error:
1. Before making any source edit, call `AskUserQuestion`: show the typecheck output and describe
   the proposed change (file, line, kind — e.g. rename / type annotation / deprecated-method
   swap). Proceed only if the user confirms. If declined, stop here, leave the working tree
   as-is, and do not commit or push.
2. Apply the minimal source fix for renamed APIs / removed items / deprecated usages.
3. Re-run typecheck.
4. Repeat steps 2–3 at most 3 times. After the third failure, stop, leave the working tree
   as-is, and report the last error output verbatim. Do not commit or push.

### Phase 5 — Format

If `inventory.format[]` is defined and non-empty, run each command in order from
`working_directory`. Format failures (non-zero exit) abort immediately — report stderr and stop
without committing. If `format` is absent or empty, skip this phase.

### Phase 6 — Gate

Run each command in `inventory.gate[]` in order, from `working_directory`. Any non-zero exit:
- Do not commit or push.
- Report the failing command and its captured stdout/stderr.
- Leave the working tree in place for the user to inspect.

### Phase 7 — Commit + PR

After Gate passes, commit atomically:
1. Stage manifests + lockfile + any source files modified during Fix + any files modified
   during Format.
2. Commit: `deps(<ecosystem>): <tier> bumps — <N> packages`.
3. If `--no-pr`, stop here.
4. Otherwise `git push -u origin <branch>`.
5. `gh pr create` with title `deps(<ecosystem>): <tier> updates` (or
   `deps(multi): updates across <N> ecosystems` if multiple ecosystems produced commits).
   Body includes the bumps table, Gate summary, skipped/excluded items, and any `notes`.
6. If the diff exceeds **1500 LOC**: do not open the PR automatically. Use `AskUserQuestion`
   to ask the user whether to proceed with one large PR or stop for manual splitting.

## Multi-ecosystem ordering

For `all` (or multiple explicit ecosystems), run **sequentially** in this order:
`rust → python → node → dockerfile → docker-compose → github-actions`. Within each ecosystem,
run the requested tiers in order `security → patch → minor → major`. Each `(ecosystem, tier)`
cycle completes its full Apply → Fix → Format → Gate → Commit pipeline before the next one
starts. All commits land on the same branch; the PR is opened once, after all ecosystems are done.

Ordering rationale: language-layer deps (rust/python/node) are updated first because container
base images (dockerfile/docker-compose) often inherit or re-install them; CI workflows
(github-actions) are updated last as they orchestrate everything. This ordering minimises rework
if a language-layer bump invalidates a base image or CI step.

PR title: `deps(<ecosystem>): <tier> updates` when a single ecosystem produced all commits;
`deps(multi): updates across <N> ecosystems` when more than one did.

## Edge cases & policies

| #  | Case                               | Policy                                                                                      |
|----|------------------------------------|---------------------------------------------------------------------------------------------|
| 1  | `excluded` list hit                | Silent skip; list at end of plan output and in PR body.                                     |
| 2  | `manual-only` list hit             | `AskUserQuestion` per package before including in the bump set.                             |
| 3  | Inventory missing or stale         | Refuse to run; print hint to `/update-manager refresh`.                                     |
| 4  | Branch name collision              | Append `-2`, `-3`, … until unused.                                                          |
| 5  | Prerequisite unreachable           | Offer to run prerequisite commands; wait for healthcheck to succeed.                        |
| 6  | Fix phase declined by user         | Stop before first source edit; leave working tree as-is; do not commit.                     |
| 6a | Fix phase exhausted (3×)           | Stop; leave working tree in place; report last error; do not commit.                        |
| 7  | Format failure                     | Stop; report stderr; do not commit or push.                                                 |
| 8  | Gate failure                       | Do not commit or push; report failing command + output.                                     |
| 9  | PR diff > 1500 LOC                 | `AskUserQuestion` — proceed with large PR or stop for manual splitting.                     |
| 10 | `notes` on bumped package          | Print at plan time; include in PR body under a "Notes" section.                             |
| 11 | Constraint hit (non-CVE)           | Silent skip; show `[blocked by constraint: <reason>]` in plan table.                        |
| 12 | Constraint hit on security/CVE     | Bypass constraint; `AskUserQuestion` — surface CVE details and ask user to confirm.         |
| 13 | User declines Docker/Compose bump  | `AskUserQuestion` — offer to record as permanent constraint in `update-manager.constraints.yml`. |

## Re-refresh preservation

The `refresh` command never overwrites the user's curated fields. Implementation: parse the
existing `inventory.md` first; for each subproject keyed by `id`, retain `excluded`,
`manual-only`, `notes`, `format`, and `prerequisites` arrays into the regenerated document.

## Version constraints

User decisions to cap automatic upgrades are stored in `update-manager.constraints.yml` at the
host project root. The reference schema and examples live in `constraints.template.yml` next to
this file.

### Writing a constraint

A constraint is added in two ways:
1. **Interactively** — when the user declines a Docker/Compose minor bump during Phase 2, the
   skill asks: "Record `<image>` max version as `<current-tag>` permanently?" On confirmation,
   the entry is appended to `update-manager.constraints.yml` (created if absent, using the
   template header) and committed as part of Phase 7 alongside the other changes.
2. **By hand** — edit `update-manager.constraints.yml` directly and run
   `/update-manager refresh` to recompute `manifest_hashes`.

### Constraint schema

```yaml
constraints:
  - ecosystem: docker-compose          # rust | python | node | dockerfile | docker-compose | github-actions | all
    package: postgres                  # image or package name; globs supported
    max_version: "17"                  # never auto-update beyond this version
    reason: "WAL format change — DBA review required"
    blocked_since: "2026-04-28"        # ISO date; set automatically when recorded interactively
```

### Security-tier exception

A constraint never suppresses a security finding. When a CVE fix requires bumping past
`max_version`, the skill bypasses the constraint, presents the CVE details and the proposed bump,
and fires `AskUserQuestion`. The user decides; the constraint is not modified automatically.

## Required tooling

- `git`, `gh` (for PRs).
- Per ecosystem: see the matching playbook's tooling-bootstrap section.
