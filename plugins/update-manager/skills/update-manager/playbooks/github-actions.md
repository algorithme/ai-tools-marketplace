# GitHub Actions playbook

Project-agnostic guidance for GitHub Actions workflows — updates `uses:` action refs and
`runs-on:` runner versions tier by tier.

## Discovery

A github-actions subproject is the entire `.github/` tree — one inventory entry per repo (not per
workflow file). Scan:

- `.github/workflows/*.y?ml` — CI/CD workflows.
- `.github/actions/*/action.y?ml` — local composite actions.

Parse every `uses:` value that references an external action:

```
uses: actions/checkout@v4             # owner/repo, ref=v4, kind=tag-major
uses: actions/checkout@v4.1.1         # ref=v4.1.1, kind=tag-semver
uses: actions/checkout@abc1234…       # ref=40-char hex, kind=sha
uses: ./.github/workflows/shared.yml  # skip — internal reusable workflow
uses: ./local-action                  # skip — local action
```

Skip refs that start with `.` (internal). Skip `docker://` image refs (managed by `docker-compose`
or `dockerfile` playbooks).

Also scan every `runs-on:` value to build a runner-version list.

## Pinning convention detection

Before planning, classify the repo's existing pinning style:

1. ≥ 80 % of external `uses:` refs are 40-char hex SHAs → convention **SHA-pinned**. Refresh
   digests; preserve inline version comments (e.g. `@abc1234 # v4.1.1`).
2. ≥ 80 % are `@vN` or `@vN.M.P` → convention **tag-pinned**. Bump tags.
3. Mixed or neither → keep each ref's existing style. Surface a `note` recommending normalisation
   (cite OpenSSF Scorecard requirement for SHA pinning in supply-chain security).

Never silently change pin style (SHA ↔ tag) — that is a convention decision, not a bump.

## Tier mapping

| Tier     | Action                                                                                      |
|----------|---------------------------------------------------------------------------------------------|
| security | Run `actionlint` (catches deprecated runners, `set-output`, EOL `node12`/`node16` actions). Query the GitHub Advisory Database (`gh api "https://api.github.com/advisories?ecosystem=actions&package={owner}/{repo}"`) per external action for known CVEs. Surface EOL runners (see Runner deprecation calendar below). |
| patch    | SHA-pinned: re-resolve current tag to its latest commit SHA. Call `gh api /repos/{owner}/{repo}/git/ref/tags/{tag}` — if `object.type == "tag"` (annotated), make a second call `gh api /repos/{owner}/{repo}/git/tags/{object.sha}` to get the commit SHA; if `object.type == "commit"` (lightweight tag), use `object.sha` directly. Tag-pinned at `@vN.M.P`: bump to latest patch on same minor. Tag-pinned at `@vN` (major alias): no-op. |
| minor    | Bump within current major: `@v4.1.0` → `@v4.2.0`. For SHA-pinned refs, also re-pin the new commit SHA. Preserve pin style. |
| major    | Bump major: `@v3` → `@v4`, `@v3.x.y` → latest `@v4.x.y`. Always `manual-only` — major bumps often change input/output names, permissions, or OIDC behaviour. |

Run security tier as a **per-advisory loop**: scan → bump one action → `actionlint` → next.

### Runner deprecation calendar

Surface the following as `security`-tier findings when found in `runs-on:`. Before surfacing,
verify current status at https://github.com/actions/runner-images — GitHub updates EOL dates and
this table may lag.

| Runner               | Status (as of 2026-04-28)  | Suggested replacement  |
|----------------------|----------------------------|------------------------|
| `ubuntu-18.04`       | EOL — removed              | `ubuntu-24.04`         |
| `ubuntu-20.04`       | EOL — removed (Apr 2025)   | `ubuntu-24.04`         |
| `ubuntu-22.04`       | active                     | —                      |
| `ubuntu-24.04`       | active (recommended)       | —                      |
| `macos-11`           | EOL — removed              | `macos-15`             |
| `macos-12`           | EOL — removed (2024)       | `macos-15`             |
| `macos-13`           | active                     | —                      |
| `macos-14`/`15`      | active (recommended)       | —                      |
| `windows-2019`       | EOL — removed (Jan 2025)   | `windows-2025`         |
| `windows-2022`       | active                     | —                      |

Do not auto-replace runner strings — surface as `manual-only` with the recommended replacement.

## Tooling bootstrap

Check for required tools at Preflight. If missing:

1. **gh** (required — already a global prerequisite of the skill):
   - Abort with hint if absent.

2. **actionlint** (required for Fix and security tier):
   ```bash
   brew install actionlint
   # or: docker run --rm -v "$PWD:/repo" --workdir /repo rhysd/actionlint:latest
   ```
   Require user confirmation before installing. On decline: write
   `"actionlint not installed — security/Fix phases skipped"` to `notes`.

3. **pinact** (optional — automates SHA pinning):
   ```bash
   brew install pinact
   ```
   Detect existing `.pinact.yaml` or `pinact.yaml` — if present, prefer `pinact run` for SHA
   refresh over manual `gh api` lookups. Require confirmation before installing if absent.

4. **yamlfmt** (format):
   ```bash
   brew install yamlfmt
   ```
   Require confirmation. On decline: omit `format`.

## Fix phase

Default validation command: `actionlint`

- Statically analyses all workflow YAML files.
- Optionally invokes `shellcheck` on inline `run:` scripts if `shellcheck` is on PATH.
- Exits non-zero on schema errors, deprecated syntax, or expression type errors.

Do not auto-fix semantic errors — surface them in the Fix-phase prompt for user decision.

## Default format command

When `refresh` generates a new inventory entry, detect in this order:

1. `yamlfmt` is on PATH → `format: [yamlfmt .github/]`.
2. Else → omit `format`.

## Notes to surface in inventory

- SHA pinning not adopted: surface "Consider SHA-pinning all `uses:` refs (OpenSSF Scorecard
  requires it for SLSA Level 2). Use `pinact run` to automate." — do not auto-pin.
- OIDC permission changes: action majors (e.g. `aws-actions/configure-aws-credentials` v2 → v4)
  often require adding `permissions: id-token: write` to the job. Flag when detected.
- Third-party action ownership transfers: `gh api /repos/{owner}/{repo}` to verify the action
  still exists and the owner hasn't changed before bumping.
- Reusable workflow refs (`uses: org/repo/.github/workflows/x.yml@ref`) — treated as external
  actions; apply the same pinning and tier logic.
- Self-hosted runners (`runs-on: [self-hosted, …]`) — skip runner-deprecation checks; surface
  a note that the user manages their own runner lifecycle.
