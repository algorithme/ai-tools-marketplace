# Node playbook

Project-agnostic guidance for Node/JavaScript/TypeScript subprojects.

## Discovery

A Node subproject is any directory containing a `package.json`. The lockfile present in that
directory selects the **package manager**:

| Lockfile             | Manager          |
|----------------------|------------------|
| `package-lock.json`  | npm              |
| `yarn.lock`          | yarn (classic or berry — see below) |
| `pnpm-lock.yaml`     | pnpm             |
| `bun.lockb` / `bun.lock` | bun          |
| (none)               | undetermined — surface a `note` recommending the user pick one |

Distinguish yarn classic from berry by reading `package.json`'s `"packageManager"` field
(e.g. `"yarn@4.x"` → berry) or the presence of `.yarnrc.yml`.

## Workspaces

- npm / yarn / bun: `package.json` `workspaces` field (array or `{packages: [...]}`).
- pnpm: `pnpm-workspace.yaml`.

When workspaces are detected, prefer landing bumps in the **root** `package.json` for any dep
that is declared there. Per-package manifests are touched only for deps unique to that package.

## Tier mapping

### npm

| Tier     | Command                                                                  |
|----------|--------------------------------------------------------------------------|
| security | `npm audit fix` (never `--force` automatically)                          |
| patch    | `npm update`                                                             |
| minor    | `npx npm-check-updates -u --target minor && npm install`                 |
| major    | `npx npm-check-updates -u --target latest && npm install`                |

### yarn (classic)

| Tier     | Command                                                                  |
|----------|--------------------------------------------------------------------------|
| security | `yarn audit` then per advisory: `yarn upgrade <pkg>@<fixed-ver>`         |
| patch    | `yarn upgrade`                                                           |
| minor    | `npx npm-check-updates -u --target minor && yarn install`                |
| major    | `npx npm-check-updates -u --target latest && yarn install`               |

`yarn upgrade` (without `--latest`) respects declared ranges in `package.json`, making it safe
as a patch-tier command.

### yarn (berry)

Yarn berry has no native command that upgrades within declared ranges. Use `npm-check-updates`
for all tier-controlled bumps.

| Tier     | Command                                                                  |
|----------|--------------------------------------------------------------------------|
| security | `yarn npm audit` then targeted `yarn up <pkg>@<fixed-ver>`               |
| patch    | `npx npm-check-updates -u --target patch && yarn install`                |
| minor    | `npx npm-check-updates -u --target minor && yarn install`                |
| major    | `npx npm-check-updates -u --target latest && yarn install`               |

### pnpm

| Tier     | Command                                                                  |
|----------|--------------------------------------------------------------------------|
| security | `pnpm audit --fix`                                                       |
| patch    | `pnpm update`                                                            |
| minor    | `npx npm-check-updates -u --target minor && pnpm install`                |
| major    | `npx npm-check-updates -u --target latest && pnpm install`               |

`pnpm audit --fix` requires pnpm ≥ 9. If the host project pins an older version via
`packageManager` in `package.json` or `.tool-versions`, fall back to running `pnpm audit`
(read-only) and applying targeted `pnpm update <pkg>@<fixed-ver>` per advisory.

### bun

| Tier     | Command                                                                  |
|----------|--------------------------------------------------------------------------|
| security | skill: run `bun audit` (Bun ≥ 1.2.15), parse JSON output, apply targeted `bun update <pkg>@<fixed>` per advisory — `bun audit fix` does not exist |
| patch    | `bun update`                                                             |
| minor    | `npx npm-check-updates -u --target minor && bun install`                 |
| major    | `npx npm-check-updates -u --target latest && bun install`                |

## Default format command

When `refresh` generates a new inventory entry for a Node subproject, detect the formatter
in this order and populate `format` accordingly:

1. `package.json` defines a `format` script → `<manager> run format`
2. `.prettierrc`, `.prettierrc.js`, `.prettierrc.json`, or `prettier.config.*` exists →
   `npx prettier --write .`
3. Otherwise → omit `format` (leave field absent).

Do not install Prettier globally. Always invoke via `npx` if not already in `devDependencies`.

## Tooling bootstrap

Prefer `npx npm-check-updates` (no global install). Only suggest a global install
(`npm i -g npm-check-updates`) if the user explicitly opts in.

## Fix phase

Default typecheck command, in order of preference:
1. If `package.json` defines a `typecheck` script → `<manager> run typecheck`.
2. Else if `tsconfig.json` is present → `npx tsc --noEmit`.
3. Else if `package.json` defines a `build` script → `<manager> run build`.
4. Else skip.

## Engine pins

After the bump set is computed, inspect each package's `engines.node` requirement against the
host project's pinned Node version (root `engines.node`, `.nvmrc`, or `.node-version`). If any
bump raises the floor past the pinned version, do **not** apply it silently — surface as a
`note` and require user confirmation via `AskUserQuestion`.

## Peer dependencies

After `<manager> install`, capture peer-dep warnings emitted to stderr. Do not auto-resolve:
list any unresolved peers in the PR body under a "Peer dependency warnings" section so a human
decides.

## Notes to surface in inventory

- Monorepo tools that maintain their own version pins — Turborepo, Nx, Lerna, Changesets. Flag
  bumps that touch their config (`turbo.json`, `nx.json`, `lerna.json`, `.changeset/config.json`)
  so the user reviews them.
- React / Next.js / framework-of-the-month majors usually need codemods — note the codemod
  command (`npx @next/codemod`, `npx react-codemod`, etc.).
