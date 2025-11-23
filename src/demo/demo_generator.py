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

def _call_groq(prompt: str) -> str:
    # ... (API key check remains the same) ...
    api_key = os.getenv("GROQ_API_KEY")
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
        # This part handles non-200 errors correctly
        raise Exception(f"Groq API error: {response.status_code}. Response: {response.text}")

    # --- ADD THIS BLOCK FOR JSON EXTRACTION DEBUGGING ---
    try:
        data = response.json()
        
        # Check if the required path exists
        if 'choices' in data and data['choices'] and 'message' in data['choices'][0]:
            return data["choices"][0]["message"].get("content", "").strip()
        else:
            # Handle cases where status is 200 but content is missing
            print(f"⚠️ WARNING: Groq response 200, but JSON content is missing required keys.")
            print(f"Full Response JSON: {json.dumps(data, indent=2)}")
            return "" # Return empty string to signify failure

    except requests.exceptions.JSONDecodeError as e:
        # Handle malformed JSON response
        print(f"❌ ERROR: Failed to decode Groq response JSON. Error: {e}")
        print(f"Raw Response Text: {response.text}")
        return "" # Return empty string

    except Exception as e:
        # Catch any other extraction errors (like KeyError)
        print(f"❌ ERROR: Unexpected error during response parsing: {e}")
        print(f"Raw Response Text: {response.text}")
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
    print("here")
    print(answer)
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
    generated_code = _llm_generate_demo(scan_summary)

    return generated_code
