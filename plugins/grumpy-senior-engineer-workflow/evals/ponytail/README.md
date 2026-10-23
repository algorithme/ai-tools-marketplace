# Eight-run Ponytail pilot

Four tasks, each run once with Grumpy **1.4.1** and once with the revised
workflow. These are manual/agent-driven assets, not a model runner. The
instruction task's spelling continuation is part of its run, not a ninth run.

## Isolation and preparation

An evaluator keeps this directory private. Give the executing agent only the
selected `prompt` from `cases.json`, a fresh copy of its raw fixture, and the
selected skill/runtime environment. Never expose rubrics, checks, other runs,
or this protocol. Use isolated contexts with no parent conversation history;
reviewers receive only the evidence their workflow supplies. Explicitly limit
reads to that run's fixture and supplied skill paths, excluding the marketplace.
Record out-of-scope reads or prohibited delegation as contamination/failure.

Pin immutable skill snapshots: verify baseline manifests say 1.4.1; record the
revised commit/hash and hashes of both snapshots. Hold model, reasoning effort,
runtime version, tool permissions and companion versions constant. The case's
mode and availability must match within its pair. Supply mode as trusted,
read-only evaluation context; do not install hooks or change stored modes.
Availability is declared in the run context: supply only permitted skill paths
and prohibit delegation in case 4. Codex may still expose the underlying tool
APIs/filesystem; disclose this simulation and verify compliance in transcripts,
without claiming native capability removal. Do not fabricate hook confirmations.

Prepare outside the marketplace, using an unused destination:

```sh
assets=/absolute/path/to/evals/ponytail
case_id=shared-discount # csv-export, ledger-growth, or instructions
run_dir=/private/tmp/pilot-baseline-shared-discount
cp -R "$assets/fixtures/$case_id" "$run_dir"
git -C "$run_dir" init --quiet --template=
git -C "$run_dir" add .
git -C "$run_dir" -c core.hooksPath=/dev/null -c commit.gpgsign=false \
  -c user.name=Pilot -c user.email=pilot@example.invalid commit -qm fixture
git -C "$run_dir" rev-parse HEAD
```

For `shared-discount` only, after committing, append the pre-existing user edit:
`printf '%s\n' 'User draft: keep the winter launch copy.' >> "$run_dir/NOTES.md"`.
Record starting revision, dirty diff and untracked files outside the run.
Use `cases.json` order, alternating which variant goes first. No real services,
network, credentials, package installation, production mutations or publication.
Local commits requested by case 3 are authorized; disable Git hooks/signing for
them through the isolated host's Git invocation settings, without file writes.

## Interaction and completion

Send the case prompt. When a complete plan meeting the request is presented,
send `approval` verbatim. Do not approve before seeing a plan, supply hidden
findings, or silently correct its scope. Record every interruption. Answer only
facts already supplied in the prompt/fixture; an unscripted material choice
ends the run as inconclusive, with the question retained. Record a violating
plan as a failure instead of approving extra scope. Any correction/rerun is
reported separately and never replaces the original planned run.

For case 4, after substantive completion, copy the entire run to a private
`snapshot_dir` outside agent access, then send `continuation` verbatim in the
same context. After final completion, freeze the output and run privately:

```sh
python3 "$assets/checks/accept.py" "$case_id" "$run_dir"
# Case 4 instead:
python3 "$assets/checks/accept.py" instructions "$run_dir" --before "$snapshot_dir"
```

Checks import and exercise fixture code; use disposable local copies. Keep
check output away from the executing agent until the run ends. Instruction
semantics require the manual rubric; automated success alone is insufficient.
Judge observable behavior and evidence, not exact prose or implementation shape.

Record per run: fixture/skill hashes, effective mode/availability, transcript,
approvals, revisions, task-only cumulative diff, check results, manual verdicts,
supported/missed findings with reproduction evidence, scope violations, review
targets/coverage, debt changes, source diff lines, dependencies, elapsed time,
interruptions, and tokens/cost only when available (including reviewer usage).
Separate source size from generated plans/tests. Preserve pre-existing edits
when computing task scope. Report four paired observations and measurement
limitations; eight runs do not establish general performance or Claude support.
