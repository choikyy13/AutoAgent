# test_scan_src.py

from code_scanner import scan_repository
import os

if __name__ == "__main__":
    # Scan the entire project OR just src — choose here:
    path_to_scan = os.path.join("src")

    print(f"Scanning folder: {path_to_scan}\n")
    result = scan_repository(path_to_scan)

    print("===== SCAN RESULT =====")
    print(result)
