---
description: Get, set/reset, improve, or add a subproject to the minimal AI-agent context stored in .contexts/
argument-hint: <get|set|reset|improve|add-sub> [target] [details...]
---

Apply the rules in the `context` skill (`grumpy-senior-engineer-workflow:context`)
to the arguments below. If that skill isn't loaded yet, load it first — it is
the single source of truth for the `.contexts/` file layout, the 500-character
body limit, the instruction-file deduplication check, and each operation's
behavior. Do not reimplement those rules here; this command only parses
arguments and hands off to them.

Raw arguments: $ARGUMENTS

Parse them as `<operation> [target] [details...]`:

- **operation** — the first word. Accepts `get`/`show`/`retrieve`,
  `set`/`reset`, `improve`/`update`/`add`, or `add-sub`/`add-sub-context`/
  `add-subcontext`. If it's missing or unrecognized, ask the user which
  operation they meant instead of guessing.
- **target** — the second word, if it names an existing or intended
  subproject (matches a `.contexts/<name>.md` file, or the user is clearly
  naming a new subproject for `add-sub`). Defaults to the root project
  (`.contexts/index.md`) when omitted or when the second word is actually
  part of the details.
- **details** — everything after the operation and (optional) target: the
  free-text content to fold into the context for `set`/`reset`/`improve`/
  `add-sub`. Not required for `get`.

Then carry out the operation exactly as the `context` skill specifies,
including reading applicable `CLAUDE.md` and `AGENTS.md` instructions first
and verifying the 500-character limit before confirming the write.
