"""
Unit tests verifying all 5 phases of Open-Source GitHub Integrations:
LiteLLMRouter, MCPBridge, RepoMap, GitCheckpoint, SWELoop, Crawl4AI, Browser-Use, Mem0Store, LangfuseTracer.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dcode.framework.loops.swe_loop import SWELoop
from dcode.integrations import (
    LangfuseTracer,
    LiteLLMRouter,
    MCPBridge,
    Mem0Store,
    RepoMap,
    get_integration_status,
    html_to_markdown,
    inspect_html_dom,
)


class TestOpenSourceIntegrations(unittest.TestCase):
    def test_phase1_litellm_router_and_mcp_bridge(self):
        router = LiteLLMRouter(mock_fn=lambda prompt, model: f"SOLVED[{model}]: {prompt}")
        res = router.complete("Fix bug #42", model="openai/gpt-4o")
        self.assertIn("SOLVED[openai/gpt-4o]", res["response"])
        self.assertGreater(res["tokens"], 0)

        bridge = MCPBridge()
        tools = bridge.list_mcp_tools()
        names = [t["name"] for t in tools]
        self.assertIn("replace_in_file", names)
        self.assertIn("search_code", names)

    def test_phase2_repomap_and_swe_loop_self_healing(self):
        with tempfile.TemporaryDirectory() as tmp:
            buggy_file = os.path.join(tmp, "calc.py")
            test_file = os.path.join(tmp, "test_calc.py")
            with open(buggy_file, "w") as f:
                f.write("def multiply(a, b):\n    return a + b\n")
            with open(test_file, "w") as f:
                f.write(
                    "import unittest\nfrom calc import multiply\n"
                    "class T(unittest.TestCase):\n"
                    "    def test_m(self):\n        self.assertEqual(multiply(3, 4), 12)\n"
                )

            rm = RepoMap(tmp)
            symbols = rm.scan()
            self.assertIn("calc.py", symbols)

            def patch_fn(issue, syms, attempt, last_err):
                with open(buggy_file, "w") as f:
                    if attempt == 1:
                        f.write("def multiply(a, b):\n    return a - b\n")
                    else:
                        f.write("def multiply(a, b):\n    return a * b\n")

            swe = SWELoop(tmp, test_command="python3 -m unittest discover -s .", max_attempts=3)
            outcome = swe.solve_issue("multiply returns sum instead of product", patch_fn)
            self.assertTrue(outcome["success"])
            self.assertEqual(outcome["attempts"], 2)
            self.assertIn("return a * b", outcome["diff"])

    def test_phase3_crawl4ai_and_browser_dom_inspector(self):
        sample_html = "<html><head><title>Docs</title></head><body><h1>API Guide</h1><button>Run</button></body></html>"
        md = html_to_markdown(sample_html)
        self.assertIn("# API Guide", md)
        dom = inspect_html_dom(sample_html)
        self.assertEqual(dom["title"], "Docs")
        self.assertIn("Run", dom["buttons"])

    def test_phase4_mem0_and_langfuse_And_phase5_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            mem = Mem0Store(db_path=os.path.join(tmp, "mem.db"))
            mem.remember("Always keep files strictly under 100 lines", user_id="dev1", category="rule")
            hits = mem.recall("100 lines modularity", user_id="dev1")
            self.assertEqual(len(hits), 1)

            tracer = LangfuseTracer(db_path=os.path.join(tmp, "traces.db"))
            tracer.record_span("swe_patch", tokens=250, cost_usd=0.0015, latency_ms=42.0)
            stats = tracer.summary()
            self.assertEqual(stats["total_spans"], 1)
            self.assertEqual(stats["total_tokens"], 250)

            catalog = get_integration_status()
            self.assertEqual(len(catalog), 8)


if __name__ == "__main__":
    unittest.main()
