# renovate-sync mappings

Translation reference from `inventory.md` and `update-manager.constraints.yml` fields to
Renovate configuration primitives. This document is the authoritative source for generation
logic; `SKILL.md` references it for brevity.

## Ecosystem → `enabledManagers`

| `inventory.ecosystem` | Renovate `enabledManagers` value(s) | Notes |
|---|---|---|
| `rust` | `cargo` | Cargo.toml + Cargo.lock |
| `python` | `pip_requirements` and/or `poetry` and/or `pep621` | Detect by lockfile: `requirements*.txt` → `pip_requirements`; `poetry.lock` → `poetry`; `uv.lock` or `pyproject.toml` without poetry → `pep621` |
| `node` | `npm` | Covers npm, yarn, pnpm, bun — Renovate auto-detects lockfile format within the `npm` manager |
| `dockerfile` | `dockerfile` | |
| `docker-compose` | `docker-compose` | |
| `github-actions` | `github-actions` | Handles `uses:` refs in `.github/workflows/*.yml` |

Only add entries for ecosystems actually present in `inventory.md`. Do not include an
ecosystem manager when no inventory entry exists for it.

## Monorepo subproject scoping (`matchFileNames`)

When `inventory.md` has multiple subprojects for the same ecosystem in different paths,
add a `packageRule` per subproject that scopes updates to its manifest files:

```json5
{
  matchFileNames: ['services/api/Cargo.toml', 'services/api/Cargo.lock'],
  // ... subproject-specific overrides (schedule, automerge, etc.)
}
```

For single-subproject repos, omit `matchFileNames` — Renovate scans the whole tree.

## Update tiers → `matchUpdateTypes`

| `/update-manager` tier | Renovate `matchUpdateTypes` values | Default behavior |
|---|---|---|
| `security` | Built-in: `vulnerabilityAlerts` | Always enabled; labels `['security']` |
| `patch` | `patch`, `digest`, `pin`, `lockFileMaintenance` | Automerge |
| `minor` | `minor` | PR opened, no automerge |
| `major` | `major` | Dashboard approval required; label `needs-update-manager` |

## `constraints.yml` → `packageRules`

Each `constraints[]` entry maps to a `packageRule` that caps the allowed version range.

### Mapping

| `constraints.yml` field | Renovate `packageRule` field |
|---|---|
| `package` (exact name) | `matchPackageNames: ['<package>']` |
| `package` (glob pattern, e.g. `postgres*`) | `matchPackagePatterns: ['^postgres']` |
| `max_version` (semver, e.g. `"17"`) | `allowedVersions: '<18'` (increment major by 1) |
| `max_version` (variant suffix, e.g. `"16-alpine"`) | Extract numeric prefix → `allowedVersions: '<17'` |
| `reason` | `description: '<reason>'` |
| `ecosystem` | `matchManagers: ['<renovate-manager>']` (use table above); omit for `all` |

### Example

```yaml
# update-manager.constraints.yml
constraints:
  - ecosystem: docker-compose
    package: postgres
    max_version: "16"
    reason: "WAL format change — DBA review required"
```

→

```json5
{
  description: 'WAL format change — DBA review required',
  matchManagers: ['docker-compose'],
  matchPackageNames: ['postgres'],
  allowedVersions: '<17',
},
```

### `max_version` parsing rules

1. Parse as semver. If valid, emit `allowedVersions: '<NEXT_MAJOR.0.0'`.
2. If it contains a variant suffix (e.g. `16-alpine`, `20-slim`), extract the leading integer,
   increment by 1, emit `allowedVersions: '<NEXT_INTEGER'`.
3. If it starts with `v` (e.g. `v4`), emit `allowedVersions: '< v5'` (keep the prefix).
4. If parsing fails, emit the raw value as `allowedVersions: '<max_version>'` with a
   `// WARNING: verify this constraint` comment.

## `inventory.manual-only[]` → `dependencyDashboardApproval`

Each `manual-only` entry maps to a rule requiring dashboard approval before Renovate
opens a PR for that package:

```json5
{
  description: '<reason>',
  matchPackageNames: ['<package-name-or-glob>'],
  dependencyDashboardApproval: true,
},
```

Glob patterns (`*`, `?`) are converted to Renovate regex patterns in `matchPackagePatterns`.
Example: `tokio*` → `matchPackagePatterns: ['^tokio']`.

## `inventory.excluded[]` → `enabled: false`

Each `excluded` entry maps to a rule that disables updates entirely for that package:

```json5
{
  description: '<reason>',
  matchPackageNames: ['<package-name-or-glob>'],
  enabled: false,
},
```

## Branch and commit conventions

| `/update-manager` convention | Renovate config field | Value |
|---|---|---|
| Branch prefix `deps/` | `branchPrefix` | `'deps/'` |
| Commit prefix `deps(<eco>):` | Per-`packageRule` `commitMessagePrefix` | `'deps(<eco>):'` |

The commit prefix is set per-ecosystem packageRule rather than globally, to match the
granularity of `/update-manager` commit messages. Omit the per-ecosystem prefix for
`lockFileMaintenance` rules (Renovate generates those commit messages autonomously).

## GitHub Actions pin convention → `extends` preset

| Inventory note (from github-actions playbook) | Action |
|---|---|
| Contains "SHA-pinned" | Include `'helpers:pinGitHubActionDigests'` in `extends` |
| Contains "tag-pinned" | Omit the preset |
| Note absent or mixed | Omit the preset; add an inventory `note` recommending normalisation |

The preset `helpers:pinGitHubActionDigests` instructs Renovate to pin `uses:` refs to
their SHA digests and maintain inline version comments (e.g. `@abc1234 # v4.1.1`).
