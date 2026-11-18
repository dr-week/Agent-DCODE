"""
Shared LLM planning and action generation functions.
"""

import json
from typing import Any, Dict, List, Optional, Union
from dcode.agents.prompts import build_actions_prompt, build_plan_prompt
from dcode.llm.ollama_client import ask_llm_structured
from dcode.llm.parser import extract_json


def _serialize_context(context: Union[str, Dict[str, Any], None]) -> str:
    if not context:
        return ""
    if isinstance(context, dict):
        return json.dumps(context, indent=2)
    return str(context)


def generate_plan(goal: str, context: Union[str, Dict[str, Any], None] = None) -> Optional[Dict[str, Any]]:
    """Request a structured step-by-step plan from the LLM."""
    try:
        prompt = build_plan_prompt(goal, _serialize_context(context))
        response = ask_llm_structured(prompt)
        data = extract_json(response)
        return data if data and "steps" in data else None
    except Exception as e:
        print(f"[Plan] Error: {e}")
        return None


def generate_actions(
    goal: str, plan: List[Dict[str, Any]], context: Union[str, Dict[str, Any], None] = None
) -> Optional[Dict[str, Any]]:
    """Request structured tool actions for a given plan from the LLM."""
    try:
        prompt = build_actions_prompt(goal, plan, _serialize_context(context))
        response = ask_llm_structured(prompt)
        data = extract_json(response)
        return data if data and "actions" in data else None
    except Exception as e:
        print(f"[Actions] Error: {e}")
        return None
