"""
github_finder.py

Determines WHICH GitHub repository from the PDF is the one we should clone.

Responsibilities:
- Clean and normalize GitHub URLs
- Remove duplicates
- Filter out irrelevant links (e.g., PDF links, subfolders)
- Ping each repo using GitHub API to check:
    • existence
    • stars
    • code language distribution
    • size
- Score them and return the "best" repo.

This gives us stable and reliable repo selection.
"""

"""
github_finder.py

Uses LLM to select the best GitHub repository from those found in a paper.
Simple, direct approach - just one LLM call.
"""

import os
import re
from typing import List
import requests

from dotenv import load_dotenv
load_dotenv()  # This reads .env files in the project root

def select_best_repository(github_links: List[str], paper_text: str) -> str:
    """
    Use LLM to pick the best repository from the paper.
    
    Args:
        github_links: List of GitHub URLs from the PDF
        paper_text: Text extracted from the paper
        
    Returns:
        URL of the best repository
    """
    # Edge case: only one repo
    if len(github_links) == 1:
        print(f"[FINDER] Only one repo: {github_links[0]}")
        return github_links[0]
    
    # Edge case: no repos
    if not github_links:
        raise ValueError("No GitHub links provided")
    
    print(f"[FINDER] Found {len(github_links)} repos, asking LLM to choose...")
    
    # Format repos for LLM
    repos_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(github_links)])
    
    # Truncate paper to first 2000 chars (save tokens)
    paper_summary = paper_text[:2000]
    
    # Create prompt
    prompt = f"""You are analyzing a scientific paper to find its MAIN GitHub repository.

PAPER EXCERPT:
{paper_summary}

GITHUB REPOSITORIES MENTIONED:
{repos_text}

Which repository is the PRIMARY implementation described in this paper?
- It should be the actual project code, not a citation or dependency
- The name/description should match the paper's topic
- Ignore examples, forks, or tutorial repos

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
    """Call Groq API via direct HTTP request."""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise Exception("GROQ_API_KEY not set. Get free key at: https://console.groq.com/")
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "moonshotai/kimi-k2-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 200
        },
        timeout=30
    )
    
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code}")
    
    return response.json()["choices"][0]["message"]["content"]


# Quick test
if __name__ == "__main__":
    test_links = [
        "https://github.com/RadonPy/RadonPy",
        "https://github.com/numpy/numpy"
    ]
    test_paper = "This paper introduces RadonPy, a Python package for molecular dynamics..."
    
    result = select_best_repository(test_links, test_paper)
    print(f"\nResult: {result}")