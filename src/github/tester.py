from github_finder import select_best_repository

test_links = [
        "https://github.com/RadonPy/RadonPy",
        "https://github.com/numpy/numpy"
    ]
    
test_paper = "This paper introduces RadonPy, a Python package for molecular dynamics..."
    
result = select_best_repository(test_links, test_paper)
print(f"\nResult: {result}")