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
