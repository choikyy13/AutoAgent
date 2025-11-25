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

import os
from typing import Dict, List
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def _call_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY is not set in the environment variables.")

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",   # or any: gpt-4o, gpt-4.1, o1-mini, etc.
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 512
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"OpenAI API error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

def _read_file(path: str) -> str:
    """Read a file safely."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def _llm_validate_demo(scan_summary: str, demo_code: str) -> bool:
    """
    Ask LLM whether an existing demo file is valid.
    Returns True/False.
    """

    prompt = f"""
    You are validating a demo code file for a project.

    Project summary:
    {scan_summary}

    Demo file contents:
    --------------------
    {demo_code}
    --------------------

    Is this demo runnable and demonstrates the project?
    
    Requirements for YES:
    - If the file is a .md file, it is not valid.
    - The code must be syntactically correct.
    - It must import necessary modules from the project.
    - Shows a working example of the main functionality.
    - Not just comments or pseudocode.
    - It must be runnable.

    answer with ONLY: YES or NO.

    DO NOT include any punctuation, explanation, or code block markers.
    """

    answer = _call_openai(prompt).upper()
    return "YES" in answer


def _llm_generate_demo(scan_summary: str, repo_path: str) -> str:
    """
    Ask AI to generate a runnable demo code file.
    """

    readme = _read_file(os.path.join(repo_path, "README.md"))[:2000]

    # Find actual example
    example_files = scan_summary.get("demos", [])
    example_content = ""
    if example_files:
        example_content = _read_file(
            os.path.join(repo_path, example_files[0])
        )[:1000]

    prompt = f"""
    You are a code generation expert. Your primary goal is to generate a script that runs successfully.

    Given this project structure summary:
    {scan_summary}

    README excerpt:
    {readme}

    Example file excerpt (if any):
    {example_content}

    Generate a SINGLE runnable demo script that:
    1. **Dependency Check (CRITICAL):** Includes necessary standard Python imports (os, sys, subprocess) at the top. For any external library required (e.g., 'fire', 'torch', 'scipy'), you MUST write a self-installing try/except block.

    Example of required self-installing block:
    import os
    import sys
    import subprocess
    
    def install_missing_dependency(package_name):
        print(f"Installing missing dependency: {{package_name}}...")
        # Use subprocess to ensure it runs correctly inside the container
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

    try:
        import <external_library>
    except ImportError:
        install_missing_dependency("<external_library>")
        import <external_library>
    
    2. Imports required project modules from the cloned repository.
    3. Has no TODOs or placeholders.
    4. Uses detected entrypoints if available.
    5. Shows a minimal working example that produces clean, informative output to stdout.

    Return only the python code for the demo script.
    REPEAT: ONLY THE CODE, NO EXTRA TEXT, NO CODE BLOCK MARKERS (e.g., ```python).

    """
    
    return _call_openai(prompt)

def generate_demo(scan_output: Dict, repo_path: str) -> str:
    """
    Main function:
    - If demo file exists → validate via LLM
    - If valid → return its CONTENT
    - Else → generate new demo via LLM and return CONTENT
    """
    print("DEMO GENERATOR START")
    scan_summary = scan_output
    demo_files = scan_output.get("demos", [])

    # 1. If existing demos are found -> validate
    for demo in demo_files:
        abs_path = os.path.join(repo_path, demo)
        source = _read_file(abs_path)

        #if not source.strip():
         #   continue

        print(f"Checking existing demo: {demo}")
        if _llm_validate_demo(scan_summary, source):
            print("LLM approved existing demo.")
            return source  # Return raw code

        print("LLM rejected this demo. Trying next…")

    # 2. Otherwise: generate new demo
    print("No valid demo found — generating a new one with LLM…")
    generated_code = _llm_generate_demo(scan_summary, repo_path)

    try:
        compile(generated_code, "<string>", "exec")
        print("Generated demo code is syntactically valid.")
    
    except SyntaxError as e:
        print(f"Generated demo code has syntax errors: {e}")
    
    return generated_code
