# Ponytail throughout Grumpy's workflow

Grumpy owns scope, approval, implementation, and completion review. Ponytail
supplies coding guidance and read-only audit, review, and debt reports. These
instructions coordinate skills; they add no commands, hooks, or persistent state.

## Availability, mode, and proportion

Discover each companion through the host's available skills and read it before
use. Do not assume a sibling install path, install a missing plugin, or invent
its instructions. If absent, perform the applicable scoped inspection/review
using Grumpy and repository guidance and disclose the limitation once.

The latest `PONYTAIL MODE:` context governs persona guidance. Never switch
modes or write mode/default files. Off retires the persona; missing context
does not imply full mode. Apply Ponytail's coding guidance only when active or
explicitly requested by the user for this task. An agent's automatic handoff
is not user authorization to reactivate the persona. Audit, review, and debt
are separate one-shot reports and remain available while off. Grumpy's own
design checks continue. Pass the effective mode, including unknown, to reviewers.

Substantial changes involving contracts, persistence, authorization, concurrency,
dependencies, or cooperating modules receive scoped audit and design challenge.
Treat substantive skill instructions as behavior. Small isolated fixes can use
ordinary inspection and one completion review. Spelling/formatting changes need
only proportionate checks. Do not manufacture stages or reopen settled choices.

## Explicit scope and handoffs

Before edits, record the starting revision and relevant pre-existing staged,
unstaged, and untracked work in the conversation. For non-Git work use the
starting file contents. Inspect relevant callers, tests, configuration, and
contracts. Preserve unrelated user changes, including changes in touched files.

Pass every operation an explicit scope: affected paths and connected contracts,
the starting state, current target/diff including new files, and exclusions.
Never use audit's whole-repository default or review's last-commit default for
a bounded task. Cumulative review includes all task commits and uncommitted work.
If attribution is ambiguous, clarify it before editing or claiming full coverage.

Use a fresh read-only agent for substantial design challenges and code reviews
when delegation is supported and permitted. Otherwise perform and disclose a
same-agent review; do not call it independent. Provide the request, settled
constraints, plan, source references, actual test results, and known limits.
Omit the author's deliberation and suggested findings. Reviewers read connected
source, return evidence and recommendations, and make no edits, saved reports,
mode changes, external posts, or further delegations. Pause edits to their target
while they review; subsequent changes require coverage before a completion claim.

## Planning: evidence before decisions

1. Establish context and scope. For substantial work, use `ponytail-audit` on
   the affected area. The coordinator separates task prerequisites from unrelated
   findings; an audit does not authorize cleanup or expand the user's request.
2. Inspect relevant deliberate deferrals with `ponytail-debt`, or repository
   guidance when unavailable. Include the repository's documented shortcut
   markers in the requested search; supplement the companion scan if needed.
   Preserve the stated limit and revisit trigger; flag absent triggers without
   inventing owners, deadlines, or requirements.
3. Draft a complete candidate design, then request one independent challenge.
   Use applicable `ponytail` guidance to seek incomplete success criteria,
   contradictory contracts, and a smaller complete alternative. This is a
   Grumpy operation, not a plan-review API provided by `ponytail-review`.
4. Validate the challenge's evidence. Resolve ordinary drafting corrections;
   bring material alternatives to the user under Grumpy's Decisions rule.
   Keep audit evidence in Non-negotiables, decisions in Decisions, affected
   limitations with Models/Functions, and justified review checkpoints in Tests.
   Each checkpoint names its boundary, scope, and verification. A single-stage
   change normally needs only completion review. Do not add an eleventh section.
5. Reconcile the plan, run its runtime preflight, and await explicit approval
   before saving or implementing. A challenger or successful check is not consent.

## Implementation: checkpoints and corrections

Revalidate evidence against the actual starting state. Refresh the scoped audit
or debt baseline only when relevant source or assumptions changed, including on
resume; do not repeat broad audits merely because a session resumed. If baseline
evidence was lost, reconstruct it from the starting source or disclose the gap.

Build the approved milestone and run its targeted checks. At a named review
checkpoint use `ponytail-review` when available, otherwise Grumpy/repository
review. Review changed contracts before dependent work; avoid a review per file
or commit. Reports use evidence-backed Must fix / Should fix / Nice to have
findings, omitting empty groups. A failed or unavailable reviewer is not a clean
verdict: use the disclosed same-agent fallback if possible, otherwise report
the coverage gap. Do not mark a required review complete without performing it.

The implementing agent validates each finding and fixes defects within existing
authorization. Routine internal simplifications follow the existing deviation
rules. Material scope/design changes return to the user; unrelated improvements
remain outside the task. Run affected checks after corrections and allow one
targeted reviewer follow-up per checkpoint. Do not loop full reviews until a
clean verdict. Remaining material issues are blockers to report or decisions
to resolve, not permission to waive correctness or claim completion.

## Completion and documented debt

Review the cumulative task change after verification. The final milestone review
also satisfies completion if it covers that complete target; do not duplicate it.
Report who reviewed, exact coverage, fallbacks, verified fixes, actual checks,
remaining findings, and material unchecked paths. Small tasks need short reports.

Compare documented deferrals using the same affected scope and marker
conventions before and after work, including repository-specific markers.
Distinguish added, changed, resolved, and material unchanged limitations; account
for moved comments. Verify the limitation in code before calling it resolved:
marker deletion alone is not proof. Highlight exceeded limits and `no-trigger`
items. This measures documented shortcuts, not all technical debt. A shortcut
never excuses a defect. For an accepted new limitation use the project's marker,
or `shortcut: <limit>, <when to revisit>` when it has none.

Keep snapshots in the conversation and relevant approved-plan evidence; report
the material delta in the handoff. Persist a separate ledger only when the user
requests it. No findings means no manufactured debt or boilerplate warning.
