import requests
import os
from typing import List, Dict
import json

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

# ------------------------------------------------------------
# 1. Detect languages
# ------------------------------------------------------------
def detect_languages(files: List[str]) -> List[str]:
    """
    Detect project languages based on file extensions.
    Returns a list of languages (not a single mixed label).
    """
    languages = set()

    for f in files:
        if f.endswith(".py"):
            languages.add("python")
        elif f.endswith(".cpp") or f.endswith(".hpp") or f.endswith(".cc"):
            languages.add("cpp")
        elif f.endswith(".js") or f.endswith(".jsx"):
            languages.add("javascript")
        elif f.endswith(".ts") or f.endswith(".tsx"):
            languages.add("typescript")
        elif f.endswith(".java"):
            languages.add("java")

    return sorted(list(languages))



# ------------------------------------------------------------
# 2. Detect model files
# ------------------------------------------------------------
def detect_models(files: List[str]) -> List[str]:
    """
    Detect model-related files using simple keyword heuristics + optional LLM refinement.
    """
    model_keywords = ["model", "weights", "checkpoint", "ckpt", "pkl", "onnx", "h5"]

    detected = [f for f in files if any(k in f.lower() for k in model_keywords)]

    # If nothing found, use LLM guessing
    if not detected:
        try:
            prompt = (
                "Given this list of files, which ones look like AI/ML model files?\n\n"
                + "\n".join(files)
                + "\n\nReturn ONLY a JSON array of filenames."
            )
            ai_resp = _call_openai(prompt)
            # Attempt to parse JSON
            
            arr = json.loads(ai_resp)
            if isinstance(arr, list):
                detected = arr
        except:
            pass

    return detected



# ------------------------------------------------------------
# 3. Detect config files
# ------------------------------------------------------------
def detect_configs(files: List[str]) -> List[str]:
    """
    Detect configuration files:
    - .yml / .yaml
    - .json
    - .cfg
    - .ini
    """

    config_ext = (".yml", ".yaml", ".json", ".cfg", ".ini")

    heuristics_found = [f for f in files if f.endswith(config_ext)]

    if heuristics_found:
        return heuristics_found

    # LLM fallback
    try:
        prompt = (
            "Given this list of files, which ones are configuration files?\n\n"
            + "\n".join(files)
            + "\n\nReturn JSON array only."
        )
        resp = _call_openai(prompt)
        
        arr = json.loads(resp)
        if isinstance(arr, list):
            return arr
    except:
        pass

    return []



# ------------------------------------------------------------
# 4. Detect entrypoints
# ------------------------------------------------------------
def detect_entrypoints(repo_path: str, files: List[str]) -> List[str]:
    """
    Detect executable entrypoints:
    - main.py
    - run.py
    - "__main__" inside Python files
    """
    entrypoints = []

    # Heuristic 1: filename pattern
    for f in files:
        name = os.path.basename(f).lower()
        if name in ("main.py", "run.py", "app.py", "server.py"):
            entrypoints.append(f)

    # Heuristic 2: search for __main__
    for f in files:
        if f.endswith(".py"):
            abs_path = os.path.join(repo_path, f)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as file:
                    if "__main__" in file.read():
                        entrypoints.append(f)
            except:
                pass

    # Remove duplicates
    entrypoints = sorted(list(set(entrypoints)))

    # AI refinement
    try:
        prompt = (
            "Given this project file list, which files are executable entrypoints?\n\n"
            + "\n".join(files)
            + "\n\nReturn JSON array only."
        )
        ai_resp = _call_openai(prompt)
        
        arr = json.loads(ai_resp)
        if isinstance(arr, list):
            # merge results
            for f in arr:
                entrypoints.append(f)
        entrypoints = sorted(list(set(entrypoints)))
    except:
        pass

    return entrypoints



# ------------------------------------------------------------
# 5. Detect demo/tutorial/example files
# ------------------------------------------------------------
def detect_demo_files(files: List[str]) -> List[str]:
    """
    Detect demo/example/tutorial files:
    Heuristics + optional AI refinement.
    """
    demo_keywords = ["demo", "example", "examples", "tutorial", "usage"]

    detected = [f for f in files if any(k in f.lower() for k in demo_keywords)]

    # AI refinement
    try:
        prompt = (
            "Which files appear to be demo/example/tutorial files?\n\nFiles:\n"
            + "\n".join(files)
            + "\n\nReturn JSON array only."
        )
        ai_resp = _call_openai(prompt)
        
        arr = json.loads(ai_resp)
        if isinstance(arr, list):
            detected.extend(arr)
    except:
        pass

    # Remove duplicates
    return sorted(list(set(detected)))



# ------------------------------------------------------------
# 6. Summarize for LLM
# ------------------------------------------------------------
def summarize_for_llm(repo_path: str, files: List[str]) -> str:
    """
    Build a structured summary of the repo for the LLM.
    """
    languages = detect_languages(files)
    configs = detect_configs(files)
    demos = detect_demo_files(files)
    models = detect_models(files)
    entrypoints = detect_entrypoints(repo_path, files)

    folders = sorted({os.path.dirname(f) for f in files})

    summary = {
        "num_files": len(files),
        "languages": languages,
        "folders": folders,
        "configs": configs,
        "models": models,
        "demos": demos,
        "entrypoints": entrypoints,
    }

    return json.dumps(summary, indent=4)



# ------------------------------------------------------------
# 7. Scan repository (main function)
# ------------------------------------------------------------
def scan_repository(repo_path: str) -> Dict:
    """
    Walk through repo and return a dictionary of detected components.
    """
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), repo_path)
            all_files.append(rel.replace("\\", "/"))

    summary_text = summarize_for_llm(repo_path, all_files)

    # return parsed dict
    return json.loads(summary_text)
