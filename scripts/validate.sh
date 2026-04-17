#!/usr/bin/env bash
# scripts/validate.sh — validation authority for the olivier-vault marketplace
#
# Checks:  1. JSON syntax (jq)
#          2. JSON Schema (ajv-cli)     — requires: npm install -g ajv-cli ajv-formats
#          3. YAML frontmatter (yq)    — requires: pip install yq
#          4. Shell script safety      — requires: shellcheck
#          5. Kebab-case plugin names
#          6. Claude plugin validate   — best-effort (requires claude CLI)
#
# Exit codes: 0 = all blocking checks passed, 1 = at least one check failed.
# See adr/0003-validation-and-ci.md for rationale.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

red()    { printf '\033[0;31m%s\033[0m\n' "$*"; }
green()  { printf '\033[0;32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[0;33m%s\033[0m\n' "$*"; }
info()   { printf '  %s\n' "$*"; }

fail() { red "FAIL: $*"; ERRORS=$((ERRORS + 1)); }
pass() { green "PASS: $*"; }
warn() { yellow "WARN: $*"; }

echo ""
echo "=== Validate olivier-vault marketplace ==="
echo ""

# ──────────────────────────────────────────────────────────────────────────────
# 1. JSON syntax — marketplace.json
# ──────────────────────────────────────────────────────────────────────────────
echo "── 1. JSON syntax ──"
CATALOG="$ROOT/.claude-plugin/marketplace.json"
if jq empty "$CATALOG" 2>/dev/null; then
  pass "marketplace.json parses as valid JSON"
else
  fail "marketplace.json has JSON syntax errors"
fi

# plugin.json files
find "$ROOT/plugins" -name "plugin.json" 2>/dev/null | while read -r f; do
  if jq empty "$f" 2>/dev/null; then
    pass "$(basename "$(dirname "$(dirname "$f")")")/plugin.json — valid JSON"
  else
    fail "$f — JSON syntax error"
  fi
done

# ──────────────────────────────────────────────────────────────────────────────
# 2. JSON Schema validation (ajv-cli)
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "── 2. JSON Schema ──"
if command -v ajv > /dev/null 2>&1; then
  if ajv validate \
      --spec=draft7 \
      -s "$ROOT/schemas/marketplace.schema.json" \
      -d "$CATALOG" \
      --errors=text 2>&1; then
    pass "marketplace.json matches schema"
  else
    fail "marketplace.json schema validation failed"
  fi

  find "$ROOT/plugins" -name "plugin.json" 2>/dev/null | while read -r f; do
    PLUGIN_DIR="$(dirname "$(dirname "$f")")"
    NAME="$(basename "$PLUGIN_DIR")"
    if ajv validate \
        --spec=draft7 \
        -s "$ROOT/schemas/plugin.schema.json" \
        -d "$f" \
        --errors=text 2>&1; then
      pass "$NAME/plugin.json matches schema"
    else
      fail "$NAME/plugin.json schema validation failed"
    fi
  done
else
  warn "ajv not found — skipping schema validation (run: npm install -g ajv-cli ajv-formats)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# 3. YAML frontmatter in SKILL.md / agents / commands
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "── 3. YAML frontmatter ──"
if command -v yq > /dev/null 2>&1; then
  while IFS= read -r -d '' md; do
    # Extract frontmatter between the first pair of --- delimiters
    FRONT=$(awk '/^---/{f++; if(f==2) exit; next} f==1' "$md")
    if [ -n "$FRONT" ]; then
      if echo "$FRONT" | yq '.' > /dev/null 2>&1; then
        pass "$(realpath --relative-to="$ROOT" "$md") — frontmatter OK"
      else
        fail "$(realpath --relative-to="$ROOT" "$md") — invalid YAML frontmatter"
      fi
    fi
  done < <(find "$ROOT/plugins" \( -name "SKILL.md" -o -name "*.md" -path "*/agents/*" -o -name "*.md" -path "*/commands/*" \) -print0 2>/dev/null)
else
  warn "yq not found — skipping frontmatter validation (run: pip install yq)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# 4. Shellcheck on scripts and plugin bin/ files
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "── 4. Shell safety (shellcheck) ──"
if command -v shellcheck > /dev/null 2>&1; then
  SHELL_FILES=$(find "$ROOT/scripts" "$ROOT/plugins" -type f \( -name "*.sh" -o -perm -111 \) 2>/dev/null | grep -v ".git")
  if [ -z "$SHELL_FILES" ]; then
    info "No shell scripts found"
  else
    while IFS= read -r sh; do
      # Only check files with a shell shebang or .sh extension
      if head -1 "$sh" | grep -qE "^#!.*(bash|sh|zsh)" || [[ "$sh" == *.sh ]]; then
        if shellcheck "$sh"; then
          pass "$(realpath --relative-to="$ROOT" "$sh")"
        else
          fail "$(realpath --relative-to="$ROOT" "$sh") — shellcheck errors"
        fi
      fi
    done <<< "$SHELL_FILES"
  fi
else
  warn "shellcheck not found — skipping (run: brew install shellcheck or apt install shellcheck)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# 5. Kebab-case plugin directory names
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "── 5. Plugin name conventions ──"
if [ -d "$ROOT/plugins" ]; then
  found_plugins=0
  while IFS= read -r -d '' dir; do
    [ -d "$dir" ] || continue
    name="$(basename "$dir")"
    found_plugins=1
    if echo "$name" | grep -qE '^[a-z0-9][a-z0-9-]*[a-z0-9]$'; then
      pass "$name — kebab-case OK"
    else
      fail "$name — plugin directory must be kebab-case (lowercase, hyphens only)"
    fi
  done < <(find "$ROOT/plugins" -mindepth 1 -maxdepth 1 -type d -print0 2>/dev/null)
  [ "$found_plugins" -eq 0 ] && info "No plugin directories found (plugins: [] is expected for scaffold)"
else
  info "plugins/ directory not found — skipping"
fi

# ──────────────────────────────────────────────────────────────────────────────
# 6. claude plugin validate (best-effort)
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "── 6. claude plugin validate (best-effort) ──"
if command -v claude > /dev/null 2>&1; then
  if claude plugin validate "$ROOT"; then
    pass "claude plugin validate passed"
  else
    warn "claude plugin validate reported issues (non-blocking)"
  fi
else
  warn "claude CLI not found — skipping (install @anthropic-ai/claude-code to run)"
fi

# ──────────────────────────────────────────────────────────────────────────────
# Result
# ──────────────────────────────────────────────────────────────────────────────
echo ""
if [ "$ERRORS" -eq 0 ]; then
  green "All checks passed."
  exit 0
else
  red "$ERRORS check(s) failed."
  exit 1
fi
