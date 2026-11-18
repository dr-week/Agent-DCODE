#!/usr/bin/env python3
"""
Unit tests for the Universal Agentic AI Framework (Core, Loops, Swarm, Memory, Guardrails, Archetypes).
"""

import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.archetypes import create_software_team, list_archetypes
from dcode.framework import END, AgentSpec, ReActAgent, ReflexionAgent, StateGraph, tool
from dcode.guardrails import GuardrailPolicy
from dcode.memory import EpisodicMemory, SemanticMemory, WorkingMemory


@tool
def multiply_values(a: int, b: int) -> int:
    """Multiply two integers and return the product."""
    return a * b


class TestAgenticFramework(unittest.TestCase):
    def test_tool_decorator_schema_and_invocation(self) -> None:
        schema = multiply_values.to_dict()
        self.assertEqual(schema["name"], "multiply_values")
        self.assertEqual(schema["parameters"]["properties"]["a"]["type"], "integer")
        self.assertEqual(multiply_values.invoke(a=6, b=7), 42)

    def test_state_graph_conditional_routing(self) -> None:
        graph = StateGraph(entry_point="plan")
        graph.add_node("plan", lambda s: {**s, "planned": True, "count": s.get("count", 0) + 1})
        graph.add_node("act", lambda s: {**s, "acted": True})
        graph.add_edge("plan", "act")
        graph.add_conditional_edges("act", lambda s: END if s.get("acted") else "plan")

        final = graph.run({"count": 0})
        self.assertTrue(final["planned"] and final["acted"])
        self.assertEqual(final["_trace"], ["plan", "act"])

    def test_react_and_reflexion_loops_with_mock_llm(self) -> None:
        responses = iter([
            json.dumps({"thought": "Use tool", "tool": "multiply_values", "tool_args": {"a": 4, "b": 5}}),
            json.dumps({"thought": "Done", "final_answer": "Result is 20"}),
        ])
        spec = AgentSpec(name="math-agent", role="Calculator", goal="Compute product", tools=[multiply_values])
        res = ReActAgent(spec, llm_fn=lambda _: next(responses)).run("Multiply 4 and 5")
        self.assertTrue(res["success"])
        self.assertEqual(res["answer"], "Result is 20")

        ref_responses = iter([
            json.dumps({"draft": "Initial code"}),
            json.dumps({"approved": True, "score": 9, "feedback": "LGTM"}),
        ])
        ref_res = ReflexionAgent(spec, llm_fn=lambda _: next(ref_responses)).run("Write module")
        self.assertTrue(ref_res["success"])

    def test_multi_agent_software_team_and_archetypes(self) -> None:
        self.assertGreaterEqual(len(list_archetypes()), 5)
        mock_llm = lambda _: json.dumps({"thought": "OK", "final_answer": "Completed stage", "draft": "OK", "approved": True})
        team = create_software_team(llm_fn=mock_llm)
        report = team.run("Build rate limiter")
        self.assertTrue(report["success"])
        self.assertEqual(len(report["handoffs"]), 3)

    def test_three_tier_memory_and_guardrails(self) -> None:
        wm = WorkingMemory(max_messages=2)
        wm.add_message("user", "m1"); wm.add_message("assistant", "m2"); wm.add_message("user", "m3")
        self.assertEqual(len(wm.messages), 2)

        sem = SemanticMemory()
        sem.add_document("doc1", "Autonomous coding agent using Ollama and CLI-Anything")
        sem.add_document("doc2", "PostgreSQL database indexing guide")
        hits = sem.search("CLI-Anything coding agent")
        self.assertEqual(hits[0]["id"], "doc1")

        ep = EpisodicMemory()
        ep.record_episode("coder", "Fix import bug", "Added sys.path", True, "Always check PYTHONPATH")
        self.assertGreaterEqual(len(ep.recall_similar("import bug")), 1)

        policy = GuardrailPolicy(allow_shell=False)
        ok, _ = policy.validate_action({"type": "run_bash", "command": "ls"})
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
