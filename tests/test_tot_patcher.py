"""
Unit tests for StateCheckpointManager and TreeOfThoughtsPatcher.
Verifies StateGraph persistence and multi-hypothesis patch exploration.
"""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.framework.core.state_checkpoint import StateCheckpointManager
from dcode.framework.loops.tot_patcher import TreeOfThoughtsPatcher


class TestToTPatcher(unittest.TestCase):
    def test_state_checkpoint_manager_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            mgr = StateCheckpointManager(base_dir=tmp_dir)
            session = "test_sess_01"
            mgr.save_checkpoint(session, 1, {"step": 1, "task": "refactor"})
            mgr.save_checkpoint(session, 2, {"step": 2, "task": "verified"})

            checkpoints = mgr.list_checkpoints(session)
            self.assertEqual(checkpoints, [1, 2])

            latest = mgr.load_checkpoint(session)
            self.assertEqual(latest["step"], 2)
            self.assertEqual(latest["task"], "verified")

    def test_tree_of_thoughts_evaluator(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "calc.py"
            file_path.write_text("def val():\n    return 0\n", encoding="utf-8")

            test_file = Path(tmp_dir) / "test_calc.py"
            test_file.write_text("import unittest\nfrom calc import val\nclass T(unittest.TestCase):\n    def test(self):\n        self.assertEqual(val(), 42)\nif __name__ == '__main__': unittest.main()\n", encoding="utf-8")

            c1 = {"target_file": "calc.py", "action": "replace_in_file", "target": "return 0", "replacement": "return 10"}
            c2 = {"target_file": "calc.py", "action": "replace_in_file", "target": "return 0", "replacement": "return 42"}

            patcher = TreeOfThoughtsPatcher(tmp_dir)
            res = patcher.evaluate_candidates([c1, c2], test_cmd=f"python3 {test_file}")

            self.assertTrue(res["resolved"])
            self.assertEqual(res["winner"]["candidate"]["replacement"], "return 42")
            self.assertIn("return 42", file_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
