# ASCII diagram templates

Three shapes cover almost every plan. Pick the one that matches what
actually needs explaining — don't draw all three out of habit.

| Shape | Use it when the plan... | Skip it when... |
|---|---|---|
| Sequence | ...adds or changes an interaction between components/services/actors over time | there's only one component involved |
| Class / component | ...introduces or reshapes data models and their relationships | no new model or structural relationship exists |
| State | ...adds a status field or lifecycle with real transitions | the "state" is just a boolean with no transition rules |

A diagram earns its place by showing something prose would take several
sentences to say precisely. If the change is "add a field," it usually
doesn't need one — say so in the plan and move on.

## Sequence diagram

Use for a new or changed interaction between two or more
participants — a request/response flow, an event publish, a retry path.

```
Client          API             Queue           Worker
  |               |               |               |
  |-- POST /x --->|               |               |
  |               |-- publish --->|               |
  |               |               |-- deliver ---->|
  |               |               |               |-- process
  |               |               |<-- ack --------|
  |<-- 202 -------|               |               |
```

Conventions:
- Vertical bars are lifelines, left to right in the order a reader
  would naturally follow the flow.
- `-->` for a request/call, label the arrow with what's actually sent
  (an endpoint, an event name), not a generic "calls."
- Show the failure/retry path only if it's the point of the change —
  don't clutter a diagram about a new field with error branches that
  aren't changing.

## Class / component diagram

Use when the plan introduces or changes a data model, or the
relationship between two or more models/components.

```
+------------------+          +------------------+
|      Order       |          |    OrderItem     |
+------------------+          +------------------+
| id: UUID         |<>------o | id: UUID         |
| tenant_id: UUID  |   1    * | order_id: UUID   |
| status: Status   |          | sku: str         |
+------------------+          | qty: int         |
                              +------------------+
```

Conventions:
- One box per model, fields that matter to the plan only — not every
  column that already exists and isn't changing.
- `<>------o` with multiplicities (`1`, `*`, `0..1`) for a
  composition/association; a plain `------` for a looser reference.
- For a component-level (not data-model) diagram, the same box shape
  works — put a component name and its main responsibility in the box
  instead of fields.

## State diagram

Use when the plan adds a status/lifecycle field with real transition
rules — not for a plain boolean flag.

```
[created] --pay--> [paid] --ship--> [shipped] --deliver--> [delivered]
    \
     \--cancel--> [cancelled]
```

Conventions:
- `[state]` in brackets, `--trigger-->` on the arrow naming what causes
  the transition (an action, an event) — not just "next."
- Terminal states (nothing transitions out) don't need special marking
  beyond having no outgoing arrow.
- Branch with a `\` continuation line rather than trying to force
  every transition onto one row.
