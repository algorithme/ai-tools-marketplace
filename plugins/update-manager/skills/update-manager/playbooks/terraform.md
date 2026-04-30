# Terraform / OpenTofu playbook

Project-agnostic guidance for Terraform and OpenTofu root modules — updates provider versions,
module versions, and the core `required_version` constraint, tier by tier.

## Tool detection

At Preflight and refresh, detect the CLI in this order:
1. `tofu --version` — if exit 0, use `tofu`.
2. `terraform --version` — if exit 0, use `terraform`.
3. Neither found → abort with install instructions for both.

Store the detected tool in the inventory entry `notes` as `"detected tool: tofu"` or
`"detected tool: terraform"`. Re-detect on every `refresh`.

The `<tool>` placeholder throughout this playbook resolves to the detected binary.

## Discovery

A Terraform subproject is a directory containing at least one `.tf` file with:
- a `terraform { required_providers { … } }` block, or
- a `module "…" { version = "…" }` argument pointing to a registry source, or
- a `terraform { required_version = "…" }` constraint.

Exclude: `.terraform/`, `.terragrunt-cache/`, `vendor/`, `.git/`.

Each qualifying directory is one inventory entry. Child modules under `./modules/**` are
separate subprojects if they qualify independently.

**Manifests**: all `.tf` files in the directory (non-recursive).
**Lockfile**: `.terraform.lock.hcl` in the same directory.

## Scope of updates

| Target | Location | Notes |
|---|---|---|
| Provider version constraints | `required_providers { x = { version = "~> …" } }` | Primary target |
| Module version constraints | `module "…" { version = "…" }` | Registry modules only |
| Core required version | `terraform { required_version = "…" }` | Patch/minor only |
| Lockfile | `.terraform.lock.hcl` | Always refreshed after any `.tf` change |

**NEVER execute**: `plan`, `apply`, `destroy`, `import`, `state`, `force-unlock`, or any
command that reads or modifies infrastructure state. Version files only.

## Tier mapping

