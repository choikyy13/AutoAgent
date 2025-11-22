import os
import tempfile
import requests
from pdfminer.high_level import extract_text
import re
from typing import List

"""
pdf_extractor.py

Responsible ONLY for handling PDF document operations.

Functions:
- download_pdf(url) — saves to /tmp and returns file path
- extract_text(pdf_path) — returns raw text from the PDF
- extract_github_links(pdf_text) — regex scan for GitHub URLs

This module does NOT:
- Call any LLMs
- Clone repos
- Analyze code

Its role is strictly PDF → text → GitHub links.
"""

def download_pdf(url: str) -> str:
    """Download the PDF from the URL and return the local path."""
    """
    Download a PDF from the given URL and save it into a temporary file.
    Returns the local file path.
    """

    print(f"[PDF] Downloading: {url}")

    # 1. Download raw HTTP content
    response = requests.get(url, timeout=20)
    response.raise_for_status()# catchers errors

    # 2. Create a temporary file path
    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)   # Close file descriptor, we will write manually

    # 3. Write binary PDF bytes
    with open(tmp_path, "wb") as f:
        f.write(response.content)

    print(f"[PDF] Saved to {tmp_path}")
    return tmp_path

def extract_text_local(pdf_path: str) -> str:
    """Return all readable text from the PDF."""
    """
    Extract raw text from a PDF file using pdfminer.
    Returns the extracted text as a clean string.
    """

    print(f"[PDF] Extracting text from: {pdf_path}")

    try:
        # 1. Let pdfminer do the extraction
        raw_text = extract_text(pdf_path)

    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

    # 2. Clean whitespace (optional but improves analysis)
    cleaned = re.sub(r"\s+", " ", raw_text).strip()

    print(f"[PDF] Extracted {len(cleaned)} characters")
    return cleaned

def extract_github_links(text: str) -> list[str]:
    """Return all GitHub links found inside the PDF text."""
    """
    Extract GitHub repository URLs from a given text.
    Returns a clean list of normalized URLs (no duplicates).
    """

    print("[GITHUB] Scanning text for GitHub links...")

    # 1. Pattern that matches:
    #    - https://github.com/user/repo
    #    - http://github.com/user/repo
    #    - github.com/user/repo

    
    pattern = r"(https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+|github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
    #crazy regular expression given by chatgpt lol
    matches = re.findall(pattern, text)

    if not matches:
        print("[GITHUB] No GitHub links detected.")
        return []

    cleaned = []
    for m in matches:
        # add https:// if missing
        if m.startswith("github.com"):
            m = "https://" + m

        # remove trailing punctuation
        m = m.rstrip(".,);")

        cleaned.append(m)

    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for url in cleaned:
        if url not in seen:
            unique.append(url)
            seen.add(url)

    print(f"[GITHUB] Found {len(unique)} repositories.")
    return unique

#everything basically
def get_github_links_from_pdf(paper_url: str) -> list[str]:
    """High-level function: download, extract text, extract links."""
    """
    Full pipeline:
    1. Download the PDF from the given URL
    2. Extract text from the PDF
    3. Extract GitHub repository URLs from the text
    """

    print("[PIPELINE] Starting GitHub link extraction from PDF...")
    print(f"[PIPELINE] Paper URL: {paper_url}")

    # Step 1 — Download the PDF
    pdf_path = download_pdf(paper_url)
    if pdf_path is None:
        print("[ERROR] Could not download PDF.")
        return []

    # Step 2 — Extract text
    text = extract_text_local(pdf_path)
    if not text.strip():
        print("[ERROR] PDF text extraction returned empty content.")
        return []

    # Step 3 — Extract GitHub links
    github_links = extract_github_links(text)

    if github_links:
        print("[PIPELINE] Extraction complete. Repositories found:")
        for repo in github_links:
            print("   -", repo)
    else:
        print("[PIPELINE] No GitHub repositories found in this PDF.")

    return github_links

