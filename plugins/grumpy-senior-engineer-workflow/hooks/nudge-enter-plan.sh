#!/usr/bin/env bash
# nudge-enter-plan.sh
# PreToolUse hook on EnterPlanMode: reminds Claude to apply the `plan`
# skill's ten-section checklist before it starts drafting, rather than
# relying only on the skill's own description to get picked up. Never
# blocks — this is a nudge, not a gate (the ExitPlanMode hook is the
# gate) — so it always allows.

set -uo pipefail

cat <<'EOF'
{"hookSpecificOutput": {"permissionDecision": "allow"}, "systemMessage": "Before drafting: apply the grumpy-senior-engineer-workflow:plan skill's ten required sections (non-negotiables, decisions, models, functions, diagram, file tree, tests, size check, ADR check, documentation check). Load the skill now if it isn't already in context."}
EOF

exit 0