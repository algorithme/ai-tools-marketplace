#!/usr/bin/env bash
# PostToolUse hook — emits a one-line reminder when inventory.md or
# update-manager.constraints.yml is edited and a renovate.json5 already exists
# in the same directory. Never blocks (always exits 0).
set -euo pipefail

EVENT=$(cat)
FILE=$(printf '%s' "$EVENT" | jq -r '.tool_input.file_path // .tool_input.path // empty' 2>/dev/null) || true

[[ -z "$FILE" ]] && exit 0

BASE=$(basename "$FILE")
DIR=$(dirname "$FILE")

case "$BASE" in
  inventory.md|update-manager.constraints.yml) ;;
  *) exit 0 ;;
esac

if [[ -f "$DIR/renovate.json5" || -f "$DIR/.github/renovate.json5" ]]; then
  printf '\e[33m→ renovate.json5 may be stale after editing %s. Run /renovate-sync.\e[0m\n' "$BASE" >&2
fi

exit 0
