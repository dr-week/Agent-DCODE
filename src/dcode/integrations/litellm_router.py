"""
Phase 1: LiteLLM Multi-Provider Router Adapter (BerriAI/litellm).
Routes completions across 100+ providers (Ollama, OpenAI, Anthropic, Gemini)
with automatic fallback to local Ollama and cost/token accounting.
"""

import time
from typing import Any, Callable, Dict, List, Optional
from dcode.llm.ollama_client import ask_llm_structured

try:
    import litellm  # type: ignore

    HAS_LITELLM = True
except ImportError:
    litellm = None  # type: ignore
    HAS_LITELLM = False


class LiteLLMRouter:
    """Unified multi-model router wrapping BerriAI/litellm with local Ollama fallback."""

    def __init__(
        self,
        primary_model: str = "ollama/qwen2.5-coder:7b",
        fallback_models: Optional[List[str]] = None,
        mock_fn: Optional[Callable[[str, str], str]] = None,
    ):
        self.primary_model = primary_model
        self.fallback_models = fallback_models or ["ollama/qwen2.5-coder:7b"]
        self.mock_fn = mock_fn
        self.history: List[Dict[str, Any]] = []

    def complete(self, prompt: str, system: str = "", model: Optional[str] = None) -> Dict[str, Any]:
        """Execute completion via LiteLLM or fallback seamlessly to stdlib Ollama client."""
        target = model or self.primary_model
        t0 = time.time()
        full_prompt = f"{system}\n\n{prompt}".strip() if system else prompt

        if self.mock_fn:
            text = self.mock_fn(prompt, target)
            return self._record(target, full_prompt, text, t0, "mock", 0.0)

        if HAS_LITELLM and litellm is not None:
            for candidate in [target] + [m for m in self.fallback_models if m != target]:
                try:
                    msgs = [{"role": "user", "content": prompt}]
                    if system:
                        msgs.insert(0, {"role": "system", "content": system})
                    resp = litellm.completion(model=candidate, messages=msgs)
                    text = resp.choices[0].message.content or ""
                    cost = float(getattr(resp, "_hidden_params", {}).get("response_cost") or 0.0)
                    return self._record(candidate, full_prompt, text, t0, "litellm", cost)
                except Exception:
                    continue

        raw_text = ask_llm_structured(full_prompt)
        return self._record(target, full_prompt, raw_text, t0, "ollama_stdlib", 0.0)

    def _record(
        self, model: str, prompt: str, response: str, t0: float, backend: str, cost: float
    ) -> Dict[str, Any]:
        est_tokens = max(1, (len(prompt) + len(response)) // 4)
        entry = {
            "model": model,
            "backend": backend,
            "response": response,
            "tokens": est_tokens,
            "cost_usd": round(cost, 6),
            "latency_ms": round((time.time() - t0) * 1000, 2),
        }
        self.history.append(entry)
        return entry
