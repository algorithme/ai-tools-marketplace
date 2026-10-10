# Changelog

## [1.4.1] - 2026-10-10

- Ground plans in the affected project's structure, terminology, and success criteria.
- Clarify user ownership of design choices and define relevant models before operations,
  adding contracts where they resolve ambiguity.
- Add ASCII context/component guidance and a final consistency review connecting
  models, operations, diagrams, files, and confidence checks.
- Follow repository ADR paths and diff limits; preserve the ten-section format,
  runtime hooks, structural preflight, and explicit approval.

## [1.4.0] - 2026-10-09

- Add a Codex manifest and command-only hooks alongside the existing Claude hooks.
- Share context, ADR, plan, and implementation skills across both runtimes,
  preserving user approval and existing stored formats.
- Add a Codex planning reminder and agent-run ten-section preflight, with
  a Stop-hook correction when final text is available. Document native Plan
  Mode's missing-text limitation, preflight responsibility, and hook review.
- Load startup context from the project root even from nested directories;
  tolerate unreadable indexes and count linked ADR identifiers.
- Validate both manifest formats and add executable hook regression tests.

## [1.3.0] - 2026-10-09

- Import the supplied Grumpy 1.3.0 archive, including its four skills, four
  commands, lifecycle hooks, ADR templates and evaluations, and diagram reference.
- Adapt repository, contact, and installation references for `olivier-vault`.
- Quote hook command paths to support plugin installations in directories with spaces.
- Document the pending `fastapi-resilience` companion skill and its follow-up.

The source version remains 1.3.0 for this initial marketplace import.
