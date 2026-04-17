# Contributing

Contributions are welcome. This document covers how to add a plugin, validate your changes, and open a pull request.

## Prerequisites

Install the validation tools used by `scripts/validate.sh`:

```bash
# JSON syntax and Schema
brew install jq
npm install -g ajv-cli ajv-formats

# YAML frontmatter
pip install yq

# Shell safety
brew install shellcheck    # macOS
sudo apt install shellcheck  # Ubuntu/Debian
```

## Adding a plugin

1. **Copy the template**:

   ```bash
   cp -r templates/plugin-template plugins/<your-plugin-name>
   ```

   Plugin names must be **kebab-case** (lowercase letters, digits, hyphens — no spaces or uppercase).

2. **Author your components**. See [docs/authoring.md](./docs/authoring.md) for the full guide.

3. **Set the version** in `.claude-plugin/plugin.json` (`1.0.0` for a new plugin).

4. **Run validation**:

   ```bash
   ./scripts/validate.sh
   ```

5. **Add the catalog entry** in `.claude-plugin/marketplace.json`:

   ```json
   { "name": "your-plugin", "source": "your-plugin", "description": "…" }
   ```

6. **Open a pull request**. The PR template checklist guides you through the final steps.

See [docs/publishing.md](./docs/publishing.md) for the full workflow including version bumps.

## Modifying an existing plugin

1. Make your changes.
2. Bump the `version` in `plugin.json` (otherwise existing users will not receive the update).
3. Add a changelog entry in `CHANGELOG.md` inside the plugin directory.
4. Run `./scripts/validate.sh`.
5. Open a PR.

## Pull request rules

- **PR diff under 1 000 lines** (soft cap — discuss in the issue if you need more).
- **`./scripts/validate.sh` must pass** before requesting review.
- **One plugin per PR** for new plugins; cross-plugin changes are allowed for infrastructure.
- **If you introduce an architectural decision**, add an ADR in `adr/` using the template in `adr/README.md`.

## Commit style

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat(plugin-name): add /my-skill skill
fix(plugin-name): correct hook event name
docs: update authoring guide for agents
chore: bump validate.sh shellcheck dependency
```

## Validation locally

```bash
# Full validation (same as CI)
./scripts/validate.sh

# Quick JSON syntax check
jq . .claude-plugin/marketplace.json

# Test the marketplace locally in Claude Code
claude plugin marketplace add ./
claude plugin marketplace list
claude plugin marketplace remove olivier-vault
```

## ADRs

Significant architectural decisions (new component type support, changes to validation strategy, layout changes) require an ADR. Copy the template from `adr/README.md` and follow the numbering sequence.
