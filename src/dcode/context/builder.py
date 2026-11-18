"""
Context preparation and compact LLM prompt formatting.
"""

from typing import Any, Dict, Optional
from dcode.context.extractors import (
    get_directory_context,
    get_file_context,
    get_selected_code_context,
)


def prepare_agent_context(
    task: str,
    selected_code: Optional[str] = None,
    active_file: Optional[str] = None,
    project_dir: str = "projects",
) -> Dict[str, Any]:
    """Prepare minimal context (<2KB) for an agent task."""
    context: Dict[str, Any] = {"task": task, "files": [], "code": []}

    if selected_code:
        context["code"].append(get_selected_code_context(selected_code))

    if active_file:
        file_ctx = get_file_context(active_file, max_lines=30)
        if file_ctx and "error" not in file_ctx:
            context["files"].append(file_ctx)

    dir_ctx = get_directory_context(project_dir, max_depth=2)
    if dir_ctx and "error" not in dir_ctx:
        context["project"] = dir_ctx

    return context


def format_context_for_llm(context: Dict[str, Any]) -> str:
    """Format context dictionary as compact markdown text for LLM prompts."""
    lines = []

    if context.get("code"):
        lines.append("## Selected Code:")
        for code_ctx in context["code"]:
            if "code" in code_ctx:
                lines.append(f"Language: {code_ctx.get('language', 'unknown')}")
                lines.append(f"```\n{code_ctx['code']}\n```")

    if context.get("files"):
        lines.append("\n## File Context:")
        for file_ctx in context["files"]:
            if "error" not in file_ctx:
                lines.append(f"File: {file_ctx['filename']} ({file_ctx['total_lines']} lines)")
                file_content = "".join(file_ctx.get("lines", [])[:20])
                lines.append(f"```\n{file_content}\n```")

    if context.get("project"):
        lines.append("\n## Project Structure:")
        for f in context["project"].get("files", [])[:10]:
            lines.append(f"  - {f['path']}")

    return "\n".join(lines)
