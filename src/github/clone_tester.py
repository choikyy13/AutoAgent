from github_clone import clone_repository
import os

test_repo = "https://github.com/Teoroo-CMC/PiNN"
    
try:
    local_path = clone_repository(test_repo)
    print(f"\n Repository at: {local_path}")
            
except Exception as e:
    print(f"\n FAILED: {e}")