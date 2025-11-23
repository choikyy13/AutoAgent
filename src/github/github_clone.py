"""
github_clone.py
----------------
Handles cloning of GitHub repositories.

Responsibilities:
- Clone a GitHub repo into ./ImportedProjects/<repo_name>
- Handle cases where the repo already exists (overwrite or skip)
- Return the local filesystem path to the cloned repo

This file must only do:
    repo_url -> local_path
No scanning, no analysis.
"""
import os
import shutil
from git import Repo

def clone_repository(repo_url: str, base_folder: str = "ImportedProjects") -> str:
    """
    Returns: Local path to the cloned repository
    Exception: If cloning fails
    """
    print(f"Starting clone of: {repo_url}")
    
    repo_name = _extract_repo_name(repo_url)
    
    # Create base folder if it doesn't exist
    os.makedirs(base_folder, exist_ok=True)
    
    # Generate unique folder name
    target_folder = _generate_unique_folder(base_folder, repo_name)
    
    print(f"Cloning into: {target_folder}")
    
    try:
        # Clone the repository
        Repo.clone_from(repo_url, target_folder)
        
        print(f"Successfully cloned to {target_folder}")
        return target_folder
        
    except Exception as e:
        # Clean up partial clone if it failed
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        
        raise Exception(f"Failed to clone {repo_url}: {e}")


def _extract_repo_name(repo_url: str) -> str:
    # Remove trailing .git if present
    url = repo_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]
    
    # Extract last part of URL
    parts = url.split('/')
    if len(parts) >= 2:
        return parts[-1]
    
    return "repository"  # Fallback


def _generate_unique_folder(base_folder: str, repo_name: str) -> str:
    """
    Generates a unique folder name in the base_folder for the given repo_name.
    """
    target = os.path.join(base_folder, repo_name)
    
    # If folder doesn't exist, use it
    if not os.path.exists(target):
        return target
    
    # Otherwise, add incrementing number
    counter = 1
    while True:
        target = os.path.join(base_folder, f"{repo_name}_{counter}")
        if not os.path.exists(target):
            return target
        counter += 1