from github_clone import clone_repository
import os

test_repo = "https://github.com/optuna/optuna"
    
try:
    local_path = clone_repository(test_repo)
    print(f"Repository at: {local_path}")
            
except Exception as e:
    print(f"\nFAILED: {e}")