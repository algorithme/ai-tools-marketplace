#!/usr/bin/env bash
# load-adr-pointer.sh
# SessionStart hook: if docs/adr/INDEX.md exists, prints a one-line
# pointer (not the full index — unlike .contexts/ it has no size cap and
# can grow past what's worth spending every session's tokens on).
# Missing or unreadable docs/adr/ must never block a session, so this
# always exits 0.

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
INDEX_FILE="$PROJECT_DIR/docs/adr/INDEX.md"

if [[ -f "$INDEX_FILE" ]]; then
  COUNT=$(grep -cE '^\| *[0-9]{4} *\|' "$INDEX_FILE" 2>/dev/null || echo 0)
  echo "## Architecture Decision Records"
  echo "$COUNT ADR(s) recorded in docs/adr/INDEX.md — check it before making or reversing an architectural decision."
fi

exit 0
