# inventory.md (template)

This file is **generated** at the host project root by `/update-manager refresh` and edited by
hand to record per-project quirks. The schema below is the canonical reference.

For capping automatic version upgrades on specific images or packages, see
`update-manager.constraints.yml` (schema in `constraints.template.yml`).

## Schema

```yaml
subprojects:
  - id: <unique-slug>                    # stable key used to merge across refreshes
    path: <relative-path-to-subproject>  # from the host project root
    ecosystem: rust | python | node | dockerfile | docker-compose | github-actions  # selects the playbook
    working_directory: <dir>             # cd into this before running any command
    manifests:                           # files staged after Commit
      - <manifest-file-1>
    lockfile: <path-or-null>             # also staged after Commit, if present
    manifest_hashes:                     # SHA-256 of each manifest at last refresh (auto-managed)
      <manifest-file>: <hex-digest>

    update_commands:                     # commands the skill runs in Phase 3 (Apply)
      security: <command>
      patch:    <command>
      minor:    <command>
      major:    <command>

    gate:                                # Phase 6 — all must exit 0 before commit
      - <command-1>
      - <command-2>

    format:                              # Phase 5 — run after Fix, before Gate (optional)
      - <formatter-command>              # e.g. cargo fmt, ruff format ., npx prettier --write .

    prerequisites:                       # Phase 1 — verified reachable before Apply
      - <setup-command>

    excluded:                            # never updated automatically
      - pattern: "<glob>"                # matches package name(s)
        reason:  "<why>"

    manual-only:                         # AskUserQuestion before including
      - pattern: "<glob>"
        reason:  "<why>"

    notes:                               # printed at plan time, surfaced in PR body
      - "<free-text warning>"
```

## Merge semantics on `refresh`

When `/update-manager refresh` runs and an `inventory.md` already exists:

| Field                | Behavior on refresh                                           |
|----------------------|---------------------------------------------------------------|
| New subproject       | Appended.                                                     |
| `path`               | Updated if the subproject moved.                              |
| `manifests`          | Updated to current discovery result.                          |
| `lockfile`           | Updated.                                                      |
| `manifest_hashes`    | **Always updated** (recomputed from current manifest content).|
| `update_commands`    | Updated to the playbook's current defaults.                   |
| `gate`               | Updated **only** if missing or empty; otherwise preserved.    |
| `format`             | **Preserved** verbatim.                                       |
| `prerequisites`      | **Preserved** verbatim.                                       |
| `excluded`           | **Preserved** verbatim.                                       |
| `manual-only`        | **Preserved** verbatim.                                       |
| `notes`              | **Preserved** verbatim.                                       |

The `id` field is the merge key. If a subproject's `path` changes, keep the same `id` to retain
its curated fields.

## Example (filled-in)

```yaml
subprojects:
  - id: api-server
    path: services/api
    ecosystem: rust
    working_directory: services/api
    manifests:
      - Cargo.toml
    lockfile: Cargo.lock
    update_commands:
      security: cargo audit
      patch:    cargo update
      minor:    cargo upgrade
      major:    cargo upgrade --incompatible allow
    gate:
      - cargo clippy --all-targets -- -D warnings
      - cargo test
    format:
      - cargo fmt
    prerequisites:
      - docker compose up -d postgres
    excluded:
      - pattern: "openssl-sys"
        reason:  "ABI pinned to system libssl 1.1"
    manual-only:
      - pattern: "tokio"
        reason:  "Major bumps require concurrency review"
    notes:
      - "sqlx query cache lives in services/api/.sqlx — regenerate after bumping sqlx."

  - id: api-dockerfile
    path: services/api/Dockerfile
    ecosystem: dockerfile
    working_directory: services/api
    manifests:
      - Dockerfile
    lockfile: null
    manifest_hashes:
      Dockerfile: <sha256-auto>
    update_commands:
      security: docker scout cves node:20-alpine
      patch:    docker buildx imagetools inspect node:20-alpine --format '{{json .Manifest.Digest}}'
      minor:    ""  # resolved per FROM line by the playbook
      major:    ""  # manual-only — requires user confirmation
    gate:
      - docker build --check .
    format:
      - hadolint Dockerfile
    prerequisites:
      - docker info
    excluded: []
    manual-only:
      - pattern: "*"
        reason:  "Major base-image bumps change ABI — always confirm"
    notes:
      - "ARG NODE_VERSION=20 drives the FROM tag — update the ARG default when bumping."

  - id: api-compose
    path: docker-compose.yml
    ecosystem: docker-compose
    working_directory: .
    manifests:
      - docker-compose.yml
    lockfile: null
    manifest_hashes:
      docker-compose.yml: <sha256-auto>
    update_commands:
      security: docker scout cves postgres:16-alpine
      patch:    docker buildx imagetools inspect postgres:16-alpine --format '{{json .Manifest.Digest}}'
      minor:    ""  # resolved per service image by the playbook; user confirmed via AskUserQuestion
      major:    ""  # manual-only — major image bumps change data formats and config keys
    gate:
      - docker compose config -q
    format:
      - yamlfmt docker-compose.yml
    prerequisites:
      - docker info
    excluded: []
    manual-only:
      - pattern: "postgres"
        reason:  "Major PostgreSQL bumps change WAL format — requires DBA sign-off"
    notes:
      - "db service uses postgres:16-alpine; postgres:17 released — check release notes before upgrading."
      - "override file docker-compose.override.yml declares additional image refs not tracked here."

  - id: ci-workflows
    path: .github/workflows
    ecosystem: github-actions
    working_directory: .
    manifests:
      - .github/workflows/validate.yml
    lockfile: null
    manifest_hashes:
      .github/workflows/validate.yml: <sha256-auto>
    update_commands:
      security: actionlint
      patch:    pinact run --dry-run   # re-resolve SHAs; replace with gh api calls if pinact absent
      minor:    ""  # resolved per uses: line by the playbook
      major:    ""  # manual-only
    gate:
      - actionlint
    format:
      - yamlfmt .github/
    prerequisites:
      - gh auth status
    excluded: []
    manual-only:
      - pattern: "*"
        reason:  "Major action bumps change inputs/outputs and OIDC permissions — always confirm"
    notes:
      - "Repo uses tag pinning (@v4). Consider SHA pinning for OpenSSF Scorecard compliance."
```
