"""
code_scanner.py
----------------
Analyzes the local cloned repository.

Responsibilities:
- Walk through the repo file structure
- Identify project type (Python, JS, C++, mixed, etc.)
- Summarize important files (main scripts, models, configs)
- Detect entry points (main methods, CLI tools)
- Check if a demo file is already present there.
- Return a structured summary for LLM consumption

This module does NOT run any code.
It only inspects files.
"""

from typing import List, Dict, Any

def list_all_files(repo_path: str) -> List[str]:
    """
    Recursively list all files in the repository (relative paths).
    """
    pass


def detect_project_type(files: List[str]) -> str:
    """
    Determine if repo is Python, JS, C++, mixed, or unknown.
    """
    pass


def detect_models(files: List[str]) -> List[str]:
    """
    Detect model-related files (heuristic keywords).
    """
    pass


def detect_configs(files: List[str]) -> List[str]:
    """
    Detect config files (.yaml, .json, .cfg, etc.).
    """
    pass


def detect_entrypoints(repo_path: str, files: List[str]) -> List[str]:
    """
    Detect entrypoints (main.py, run.py, or files with __main__ block).
    """
    pass


def detect_existing_demo(files: List[str]) -> List[str]:
    """
    Detect demo/example/tutorial files already present.
    """
    pass


def scan_repository(repo_path: str) -> Dict[str, Any]:
    """
    Main coordinator:
    - list files
    - detect type
    - detect models/configs
    - detect entrypoints
    - detect demo scripts
    Returns a structured summary dict.
    """
    pass