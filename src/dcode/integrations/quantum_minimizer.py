"""
Quantum QUBO Test Suite Minimizer.
Formulates test suite selection as a QUBO set-cover optimization problem
and minimizes regression test duration via Simulated Quantum Annealing.
"""

from typing import Any, Dict, List, Set
from dcode.integrations.quantum_engine import quantum_optimize_qubo


class QuantumTestMinimizer:
    """Selects the minimum subset of test cases that cover modified code symbols."""

    def __init__(self, test_coverage: Dict[str, List[str]]):
        self.tests = sorted(list(test_coverage.keys()))
        self.coverage = {t: set(syms) for t, syms in test_coverage.items()}

    def build_qubo(self, target_symbols: List[str]) -> List[List[float]]:
        """Construct square QUBO cost matrix penalizing uncovered symbols and test count."""
        n = len(self.tests)
        targets = set(target_symbols)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]

        # Diagonal: reward tests covering more targets, plus small penalty for each test selected
        for i, t in enumerate(self.tests):
            overlap = len(self.coverage[t] & targets)
            matrix[i][i] = 1.0 - (2.5 * overlap)

        # Off-diagonal: penalize redundant overlapping tests
        for i in range(n):
            for j in range(i + 1, n):
                redundancy = len(self.coverage[self.tests[i]] & self.coverage[self.tests[j]] & targets)
                matrix[i][j] = 1.5 * redundancy
                matrix[j][i] = 1.5 * redundancy

        return matrix

    def minimize(self, target_symbols: List[str], steps: int = 120) -> Dict[str, Any]:
        """Run simulated quantum annealing to find minimal test set."""
        if not self.tests or not target_symbols:
            return {"selected_tests": self.tests, "covered_symbols": [], "reduction_percent": 0.0}

        qubo = self.build_qubo(target_symbols)
        res = quantum_optimize_qubo(qubo, steps=steps)
        state = res.get("optimal_bitstring") or res.get("best_state", [])

        selected = [self.tests[i] for i, bit in enumerate(state) if bit == 1]
        if not selected and self.tests:
            selected = [self.tests[0]]

        all_covered: Set[str] = set()
        for t in selected:
            all_covered |= self.coverage.get(t, set())

        reduction = round((1.0 - len(selected) / max(1, len(self.tests))) * 100, 1)
        return {
            "selected_tests": selected,
            "covered_symbols": sorted(list(all_covered & set(target_symbols))),
            "total_available": len(self.tests),
            "selected_count": len(selected),
            "reduction_percent": max(0.0, reduction),
        }
