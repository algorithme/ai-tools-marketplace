import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "validate_codex_plugins", Path(__file__).resolve().parents[1] / "validate_codex_plugins.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CodexPackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.plugin = self.root / "plugins/example"
        self.manifest = self.plugin / ".codex-plugin/plugin.json"
        self.data = {"name": "example", "version": "1.0.0", "skills": "./skills/"}
        (self.plugin / "skills").mkdir(parents=True)
        (self.root / "outside").mkdir()
        self.write(self.plugin / ".claude-plugin/plugin.json", self.data)
        self.write(self.manifest, self.data)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def hooks(self, command="true"):
        return {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": command}]}]}}

    def check(self, valid):
        errors = VALIDATOR.validate_codex_plugins(self.root)
        if valid:
            self.assertEqual(errors, [])
        else:
            self.assertEqual(len(errors), 1, errors)
            self.assertTrue(errors[0].startswith("plugins/example/.codex-plugin/plugin.json:"))

    def test_skills_only_package(self):
        self.check(True)

    def test_explicit_hooks_override_default(self):
        self.write(self.plugin / "hooks/hooks.json", {"hooks": {}})
        self.write(self.plugin / "hooks.codex.json", self.hooks())
        self.data["hooks"] = "./hooks.codex.json"
        self.write(self.manifest, self.data)
        self.check(True)

    def test_default_hooks(self):
        self.write(self.plugin / "hooks/hooks.json", self.hooks())
        self.check(True)
        self.write(self.plugin / "hooks/hooks.json", {"hooks": {}})
        self.check(False)

    def test_invalid_declared_hooks_do_not_fall_back(self):
        self.write(self.plugin / "hooks/hooks.json", self.hooks())
        for value in (None, "", "./missing.json", "hooks/hooks.json"):
            with self.subTest(value=value):
                self.data["hooks"] = value
                self.write(self.manifest, self.data)
                self.check(False)

    def test_malformed_hooks(self):
        path = self.plugin / "hooks/hooks.json"
        for value in ({}, {"hooks": {}}, {"hooks": []}, {"hooks": {"Unknown": []}},
                      {"hooks": {"Stop": []}}, {"hooks": {"Stop": [{"hooks": []}]}},
                      {"hooks": {"Stop": [{"hooks": [{"type": "prompt"}]}]}},
                      self.hooks(""), self.hooks(None), self.hooks("\"")):
            with self.subTest(value=value):
                self.write(path, value)
                self.check(False)
        path.write_text("not JSON")
        self.check(False)

    def test_identity_and_version_must_match(self):
        for key, value in (("name", "different"), ("version", "2.0.0")):
            with self.subTest(key=key):
                self.write(self.manifest, {**self.data, key: value})
                self.check(False)

    def test_skill_paths_stay_inside_package(self):
        (self.plugin / "linked-skills").symlink_to(self.root / "outside", target_is_directory=True)
        (self.plugin / "file").write_text("not a directory")
        for value in ("./missing", "./../../outside", "./linked-skills", "./file", "skills"):
            with self.subTest(value=value):
                self.write(self.manifest, {**self.data, "skills": value})
                self.check(False)

    def test_hook_paths_stay_inside_package(self):
        outside = self.root / "outside/hooks.json"
        self.write(outside, self.hooks())
        default = self.plugin / "hooks/hooks.json"
        default.parent.mkdir()
        default.symlink_to(outside)
        self.check(False)
        default.unlink()
        default.symlink_to(self.root / "missing.json")
        self.check(False)
        for value in ("./../../outside/hooks.json", "./hooks/hooks.json"):
            with self.subTest(value=value):
                self.write(self.manifest, {**self.data, "hooks": value})
                self.check(False)

    def test_hook_command_paths_stay_inside_package(self):
        for variable in ("${PLUGIN_ROOT}", "${CLAUDE_PLUGIN_ROOT}"):
            with self.subTest(variable=variable):
                self.write(self.plugin / "hooks/hooks.json", self.hooks(f"bash {variable}/missing.sh"))
                self.check(False)


if __name__ == "__main__":
    unittest.main()
