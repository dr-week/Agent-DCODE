"""
Context Compressor: Token Budgeting & Relevance Pruning.
Filters symbol maps and diffs to prevent LLM context saturation on large codebases.
"""

from typing import Dict, List, Optional


class ContextCompressor:
    """Compresses repository maps, diffs, and file contexts under token budgets."""

    @staticmethod
    def prune_symbol_map(
        symbol_map: Dict[str, List[str]],
        query: Optional[str] = None,
        max_symbols: int = 150,
        max_tokens: int = 2000,
    ) -> Dict[str, List[str]]:
        """Filter symbols by query relevance or core path heuristics within token budget."""
        if not symbol_map:
            return {}
        query_words = set(query.lower().split()) if query else set()

        def score_entry(rel_path: str, syms: List[str]) -> float:
            score = 0.0
            p_lower = rel_path.lower()
            if any(core in p_lower for core in ["core", "main", "app", "api", "cli"]):
                score += 2.0
            if query_words:
                matched_words = sum(1 for w in query_words if w in p_lower)
                score += matched_words * 3.0
                for s in syms:
                    score += sum(0.5 for w in query_words if w in s.lower())
            return score

        sorted_files = sorted(symbol_map.keys(), key=lambda f: score_entry(f, symbol_map[f]), reverse=True)
        pruned: Dict[str, List[str]] = {}
        total_syms = 0
        est_tokens = 0

        for fpath in sorted_files:
            syms = symbol_map[fpath]
            selected = syms[:15]
            pruned[fpath] = selected
            total_syms += len(selected)
            est_tokens += len(fpath) // 4 + sum(len(s) // 4 for s in selected)
            if total_syms >= max_symbols or est_tokens >= max_tokens:
                break
        return pruned

    @staticmethod
    def compress_diff(diff_text: str, max_lines: int = 120) -> str:
        """Condense large unified diffs while preserving file headers and hunks."""
        lines = diff_text.splitlines()
        if len(lines) <= max_lines:
            return diff_text
        retained = []
        for line in lines:
            if line.startswith(("---", "+++", "@@", "diff --git")):
                retained.append(line)
            elif line.startswith(("+", "-")) and len(retained) < max_lines - 10:
                retained.append(line)
        retained.append(f"... [Diff truncated: {len(lines) - len(retained)} context lines omitted]")
        return "\n".join(retained)
