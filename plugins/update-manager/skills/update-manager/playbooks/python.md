# Python playbook

Project-agnostic guidance for Python subprojects.

## Discovery

A Python subproject is any directory containing one of:
- `pyproject.toml`
- `requirements.txt` (or `requirements-*.txt`)
- `uv.lock`
- `poetry.lock`
- `Pipfile` / `Pipfile.lock`

Determine the **toolchain** from the lockfile present:

| Lockfile      | Toolchain  |
|---------------|------------|
| `uv.lock`     | uv         |
| `poetry.lock` | Poetry     |
| `Pipfile.lock`| Pipenv     |
| (none)        | pip + pinned `requirements.txt` (manual) |

Set `working_directory` to the directory holding the manifest. Manifests = `pyproject.toml`
and any `requirements*.txt`; lockfile = whichever of the four above is present.

## Tier mapping

### uv

| Tier     | Command                                                       |
|----------|---------------------------------------------------------------|
| security | `uv lock --upgrade-package <pkg>` per pip-audit advisory      |
| patch    | `uv lock --upgrade`                                           |
| minor    | `uv lock --upgrade`                                           |
| major    | edit version specifiers in `pyproject.toml`, then `uv lock`   |

> uv resolves to the latest version within `pyproject.toml` constraints; it does not
> distinguish patch vs minor. Both tiers run the same command — the user's version
> specifiers (e.g. `>=1.0,<2.0`) control the ceiling. The Plan-phase table annotates
> uv bumps as `minor (uv: patch≡minor)` when `patch` was requested so the user can see this.

### Poetry

| Tier     | Command                                              |
|----------|------------------------------------------------------|
| security | `poetry update <pkg>` per advisory                   |
| patch    | `poetry update`                                      |
| minor    | `poetry update`                                      |
| major    | edit specifiers in `pyproject.toml`, then `poetry lock` |

### Pipenv

| Tier     | Command                                                              |
|----------|----------------------------------------------------------------------|
| security | `pipenv check`; then targeted `pipenv update <pkg>` per advisory    |
| patch    | `pipenv update`                                                      |
| minor    | `pipenv update`                                                      |
| major    | edit version specifiers in `Pipfile`, then `pipenv lock`             |

`pipenv update` (without arguments) respects the version specifiers declared in `Pipfile`, so
patch and minor run the same command — the specifiers control the ceiling. `pipenv check` uses
PyUp's safety database; alternatively, run `pip-audit` against the locked set if `pipenv check`
is unavailable.

### pip + pinned `requirements.txt`

| Tier     | Command                                                    |
|----------|------------------------------------------------------------|
| security | `pip-audit --fix` (requires `pip-audit` installed)         |
| patch/minor/major | manual: diff `pip list --outdated` and edit pins  |

## Tooling bootstrap

If the user has uv lock files but no `uv` on PATH, offer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `pip-audit` is missing, offer `pipx install pip-audit`. Do not install silently.

## Fix phase

Default typecheck command:
- If `mypy.ini` / `[tool.mypy]` is configured → `mypy <package-dir>`.
- Else if `pyrightconfig.json` is present → `pyright`.
- Else skip the Fix phase (Python is dynamic; rely on the gate).

## Default format command

When `refresh` generates a new inventory entry for a Python subproject, detect the formatter
in this order and populate `format` accordingly:

1. `[tool.ruff.format]` in `pyproject.toml` → `ruff format .`
2. `[tool.black]` in `pyproject.toml` or `black` in dependencies → `black .`
3. Otherwise → omit `format` (leave field absent).

Do not install a formatter that is not already declared as a dependency.

## Recommendation (non-enforced)

If the subproject has only an unpinned `requirements.txt` and no lockfile at all, surface a
`notes` entry recommending migration to `uv` + `pyproject.toml` + `uv.lock` for proper
transitive resolution. Do not block; do not auto-migrate.

## Notes to surface in inventory

- Native extensions (numpy, pandas, lxml, cryptography) — bumps may pull new wheels with
  different glibc / OpenSSL requirements. Note the deployment target.
- Pinned tool versions in `[tool.*]` sections are not part of dependency resolution; bumping
  them needs a separate decision.
