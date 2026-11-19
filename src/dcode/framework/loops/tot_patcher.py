"""
Tree-of-Thoughts / Best-of-N Patch Evaluator.
Explores multiple candidate repair hypotheses, grades each in isolation, and commits the winner.
"""

import os
from typing import Any, Dict, List
from dcode.runtime.git_checkpoint import GitCheckpoint


class TreeOfThoughtsPatcher:
    """Evaluates N candidate patches in sandboxed checkpoints and applies the optimal fix."""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.checkpoint = GitCheckpoint(self.workspace_dir)
        from dcode.harness.grader import HarnessGrader

        self.grader = HarnessGrader(self.workspace_dir)

    def evaluate_candidates(
        self, candidates: List[Dict[str, Any]], test_cmd: str = "python3 -m unittest"
    ) -> Dict[str, Any]:
        """Test each patch candidate in a rollbacked checkpoint; rank by test pass and diff size."""
        from dcode.harness.linter_guard import LinterGuard

        evaluated = []
        base_snap = self.checkpoint.snapshot()

        for idx, cand in enumerate(candidates):
            self.checkpoint.rollback(base_snap)
            applied = self._apply_candidate(cand)
            lint = LinterGuard.check_workspace(self.workspace_dir)
            grade = self.grader.grade_command(test_cmd) if applied and lint["clean"] else {"passed": False}
            diff = self.checkpoint.diff_since(base_snap)

            score = 0.0
            if grade.get("passed"):
                score += 10.0
            if lint.get("clean"):
                score += 2.0
            score -= len(diff) * 0.001

            evaluated.append({"index": idx, "candidate": cand, "score": score, "passed": grade.get("passed", False), "diff": diff})

        self.checkpoint.rollback(base_snap)
        evaluated.sort(key=lambda x: x["score"], reverse=True)
        winner = evaluated[0] if evaluated else None

        if winner and winner["passed"]:
            self._apply_candidate(winner["candidate"])
            final_diff = self.checkpoint.diff_since(base_snap)
            return {"resolved": True, "winner": winner, "candidates_tested": len(candidates), "diff": final_diff}

        return {"resolved": False, "winner": winner, "candidates_tested": len(candidates), "diff": ""}

    def _apply_candidate(self, cand: Dict[str, Any]) -> bool:
        rel = cand.get("target_file", "").lstrip("/\\")
        if not rel:
            return False
        full = os.path.join(self.workspace_dir, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        try:
            if cand.get("action") == "write_file":
                with open(full, "w", encoding="utf-8") as f:
                    f.write(cand.get("content", ""))
                return True
            if cand.get("action") == "replace_in_file" and os.path.isfile(full):
                with open(full, "r", encoding="utf-8") as f:
                    text = f.read()
                tgt = cand.get("target", "")
                if tgt in text:
                    with open(full, "w", encoding="utf-8") as f:
                        f.write(text.replace(tgt, cand.get("replacement", ""), 1))
                    return True
        except Exception:
            return False
        return False
