# 0004 — Documentation structure — modular files over monolithic guides

**Status**: Accepted

## Context

Plugin documentation could be organised in several ways:

1. **One large README** — all docs in `README.md`. Easy to start, hard to navigate as the project grows.
2. **Single `/docs` directory with flat files** — one file per topic (`getting-started.md`, `authoring.md`, etc.). Moderate discoverability.
3. **Nested `/docs` with a component-per-file authoring section** — `docs/authoring/skills.md`, `docs/authoring/hooks.md`, etc. Granular, searchable, cross-linkable.

## Decision

Use option 3: **nested `/docs` with component-level files**.

```
docs/
├── getting-started.md          ← user-facing install guide
├── authoring.md                ← overview + component matrix linking to deep dives
├── publishing.md               ← contributor workflow
├── troubleshooting.md          ← common errors
└── authoring/                  ← one file per component type
    ├── skills.md
    ├── commands.md
    ├── agents.md
    ├── hooks.md
    ├── mcp-servers.md
    ├── lsp-servers.md
    ├── output-styles.md
    ├── monitors.md
    ├── executables.md
    ├── user-config.md
    └── channels.md
```

No file should exceed ~150 lines. If a file grows beyond that, split it.

## Consequences

### Positive
- Each component type has a canonical URL for linking from `docs/authoring.md` and component-specific PRs.
- Short files are easy to review and maintain.
- New component types can be added without touching existing files.
- GitHub renders the `docs/authoring/` directory as a browsable index.

### Negative / trade-offs
- More files to create upfront.
- Contributors must know which file to edit — mitigated by the component matrix in `docs/authoring.md`.

### Neutral
- `README.md` at the repo root serves only as a public landing page and links into `docs/`. It does not duplicate content from `docs/`.
