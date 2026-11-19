"""
LLM-powered surgical patch generator for SWELoop.
Uses LiteLLMRouter, RepoMap symbols, and test failure output to construct
and apply surgical replace_in_file or write_file edits to a target codebase.
"""

import json
import os
from typing import Any, Dict, Optional
from dcode.integrations.langfuse_tracer import LangfuseTracer
from dcode.integrations.litellm_router import LiteLLMRouter
from dcode.llm.parser import extract_json

PATCH_PROMPT = """You are an expert SWE agent. Solve this issue in the repository.
Issue: {issue}
Attempt: {attempt}
Repository Symbols:
{symbols}

Previous Test Failure Output:
{last_error}

Respond with ONLY JSON specifying a single surgical fix:
{{"target_file": "path/to/file.py", "action": "replace_in_file", "target": "old code", "replacement": "new code"}}
OR for complete file rewrites:
{{"target_file": "path/to/file.py", "action": "write_file", "content": "new full file content"}}
"""


class SWEPatcher:
    """Generates and executes LLM-driven surgical patches for SWELoop."""

    def __init__(self, router: Optional[LiteLLMRouter] = None, tracer: Optional[LangfuseTracer] = None):
        self.router = router or LiteLLMRouter()
        self.tracer = tracer or LangfuseTracer()

    def generate_and_apply(
        self,
        workspace_dir: str,
        issue: str,
        symbols: Dict[str, Any],
        attempt: int,
        last_error: str,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ask LLM for surgical patch JSON and apply it to workspace_dir."""
        sym_summary = "\n".join(f"{f}: {', '.join(s[:5])}" for f, s in list(symbols.items())[:15])
        prompt = PATCH_PROMPT.format(
            issue=issue,
            attempt=attempt,
            symbols=sym_summary or "No symbols detected",
            last_error=last_error or "Initial attempt",
        )
        resp = self.router.complete(prompt, model=model)
        data = extract_json(resp.get("response", "")) or {}
        target_rel = data.get("target_file", "").lstrip("/\\")
        target_path = os.path.join(workspace_dir, target_rel) if target_rel else ""
        action = data.get("action", "replace_in_file")

        res: Dict[str, Any] = {"success": False, "patch": data}
        if target_path and action == "replace_in_file":
            tgt = data.get("target", "")
            if os.path.exists(target_path) and tgt:
                with open(target_path, "r", encoding="utf-8") as f:
                    txt = f.read()
                if tgt in txt:
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(txt.replace(tgt, data.get("replacement", ""), 1))
                    res = {"success": True, "file": target_path}
        elif target_path and action == "write_file":
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(data.get("content", ""))
            res = {"success": True, "file": target_path}

        self.tracer.record_span(
            name="swe_llm_patch",
            tokens=resp.get("tokens", 0),
            cost_usd=resp.get("cost_usd", 0.0),
            latency_ms=resp.get("latency_ms", 0.0),
            status="ok" if res.get("success") else "patch_error",
        )
        return res
