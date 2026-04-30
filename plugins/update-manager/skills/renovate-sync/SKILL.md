---
description: Generate and keep a Renovate config (renovate.json5 + GH Actions workflow) in sync with update-manager's inventory.md and constraints.yml.
---

# renovate-sync

Generates a `renovate.json5` + `.github/workflows/renovate.yml` from the host project's
`inventory.md` and `update-manager.constraints.yml`. Keeps them in sync when those sources change.

**Division of labor:**

| Renovate (CI, daily) | `/update-manager` (interactive) |
|---|---|
| Security / patch / minor PRs | Major bumps, multi-ecosystem orchestration |
| Automerge on safe tiers | Conflict resolution, ad-hoc / offline runs |
| Shared source: `update-manager.constraints.yml` | Shared source: `update-manager.constraints.yml` |

## Invocation

```
/renovate-sync            # diff current sources against renovate.json5, ask to apply
/renovate-sync init       # first-time setup (idempotent)
/renovate-sync --apply    # apply without interactive prompt
/renovate-sync --dry-run  # show generated output without writing
```

`init` and the bare invocation follow the same generation logic — the only difference is that
`init` always writes the files while the bare form diffs and prompts.

## Preflight

1. Verify `inventory.md` exists in the host project root. If absent, stop and instruct the user
   to run `/update-manager refresh` first.
2. Verify `yq` is on PATH (required for constraint YAML parsing). `gh` and `diff` are optional but
   recommended; surface a note if absent.
3. Read `update-manager.constraints.yml` if present. If absent, treat as an empty constraints
   list — do not create the file.

## Sources

Two files drive generation — both live at the host project root:

- **`inventory.md`** — provides ecosystem list, `manifests[]`, `manual-only[]`, `excluded[]`,
  `notes[]`, and per-ecosystem pinning convention note (from the github-actions playbook).
- **`update-manager.constraints.yml`** — provides `constraints[]` entries, each with `ecosystem`,
  `package`, `max_version`, and `reason`.

See `mappings.md` (next to this file) for the complete field-by-field translation table.

## Drift detection

Every generated `renovate.json5` embeds a managed-by marker on its first non-comment line:

```
// managed-by: update-manager#<sha>
```

where `<sha>` is the SHA-256 of the concatenation of the raw content of `inventory.md` and
`update-manager.constraints.yml` (empty string if the constraints file is absent). On each
invocation, recompute the expected sha and compare it with the stored one. If they differ (or if
no marker is found), the config is stale.

Compute sha:
```bash
INV=$(cat inventory.md)
CONS=$(cat update-manager.constraints.yml 2>/dev/null || echo '')
_sha256() { command -v sha256sum &>/dev/null && sha256sum | awk '{print $1}' || shasum -a 256 | awk '{print $1}'; }
EXPECTED_SHA=$(printf '%s%s' "$INV" "$CONS" | _sha256)
```

## Generation rules

Build the `renovate.json5` content according to `mappings.md`. Key decisions:

- `enabledManagers` — one entry per ecosystem found in `inventory.md`. See mappings table.
- `branchPrefix: 'deps/'` — mirrors the manual-flow branch convention.
- `vulnerabilityAlerts` — always enabled; labels as `['security']`.
- `automerge` on patch/digest/pin/lockFileMaintenance `matchUpdateTypes`.
- `automerge: true` for `minor` updates **per ecosystem**, opt-in only — see
  "Per-ecosystem minor automerge" below.
- Major bumps → `dependencyDashboardApproval: true` + label `needs-update-manager`.
- **`gitAuthor`**: read `git config user.name` and `git config user.email`. Format as
  `'Name <email>'` and substitute into the `<<GIT_AUTHOR>>` marker in the template.
  If either value is empty, prompt via `AskUserQuestion` with three options:
  "Set it in git config and retry", "Enter name/email manually", or
  "Skip (Renovate will use its Mend default — commits will show Unverified on GitHub.com)".
  If the target `renovate.json5` already contains a `gitAuthor` line without the
  `<<GIT_AUTHOR>>` marker, leave it unchanged (the user has a manual override).
- Per `constraints.yml` entry → a `packageRule` with `allowedVersions: '<X.Y.Z'`.
  Docker variant-suffix handling: `16-alpine` → extract numeric prefix → `allowedVersions: '<17'`.
- Per `inventory.manual-only[]` pattern → `dependencyDashboardApproval: true`.
- Per `inventory.excluded[]` pattern → `enabled: false`.
- GitHub Actions pinning preset: include `helpers:pinGitHubActionDigests` in `extends` only if
  the github-actions inventory entry notes contains "SHA-pinned". If tag-pinned or absent, omit.

Use `renovate.template.json5` (next to this file) as the structural skeleton.

## User-managed region

If `renovate.json5` already exists, look for a user-managed block:

```json5
// region: user-managed
...
// endregion: user-managed
```

Preserve the content of this block verbatim inside the generated `packageRules` array. When
re-generating, place the user-managed region at the end of `packageRules`, after all generated
rules. If no such block exists in a pre-existing file, append an empty block to the generated
output so the user knows where to add custom rules.

