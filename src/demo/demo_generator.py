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

def _call_groq(prompt: str, max_tokens: int = 5) -> str:
    # call groq API through http requests
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set. Please set it in your environment variables.")

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",  # ✅ CORRECT MODEL!
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,  # Slight creativity helps
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ groq API error {response.status_code}: {response.text}")
            return ""
        
        data = response.json()
        
        # Validate response structure
        if 'choices' in data and data['choices'] and 'message' in data['choices'][0]:
            content = data["choices"][0]["message"].get("content", "").strip()
            
            if not content:
                print("⚠️ LLM returned empty content")
                print(f"Full response: {json.dumps(data, indent=2)}")
            
            return content
        else:
            print(f"⚠️ Unexpected response structure: {json.dumps(data, indent=2)}")
            return ""
            
    except Exception as e:
        print(f"❌ Error calling groq: {e}")
        return ""

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
    - The code must be syntactically correct.
    - It must import necessary modules from the project.
    - Shows a working example of the main functionality.
    - Not just comments or pseudocode.

    answer with ONLY: YES or NO.

    DO NOT include any punctuation, explanation, or code block markers.
    """

    answer = _call_groq(prompt).upper()
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
    You are a code generation expert.

    Given this project structure summary:
    {scan_summary}

    README excerpt:
    {readme}

    Example file excerpt (if any):
    {example_content}

    Generate a SINGLE runnable demo script that:
    - imports required modules
    - has no TODOs or placeholders
    - uses detected entrypoints if available
    - shows a minimal working example
    - does NOT include explanations or markdown
    - returns ONLY pure code

    Return only the python code for the demo script, no explanations.
    REPEAT: ONLY THE CODE, NO EXTRA TEXT. 
    Don't add any intro or explanation. JUST THE RAW CODE.
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
            print("✓ LLM approved existing demo.")
            return source  # Return raw code

        print("✗ LLM rejected this demo. Trying next…")

    # 2. Otherwise: generate new demo
    print("No valid demo found — generating a new one with LLM…")
    generated_code = _llm_generate_demo(scan_summary, repo_path)

    try:
        compile(generated_code, "<string>", "exec")
        print("Generated demo code is syntactically valid.")
    
    except SyntaxError as e:
        print(f"Generated demo code has syntax errors: {e}")
    
    return generated_code
