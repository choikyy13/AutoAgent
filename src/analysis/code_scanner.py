"""
code_scanner.py
----------------
Analyzes the local cloned repository.

Responsibilities:
- Walk through the repo file structure
- Identify project type (Python, JS, C++, mixed, etc.)
- Summarize important files (main scripts, models, configs)
- Detect entry points (main methods, CLI tools)
- Return a structured summary for LLM consumption

This module does NOT run any code.
It only inspects files.
"""
