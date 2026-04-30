# Changelog

## 0.4.0

- Add Terraform/OpenTofu playbook: discovers root modules, updates provider/module version
  constraints and `.terraform.lock.hcl` via `tfupdate` + `<tool> init -upgrade`.
- CLI accepts `terraform`, `tofu`, and `opentofu` as ecosystem arguments (all map to the
  same playbook; tool preference: `tofu` > `terraform`).
- Security tier uses `checkov` for HCL misconfiguration findings via a per-finding loop;
  provider-binary CVEs are manual-only (advisory URLs surfaced; no automated provider CVE
  scan exists).
- Add `terraform` to multi-ecosystem ordering (runs after docker-compose, before github-actions).
- Update `renovate-sync` mappings: `terraform` ecosystem → Renovate `terraform` manager.
- Safety constraint: `plan`, `apply`, `destroy`, `state`, and `import` commands are
  explicitly forbidden — version files only.
- Minor tier offers the constraints.yml decline path on `AskUserQuestion`, matching the
  dockerfile and docker-compose playbooks.
- `renovate-sync` workflow template: relax `actions/checkout@v4.2.2` → `@v4` to match the
  tag-major style used by `validate.yml` and documented in the github-actions playbook.

## 0.3.0

- Add `renovate-sync` skill: generate and maintain `renovate.json5` + GitHub Actions
  workflow from `inventory.md` + `update-manager.constraints.yml`.
- Add PostToolUse hook that reminds the user to run `/renovate-sync` when its source
  files (`inventory.md` or `update-manager.constraints.yml`) are edited.

## 0.2.0

- Add Dockerfile, docker-compose, and GitHub Actions playbooks.

## 0.1.0

- Initial Rust, Python, and Node playbooks.
