from src.pdf.pdf_extractor import get_github_links_from_pdf
from src.pdf.pdf_extractor import extract_text_local
from src.pdf.pdf_extractor import download_pdf
import src.github.github_finder as github_finder

test_links = get_github_links_from_pdf("https://pdfs.semanticscholar.org/d4f4/9717c9adb46137f49606ebbdf17e3598b5a5.pdf")
path = download_pdf("https://pdfs.semanticscholar.org/d4f4/9717c9adb46137f49606ebbdf17e3598b5a5.pdf")
test_paper = extract_text_local(path)

result = github_finder.select_best_repository(test_links, test_paper)
print(f"\nResult: {result}")