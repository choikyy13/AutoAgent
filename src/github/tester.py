from github_finder import select_best_repository

test_links = [
    "https://github.com/hyperopt/hyperopt",
    "https://github.com/Teoroo-CMC/PiNN",
    "https://github.com/optuna/optuna",
    "https://github.com/hyperopt/hyperopt"
]
    
test_paper = "This paper introduces hyperopt..."
    
result = select_best_repository(test_links, test_paper)
print(f"\nResult: {result}")