| Tier     | Action |
|----------|--------|
| security | Run `checkov -d . --quiet --compact -o json` for HCL misconfiguration findings (open ingress, missing encryption, public buckets, etc.). This is a misconfiguration surface, not a CVE scan. Provider-binary CVEs are tracked separately as **manual-only** — surface the HashiCorp security advisories feed (https://discuss.hashicorp.com/c/security/) and the OpenTofu security page; the user reviews and approves provider bumps by hand. |
| patch    | Query registry API per provider/module → latest patch within current major.minor; bump with `tfupdate`. |
| minor    | Query registry API per provider/module → latest minor within current major; bump with `tfupdate`. **Before applying:** `AskUserQuestion` per provider/module — show `<source> <old-constraint>` → `<source> <new-constraint>` and ask the user to confirm. On decline, offer to record the provider/module in `update-manager.constraints.yml` (see SKILL.md § Version constraints). |
| major    | Always `manual-only`. Surface provider changelog URL. User edits constraints; skill runs Fix + Gate after confirmation. |

After any tier that modifies `.tf` files, refresh the lockfile:
```bash
<tool> init -upgrade
```
`init -upgrade` resolves new provider binaries into cache and rewrites `.terraform.lock.hcl`
hashes. It does not initialise remote backends or touch infrastructure state.

`init -upgrade` requires outbound network access to the configured provider registries
(`registry.terraform.io` and/or `registry.opentofu.org`). In air-gapped or restricted-egress
environments, the security/patch/minor tiers will fail at lockfile refresh; surface this as a
preflight warning when egress is constrained.

## Registry API

```bash
# Provider versions (Terraform registry)
curl -s "https://registry.terraform.io/v1/providers/<namespace>/<type>/versions" \
  | jq -r '.versions[].version' | sort -V

# Module versions
curl -s "https://registry.terraform.io/v1/modules/<namespace>/<name>/<provider>/versions" \
  | jq -r '.modules[0].versions[].version' | sort -V
```

When the detected tool is `tofu`, query the OpenTofu registry first; fall back to
`registry.terraform.io` on 404:
```bash
curl -s "https://registry.opentofu.org/v1/providers/<namespace>/<type>/versions"
```

Derive `<namespace>/<type>` from the `source` attribute in `required_providers`. Default
namespace is `hashicorp` when only the type name is present (e.g. `aws` → `hashicorp/aws`).

## Constraint bumping rules

| Current constraint        | Tier  | New constraint example |
|---------------------------|-------|------------------------|
| `~> 5.0`                  | patch | `~> 5.0.10`            |
| `~> 5.0` / `~> 5.0.x`    | minor | `~> 5.3`               |
| `>= 5.0, < 6.0`           | minor | `>= 5.3, < 6.0`        |
| any                       | major | `~> 6.0` (manual-only) |

When `tfupdate` cannot parse the current constraint, emit a warning in the plan table and skip
the entry rather than overwriting with an unexpected format.

### Constraints check

Before presenting any candidate bump (minor or major), check `update-manager.constraints.yml`
in the host project root. If the provider source or module address matches a constraint and
the candidate's new version exceeds `max_version`, skip the candidate — mark it as
`[blocked by constraint]` in the plan table with the recorded reason.

## Tooling bootstrap

Check at Preflight. Prompt before installing; on decline, abort with instructions.

1. **terraform or tofu** (required — abort if neither found):
   ```bash
   brew install opentofu   # or: brew install terraform
   ```

2. **tfupdate** (required for constraint edits):
   ```bash
   brew install tfupdate
   # or: go install github.com/minamijoyo/tfupdate@latest
   ```

3. **checkov** (required for security tier — HCL misconfiguration scanning):
   ```bash
   brew install checkov
   # or: pipx install checkov
   ```
   On decline, skip security tier and record `"checkov not installed — security tier skipped"`
   in `notes`.

4. **tflint** (optional gate):
   ```bash
   brew install tflint
   ```
   Only install if the user opts in. When absent, omit from generated `gate[]`.

## Fix phase

Default typecheck command:
```bash
<tool> validate
```

`validate` requires an initialised working directory. If `.terraform/` is absent, run
`<tool> init` (without `-upgrade`) before validate — this downloads locked provider versions
from cache only and does not modify infrastructure state.

On failure, follow the standard Fix loop (Ask → patch → retry up to 3×). Auto-fix only HCL
syntax issues (deprecated attributes, removed arguments). Do not auto-fix resource
configuration.

## Format phase

```bash
<tool> fmt -recursive .
```

## Gate phase (default)

When `refresh` generates a new inventory entry, populate `gate[]` as:
```yaml
gate:
  - <tool> validate
  # - tflint --recursive   # added only when tflint is present at refresh time;
  #                        # remind the user to run `tflint --init` after a provider
  #                        # bump so plugin rules cover the new provider version
```

## Per-finding loop

Security tier runs as a **per-finding loop** for misconfig results: scan → present finding →
ask the user to confirm a remediation edit → validate → next finding. Do not batch all
remediations in one pass. Misconfig fixes typically modify resource arguments (e.g. add
`encryption = true`); never edit constraints, only resource blocks, and require user
confirmation for each one.

Provider-binary CVEs are out of scope for the automated loop — the tier surfaces advisory
URLs and asks the user to approve any provider version bumps manually.

## Notes to surface in inventory

- Backend blocks (`terraform { backend "…" { … } }`) are never touched.
- Providers without an explicit `version` constraint are recorded as unmanaged in `notes`.
- Modules with a `git::` or local-path `source` have no registry version — exclude from
  version updates; record in `notes`.
- `required_version` for the core binary is updated for patch/minor only; major core version
  upgrades are always `manual-only`.
- When `init -upgrade` changes a significant number of provider hashes, include a lockfile
  summary line in the commit message.
