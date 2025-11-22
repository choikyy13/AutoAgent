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
    