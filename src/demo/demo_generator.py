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

def _call_groq(prompt: str) -> str:
    # call Groq API through http requests
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set. Please set it in your environment variables.")
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 200
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code}")
    
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
    You are an expert software engineer.

    Project summary:
    {scan_summary}

    Demo file contents:
    --------------------
    {demo_code}
    --------------------

    Is this demo runnable and correct for this project?
    Answer strictly: YES or NO.
    """

    answer = _call_groq(prompt).strip().upper()

    return "YES" in answer


def _llm_generate_demo(scan_summary: str) -> str:
    """
    Ask AI to generate a runnable demo code file.
    """

    prompt = f"""
    You are a code generation expert.

    Given this project structure summary:
    {scan_summary}

    Generate a SINGLE runnable demo script that:
    - imports required modules
    - uses detected entrypoints if available
    - shows a minimal working example
    - does NOT include explanations or markdown
    - returns ONLY pure code

    Return only the code.
    """

    return _call_groq(prompt)




def generate_demo(scan_output: Dict, repo_path: str) -> str:
    """
    Main function:
    - If demo file exists → validate via LLM
    - If valid → return its CONTENT
    - Else → generate new demo via LLM and return CONTENT
    """
    print("DEMO GENERATOR START")
    scan_summary = scan_output.get("repo_summary", "No summary available.")
    demo_files = scan_output.get("demos", [])

    # 1. If existing demos are found -> validate
    for demo in demo_files:
        abs_path = os.path.join(repo_path, demo)
        source = _read_file(abs_path)

        if not source.strip():
            continue

        print(f"Checking existing demo: {demo}")
        if _llm_validate_demo(scan_summary, source):
            print("✓ LLM approved existing demo.")
            return source  # Return raw code

        print("✗ LLM rejected this demo. Trying next…")

    # 2. Otherwise: generate new demo
    print("No valid demo found — generating a new one with LLM…")
    generated_code = _llm_generate_demo(scan_summary)

    return generated_code
