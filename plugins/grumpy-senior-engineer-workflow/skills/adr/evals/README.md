# ADR evaluations

`evals.json` describes the prompts, expected behavior, and assertions for
manual or agent-driven evaluation. This repository does not include an
evaluation runner; `scripts/validate.sh` does not execute these cases.

## Isolated repositories and fixtures

Run each independent case in a fresh, isolated repository, separate from
this marketplace checkout. Load the ADR skill from the plugin for a
with-skill run. A baseline run uses the same prompt and starting files
without loading the skill.

Resolve every `files` entry relative to this directory (`evals.json`'s
directory). Copy the listed files into the test repository, preserving
the paths after `fixtures/<case-name>/`. For eval 2, the resulting layout
must be:

```text
<test-repository>/docs/adr/
  INDEX.md
  0001-use-redis-for-idempotency-cache.md
```

Use identical fixture copies for with-skill and baseline runs. The fixture
contains one accepted Redis technology decision and no scheduled-report
decision. Do not depend on files produced by another eval or modify the
committed fixtures during a run.

Cases with an empty `files` list start without `docs/adr/`, except for the
continuations below. Keep captured responses and evaluation reports outside
the test repository so they cannot affect file-creation assertions.

## Approval continuations

Evals 0 and 1 present a draft and wait for approval, without writing files
or bootstrapping `docs/adr/`. Evals 4 and 5 continue the respective with-skill
conversation and repository from those first turns, preserving the actual
draft response before supplying the approval turn described in the prompt.
They are not standalone prompts and have no separate baseline arm.

Check each case's assertions against its captured response and resulting
repository. For eval 2, also confirm the fixture files remain unchanged.
