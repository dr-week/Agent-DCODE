"""
Robust JSON extraction and schema validation for LLM responses.
Fixes legacy backslash corruption while handling markdown code fences.
"""

import json
import re
from typing import Any, Dict, Optional


def extract_json(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse a JSON object from raw LLM output."""
    if not text or not isinstance(text, str):
        return None

    cleaned = text.strip()

    # 1. Direct JSON parse (standard for format="json" outputs)
    try:
        data = json.loads(cleaned)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        pass

    # 2. Extract from ```json ... ``` markdown fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Extract outer { ... } block
    brace_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not brace_match:
        return None

    candidate = brace_match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        try:
            # Fallback only for unescaped Windows paths
            repaired = re.sub(r'\\(?![/u"\\bfnrt])', r"\\\\", candidate)
            return json.loads(repaired)
        except Exception as e:
            print("[PARSER ERROR]", e)
            return None
