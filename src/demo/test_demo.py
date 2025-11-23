import os
import sys

# Make sure root is importable
sys.path.append(os.path.abspath("."))

from src.demo.demo_generator import generate_demo

# Use your manually provided output
scan_output = {
    'num_files': 26,
    'languages': ['python'],
    'folders': [
        '', 'AI', 'AI/__pycache__', 'AIv2', 'AIv2/__pycache__', 
        'analysis', 'analysis/__pycache__', 'demo', 'demo/__pycache__',
        'github', 'github/__pycache__', 'pdf', 'pdf/__pycache__'
    ],
    'configs': [],
    'models': [],
    'demos': [
        'src/demo/demo_generator.py', 
        'src/demo/test_demo.py',
        'non_existent_demo.py'
    ],
    'entrypoints': [
        'analysis/code_scanner.py',
        'analysis/test_scanner.py'
    ]
}

def test_demo_generation():
    """
    Test demo_generator using the precomputed scan_output.
    Does NOT call the scanner again.
    """

    # path to local repo root
    repo_root = os.path.abspath(".")
    print(repo_root)

    print("\n🧪 TEST: demo generation using static scan_output")

    demo_code = generate_demo(scan_output, repo_root)

    print("\n=== DEMO CODE GENERATED ===")
    print(demo_code)
    print("============================\n")

if __name__ == "__main__":
    test_demo_generation()
