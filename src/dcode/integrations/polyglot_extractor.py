"""
Polyglot AST Symbol Extractor for Rust, Go, C/C++, and Shell.
Extracts function, struct, and class signatures using regex-based AST heuristics.
"""

from pathlib import Path
import re
from typing import List

RUST_PATTERNS = re.compile(r"(?:pub\s+)?(?:fn\s+\w+\s*\([^)]*\)|struct\s+\w+|impl\s+\w+)")
GO_PATTERNS = re.compile(r"(?:func\s+(?:\([^)]+\)\s+)?\w+\s*\([^)]*\)|type\s+\w+\s+(?:struct|interface))")
CPP_PATTERNS = re.compile(r"(?:(?:class|struct)\s+\w+|(?:void|int|bool|double|float|auto|\w+::\w+)\s+\w+\s*\([^)]*\)\s*(?:const)?\s*\{?)")
SH_PATTERNS = re.compile(r"(?:function\s+\w+|\b\w+\s*\(\)\s*\{)")


def extract_polyglot_symbols(file_path: str, ext: str) -> List[str]:
    """Extract symbol signatures from Rust, Go, C/C++, or Shell source files."""
    try:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    ext_clean = ext.lower().lstrip(".")
    if ext_clean == "rs":
        matches = RUST_PATTERNS.findall(text)
    elif ext_clean == "go":
        matches = GO_PATTERNS.findall(text)
    elif ext_clean in {"c", "cpp", "cc", "h", "hpp"}:
        matches = CPP_PATTERNS.findall(text)
    elif ext_clean in {"sh", "bash"}:
        matches = SH_PATTERNS.findall(text)
    else:
        matches = []

    return [m.strip().rstrip("{").strip() for m in matches[:25]]
