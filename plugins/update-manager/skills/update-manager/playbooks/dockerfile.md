# Dockerfile playbook

Project-agnostic guidance for Dockerfiles — updates base image tags and digest pins tier by tier.

## Discovery

A Dockerfile subproject is any file named `Dockerfile`, `Dockerfile.<variant>`, or `*.Dockerfile`
anywhere in the tree (excluding `node_modules`, `.git`, `target`, `vendor`). One inventory entry
per Dockerfile. Multi-stage builds (`FROM … AS <alias>`) are collapsed into a single entry; all
`FROM` lines are managed together.

Parse each `FROM` line into a record: `{image, tag, digest, alias}`. Examples:

```
FROM node:20.10-alpine                    # image=node, tag=20.10-alpine, digest=none
FROM node:20-alpine@sha256:abc123…        # image=node, tag=20-alpine, digest=sha256:abc123…
FROM scratch                              # skip — no image to update
```

Skip `FROM scratch` and `FROM <alias>` (re-use stage) entries.

## Tier mapping

| Tier     | Action                                                                                      |
|----------|---------------------------------------------------------------------------------------------|
| security | Run `docker scout cves <image>:<tag>` per FROM record; on any CVE hit, bump to the lowest tag version where the CVE is fixed. Fallback: `trivy image --severity HIGH,CRITICAL <image>:<tag>`. |
| patch    | If the FROM line is digest-pinned (`@sha256:`): re-resolve the current tag → latest digest for that tag (`docker buildx imagetools inspect <image>:<tag> --format '{{json .Manifest.Digest}}'`). This is a same-version digest refresh — no prompt needed. Tag-only refs: no-op — annotate as "no digest pin; consider pinning" in the Plan table. |
| minor    | Bump the tag within the current major: `node:20.10-alpine` → `node:20.13-alpine`. Preserve the variant suffix exactly (`-alpine`, `-slim`, `-bookworm`, etc.). **Before applying:** `AskUserQuestion` per FROM record — show `<image>:<old-tag>` → `<image>:<new-tag>` and ask the user to confirm. On decline, offer to record the image in `update-manager.constraints.yml` (see SKILL.md § Version constraints). |
| major    | Bump to the next major: `node:20-alpine` → `node:22-alpine`. Always registered as `manual-only` in inventory — major base-image bumps change ABI, libc, and package availability. |

Run security tier as a **per-FROM loop**: scan → bump → validate (Fix phase) → next FROM. Do not
batch all FROM bumps in one pass.

### Constraints check

Before presenting any candidate bump (minor or major), check `update-manager.constraints.yml` in
the host project root. If the image name matches a constraint and the candidate's new version
exceeds `max_version`, skip the candidate — mark it as `[blocked by constraint]` in the plan
table with the recorded reason.

## Tooling bootstrap

Check for required tools at Preflight. If missing:

1. **docker** (required):
   - Not negotiable — abort with a clear message if absent.

2. **docker scout** (preferred for CVE scanning):
   ```bash
   # Included with Docker Desktop. Enable in Docker settings → Docker Scout.
   docker scout version
   ```
   On missing or disabled: offer to install, or fall back to `trivy`.

3. **trivy** (fallback CVE scanner):
   ```bash
   brew install trivy
   ```
   Require user confirmation before installing. On decline: write `"trivy not installed — security tier skipped"` to `notes`.

4. **hadolint** (lint/format):
   ```bash
   brew install hadolint
   # or: docker run --rm -i hadolint/hadolint < Dockerfile
   ```
   If absent, omit `format` in the generated inventory entry (do not install silently).

## Fix phase

Default build-check command, in order of preference:

1. If Docker Engine ≥ 26 / Docker Desktop ≥ 4.30 (ships Buildx ≥ 0.13): `docker build --check .`
   — static lint, no image produced, fast. Detect with:
   `docker buildx version | grep -qE 'v0\.(1[3-9]|[2-9][0-9])\.|v[1-9]\.'`
2. Else: skip — do not run a full `docker build` automatically. The user opts in via `gate[]`.

If the check returns non-zero, follow the standard Fix loop (Ask → patch → retry up to 3×) for
linter errors (e.g. deprecated `MAINTAINER`, missing `HEALTHCHECK`, pinned `--platform` conflicts).
Do not auto-fix semantic errors.

## Default format command

When `refresh` generates a new inventory entry, detect the linter/formatter in this order:

1. `hadolint` is on PATH → populate `format: [hadolint <dockerfile-path>]`.
2. Else → omit `format` (leave field absent).

`hadolint` runs as the format step (before `gate[]`) because it is deterministic and fast — the
same role `cargo fmt` plays for Rust.

## Notes to surface in inventory

- `ARG`-driven base tags (e.g. `ARG NODE_VERSION=20`) make the `FROM` line dynamic — note that the
  `ARG` default must also be updated and `manifest_hashes` may not capture the effective image.
- Distro-variant switches (`-debian` → `-alpine`) change libc; flag if detected mid-bump.
- Multi-arch: after a major bump, run `docker buildx imagetools inspect <image>:<new-tag>` to
  confirm the required platforms (`linux/amd64`, `linux/arm64`) are still available.
- `HEALTHCHECK` commands may invoke binaries whose paths change across distro variants.
