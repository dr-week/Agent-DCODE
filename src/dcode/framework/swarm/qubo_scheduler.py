"""
QUBO Swarm Task Scheduler.
Maps multi-agent task allocations into Quadratic Unconstrained Binary Optimization problems
and solves them via Simulated Quantum Annealing.
"""

from typing import Any, Dict, List
from dcode.integrations.quantum_engine import quantum_optimize_qubo


class QUBOSwarmScheduler:
    """Allocates tasks to specialized agents using quantum annealing optimization."""

    def __init__(self, agents: List[str], tasks: List[str]):
        self.agents = agents
        self.tasks = tasks

    def build_qubo_matrix(self, affinities: Dict[str, Dict[str, float]]) -> List[List[float]]:
        """Construct an (agents*tasks) square QUBO cost matrix."""
        n_a = len(self.agents)
        n_t = len(self.tasks)
        dim = n_a * n_t
        matrix = [[0.0 for _ in range(dim)] for _ in range(dim)]

        for a_idx, agent in enumerate(self.agents):
            for t_idx, task in enumerate(self.tasks):
                var_i = a_idx * n_t + t_idx
                affinity = affinities.get(agent, {}).get(task, 0.5)
                matrix[var_i][var_i] = -2.0 * affinity

        for t_idx in range(n_t):
            for a1 in range(n_a):
                for a2 in range(a1 + 1, n_a):
                    v1 = a1 * n_t + t_idx
                    v2 = a2 * n_t + t_idx
                    matrix[v1][v2] = 4.0
                    matrix[v2][v1] = 4.0

        return matrix

    def schedule(self, affinities: Dict[str, Dict[str, float]], steps: int = 150) -> Dict[str, Any]:
        """Solve task allocation via simulated quantum annealing."""
        matrix = self.build_qubo_matrix(affinities)
        res = quantum_optimize_qubo(matrix, steps=steps)
        state = res.get("best_state", [])

        assignments: List[Dict[str, str]] = []
        n_t = len(self.tasks)
        for idx, bit in enumerate(state):
            if bit == 1:
                a_idx = idx // n_t
                t_idx = idx % n_t
                if a_idx < len(self.agents) and t_idx < len(self.tasks):
                    assignments.append({"agent": self.agents[a_idx], "task": self.tasks[t_idx]})

        return {
            "method": "simulated_quantum_annealing",
            "energy": res.get("min_energy", 0.0),
            "assignments": assignments,
        }
