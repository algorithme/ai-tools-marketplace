# Changelog

## 0.3.0

- Add `renovate-sync` skill: generate and maintain `renovate.json5` + GitHub Actions
  workflow from `inventory.md` + `update-manager.constraints.yml`.
- Add PostToolUse hook that reminds the user to run `/renovate-sync` when its source
  files (`inventory.md` or `update-manager.constraints.yml`) are edited.

## 0.2.0

- Add Dockerfile, docker-compose, and GitHub Actions playbooks.

## 0.1.0

- Initial Rust, Python, and Node playbooks.
