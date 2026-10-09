---
description: Create, read, list, audit, or transition Architecture Decision Records stored in docs/adr/
argument-hint: <new|show|list|audit|accept|implement|supersede|deprecate|bootstrap> [target] [details...]
---

Apply the rules in the `adr` skill (`grumpy-senior-engineer-workflow:adr`)
to the arguments below. If that skill isn't loaded yet, load it first — it
is the single source of truth for the `docs/adr/` file layout, the
capability/technology templates, the numbering rule, the approval gate
before anything is written, the status lifecycle, and the exact behavior
of each operation. Do not reimplement those rules here; this command only
parses arguments and hands off to them.

Raw arguments: $ARGUMENTS

Parse them as `<operation> [target] [details...]`:

- **operation** — the first word. Accepts `new`/`create`/`record`,
  `show`/`get`/`read`, `list`, `audit`/`lint`/`check`, `accept`,
  `implement`/`ship`, `supersede`, `deprecate`/`retire`, or
  `bootstrap`/`init`. If it's missing or unrecognized, ask the user which
  operation they meant instead of guessing.
- **target** — an ADR number or a title/keyword fragment, where relevant
  (`show`, `accept`, `implement`, `supersede`, `deprecate`). Not required
  for `new`, `list`, `audit`, or `bootstrap`.
- **details** — everything after operation and (optional) target: the
  decision content for `new`, the replacement rationale for `supersede`,
  the reason for `deprecate`, an optional status/tag filter for `list`.

Then carry out the operation exactly as the `adr` skill specifies,
including the approval gate before writing anything, re-scanning for the
next number immediately before writing (never earlier), and regenerating
`docs/adr/INDEX.md` after any operation that changes it.
