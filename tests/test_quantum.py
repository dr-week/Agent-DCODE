"""
Unit tests for the Quantum Mechanics Engine & Qiskit SDK Integration (<100 lines).
Tests Hadamard superposition, Bell State entanglement (H + CNOT), and QUBO Simulated Annealing.
"""

import unittest
from dcode.archetypes.templates import create_quantum_engineer_spec
from dcode.integrations.quantum_engine import (
    QuantumSimulator,
    quantum_optimize_qubo,
    simulate_quantum_circuit,
)


class TestQuantumEngine(unittest.TestCase):
    def test_superposition_hadamard(self):
        sim = QuantumSimulator(num_qubits=1)
        sim.apply_h(0)
        probs = sim.probabilities()
        self.assertAlmostEqual(probs.get("0", 0.0), 0.5, places=2)
        self.assertAlmostEqual(probs.get("1", 0.0), 0.5, places=2)

    def test_bell_state_entanglement(self):
        sim = QuantumSimulator(num_qubits=2)
        sim.apply_h(0)
        sim.apply_cnot(control=0, target=1)
        probs = sim.probabilities()
        self.assertIn("00", probs)
        self.assertIn("11", probs)
        self.assertAlmostEqual(probs["00"], 0.5, places=2)
        self.assertAlmostEqual(probs["11"], 0.5, places=2)
        self.assertNotIn("01", probs)
        self.assertNotIn("10", probs)

    def test_simulate_circuit_tool(self):
        gates = [{"gate": "H", "qubit": 0}, {"gate": "X", "qubit": 1}]
        res = simulate_quantum_circuit(num_qubits=2, gates=gates)
        self.assertIn("probabilities", res)
        self.assertIn("10", res["probabilities"])
        self.assertIn("11", res["probabilities"])

    def test_qubo_simulated_quantum_annealing(self):
        matrix = [[-2.0, 1.0], [1.0, -2.0]]
        res = quantum_optimize_qubo(matrix, steps=80)
        self.assertIn("optimal_bitstring", res)
        self.assertIn("energy", res)
        self.assertLessEqual(res["energy"], 0.0)

    def test_quantum_engineer_archetype(self):
        spec = create_quantum_engineer_spec()
        self.assertEqual(spec.name, "quantum-engineer")
        self.assertIn("Quantum", spec.role)
        self.assertEqual(spec.loop_type, "react")


if __name__ == "__main__":
    unittest.main()
