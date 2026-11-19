"""
Unit tests for End-to-End CLI workflows: fix (SWE loop), research, and QA.
Strictly under 100 lines.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.framework.loops.swe_patcher import SWEPatcher
from dcode.integrations.cli_workflows import run_fix_workflow, run_qa_workflow, run_research_workflow
from dcode.integrations.litellm_router import LiteLLMRouter


class TestCLIWorkflows(unittest.TestCase):
    def test_fix_workflow_with_swe_patcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            calc_f = os.path.join(tmp, "math_tool.py")
            test_f = os.path.join(tmp, "test_math.py")
            Path(calc_f).write_text("def add_five(x):\n    return x + 10\n", encoding="utf-8")
            Path(test_f).write_text(
                "import unittest\nfrom math_tool import add_five\nclass T(unittest.TestCase):\n"
                "    def test_add(self):\n        self.assertEqual(add_five(5), 10)\n",
                encoding="utf-8",
            )

            mock_json = json.dumps({
                "target_file": "math_tool.py",
                "action": "replace_in_file",
                "target": "return x + 10",
                "replacement": "return x + 5",
            })
            router = LiteLLMRouter(mock_fn=lambda p, m: mock_json)
            patcher = SWEPatcher(router=router)

            def _patch(iss, syms, att, err):
                patcher.generate_and_apply(tmp, iss, syms, att, err)

            from dcode.framework.loops.swe_loop import SWELoop

            loop = SWELoop(tmp, test_command="python3 -m unittest discover -s .", max_attempts=2)
            res = loop.solve_issue("add_five adds 10 instead of 5", _patch)
            self.assertTrue(res["success"])
            self.assertIn("return x + 5", res["diff"])

    def test_research_workflow(self):
        html_doc = "<html><body><h1>Architecture</h1><p>DCode uses LiteLLM</p></body></html>"
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html_doc)
            f_path = f.name
        try:
            res = run_research_workflow(
                url=f"file://{f_path}",
                prompt="What does DCode use?",
            )
            self.assertTrue(res["success"])
            self.assertIn("response", res)
        finally:
            os.unlink(f_path)

    def test_qa_workflow_dom(self):
        html_doc = "<html><head><title>App</title></head><body><h1>Welcome</h1><button>Submit</button></body></html>"
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(html_doc)
            f_path = f.name
        try:
            res = run_qa_workflow(f"file://{f_path}", expect_texts=["Welcome"])
            self.assertTrue(res["success"])
            self.assertEqual(res["dom"]["title"], "App")
        finally:
            os.unlink(f_path)

    def test_dcode_cli_subcommands_subprocess(self):
        cmd = [sys.executable, "scripts/dcode_cli.py", "integrations", "--json"]
        out = subprocess.check_output(cmd, text=True)
        data = json.loads(out)
        self.assertIn("integrations", data)


if __name__ == "__main__":
    unittest.main()
