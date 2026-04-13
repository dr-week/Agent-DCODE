"""
Context Handler - Extract minimal, relevant context for agent tasks
"""

import os
import json
from pathlib import Path


def get_file_context(file_path: str, max_lines: int = 50) -> dict:
    """
    Get context of a specific file.
    
    Args:
        file_path: Path to the file
        max_lines: Maximum lines to include
    
    Returns:
        dict: {filename, lines, size, type}
    """
    try:
        abs_path = os.path.join("projects", file_path)
        if not os.path.exists(abs_path):
            return None

        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        return {
            "filename": file_path,
            "lines": lines[:max_lines],
            "total_lines": len(lines),
            "truncated": len(lines) > max_lines,
            "type": Path(file_path).suffix
        }
    except Exception as e:
        return {"error": str(e)}


def get_directory_context(dir_path: str = "projects", max_depth: int = 2) -> dict:
    """
    Get directory structure context.
    
    Args:
        dir_path: Directory path
        max_depth: Maximum depth to traverse
    
    Returns:
        dict: {files, directories}
    """
    try:
        abs_path = os.path.join("projects", dir_path) if dir_path != "projects" else "projects"
        if not os.path.exists(abs_path):
            return None

        file_list = []
        for root, dirs, files in os.walk(abs_path):
            depth = root.replace(abs_path, '').count(os.sep)
            if depth > max_depth:
                continue
            
            for file in files[:10]:  # Limit files per directory
                file_list.append({
                    "name": file,
                    "path": os.path.join(root, file).replace(abs_path, "").strip(os.sep),
                    "size": os.path.getsize(os.path.join(root, file))
                })

        return {
            "directory": dir_path,
            "files": file_list[:20],  # Limit total files
            "file_count": len(file_list)
        }
    except Exception as e:
        return {"error": str(e)}


def get_selected_code_context(code: str, language: str = "python") -> dict:
    """
    Get context from selected code snippet.
    
    Args:
        code: Code snippet
        language: Programming language
    
    Returns:
        dict: {code, language, lines}
    """
    lines = code.strip().split('\n')
    return {
        "code": code[:1000],  # Limit size
        "language": language,
        "lines": len(lines),
        "truncated": len(code) > 1000
    }


def prepare_agent_context(task: str, selected_code: str = None, active_file: str = None, 
                         project_dir: str = "projects") -> dict:
    """
    Prepare minimal context for agent task.
    Keep it under 2KB to minimize tokens.
    
    Args:
        task: User task description
        selected_code: Selected code if any
        active_file: Current active file if any
        project_dir: Project directory
    
    Returns:
        dict: Context object with file/code snippets
    """
    context = {
        "task": task,
        "files": [],
        "code": []
    }

    # Include selected code
    if selected_code:
        context["code"].append(get_selected_code_context(selected_code))

    # Include active file context
    if active_file:
        file_ctx = get_file_context(active_file, max_lines=30)
        if file_ctx and 'error' not in file_ctx:
            context["files"].append(file_ctx)

    # Include directory structure
    dir_ctx = get_directory_context(project_dir, max_depth=2)
    if dir_ctx and 'error' not in dir_ctx:
        context["project"] = dir_ctx

    return context


def format_context_for_llm(context: dict) -> str:
    """
    Format context as compact text for LLM prompt.
    Minimizes token usage.
    """
    lines = []

    if context.get("code"):
        lines.append("## Selected Code:")
        for code_ctx in context["code"]:
            if 'code' in code_ctx:
                lines.append(f"Language: {code_ctx.get('language', 'unknown')}")
                lines.append(f"```\n{code_ctx['code']}\n```")

    if context.get("files"):
        lines.append("\n## File Context:")
        for file_ctx in context["files"]:
            if 'error' not in file_ctx:
                lines.append(f"File: {file_ctx['filename']} ({file_ctx['total_lines']} lines)")
                file_content = ''.join(file_ctx.get('lines', [])[:20])
                lines.append(f"```\n{file_content}\n```")

    if context.get("project"):
        lines.append("\n## Project Structure:")
        files = context["project"].get("files", [])
        for f in files[:10]:
            lines.append(f"  - {f['path']}")

    return "\n".join(lines)
