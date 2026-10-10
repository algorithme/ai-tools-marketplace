"""Validate local Codex package paths, identities, and optional command hooks."""

import argparse
import json
import shlex
import sys
from pathlib import Path

EVENTS = {"SessionStart", "SessionEnd", "UserPromptSubmit", "Stop", "Interrupt",
          "PreToolUse", "PostToolUse", "PermissionRequest", "PreCompact",
          "PostCompact", "SubagentStart", "SubagentStop"}


def local_path(plugin, value):
    if not isinstance(value, str) or not value.startswith("./"):
        raise ValueError(f"expected a ./-prefixed package path: {value!r}")
    target = (plugin / value).resolve()
    if plugin not in target.parents or not target.exists():
        raise ValueError(f"missing path or path outside plugin: {value}")
    return target


def validate_codex_plugins(root):
    """Return diagnostics for each invalid package under the marketplace root."""
    root = Path(root).resolve()
    errors = []
    for manifest in sorted((root / "plugins").glob("*/.codex-plugin/plugin.json")):
        try:
            plugin = manifest.parent.parent.resolve()
            data = json.loads(manifest.read_text())
            claude = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
            if any(data.get(key) != claude.get(key) for key in ("name", "version")):
                raise ValueError("Claude and Codex names/versions differ")
            if not local_path(plugin, data["skills"]).is_dir():
                raise ValueError("skills must reference a directory")
            default_hooks = plugin / "hooks/hooks.json"
            if "hooks" in data:
                hook_path = local_path(plugin, data["hooks"])
            elif default_hooks.exists() or default_hooks.is_symlink():
                hook_path = local_path(plugin, "./hooks/hooks.json")
            else:
                continue
            hooks = json.loads(hook_path.read_text())["hooks"]
            if not isinstance(hooks, dict) or not hooks:
                raise ValueError("hooks must be a nonempty event map")
            for event, groups in hooks.items():
                if event not in EVENTS or not isinstance(groups, list) or not groups:
                    raise ValueError(f"unsupported event or invalid groups: {event}")
                for group in groups:
                    handlers = group["hooks"]
                    if not isinstance(handlers, list) or not handlers:
                        raise ValueError(f"empty or invalid handlers: {event}")
                    for handler in handlers:
                        if handler["type"] != "command":
                            raise ValueError(f"Codex package requires command hooks: {event}")
                        if not isinstance(handler["command"], str):
                            raise ValueError(f"invalid hook command: {event}")
                        tokens = shlex.split(handler["command"])
                        if not tokens:
                            raise ValueError(f"empty hook command: {event}")
                        for token in tokens:
                            for variable in ("${PLUGIN_ROOT}", "${CLAUDE_PLUGIN_ROOT}"):
                                if token.startswith(variable + "/"):
                                    local_path(plugin, "." + token[len(variable):])
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{manifest.relative_to(root)}: {exc}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="marketplace repository root")
    errors = validate_codex_plugins(parser.parse_args().root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())
