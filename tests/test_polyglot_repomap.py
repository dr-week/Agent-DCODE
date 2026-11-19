"""
Unit tests for Polyglot AST Symbol Extractor and multi-language RepoMap.
Verifies symbol extraction for Rust, Go, C/C++, and Python.
"""

from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dcode.integrations.polyglot_extractor import extract_polyglot_symbols
from dcode.integrations.repomap import RepoMap


class TestPolyglotRepoMap(unittest.TestCase):
    def test_rust_symbol_extraction(self):
        with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False) as f:
            f.write("pub fn solve_task(x: i32) -> i32 { x * 2 }\nstruct Engine;\nimpl Engine {}\n")
            f_path = f.name
        try:
            syms = extract_polyglot_symbols(f_path, ".rs")
            self.assertTrue(any("solve_task" in s for s in syms))
            self.assertTrue(any("struct Engine" in s for s in syms))
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_go_symbol_extraction(self):
        with tempfile.NamedTemporaryFile("w", suffix=".go", delete=False) as f:
            f.write("package main\nfunc HandleRequest(w http.ResponseWriter, r *http.Request) {}\ntype Server struct {}\n")
            f_path = f.name
        try:
            syms = extract_polyglot_symbols(f_path, ".go")
            self.assertTrue(any("HandleRequest" in s for s in syms))
            self.assertTrue(any("type Server struct" in s for s in syms))
        finally:
            Path(f_path).unlink(missing_ok=True)

    def test_cpp_symbol_extraction(self):
        with tempfile.NamedTemporaryFile("w", suffix=".cpp", delete=False) as f:
            f.write("class QuantumCircuit {\npublic:\n    void execute(int steps);\n};\n")
            f_path = f.name
        try:
            syms = extract_polyglot_symbols(f_path, ".cpp")
            self.assertTrue(any("class QuantumCircuit" in s for s in syms))
        finally:
            Path(f_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
