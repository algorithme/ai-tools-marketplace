#!/usr/bin/env python3
"""Stateless Codex reminder and structural check; never grants user approval."""

import argparse
import json
import re
import sys

SECTIONS = (
    "Non-negotiables", "Decisions", "Models", "Functions", "Diagram",
    "File tree", "Tests", "Size check", "ADR check", "Documentation check",
)
TITLES = {title.casefold(): title for title in SECTIONS}
PLACEHOLDER = re.compile(r"(?:todo|tbd|none|n/a|\.{3}|…)[.!?]?", re.IGNORECASE)


def heading(line):
    value = re.sub(r"^\s{0,3}#{1,6}\s+", "", line.strip())
    value = re.sub(r"\s+#+$", "", value).strip("*_ ")
    value = re.sub(r"^\d+[.)]\s+", "", value).strip("*_ ")
    return TITLES.get(value.casefold())


def plan_errors(body):
    """Recognize section headings outside code; retain code as body content."""
    sections = []
    fence = None
    current = None
    level = None
    for line in body.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            elif current is not None:
                sections[current][1].append(line)
            continue
        if marker:
            fence = marker[1]
            continue
        title = heading(line)
        atx = re.match(r"^ {0,3}(#{1,6})\s+", line)
        if title:
            sections.append((title, []))
            current = len(sections) - 1
            level = len(atx[1]) if atx else None
        elif atx:
            if level is not None and len(atx[1]) <= level:
                current = None
        elif current is not None:
            sections[current][1].append(line)

    names = [title for title, _ in sections]
    missing = [title for title in SECTIONS if title not in names]
    duplicates = [title for title in SECTIONS if names.count(title) > 1]
    empty = []
    for title, lines in sections:
        content = [re.sub(r"^(?:[-+*]|\d+[.)])\s+(?:\[[ xX]\]\s*)?", "", line.strip())
                   .strip(" \t*_`#>-!") for line in lines]
        content = [line for line in content if line]
        if not content or all(PLACEHOLDER.fullmatch(line) for line in content):
            empty.append(title)
    errors = []
    for label, items in (("Missing", missing), ("Repeated", duplicates), ("Empty or placeholder", empty)):
        if items:
            errors.append(f"{label}: {', '.join(items)}")
    if [SECTIONS.index(name) for name in names] != sorted(SECTIONS.index(name) for name in names):
        errors.append("Sections must follow the canonical ten-section order")
    return errors


def plan_body(message):
    if not isinstance(message, str):
        return None
    lines = message.strip().splitlines()
    if len(lines) < 2 or lines[0].strip() != "<proposed_plan>" or lines[-1].strip() != "</proposed_plan>":
        return None
    fence = None
    for line in lines[1:-1]:
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
        elif re.fullmatch(r"\s*(?:</?proposed_plan>\s*)+", line):
            return None
    return "\n".join(lines[1:-1]) if fence is None else None


def dispatch(event):
    if not isinstance(event, dict):
        return {"systemMessage": "Grumpy: invalid hook input; structural check skipped."}
    if event.get("hook_event_name") == "UserPromptSubmit":
        return {"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                "For planning tasks, use Grumpy's plan skill: establish context and scope, "
                "include its ten canonical sections in one complete <proposed_plan> envelope, "
                "run the skill's --check-plan preflight before presenting the final plan, "
                "and await user approval before implementation. Stop is only a backstop; "
                "clarification replies stay ordinary messages. Passing the check is not approval."
            ),
        }}
    if event.get("hook_event_name") != "Stop" or event.get("stop_hook_active") is True:
        return {}
    body = plan_body(event.get("last_assistant_message"))
    if body is None:
        return {}
    errors = plan_errors(body)
    if not errors:
        return {}
    return {
        "decision": "block",
        "reason": "Grumpy plan structure: " + "; ".join(errors) + ". Return only the corrected "
                  "complete <proposed_plan> message, then await user approval. This check "
                  "does not evaluate plan quality or grant approval.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-plan", action="store_true", help="check a complete plan from stdin")
    if parser.parse_args().check_plan:
        body = plan_body(sys.stdin.read())
        errors = plan_errors(body) if body is not None else ["Expected exactly one complete <proposed_plan> envelope"]
        if errors:
            print("Grumpy plan structure: " + "; ".join(errors), file=sys.stderr)
            sys.exit(1)
        print("Grumpy plan structure OK; user approval is still required.")
        sys.exit(0)
    try:
        result = dispatch(json.load(sys.stdin))
    except (ValueError, UnicodeError):
        result = {"systemMessage": "Grumpy: invalid hook input; structural check skipped."}
    print(json.dumps(result))
