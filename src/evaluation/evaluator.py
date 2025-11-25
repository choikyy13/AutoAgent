import subprocess
import os
import time
from typing import Dict, Any
import requests
import json
from dotenv import load_dotenv
import sys

# Load environment variables (needed for LLM API Key)
load_dotenv()

# --- Scoring Constants ---
SCORE_SYNTAX = 1
SCORE_EXIT_CODE = 1
SCORE_RUN_TIME = 1
SCORE_STDOUT = 1
SCORE_STDERR = 1
MAX_LLM_QUALITATIVE_SCORE = 5
MAX_EXECUTION_TIME = 30 # seconds
MAX_TOTAL_SCORE = SCORE_SYNTAX + SCORE_EXIT_CODE + SCORE_RUN_TIME + SCORE_STDOUT + SCORE_STDERR + MAX_LLM_QUALITATIVE_SCORE

# =========================================================================
# LLM Interaction Helper (OpenAI Implementation)
# =========================================================================

def _call_openai(prompt: str) -> int:
    """Helper function to call the OpenAI API for scoring."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in environment. Qualitative score defaulted to 0.")
        return 0

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are an code reviewer tasked with evaluating generated demo scripts for software projects. "
        "Your goal is to assess the quality, but also the intent and potential of the generated code. "
        "However, award generous partial credit if the code's structure and logic were sound, even if execution failed due to environment-specific errors (like missing imports or file paths). "
        "You are evaluating on the content and quality of the code itself according to the paper's project summary provided. "
        "Score the demo on a scale of 0 to 5 (integer only) based on the criteria provided. "
        "Output ONLY a single integer score from 0 to 5. DO NOT include any extra text or explanation."
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        
        # Extract and sanitize the LLM response to get a score between 0 and 5
        content = response.json()["choices"][0]["message"]["content"].strip()
        
        # Robustly parse the integer score
        try:
            score_str = ''.join(filter(str.isdigit, content))
            score = int(score_str) if score_str else 0
            return max(0, min(MAX_LLM_QUALITATIVE_SCORE, score))
        except ValueError:
            print(f"Warning: LLM returned non-integer score: '{content}'. Defaulting to 0.")
            return 0
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling OpenAI API: {e}. Defaulting qualitative score to 0.")
        return 0


# =========================================================================
# LLM Judge Function
# =========================================================================

def get_llm_qualitative_score(demo_code: str, exec_results: Dict[str, Any], project_summary: Dict[str, Any]) -> int:
    """
    Asks an LLM (OpenAI) to score the demo code qualitatively (5 points) using a generous prompt.
    """
    # If there was a syntax error, the LLM score is automatically 0.
    if exec_results.get("status") == "syntax_error":
        return 0
    
    print("[EVALUATOR] Calling LLM (OpenAI) for qualitative scoring (5 points, Generous Mode)...")

    # --- GENEROUS USER PROMPT ---
    prompt = f"""
    Evaluate the following generated demo script for a project summarized below. Remember to be generous and focus on the *quality of the generated code* itself, regardless of execution failure due to external factors like missing pip dependencies.

    Project Summary:
    {json.dumps(project_summary, indent=2)}

    Generated Code (Focus on this):
    --------------------
    {demo_code}
    --------------------

    Execution Output (stdout):
    --------------------
    {exec_results["stdout"]}
    --------------------

    Execution Errors (stderr) - Use this only to assess if the error was due to bad code vs. environment (e.g., ModuleNotFoundError):
    --------------------
    {exec_results["stderr"]}
    --------------------

    Score the demo from 0 to {MAX_LLM_QUALITATIVE_SCORE} based on these revised, generous criteria:

    1. Relevance (2 points max): Did the code *attempt* to import and use the core functions of the project's library?
        - Award 2 points if the correct modules/functions were called, even if they failed to load.
        - Award 1 point if the code was syntactically Python but lacked specific project imports.

    2. Clarity (2 points max): Is the code logic clear, clean, and easy to understand? Does the code structure look professional (ignoring execution errors)?
        - Award 2 points if the logic is clear.
        - Award 1 point if the code looks like a raw conversion (e.g., from a notebook) but is syntactically sound.

    3. Completeness (1 point max): Did the code mock required data or call necessary setup steps?
        - Award 1 point if the code included any placeholder data or demonstrated an awareness of the necessary input structure.

    Output ONLY a single integer score from 0 to {MAX_LLM_QUALITATIVE_SCORE} (Sum of the above criteria).
    """
    
    return _call_openai(prompt)


# =========================================================================
# Execution and Automated Scoring (Remaining functions unchanged)
# =========================================================================

def execute_demo(demo_file_path: str, repo_path: str) -> Dict[str, Any]:
    # ... (function body remains the same as previous) ...
    # Omitted for brevity, but logically identical to the last version provided
    
    print(f"[EVALUATOR] Executing demo script: {os.path.basename(demo_file_path)}")
    
    # 1. Pre-Check for Syntax Error (Vital for score 1)
    try:
        with open(demo_file_path, "r", encoding="utf-8") as f:
            demo_code = f.read()
            compile(demo_code, demo_file_path, "exec")
    except SyntaxError as e:
        print(f"[EVALUATOR] Syntax Error detected in {os.path.basename(demo_file_path)}.")
        return {
            "status": "syntax_error",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"SyntaxError: {e}",
            "run_time": 0.0,
        }
    except FileNotFoundError:
        return {
            "status": "error",
            "exit_code": 1,
            "stdout": "",
            "stderr": "Demo file not found for execution.",
            "run_time": 0.0,
        }

    # 2. Subprocess Execution
    command = [sys.executable, os.path.basename(demo_file_path)] # Use sys.executable for 'python'

    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=MAX_EXECUTION_TIME,
            check=False
        )
        end_time = time.time()
        
        execution_output = {
            "status": "completed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "run_time": round(end_time - start_time, 2),
        }

    except subprocess.TimeoutExpired:
        end_time = time.time()
        execution_output = {
            "status": "timeout",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"Execution timed out after {MAX_EXECUTION_TIME} seconds.",
            "run_time": round(end_time - start_time, 2),
        }

    except Exception as e:
        execution_output = {
            "status": "error",
            "exit_code": 1,
            "stdout": "",
            "stderr": f"Subprocess setup error: {str(e)}",
            "run_time": 0.0,
        }

    return execution_output


def evaluate_demo(demo_code: str, exec_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies the automated 5-point scoring system to the execution results.
    """
    print("[EVALUATOR] Scoring demo execution (5 Binary Points)...")
    
    score_breakdown = {
        "syntax_error": 0,
        "exit_code_0": 0,
        "within_time": 0,
        "prints_output": 0,
        "no_stderr": 0,
        "llm_qualitative": 0, 
    }
    
    # Check 1: No Syntax Error
    if exec_results.get("status") != "syntax_error":
        score_breakdown["syntax_error"] = SCORE_SYNTAX
        print("✓ Syntax check passed.")
    else:
        print("✗ Syntax Error detected.")

    # Check 2: Exit Code 0 (Success)
    if exec_results["exit_code"] == 0 and exec_results["status"] == "completed":
        score_breakdown["exit_code_0"] = SCORE_EXIT_CODE
        print("✓ Exit Code 0.")
    else:
        print(f"✗ Non-zero exit code or failed status: {exec_results['exit_code']} ({exec_results['status']}).")

    # Check 3: Finishes within reasonable time
    if exec_results["run_time"] < MAX_EXECUTION_TIME and exec_results["status"] != "timeout":
        score_breakdown["within_time"] = SCORE_RUN_TIME
        print(f"✓ Completed within {MAX_EXECUTION_TIME}s ({exec_results['run_time']}s).")
    else:
        print(f"✗ Execution time exceeded {MAX_EXECUTION_TIME}s or timed out.")

    # Check 4: Prints something (positive confirmation)
    if exec_results["stdout"].strip():
        score_breakdown["prints_output"] = SCORE_STDOUT
        print("✓ Printed output detected.")
    else:
        print("✗ No output printed to stdout.")

    # Check 5: No error in stderr
    if not exec_results["stderr"].strip():
        score_breakdown["no_stderr"] = SCORE_STDERR
        print("✓ No errors in stderr.")
    else:
        print("✗ Errors detected in stderr.")
        print("   --- Stderr Output ---\n" + exec_results["stderr"].strip())
    
    total_automated_score = sum(score_breakdown.values()) - score_breakdown["llm_qualitative"]

    return {
        "total_automated_score": total_automated_score,
        "score_breakdown": score_breakdown
    }

def run_evaluation_pipeline(demo_code: str, demo_file_path: str, repo_path: str, project_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs the full execution and scoring sequence, including the LLM qualitative score.
    """
    exec_results = execute_demo(demo_file_path, repo_path)
    eval_results = evaluate_demo(demo_code, exec_results)
    
    # Step 3: Get LLM Qualitative Score (Out of 5)
    llm_score = get_llm_qualitative_score(demo_code, exec_results, project_summary)
    
    final_total_score = eval_results["total_automated_score"] + llm_score
    eval_results["score_breakdown"]["llm_qualitative"] = llm_score

    print(f"[EVALUATOR] LLM Qualitative Score: {llm_score} / {MAX_LLM_QUALITATIVE_SCORE}")
    print(f"[EVALUATOR] TOTAL SCORE: {final_total_score} / {MAX_TOTAL_SCORE}")

    return {
        "execution_results": exec_results,
        "evaluation_results": {
            "total_score": final_total_score,
            "total_automated_score": eval_results["total_automated_score"],
            "llm_qualitative_score": llm_score,
            "score_breakdown": eval_results["score_breakdown"]
        }
    }