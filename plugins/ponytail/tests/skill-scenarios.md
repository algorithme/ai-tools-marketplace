# Ponytail behavioral scenarios

Run each prompt in a fresh isolated temporary fixture. Supply only the named
skill, prompt, and raw fixture; keep acceptance criteria out of the evaluator's
context. Record the response and resulting diff. Never use a real service,
credential, or private project. The hook suite tests deterministic state;
these scenarios exercise how an agent uses the prose guidance.

| Skill | Request and fixture | Acceptance |
|---|---|---|
| ponytail | Add case-insensitive matching to a small search function; explicitly preserve existing substring matching and result order. | Implements all requested behavior and checks it; no unrelated rewrite. |
| ponytail | Latest hook context says off; user asks for an explanation of a named function. | Explains it without activating modes, editing configuration, or imposing the persona. |
| ponytail-review | Review a small authorization check whose bypass is marked `shortcut:`. | Reports the concrete bypass with evidence; makes no edits. |
| ponytail-audit | Audit the folder containing that authorization check and its caller. | Traces and reports the defect without treating the comment as a waiver; makes no edits. |
| ponytail-debt | List deferrals, including a comment without a revisit trigger and prose about keyboard shortcuts. | Lists only genuine deferrals, identifies the absent trigger, writes nothing. |
| ponytail-debt | Use a literal marker containing shell punctuation. | Searches safely without executing the marker. |
| ponytail-help | Explain switching modes and using reports while off. | Describes only this edition's features, changes nothing, and does not claim hook trust or installation. |

Report observed behavior, not a pass based on matching the skill's wording.
