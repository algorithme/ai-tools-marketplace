"""Exercise installed hook entrypoints over their actual stdin/stdout contract."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
SECTIONS = (
    "Non-negotiables", "Decisions", "Models", "Functions", "Diagram",
    "File tree", "Tests", "Size check", "ADR check", "Documentation check",
)


def plan(sections=SECTIONS, bodies=None, title=lambda i, name: f"## {i}. {name}"):
    bodies = bodies or {}
    text = "\n\n".join(f"{title(i, name)}\n{bodies.get(name, 'Concrete content.')}"
                       for i, name in enumerate(sections, 1))
    return f"<proposed_plan>\n# Task\n{text}\n</proposed_plan>"


class PlanHooks(unittest.TestCase):
    def run_hook(self, message=None, raw=None, **fields):
        event = {"hook_event_name": "Stop", "last_assistant_message": message, **fields}
        run = subprocess.run([sys.executable, str(PLUGIN / "hooks/codex-plan.py")],
                             input=json.dumps(event) if raw is None else raw,
                             text=True, capture_output=True, check=True)
        self.assertEqual(run.stderr, "")
        return json.loads(run.stdout)

    def test_valid_headings_and_explained_absence(self):
        for title in (lambda i, name: f"## {i}. {name}",
                      lambda i, name: f"### **{name.upper()}**",
                      lambda i, name: f"**{i}) {name}**",
                      lambda i, name: f"{i}. **{name}**"):
            with self.subTest(title=title):
                self.assertEqual(self.run_hook(plan(title=title, bodies={
                    "Models": "None — no data models change.",
                    "Diagram": "```text\nrequest -> validation -> result\n```",
                    "File tree": "~~~\nsrc/check.py # validate requests\n~~~",
                }), permission_mode="default"), {})

    def test_missing_duplicate_order_and_empty_are_explained(self):
        cases = (
            (plan(SECTIONS[1:]), "Missing: Non-negotiables"),
            (plan((*SECTIONS, "Tests")), "Repeated: Tests"),
            (plan(("Decisions", "Non-negotiables", *SECTIONS[2:])), "canonical ten-section order"),
            (plan(bodies={"Models": ""}), "Empty or placeholder: Models"),
            (plan(bodies={"Models": "### Model details"}), "Empty or placeholder: Models"),
            (plan(bodies={"Models": "## Future work\nUnrelated prose."}), "Empty or placeholder: Models"),
            (plan(bodies={"Models": "# Other topic\nUnrelated prose."}), "Empty or placeholder: Models"),
            (plan(bodies={"Diagram": "```text\n\n```"}), "Empty or placeholder: Diagram"),
        )
        for message, reason in cases:
            with self.subTest(reason=reason):
                result = self.run_hook(message)
                self.assertEqual(result["decision"], "block")
                self.assertIn(reason, result["reason"])
                self.assertIn("await user approval", result["reason"])

    def test_placeholders_are_not_content(self):
        for placeholder in ("TODO", "TBD", "...", "…", "None", "N/A", "- **None**", "TODO\nTBD", "- [ ] TODO"):
            with self.subTest(placeholder=placeholder):
                result = self.run_hook(plan(bodies={"Models": placeholder}))
                self.assertIn("Empty or placeholder: Models", result["reason"])

    def test_nested_headings_preserve_real_body(self):
        self.assertEqual(self.run_hook(plan(bodies={
            "Models": "### Existing model\nRetain Payment unchanged."
        })), {})

    def test_fenced_headings_cannot_supply_or_duplicate_sections(self):
        message = plan(SECTIONS[:-1], bodies={"Tests": "```md\n## Documentation check\nDetails\n```"})
        self.assertIn("Missing: Documentation check", self.run_hook(message)["reason"])
        for fence in ("```md", "~~~~md"):
            self.assertEqual(self.run_hook(plan(bodies={
                "Tests": f"{fence}\n## Tests\n### Models\n{fence.rstrip('md')}"
            })), {})

    def test_ordinary_messages_and_examples_are_not_gated(self):
        incomplete = plan(SECTIONS[:1])
        for message in (None, 7, "", "Which approach do you prefer?", "Please approve the saved plan.",
                        f"Example:\n{incomplete}", f"```md\n{incomplete}\n```",
                        "\n".join("> " + line for line in incomplete.splitlines()),
                        "<proposed_plan>unfinished", incomplete + incomplete):
            with self.subTest(message=message):
                self.assertEqual(self.run_hook(message, permission_mode="plan"), {})

    def test_stop_continuation_does_not_loop(self):
        self.assertEqual(self.run_hook(plan(SECTIONS[:1]), stop_hook_active=True), {})

    def test_malformed_input_fails_open_without_echo(self):
        for raw in ("{secret", "null", "[]", '"private text"'):
            with self.subTest(raw=raw):
                result = self.run_hook(raw=raw)
                self.assertEqual(set(result), {"systemMessage"})
                self.assertNotIn("private", result["systemMessage"])
                self.assertNotIn("secret", result["systemMessage"])
        self.assertEqual(self.run_hook(raw="{}"), {})

    def test_reminder_adds_context_without_blocking(self):
        result = self.run_hook(hook_event_name="UserPromptSubmit", prompt="Hello")
        self.assertEqual(set(result), {"hookSpecificOutput"})
        output = result["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "UserPromptSubmit")
        self.assertIn("For planning tasks", output["additionalContext"])
        self.assertIn("await user approval", output["additionalContext"])
        self.assertIn("--check-plan preflight", output["additionalContext"])
        self.assertEqual(self.run_hook(hook_event_name="SessionEnd"), {})

    def test_preflight_accepts_fenced_content_and_envelope_examples(self):
        message = plan(bodies={
            "Diagram": "```text\ninput -> check -> output\n```",
            "Functions": "Emit `<proposed_plan>` and `</proposed_plan>` tags.\n"
                         "> <proposed_plan>\n> Quoted example\n> </proposed_plan>\n"
                         "```md\n<proposed_plan>\nFenced example\n</proposed_plan>\n```",
        })
        run = subprocess.run([sys.executable, str(PLUGIN / "hooks/codex-plan.py"), "--check-plan"],
                             input=message, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(run.stderr, "")
        self.assertIn("user approval is still required", run.stdout)
        self.assertEqual(self.run_hook(message), {})

    def test_preflight_rejects_envelopes_and_same_structural_failures(self):
        for message, expected in (("", "envelope"), ("Plain plan", "envelope"),
                                  ("<proposed_plan>unfinished", "envelope"), (plan() * 2, "envelope"),
                                  (plan() + "\n" + plan(), "envelope"),
                                  ("<proposed_plan>inline wrapper</proposed_plan>", "envelope"),
                                  (plan(bodies={"Functions": "<proposed_plan>\nNested\n</proposed_plan>"}), "envelope"),
                                  (plan(SECTIONS[1:]), "Missing: Non-negotiables"),
                                  (plan(bodies={"Models": "TODO"}), "Empty or placeholder: Models")):
            with self.subTest(message=message):
                run = subprocess.run([sys.executable, str(PLUGIN / "hooks/codex-plan.py"), "--check-plan"],
                                     input=message, text=True, capture_output=True)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(run.stdout, "")
                self.assertIn(expected, run.stderr)
                if expected != "envelope":
                    self.assertIn(expected, self.run_hook(message)["reason"])


class StartupReaders(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="grumpy hooks ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}

    def run_reader(self, name, cwd=None, **env):
        run = subprocess.run(["bash", str(PLUGIN / "hooks" / name)], cwd=cwd or self.root,
                             env={**self.env, **env}, text=True, capture_output=True, check=True)
        self.assertEqual(run.stderr, "")
        return run.stdout

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def test_missing_indexes_are_silent(self):
        for script in ("load-context.sh", "load-adr-pointer.sh"):
            self.assertEqual(self.run_reader(script), "")

    def test_empty_header_and_mixed_adr_rows_have_one_count(self):
        cases = (("", 0), ("| Number | Title |\n|---|---|\n", 0),
                 ("| 0001 | First |\n| 0002 | Second |\n", 2),
                 ("| [0001](one.md) | First |\n| [ADR-0002](two.md) | Second |\n"
                  "| 0003 | Third |\n| 12345 | Invalid |\n", 3))
        for content, count in cases:
            with self.subTest(content=content):
                self.write("docs/adr/INDEX.md", content)
                output = self.run_reader("load-adr-pointer.sh")
                self.assertEqual(len(output.splitlines()), 2)
                self.assertRegex(output, rf"\n{count} ADR\(s\) recorded")

    def test_empty_and_populated_context(self):
        for content in ("", "Project context\nwith another line\n"):
            self.write(".contexts/index.md", content)
            output = self.run_reader("load-context.sh")
            self.assertIn("## Project context", output)
            self.assertIn(content.rstrip(), output)

    def test_unreadable_indexes_do_not_block_or_leak_errors(self):
        for path, script in ((".contexts/index.md", "load-context.sh"),
                             ("docs/adr/INDEX.md", "load-adr-pointer.sh")):
            target = self.write(path, "private data")
            target.chmod(0)
            try:
                output = self.run_reader(script)
                if not os.access(target, os.R_OK):
                    self.assertEqual(output, "")
            finally:
                target.chmod(0o600)

    def test_git_root_and_explicit_project_dir_from_nested_cwd(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        nested = self.root / "nested project"
        nested.mkdir()
        self.write(".contexts/index.md", "root context")
        self.write("docs/adr/INDEX.md", "| 0001 | Root decision |\n")
        self.write("nested project/.contexts/index.md", "explicit context")
        self.write("nested project/docs/adr/INDEX.md", "")
        self.assertIn("root context", self.run_reader("load-context.sh", cwd=nested))
        self.assertIn("1 ADR(s)", self.run_reader("load-adr-pointer.sh", cwd=nested))
        self.assertIn("explicit context", self.run_reader("load-context.sh", cwd=nested,
                                                         CLAUDE_PROJECT_DIR=str(nested)))
        self.assertIn("0 ADR(s)", self.run_reader("load-adr-pointer.sh", cwd=nested,
                                                 CLAUDE_PROJECT_DIR=str(nested)))


if __name__ == "__main__":
    unittest.main()
