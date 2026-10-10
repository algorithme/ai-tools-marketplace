# ASCII diagram templates

Pick the view that answers the reader's question. Use a context/component
view for boundaries and responsibilities, then a behavioral or model view
only when it explains something else. Don't draw every shape out of habit.

| Shape | Use it when the plan... | Skip it when... |
|---|---|---|
| Context / component | ...needs to explain actors, system boundaries, or which component owns a responsibility | those relationships are already clear and unchanged |
| Sequence | ...adds or changes an interaction between components/services/actors over time | there's only one component involved |
| Class / component | ...introduces or reshapes data models and their relationships | no new model or structural relationship exists |
| State | ...adds a status field or lifecycle with real transitions | the "state" is just a boolean with no transition rules |

A diagram earns its place by showing something prose would take several
sentences to say precisely. If the change is "add a field," it usually
doesn't need one — say so in the plan and move on.
For a simple prose or link correction, explain why no diagram is needed
instead of drawing the edit.

## Context / component diagram

Use C4-inspired boundaries and responsibilities to orient the reader in
the affected area. Show the actors and external systems that matter to
the change; expand beyond that area only when the change crosses it.
This is an ASCII explanation, not a requirement for formal C4 compliance.

```text
[Customer]
    |
    | submit order
    v
+---------------- Shop service boundary -----------------+
| +-------------------+      +--------------------------+ |
| | Order API         | save | Order repository         | |
| | validates orders  |----->| stores order state       | |
| +-------------------+      +--------------------------+ |
+----------|---------------------------------------------+
           | authorize payment
           v
+--------------------+
| Payment provider   | (external system)
| authorizes payment |
+--------------------+
```

Conventions:
- Name the boundary and give each component a short responsibility.
- Label relationships with the action or data passed between them.
- Keep names and ownership consistent with the Models, Functions, and
  File tree sections; use sequence or state views for timing and lifecycle.

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
