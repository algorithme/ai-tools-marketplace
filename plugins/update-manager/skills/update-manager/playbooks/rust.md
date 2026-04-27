# Rust playbook

Project-agnostic guidance for Rust/Cargo subprojects.

## Discovery

A Rust subproject is any directory containing a `Cargo.toml` that has either:
- a `[workspace]` section (workspace root), or
- a `[package]` section and is not a member of an outer workspace.

For each detected root, set `working_directory` to the directory holding that `Cargo.toml`.
Manifest list = `Cargo.toml` plus all `crates/*/Cargo.toml` under a workspace. Lockfile is
`Cargo.lock` next to the workspace root.

## Tier mapping

| Tier     | Command (default)                         | Notes                                                  |
|----------|-------------------------------------------|--------------------------------------------------------|
| security | `cargo audit`                             | Per advisory: `cargo update -p <crate> --precise <v>`. |
| patch    | `cargo update`                            | Lockfile only; semver-compatible.                      |
| minor    | `cargo upgrade`                           | Default behavior upgrades within compatible ranges.    |
| major    | `cargo upgrade --incompatible allow`      | Rewrites version requirements; expect breakage.        |

## Workspace deps

If the workspace declares `[workspace.dependencies]`, prefer landing bumps there. Member crates
should only have their own `[dependencies]` updated when the dep is not declared at workspace
level.

## Tooling bootstrap

`cargo audit` and `cargo upgrade` ship as separate binaries (`cargo-audit` and `cargo-edit`
respectively). If absent, offer to install them once with user confirmation:

```bash
cargo install cargo-audit cargo-edit
```

Do not install silently. If the user declines, surface the install command in the inventory's
`notes` so the next run can prompt again.

## Fix phase

Default typecheck command: `cargo check --all-targets`.

If a major bump triggers compilation errors:
- Read the failing build output for `error[E0...]` codes pointing at renamed APIs, removed
  items, or trait bound changes.
- Before applying any source fix, `AskUserQuestion`: show the error and describe the proposed
  change (file, line, kind). Proceed only on user confirmation.
- Apply the minimal source fix (rename, re-add explicit type, swap deprecated method for the
  documented replacement).
- Re-run `cargo check --all-targets` after each fix.

## Default format command

When `refresh` generates a new inventory entry for a Rust subproject, populate `format` with:

```yaml
format:
  - cargo fmt
```

`cargo fmt` is part of the standard Rust toolchain and always available alongside `cargo`.

## Notes to surface in inventory

When generating `notes` during `refresh`, include hazards that bite later:
- Compile-time query caches (e.g. `sqlx`'s `.sqlx/` directory) need regeneration after a sqlx
  bump.
- `rust-toolchain.toml` pins must move in lockstep with any CI workflow toolchain version.
- `build.rs` calling out to system libraries — note the system dependency so the user knows
  which OS package controls the ABI.
