"""
Centralized configuration for Agent-DCODE.
Consolidates paths, ports, and model configurations across all modules.
"""

import os
from pathlib import Path

# Repository root directory
PROJECT_ROOT = Path(os.getenv("DCODE_ROOT", Path(__file__).resolve().parents[2]))

# Sandboxed workspace & logs directories
PROJECTS_DIR = Path(os.getenv("DCODE_PROJECTS_DIR", PROJECT_ROOT / "projects")).resolve()
LOGS_DIR = Path(os.getenv("DCODE_LOGS_DIR", PROJECT_ROOT / ".logs")).resolve()

# Ensure workspace directories exist
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# LLM Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_GENERATE_URL = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
OLLAMA_MODEL = os.getenv("DCODE_MODEL", "qwen2.5-coder:7b")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Server & Orchestrator Configuration
BACKEND_HOST = os.getenv("DCODE_BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("DCODE_BACKEND_PORT", "5000"))
OLLAMA_PORT = int(os.getenv("DCODE_OLLAMA_PORT", "11434"))
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("DCODE_TIMEOUT", "30"))
MAX_LOG_ENTRIES = int(os.getenv("DCODE_MAX_LOGS", "20"))
