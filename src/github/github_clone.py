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
