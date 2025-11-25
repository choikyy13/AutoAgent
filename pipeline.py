"""

Central coordinator of the entire processing pipeline.

Pipeline steps:
1. Download PDF and extract text.
2. Detect GitHub links inside the text.
3. Select the most relevant / highest-quality GitHub repo.
4. Clone the repo locally.
5. Scan the repo: languages, structure, main files, unusual patterns.
6. Generate a demo script or runnable example using an LLM.
7. Execute and evaluate the generated demo (NEW STEP).
8. Return all results as a structured object.

This is the core "brain" that links all modules together.
"""
# Import all the necessary modules

import os
import sys
from src.pdf.pdf_extractor import download_pdf, extract_text_local, get_github_links_from_pdf
from src.github.github_finder import select_best_repository
from src.github.github_clone import clone_repository
from src.analysis.code_scanner import scan_repository
from src.demo.demo_generator import generate_demo
# --- FIX: CORRECTED IMPORT PATH ---
from src.evaluation.evaluator import run_evaluation_pipeline

class PipelineError(Exception):
    """Custom exception for pipeline errors."""
    pass

def run_pipeline(pdf_url: str) -> dict:
    """
    Runs the full processing pipeline on the given PDF URL.

    Returns:
        A dictionary with all results from each step.
    """

    results = {"input_url": pdf_url, "status": "In Progress", "errors": [], "evaluation": {}}

    try:
        # Step 1: Download PDF, extract text, and find GitHub links
        print("[PIPELINE] Starting GitHub link extraction from PDF...")
        github_links = get_github_links_from_pdf(pdf_url)
        results['github_links'] = github_links

        if not github_links:
            raise PipelineError("No GitHub links found in the PDF.")
        print(f"[PIPELINE] Extraction complete. Repositories found:\n    - " + "\n    - ".join(github_links))

        # Step 2: Select best repository
        paper_text = extract_text_local(download_pdf(pdf_url))
        best_repo_url = select_best_repository(github_links, paper_text)
        results['best_repo_url'] = best_repo_url
        print(f"Only one repo: {best_repo_url}")

        # Step 3: Clone the repository
        local_repo_path = clone_repository(best_repo_url)
        results['local_repo_path'] = local_repo_path
        if not local_repo_path:
            raise PipelineError("Failed to clone the selected repository.")
        print(f"Successfully cloned to {os.path.basename(local_repo_path)}")
        
        # Step 4: Scan the repository
        print("[PIPELINE] Starting repository scanning...")
        scan_report = scan_repository(local_repo_path)
        results['scan_report'] = scan_report
        print("Scanning complete.")

        # Step 5: Generate demo script
        demo_code = generate_demo(scan_report, local_repo_path)
        results['demo_code'] = demo_code

        # Step 6: Create a python script file with the demo code on the local repo path
        demo_file_path = os.path.join(local_repo_path, "demo_generated.py")
        with open(demo_file_path, "w", encoding="utf-8") as f:
            f.write(demo_code)
        results['demo_file_path'] = demo_file_path
        print(f"[PIPELINE] Demo script saved to {os.path.basename(demo_file_path)}")
        
        # --- Step 7: EXECUTE AND EVALUATE (10 Points) ---
        print("\n[PIPELINE] Starting demo execution and evaluation (Total 10 Points)...")
        # NOTE: scan_report (project_summary) is now passed to the evaluation pipeline
        evaluation_data = run_evaluation_pipeline(demo_code, demo_file_path, local_repo_path, scan_report)
        results["evaluation"] = evaluation_data
        print(f"[PIPELINE] Automated Score: {evaluation_data['evaluation_results']['total_automated_score']} / 5 (Binary Points)")
        print(f"[PIPELINE] TOTAL SCORE: {evaluation_data['evaluation_results']['total_score']} / 10")
        
        results['status'] = 'success'

    except PipelineError as e:
        results['status'] = 'failed'
        results['errors'].append(str(e))
        print(f"\nPipeline Error: {e}")
        
    except Exception as e:
        results['status'] = 'failed'
        results['errors'].append(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected Error: {e}")
        import traceback
        traceback.print_exc()

    return results