"""
End-to-End CLI workflows: fix (SWE Issue-to-PR), research (Crawl+Mem0+LLM), and qa (Browser-Use QA).
All workflows wrap micro-modular engines under 100 lines per file.
"""

import os
from typing import Any, Dict, List, Optional
from dcode.config import PROJECT_ROOT
from dcode.integrations.browser_tool import browser_verify
from dcode.integrations.crawl4ai_tool import crawl_url
from dcode.integrations.litellm_router import LiteLLMRouter
from dcode.integrations.mem0_store import Mem0Store


def run_fix_workflow(
    issue: str,
    repo_dir: Optional[str] = None,
    test_cmd: str = "python3 -m unittest",
    max_attempts: int = 3,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Run autonomous SWE Issue-to-PR loop on repo_dir with test-driven self-healing."""
    from dcode.framework.loops.swe_loop import SWELoop
    from dcode.framework.loops.swe_patcher import SWEPatcher

    target_dir = os.path.abspath(repo_dir or str(PROJECT_ROOT))
    router = LiteLLMRouter(primary_model=model or "ollama/qwen2.5-coder:7b")
    patcher = SWEPatcher(router=router)

    def _patch(iss: str, syms: Dict[str, Any], attempt: int, last_err: str) -> None:
        patcher.generate_and_apply(target_dir, iss, syms, attempt, last_err, model=model)

    loop = SWELoop(target_dir, test_command=test_cmd, max_attempts=max_attempts)
    res = loop.solve_issue(issue, _patch)
    res["workspace"] = target_dir
    res["test_command"] = test_cmd
    return res


def run_research_workflow(
    url: str,
    prompt: str,
    user_id: str = "default",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Crawl a live doc/issue URL, remember findings in Mem0, and generate code/analysis."""
    crawl_res = crawl_url(url)
    md = crawl_res.get("markdown", "")
    mem = Mem0Store()
    if md:
        mem.remember(f"Researched {url}: {md[:300]}", user_id=user_id, category="research")

    sys_p = "You are an expert technical researcher. Use the provided live documentation to solve the user task."
    full_prompt = f"Documentation URL: {url}\n\nDocument Content:\n{md[:5000]}\n\nTask:\n{prompt}"
    router = LiteLLMRouter(primary_model=model or "ollama/qwen2.5-coder:7b")
    resp = router.complete(prompt=full_prompt, system=sys_p, model=model)
    return {
        "success": bool(resp.get("response")),
        "url": url,
        "backend": crawl_res.get("backend", "unknown"),
        "response": resp.get("response", ""),
        "tokens": resp.get("tokens", 0),
        "cost_usd": resp.get("cost_usd", 0.0),
    }


def run_qa_workflow(url: str, expect_texts: Optional[List[str]] = None) -> Dict[str, Any]:
    """Verify live web app DOM, status code, buttons, and assertions via Browser-Use adapter."""
    return browser_verify(url, expected_texts=expect_texts or [])
