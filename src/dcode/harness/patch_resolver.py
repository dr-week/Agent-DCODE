"""
Surgical Patch Conflict Resolver with Fuzzy Matching.
Applies surgical replace edits with tolerance for whitespace and minor line shifts.
"""

import difflib
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


class PatchResolver:
    """Applies surgical edits using exact, whitespace-tolerant, and fuzzy matching."""

    @staticmethod
    def apply_replacement(source_text: str, target: str, replacement: str) -> Tuple[bool, str, str]:
        """Apply replacement returning (success, new_text, match_method)."""
        if not target:
            return False, source_text, "empty_target"
        if target in source_text:
            return True, source_text.replace(target, replacement, 1), "exact"

        # Whitespace-insensitive line matching
        target_lines = [l.strip() for l in target.splitlines() if l.strip()]
        source_lines = source_text.splitlines()

        for i in range(len(source_lines) - len(target_lines) + 1):
            window = [source_lines[i + j].strip() for j in range(len(target_lines))]
            if window == target_lines:
                before = "\n".join(source_lines[:i])
                after = "\n".join(source_lines[i + len(target_lines):])
                merged = f"{before}\n{replacement}\n{after}".strip()
                return True, merged, "whitespace_normalized"

        # Fuzzy sequence matching (>0.85 ratio)
        matcher = difflib.SequenceMatcher(None, target, source_text)
        match = matcher.find_longest_match(0, len(target), 0, len(source_text))
        if match.size >= int(len(target) * 0.85):
            new_text = source_text[:match.b] + replacement + source_text[match.b + match.size:]
            return True, new_text, "fuzzy_similarity"

        return False, source_text, "no_match"

    @classmethod
    def patch_file(cls, file_path: str | Path, target: str, replacement: str) -> Dict[str, Any]:
        """Read file, apply patch, and save if successful."""
        path = Path(file_path)
        if not path.is_file():
            return {"success": False, "error": f"File not found: {file_path}", "method": "none"}
        try:
            content = path.read_text(encoding="utf-8")
            ok, new_content, method = cls.apply_replacement(content, target, replacement)
            if ok:
                path.write_text(new_content, encoding="utf-8")
            return {"success": ok, "method": method, "modified": ok}
        except Exception as e:
            return {"success": False, "error": str(e), "method": "error"}
