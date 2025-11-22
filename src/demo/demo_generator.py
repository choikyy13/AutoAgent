"""
demo_generator.py
------------------
Uses an LLM (OpenAI/Gemini/Constructor) to generate a runnable demo script.

Responsibilities:
- Take code summary from code_scanner
- Build an LLM prompt describing the project
- Ask LLM to generate:
      - a minimal runnable demo.py
      - OR instructions for running the project
- Save the demo file into the repo folder

This file contains ALL LLM interactions.
The rest of the repo never talks to the model.
"""
