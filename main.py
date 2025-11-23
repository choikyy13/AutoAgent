"""
main.py

Entry point of the Track 2 pipeline.

This script:
1. Accepts a PDF URL from the user.
2. Calls the pipeline runner.
3. Prints or saves the final results (demo script, repo summary, etc).

It contains *no logic*, only orchestration.
"""

"""
main.py - Entry point with CLI
"""

from pipeline import run_pipeline
import sys


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <pdf_url>")
        print("\nExample:")
        print("  python main.py https://arxiv.org/pdf/2203.14090")
        sys.exit(1)
    
    pdf_url = sys.argv[1]
    
    print(f"\n🚀 Starting AutoAgent Pipeline")
    print(f"📄 Paper: {pdf_url}\n")
    
    # Run pipeline
    results = run_pipeline(pdf_url)
    
    # Exit with appropriate code
    sys.exit(0 if results['status'] == 'success' else 1)


if __name__ == "__main__":
    main()