# Grumpy and Ponytail evaluation

The 2026-10-23 pilot compares Grumpy 1.4.1 with the 1.5.0 workflow on four
local tasks, once per variant. The [fixtures and protocol](../../../plugins/grumpy-senior-engineer-workflow/evals/ponytail/README.md)
include private acceptance checks and scripted approval continuations.

This release coordinates the local Ponytail skills. Upstream Ponytail's band,
board, transcript import, and scoreboard remain outside the update.

## Method and reproducibility

Baseline source is commit `5e13ceb0ea31bec4704dc399dfb1601dfeabdbe6`.
Both variants use the same frozen Ponytail 1.0.0 package, source fixture,
declared capabilities, and mode within each pair. Order alternates by task.
Every workflow starts in a fresh Codex agent context; approval and the spelling
continuation reuse that context. Grading criteria and checks remain with the
evaluator. Agents see only their fixture, task, and permitted skill sources.

Snapshot digests are SHA-256 of the sorted, compact JSON map of relative
file paths to SHA-256 content hashes:

| Snapshot | Digest |
|---|---|
| Grumpy 1.4.1 | `fff28f0d31ff794bebbfdf9d54d198134593902fd13ba3541738f811597c655d` |
| Grumpy 1.5.0 candidate | `e032cfca3be71bb518828d71007f7724d5f06b24faf60b00a685a78c4c89c8c2` |
| Ponytail 1.0.0 | `0f75e0da60c6ab148b7bfc038a7e419d3e0d639f8f6735a3032966514a998153` |

The candidate's shared workflow digest is
`dc470b8378401ab2f343fe25197982ef7c226ec3297c677250c2cda783b34dd8`.
Package snapshots exclude evaluation assets and Python caches. Later result
documentation does not change the instructions used by the pilot.

## Observations

All eight runs passed their task acceptance criteria, with no behavioral reruns.
The evaluator ran the private code checks against disposable output copies and
manually assessed the instruction semantics. Both spelling continuations passed
the exact before/after file comparison. The checker itself passed 12 controls:
original defects fail, corrected fixtures pass, and four deliberate regressions fail.

Line counts sum additions and deletions. Source/docs exclude generated tests,
saved plans, and the pre-existing user draft. Minutes are observed planning plus
implementation and continuation wall time, excluding the plan-approval gap;
they include reviewers and orchestration waits.

| Task | Variant | Outcome | Source/docs lines | Test lines | Saved plan lines | Minutes |
|---|---|---|---:|---:|---:|---:|
| Shared discount | Baseline | Pass | 4 | 71 | 75 | 6.6 |
| Shared discount | Revised | Pass | 4 | 90 | 93 | 9.9 |
| CSV export | Baseline | Pass | 45 | 93 | 91 | 6.5 |
| CSV export | Revised | Pass | 44 | 99 | 83 | 12.2 |
| Ledger growth | Baseline | Pass | 53 | 174 | 116 | 7.8 |
| Ledger growth | Revised | Pass | 64 | 168 | 115 | 14.1 |
| Instructions + spelling | Baseline | Pass | 46 | 0 | 0 | 5.7 |
| Instructions + spelling | Revised | Pass | 58 | 0 | 0 | 6.6 |

- **Shared discount:** both fixed the shared arithmetic and preserved both
  callers and the unrelated draft. The revised audit reproduced truncation,
  floating-point precision loss, and overflow; its independent challenge and
  review found no additional defects. Baseline tests also covered large integers.
- **CSV export:** both composed the settled query/renderer helpers and preserved
  filtering, ordering, escaping, empty headers, and CLI flags. The revised design
  challenge and completion review independently checked those same boundaries.
- **Ledger growth:** both produced the two requested commits and correct results.
  The revised run reviewed storage/summary before export work, then reviewed the
  original baseline through the first commit and all current changes. It verified
  that the truncation shortcut was resolved in code and tests while the existing
  recalculation trigger remained unchanged: two markers before, one after.
  Ponytail stayed off. Baseline used self-review at both milestones.
- **Instructions:** both produced coherent fallback and cumulative-review rules,
  disclosed same-agent review, and handled the later typo without new planning,
  tests, delegation, or approval. The revised wording explicitly retains or
  reconstructs the original baseline on resume. These were policy walkthroughs,
  not a live mixed-history instruction task.

The revised runs used three fresh design challengers and four fresh code
reviewers; baseline runs used self-review. No supported implementation-review
findings remained, and the evaluator found no missed defects within its checks.
All runs used one scripted plan approval and no extra questions. None added
dependencies. Retained evidence shows no scope or mode changes outside the task.
One baseline instruction command used a nonexistent workdir and failed before
execution; a corrected invocation succeeded with no unintended file changes.

This pilot demonstrates execution of the expanded workflow and more explicit
review/debt evidence. It does not demonstrate a correctness advantage. Revised
runs had longer observed elapsed times in all four pairs; keep extra stages
proportionate to the work rather than treating stage counts as quality scores.

Both skill validators and the full repository validator passed, including all
42 existing tests, JSON schemas, YAML frontmatter, and ShellCheck. These checks
are separate from the eight workflow outcomes above.

## Measurement limits

This is a small observational pilot, with one sample per task and variant.
Agents inherit the same model and reasoning configuration; the collaboration
API does not expose their exact identifiers or token/cost usage, including
reviewers. Independent task runs can overlap, so elapsed time is not a speed
benchmark. The installed Codex CLI is 0.163.0; runs use the collaboration API,
not a CLI runner. Local task tools are Python 3.15.0 and Node 26.12.1.

Mode and missing capabilities are supplied as trusted fixture context and
declared permissions. APIs and filesystem access are not natively removed.
Evidence consists of returned plans/handoffs, agent-recorded commands and review
reports, task diffs, and evaluator-run acceptance checks; it is not a complete
host audit log. This does not establish hook lifecycle or isolation enforcement.

Claude Code 2.1.309 package validation passes, but its CLI reports no signed-in
account here. A live Claude workflow was not exercised. Structural validation
and the existing hook tests are separate from these behavioral observations.
