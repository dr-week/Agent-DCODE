"""
Google Gemini / Colab LLM client and environment checks.
"""

import logging
import psutil
import requests
from dcode.config import GEMINI_MODEL, GOOGLE_API_KEY

MAX_CODE_LENGTH = 2000
MEMORY_THRESHOLD_BYTES = 600 * 1024 * 1024  # 600 MB
TIMEOUT_SECONDS = 20
logger = logging.getLogger("colab_agent")


class ColabAgentError(Exception):
    """Custom exception for Colab/Gemini agent errors."""


def check_environment() -> None:
    if not GOOGLE_API_KEY:
        raise ColabAgentError("GOOGLE_API_KEY not set in environment.")


def check_memory() -> None:
    memory = psutil.virtual_memory()
    if memory.available < MEMORY_THRESHOLD_BYTES:
        raise ColabAgentError("Colab RAM is low (<600MB free).")


def build_colab_prompt(task: str, code: str) -> str:
    code_snippet = f"\n\nCode:\n{code}" if code else ""
    return (
        f"You are a concise expert coding assistant.\nTask: {task}{code_snippet}\n\n"
        "Return ONLY valid JSON with keys: 'plan' (list), 'actions' (list), 'result' (string)."
    )


def call_gemini(prompt: str, model: str = GEMINI_MODEL) -> str:
    check_environment()
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generate"
    headers = {"Authorization": f"Bearer {GOOGLE_API_KEY}", "Content-Type": "application/json"}
    body = {"prompt": {"text": prompt}, "temperature": 0.2, "max_output_tokens": 800}

    response = requests.post(url, headers=headers, json=body, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()

    candidates = payload.get("candidates", [])
    if not candidates:
        raise ColabAgentError("Gemini response did not include candidates.")

    candidate = candidates[0]
    content = candidate.get("content", [])
    if isinstance(content, list):
        text = "".join(
            item.get("text", "") for item in content if item.get("type") in ("output_text", "text")
        )
    else:
        text = candidate.get("output", "") or candidate.get("text", "")

    if not text:
        raise ColabAgentError("Gemini returned empty text content.")
    return text
