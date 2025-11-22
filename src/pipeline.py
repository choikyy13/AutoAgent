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
