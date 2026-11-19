"""
Harness Scorecard & Metrics Aggregator (<100 lines).
Calculates Pass@1, Pass@k, cost, and latency percentiles, formatting clean Markdown scorecards.
"""

from typing import Any, Dict, List


class HarnessScorecard:
    """Aggregates benchmark results into structured scorecards."""

    @staticmethod
    def calculate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute aggregate benchmark metrics across all task runs."""
        total = len(results)
        if total == 0:
            return {"total": 0, "pass_rate_percent": 0.0, "pass_count": 0}

        pass_1 = sum(1 for r in results if r.get("passed") and r.get("attempts", 1) == 1)
        pass_k = sum(1 for r in results if r.get("passed"))
        total_tokens = sum(r.get("tokens", 0) for r in results)
        total_cost = sum(r.get("cost_usd", 0.0) for r in results)
        avg_lat = sum(r.get("latency_ms", 0.0) for r in results) / total

        return {
            "total_tasks": total,
            "pass_at_1_count": pass_1,
            "pass_at_1_percent": round((pass_1 / total) * 100, 1),
            "pass_at_k_count": pass_k,
            "pass_at_k_percent": round((pass_k / total) * 100, 1),
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(avg_lat, 2),
            "results": results,
        }

    @staticmethod
    def render_markdown(metrics: Dict[str, Any]) -> str:
        """Format metrics dictionary into a clean Markdown table."""
        lines = [
            "# Agent Harness Benchmark Scorecard",
            "",
            "| Metric | Result |",
            "| :--- | :--- |",
            f"| **Total Tasks** | {metrics.get('total_tasks', 0)} |",
            f"| **Pass@1 (First-Attempt)** | {metrics.get('pass_at_1_percent', 0.0)}% ({metrics.get('pass_at_1_count', 0)}/{metrics.get('total_tasks', 0)}) |",
            f"| **Pass@k (Self-Healing)** | {metrics.get('pass_at_k_percent', 0.0)}% ({metrics.get('pass_at_k_count', 0)}/{metrics.get('total_tasks', 0)}) |",
            f"| **Total Tokens** | {metrics.get('total_tokens', 0):,} |",
            f"| **Total Cost** | ${metrics.get('total_cost_usd', 0.0):.4f} |",
            f"| **Average Latency** | {metrics.get('avg_latency_ms', 0.0)} ms |",
        ]
        return "\n".join(lines)
