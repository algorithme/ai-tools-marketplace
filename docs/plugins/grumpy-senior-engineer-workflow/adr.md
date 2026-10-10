# Architecture decisions

[Plugin overview](../../../plugins/grumpy-senior-engineer-workflow/README.md)

`grumpy-senior-engineer-workflow` also maintains `docs/adr/` at the
project root:

```text
project_root/docs/adr/
  INDEX.md                 # generated — never hand-edit
  templates/
    capability-adr.md
    technology-adr.md
  0001-<slug>.md
  0002-<slug>.md
```

Every ADR is drafted, presented, and only written to disk once approved —
nothing is created on a hunch. Each one carries a TL;DR (for humans
skimming the index) and an Agent guidance field (a direct instruction for
what an agent should do differently because the decision exists), on top
of the usual Context/Decision/Consequences shape. Decisions move through a
status lifecycle as they mature:

```text
proposed -> accepted -> implemented -> superseded
                     \-> deprecated       (from any non-terminal state)
```

Nine operations, available through Claude's slash command or the shared skill
in either runtime:

| Operation | Effect |
| --- | --- |
| `new` | Draft and, on approval, record a new ADR |
| `show` | Read a past decision by number or keyword |
| `list` | Print the index, optionally filtered |
| `accept` | `proposed` -> `accepted` |
| `implement` | `accepted` -> `implemented` |
| `supersede` | Draft a replacement ADR and link it to the one it replaces |
| `deprecate` | Retire an ADR with no successor |
| `audit` | Lint numbering, index sync, and status consistency |
| `bootstrap` | Scaffold `docs/adr/` in a repo that doesn't have it yet |

A `SessionStart` hook prints a one-line pointer ("N ADRs recorded, see
docs/adr/INDEX.md") when the index exists, rather than the full index —
unlike `.contexts/`, it has no size cap and can grow past what's worth
loading into every session. Hooks must be enabled and, in Codex, reviewed.
The reader counts plain or linked four-digit ADR IDs; unreadable indexes do
not block startup.

## Usage

Claude command examples (Codex uses skill selection or natural language):

```text
/grumpy-senior-engineer-workflow:grumpy-adr new we decided to use Postgres instead of Mongo for billing, we need cross-table transactions
/grumpy-senior-engineer-workflow:grumpy-adr show 0004
/grumpy-senior-engineer-workflow:grumpy-adr supersede 0004 moving billing to CockroachDB for multi-region writes
/grumpy-senior-engineer-workflow:grumpy-adr audit
```

It also triggers from plain language — "why did we choose Postgres for
billing?" or "let's record this decision" work without the slash command.

## How It Works

- **[`skills/adr/SKILL.md`](../../../plugins/grumpy-senior-engineer-workflow/skills/adr/SKILL.md)** is the single source of truth for the ADR
  lifecycle: templates, numbering, the approval gate, the status machine,
  and the audit checks. Its `assets/templates/` holds the actual
  capability/technology templates and the empty `INDEX.md` shape used by
  `bootstrap`.
- **[`commands/grumpy-adr.md`](../../../plugins/grumpy-senior-engineer-workflow/commands/grumpy-adr.md)** is a thin dispatcher for the explicit
  `/grumpy-senior-engineer-workflow:grumpy-adr` command, same pattern as
  [`commands/grumpy-context.md`](../../../plugins/grumpy-senior-engineer-workflow/commands/grumpy-context.md).
- **[`hooks/load-adr-pointer.sh`](../../../plugins/grumpy-senior-engineer-workflow/hooks/load-adr-pointer.sh)** runs on `SessionStart` and prints a
  one-line pointer to `docs/adr/INDEX.md` when it exists.
