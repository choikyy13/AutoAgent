"""
github_finder.py

Determines WHICH GitHub repository from the PDF is the one we should clone.

Responsibilities:
- Use LLM to match paper content to repo descriptions
- Filter out irrelevant links (e.g., PDF links, subfolders)

This gives us stable and reliable repo selection.
"""

import os
import re
from typing import List
import requests

from dotenv import load_dotenv
load_dotenv()  # This reads .env files in the project root

def select_best_repository(github_links: List[str], paper_text: str) -> str:
    # only one repo in the list
    if len(github_links) == 1:
        print(f"[FINDER] Only one repo: {github_links[0]}")
        return github_links[0]
    
    # no repo in the list
    if not github_links:
        raise ValueError("No GitHub links provided")
        
    # Format repos for LLM
    repos_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(github_links)])
    
    # Truncate paper to first 2000 chars 
    paper_summary = paper_text[:2000]
    
    # Create prompt for the LLM
    prompt = f"""You are analyzing a scientific paper to find its most relevant GitHub repository.

Paper Summary:
{paper_summary}

List of GitHub Repositories to choose from (only consider these):
{repos_text}

Which repository is the PRIMARY implementation described in this paper?
- It should be the actual project code, not a citation or dependency
- The name/description should match the paper's topic
- Ignore examples, forks, or tutorial repositories

Respond with ONLY the number (1, 2, 3, etc.) and brief reason.
Format: "Repository X: [reason]"
"""
    
    # Call LLM
    try:
        answer = _call_groq(prompt)
        print(f"[LLM] {answer}")
        
        # Parse response
        match = re.search(r'Repository\s+(\d+)', answer, re.IGNORECASE)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(github_links):
                selected = github_links[idx]
                print(f"[FINDER] Selected: {selected}")
                return selected
    
    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
    
    # Fallback: return first repo
    print(f"[FINDER] Falling back to first repo: {github_links[0]}")
    return github_links[0]


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
