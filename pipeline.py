"""
pipeline.py

Central coordinator of the entire processing pipeline.

Pipeline steps:
1. Download PDF and extract text.
2. Detect GitHub links inside the text.
3. Select the most relevant / highest-quality GitHub repo.
4. Clone the repo locally.
5. Scan the repo: languages, structure, main files, unusual patterns.
6. Generate a demo script or runnable example using an LLM.
7. Return all results as a structured object.

This is the core "brain" that links all modules together.
"""
# Import all the necessary modules

from src.pdf.pdf_extractor import download_pdf, extract_text_local, get_github_links_from_pdf
from src.github.github_finder import select_best_repository
from src.github.github_clone import clone_repository
from src.analysis.code_scanner import scan_repository

def run_pipeline(pdf_url: str) -> dict:
    """
    Runs the full processing pipeline on the given PDF URL.

    Returns:
        A dictionary with all results from each step.
    """

    print(f"Starting pipeline for PDF: {pdf_url}")

    results = {'input_url' : pdf_url, "Status": "In Progress"}

    # Step 1: Download PDF and extract text
    try:
        pdf_path = download_pdf(pdf_url)
        paper_text = extract_text_local(pdf_path)
        results['pdf_path'] = pdf_path
        results['paper_text'] = paper_text
    except Exception as e:
        raise Exception(f"Failed during PDF processing: {e}")    
    
    # Step 3: Detect GitHub links
    github_links = get_github_links_from_pdf(paper_text)
    results['github_links'] = github_links

    # Step 4: Select best repository
    best_repo_url = select_best_repository(github_links, paper_text)
    results['best_repo_url'] = best_repo_url

    # Step 5: Clone the repository
    local_repo_path = clone_repository(best_repo_url)
    results['local_repo_path'] = local_repo_path

    # Further steps (scanning, demo generation) would go here...

    # Step 6: Scan the repository
    print("Scanning the repository...")
    scan_report = scan_repository(local_repo_path)
    results['scan_report'] = scan_report

    # Step 7: (Placeholder for demo generation)

    """
    print_demo = "TODO: Demo generation not yet implemented."
    results['demo_script'] = print_demo
    """



    return results

