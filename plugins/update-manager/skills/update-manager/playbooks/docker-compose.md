# Docker Compose playbook

Project-agnostic guidance for Compose files — updates service image references tier by tier.

## Discovery

A docker-compose subproject is any file matching `docker-compose.y?ml`, `compose.y?ml`, or
`docker-compose.*.y?ml` anywhere in the tree (excluding `node_modules`, `.git`). One inventory
entry per top-level compose file.

Parse every `services.<name>.image:` value into a record `{service, image, tag, digest}`.
- Services with `image:` only: managed as a registry image.
- Services with **both** `build:` and `image:`: `image:` names the locally built result — managed
  for CVE scanning purposes (the named image may be pushed), but tag bumps are skipped (no
  registry tag to advance). Surface a note: "service <name> has both build+image — tag bumps
  skipped; check Dockerfile via the dockerfile playbook."
- Services with `build:` only and no `image:`: skip entirely — managed by the `dockerfile`
  playbook for the referenced `Dockerfile`.

```yaml
services:
  api:
    image: node:20-alpine             # managed: image=node, tag=20-alpine
  worker:
    build: ./worker                   # skip — no external image
  db:
    image: postgres:16@sha256:abc…    # managed: digest-pinned
  gateway:
    build: ./gateway
    image: myorg/gateway:latest       # CVE scan only; skip tag bumps
```

Also note `include:` and `extends:` references — surface them in `notes` so the user knows other
compose files may declare additional `image:` values not covered by this entry.

## Tier mapping

| Tier     | Action                                                                                      |
|----------|---------------------------------------------------------------------------------------------|
| security | Run `docker scout cves <image>:<tag>` (or `trivy image --severity HIGH,CRITICAL`) per service image; bump tag to the lowest fixed version on CVE hit. |
| patch    | Digest-pinned refs: re-resolve current tag → latest digest (`docker buildx imagetools inspect`). This is a same-version digest refresh — no prompt needed. Tag-only refs: no-op — annotate as "no digest pin" in Plan table. |
| minor    | Bump tag within current major (`postgres:16.1` → `postgres:16.4`); preserve variant suffix. **Before applying:** `AskUserQuestion` per service — show `<image>:<old-tag>` → `<image>:<new-tag>` and ask the user to confirm. On decline, offer to record the image in `update-manager.constraints.yml` (see SKILL.md § Version constraints). |
| major    | Bump major (`postgres:16` → `postgres:17`); always registered as `manual-only` — major image bumps change data formats, protocols, and config keys. |

Run security tier as a **per-service loop**: scan → bump → validate → next service. Do not batch.

### Constraints check

Before presenting any candidate bump (minor or major), check `update-manager.constraints.yml` in
the host project root. If the image name matches a constraint and the candidate's new version
exceeds `max_version`, skip the candidate — mark it as `[blocked by constraint]` in the plan
table with the recorded reason.

## Tooling bootstrap

Check for required tools at Preflight. If missing:

1. **docker compose** (Compose V2 plugin — required):
   ```bash
   docker compose version   # must print "Docker Compose version v2.x"
   ```
   If only legacy `docker-compose` (V1, separate binary) is detected: surface a `note` recommending
   migration to Compose V2 and use the V1 binary for this run only. Do not abort.

2. **docker scout** or **trivy** — same bootstrap logic as the `dockerfile` playbook.

3. **yamlfmt** (format):
   ```bash
   brew install yamlfmt
   # or: go install github.com/google/yamlfmt/cmd/yamlfmt@latest
   ```
   Require user confirmation before installing. On decline: omit `format`.

## Fix phase

Default validation command: `docker compose config -q`

- Parses and validates the compose file schema including variable interpolation (reads `.env` if
  present).
- Exits non-zero on schema errors or unresolved required variables.
- Does **not** pull images or contact a registry — fast and offline-safe.

Do not automatically run `docker compose pull` or `docker compose build` — opt-in via `gate[]`.

## Default format command

When `refresh` generates a new inventory entry, detect in this order:

1. `yamlfmt` is on PATH → `format: [yamlfmt -lint <compose-file>]`.
2. Else → omit `format`.

## Notes to surface in inventory

- Top-level `version:` field (e.g. `version: "3.9"`) is deprecated in Compose V2 and ignored.
  Flag its presence so the user can remove it.
- `extends:` / `include:` chains: other compose files (e.g. `docker-compose.override.yml`) may
  declare additional `image:` references not visible to this playbook run. List them in `notes`.
- `${VAR}` interpolation: if any `image:` value contains a variable (e.g. `image: myapp:${TAG}`),
  skip that service and note it — the effective image depends on the runtime environment.
- `profiles:` may gate services behind named profiles; bump applies to all parsed services
  regardless of active profile. Document active profiles in `notes` if detected.
- Services using `network_mode: host` or privileged settings may fail after image major bumps —
  surface as a note when major tier is requested.
