"""
Unit tests for QUBOSwarmScheduler and ConsensusEngine.
Verifies quantum annealing task assignment and multi-agent debate loops.
"""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.framework.swarm.consensus import ConsensusEngine, ReviewFeedback
from dcode.framework.swarm.qubo_scheduler import QUBOSwarmScheduler


class TestSwarmAdvanced(unittest.TestCase):
    def test_qubo_scheduler_allocation(self):
        agents = ["frontend_agent", "backend_agent"]
        tasks = ["react_ui", "sql_api"]
        affinities = {
            "frontend_agent": {"react_ui": 1.0, "sql_api": 0.1},
            "backend_agent": {"react_ui": 0.2, "sql_api": 1.0},
        }
        scheduler = QUBOSwarmScheduler(agents, tasks)
        res = scheduler.schedule(affinities, steps=100)
        self.assertEqual(res["method"], "simulated_quantum_annealing")
        self.assertIsInstance(res["assignments"], list)

    def test_consensus_engine_approval(self):
        engine = ConsensusEngine(threshold=0.6)
        c1 = lambda p: ReviewFeedback("security_agent", True, 0.9, "Clean AST")
        c2 = lambda p: ReviewFeedback("qa_agent", True, 0.85, "Tests cover logic")
        c3 = lambda p: ReviewFeedback("style_agent", False, 0.4, "Minor docstring issue")

        res = engine.evaluate_proposal("def safe_func(): pass", [c1, c2, c3])
        self.assertTrue(res["passed"])
        self.assertEqual(res["consensus"], "APPROVED")
        self.assertAlmostEqual(res["approval_rate"], 0.67, places=2)

    def test_consensus_engine_rejection(self):
        engine = ConsensusEngine(threshold=0.66)
        c1 = lambda p: ReviewFeedback("security_agent", False, 0.2, "SQL injection risk")
        c2 = lambda p: ReviewFeedback("qa_agent", False, 0.3, "No regression tests")

        res = engine.evaluate_proposal("raw_sql_query", [c1, c2])
        self.assertFalse(res["passed"])
        self.assertEqual(res["consensus"], "REJECTED_OR_NEEDS_REVISION")


if __name__ == "__main__":
    unittest.main()
