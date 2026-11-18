"""
Local Ollama API client for structured and single-shot prompts.
Uses requests when available with a standard-library urllib fallback.
"""

import json
from typing import Any, Dict
import urllib.request
from dcode.config import OLLAMA_GENERATE_URL, OLLAMA_MODEL

SYSTEM_PROMPT = """Output ONLY JSON. Available actions:
1. write_file: {"type": "write_file", "path": "projects/file.py", "content": "code"}
2. append_file: {"type": "append_file", "path": "projects/file.py", "content": "more"}
3. replace_in_file: {"type": "replace_in_file", "path": "projects/file.py", "target": "old", "replacement": "new"}
4. read_file: {"type": "read_file", "path": "projects/file.py"}
5. search_code: {"type": "search_code", "pattern": "def main", "path": "projects"}
6. list_files: {"type": "list_files", "path": "projects", "max_depth": 3}
7. run_python: {"type": "run_python", "code": "print('hello')"}
8. run_bash: {"type": "run_bash", "command": "ls -la"}
9. run_js: {"type": "run_js", "code": "console.log('hello')"}
10. get_processes: {"type": "get_processes", "sort_by": "memory", "limit": 10}
11. show_progress: {"type": "show_progress", "steps": 10, "delay": 0.1}

Return JSON with "actions" array:
{"actions": [{"type": "write_file", "path": "projects/test.py", "content": "print('hi')"}]}
"""


def _post_json(url: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ask_llm(user_input: str, model: str = OLLAMA_MODEL) -> str:
    """Send a user prompt with the default action system prompt to Ollama."""
    payload = {
        "model": model,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {user_input}",
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }
    return _post_json(OLLAMA_GENERATE_URL, payload)["response"]


def ask_llm_structured(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Single structured API call for planning or action generation."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0, "num_predict": 1000},
    }
    return _post_json(OLLAMA_GENERATE_URL, payload)["response"]
