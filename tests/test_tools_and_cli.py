#!/usr/bin/env python3
"""
Unit tests for Agent-DCODE modular tools, JSON parser, verifier, and CLI-Anything harness generator.
"""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.agents.verifier import check_goal_complete, execute_and_verify
from dcode.cli_anything import (
    discover_cli_harnesses,
    generate_cli_anything_harness,
    run_cli_harness,
    undo_last_mutation,
)
from dcode.config import PROJECTS_DIR
from dcode.llm.parser import extract_json
from dcode.tools import replace_in_file, safe_path, search_code, write_file


class TestDCodeModules(unittest.TestCase):
    def tearDown(self) -> None:
        for fname in (
            "math_mod.py",
            "sample_calc.py",
            "cli_anything_sample_calc.py",
            "cli_anything_sample_calc.SKILL.md",
        ):
            p = PROJECTS_DIR / fname
            if p.exists():
                p.unlink()

    def test_parser_handles_fences_and_escapes(self) -> None:
        raw = '```json\n{"actions": [{"type": "write_file", "path": "projects/a.py", "content": "print(\\"hi\\n\\")"}]}\n```'
        parsed = extract_json(raw)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["actions"][0]["type"], "write_file")

    def test_safe_path_blocks_traversal(self) -> None:
        self.assertIsNone(safe_path("../../etc/passwd"))
        self.assertIsNotNone(safe_path("projects/demo_unit.py"))

    def test_file_edit_search_and_undo(self) -> None:
        res = execute_and_verify([{
            "type": "write_file",
            "path": "projects/math_mod.py",
            "content": "def add_nums(a, b):\n    \"\"\"Add two numbers.\"\"\"\n    return a + b\n",
        }])
        self.assertTrue(res["success"])
        self.assertTrue(check_goal_complete(res))

        upd = replace_in_file({
            "path": "projects/math_mod.py",
            "target": "return a + b",
            "replacement": "return int(a) + int(b)",
        })
        self.assertIn("[UPDATED]", upd)

        found = search_code({"pattern": "def add_nums", "path": "projects"})
        self.assertIn("math_mod.py", found)

    def test_cli_anything_generation_and_json_execution(self) -> None:
        write_file({
            "path": "projects/sample_calc.py",
            "content": "def multiply(x, y):\n    \"\"\"Multiply x and y.\"\"\"\n    return x * y\n",
        })
        gen = generate_cli_anything_harness("projects/sample_calc.py")
        self.assertTrue(gen["success"])
        self.assertIn("multiply", gen["commands_exposed"])

        harnesses = discover_cli_harnesses()
        self.assertTrue(any(h["entrypoint"] == "cli_anything_sample_calc.py" for h in harnesses))

        run_res = run_cli_harness([sys.executable, "cli_anything_sample_calc.py", "multiply", "6", "7"])
        self.assertTrue(run_res["success"])
        self.assertEqual(run_res["data"]["result"], 42)

        undo_res = undo_last_mutation()
        self.assertIn("success", undo_res)


if __name__ == "__main__":
    unittest.main()
