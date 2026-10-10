#!/usr/bin/env bash
# load-context.sh
# SessionStart hook: prints .contexts/index.md (if present) so it becomes
# part of the session context. Missing or unreadable .contexts/ must never
# block a session, so this always exits 0.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
INDEX_FILE="$PROJECT_DIR/.contexts/index.md"

if [[ -f "$INDEX_FILE" && -r "$INDEX_FILE" ]] && CONTENT=$(cat "$INDEX_FILE" 2>/dev/null); then
  echo "## Project context (from .contexts/index.md)"
  echo
  printf '%s\n' "$CONTENT"
fi

exit 0