## Per-ecosystem minor automerge

For each unique ecosystem appearing in `inventory.md`:

1. If every subproject of that ecosystem already has `automerge_minor` set (true or false),
   skip — the choice is already persisted.
2. Otherwise call `AskUserQuestion`:
   *"Automerge minor updates for `<ecosystem>`? (default no)"*
   with **Yes** and **No** options.
3. Write the answer as `automerge_minor: true|false` on every unset subproject of that
   ecosystem in `inventory.md` (preserve all other fields).
4. When generating `renovate.json5`, for each ecosystem where at least one subproject has
   `automerge_minor: true`:
   - **All subprojects opted in** → emit a rule scoped by `matchManagers`:
     ```json5
     {
       description: 'User opt-in (inventory.automerge_minor): automerge minor for <eco>',
       matchManagers: ['<manager>'],
       matchUpdateTypes: ['minor'],
       automerge: true,
     }
     ```
   - **Only some subprojects opted in** → emit a rule scoped by `matchFileNames`
     (see `mappings.md` "Monorepo subproject scoping"):
     ```json5
     {
       description: 'User opt-in (inventory.automerge_minor): automerge minor for <eco> at <path>',
       matchFileNames: ['<manifest-path-1>', '<manifest-path-2>'],
       matchUpdateTypes: ['minor'],
       automerge: true,
     }
     ```
   Place these rules **after** the default `minor → automerge: false` rule in
   `packageRules` so they override it (Renovate evaluates rules in order; later wins).

## Apply phase

1. Build the full generated content for `renovate.json5` and `.github/workflows/renovate.yml`.
2. If `--dry-run`: print both files to stdout and stop.
3. If files exist, compute diff against current on-disk content.
   - No diff: report "already in sync" and exit.
4. Show the unified diff. Unless `--apply`, call `AskUserQuestion`:
   - **Apply** — write files.
   - **Dry-run** — print generated content and stop.
   - **Cancel** — exit without writing.
5. Write `renovate.json5` and `.github/workflows/renovate.yml` (create
   `.github/workflows/` if absent).
6. Stage and commit on a new branch `deps/renovate-sync-<YYYY-MM-DD>`:
   ```
   git add renovate.json5 .github/workflows/renovate.yml
   git commit -m "deps(renovate): sync config with inventory and constraints"
   ```
7. Remind the user to add the `RENOVATE_TOKEN` secret if this is the first-time setup.

## GitHub Actions workflow

The generated `.github/workflows/renovate.yml` runs the self-hosted Renovate action:

- Schedule: daily at 06:00 UTC + `workflow_dispatch` for on-demand runs.
- The workflow uses `renovatebot/github-action` floated at its major version tag so Renovate
  can keep the pin current. Use `workflow.template.yml` (next to this file) as the canonical source.
- The skill reminds the user to add `RENOVATE_TOKEN` at first-time setup. Required scopes:
  - **Classic PAT**: `repo`, `workflow`
  - **Fine-grained PAT**: Contents R/W · Pull requests R/W · Issues R/W · Workflows R/W ·
    Commit statuses **Read** (missing this scope silently prevents automerge from evaluating CI status)
  - **GitHub App**: equivalent permissions above (preferred — avoids PAT rotation)
- Note: when `helpers:pinGitHubActionDigests` is enabled, Renovate rewrites `uses: actions/checkout@v4`
  to a SHA pin on its first run and re-bumps the SHA on subsequent runs. This is expected and
  keeps Node-runtime drift bounded.

If the repository remote is not on GitHub (detected via `git remote get-url origin`), skip
workflow generation and emit a note: "Non-GitHub remote detected — skipping workflow. Add
Renovate support manually or via a self-hosted runner."

## Edge cases

| Case | Policy |
|---|---|
| `inventory.md` absent | Abort; instruct user to run `/update-manager refresh`. |
| `renovate.json5` absent (first run) | Generate from scratch; no diff step; prompt before writing. |
| Repo not on GitHub | Skip `renovate.yml` generation; emit a note. |
| `--apply` with no diff | No-op; exit 0. |
| `constraints.yml` absent | Treat as empty list; generate without packageRules for constraints. |
| User-managed region exists | Preserve verbatim; place at end of `packageRules`. |
| `yq` absent | Abort with install hint (`brew install yq` / `pip install yq`). |
| `git config user.email` empty | Prompt for `gitAuthor` value or emit a warning and write `'Renovate Bot <CHANGEME@example.com>'` as fallback. |
| `renovate.json5` has a manual `gitAuthor` (no `<<GIT_AUTHOR>>` marker) | Leave as-is; skip auto-detection for this field. |
| `automerge_minor` unset on a subproject | Prompt once per ecosystem at sync time; persist answer back into `inventory.md`. |

## Required tooling

- `yq` — parse `update-manager.constraints.yml` to JSON (`yq -o=json . update-manager.constraints.yml`).
- `sha256sum` / `shasum` — drift detection; use the portability shim in the Drift detection section above.
- `diff` — optional; used for the unified diff display.
- `git` — branch and commit.
- `gh` — optional; used only if opening a PR is requested by the user.
