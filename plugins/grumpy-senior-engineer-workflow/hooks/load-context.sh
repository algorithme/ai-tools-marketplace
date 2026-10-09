#!/usr/bin/env bash
# load-context.sh
# SessionStart hook: prints .contexts/index.md (if present) so it becomes
# part of the session context. Missing or unreadable .contexts/ must never
# block a session, so this always exits 0.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
INDEX_FILE="$PROJECT_DIR/.contexts/index.md"

if [[ -f "$INDEX_FILE" ]]; then
  echo "## Project context (from .contexts/index.md)"
  echo
  cat "$INDEX_FILE"
fi

exit 0
