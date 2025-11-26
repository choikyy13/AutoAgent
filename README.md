# AutoAgent

An automated AI agent designed to verify the reproducibility of scientific papers. The agent extracts code repositories from PDF papers, autonomously generates runnable demo scripts, and evaluates the execution quality using a comprehensive scoring system.

## Key Features

* **PDF Intelligence**: Downloads PDFs and extracts raw text to identify potential GitHub repository links.
* **Smart Repository Selection**: Uses an LLM to analyze the paper summary and filter through extracted links to identify the primary implementation repository, ignoring citations or unrelated libraries.
* **Automated Cloning**: Handles Git operations to clone the selected repository into a local sandboxed environment.
* **Code Analysis**: Scans the repository to detect languages, configuration files, models, and existing entry points.
* **Generative Execution**: Uses an LLM to generate a `demo_generated.py` script (or validate an existing one) that installs dependencies and attempts to run the project.
* **Automated Evaluation**: Assigns a reliability score (0-10) based on execution success and code quality.

---

## The Pipeline Workflow

The system operates via a central coordinator (`pipeline.py`) that orchestrates the following 7 steps:

1.  **Ingestion**: Download the PDF from a provided URL and extract text content.
2.  **Link Detection**: Identify all GitHub links present in the paper text.
3.  **Repo Selection**: Compare the paper's content against the found links using an LLM to select the "Best Repository".
4.  **Cloning**: Clone the target repository to a local `ImportedProjects/` directory.
5.  **Scanning**: Analyze the file structure to build a summary for the LLM (detecting languages, configs, and models).
6.  **Demo Generation**: Generate a `demo_generated.py` script tailored to the repo's structure, handling dependency checks and imports.
7.  **Evaluation**: Execute the demo in a subprocess and calculate a final score.

---

## Scoring System

The agent evaluates every run on a scale of **0 to 10**, combining automated execution metrics with qualitative LLM assessment.

### 1. Automated Metrics (5 Points)
Scores are binary (1 or 0) based on the execution result:
* **Syntax**: Code parses without syntax errors.
* **Exit Code**: Process finishes with exit code 0.
* **Performance**: Execution completes within 30 seconds.
* **Output**: Valid output detected in `stdout`.
* **Cleanliness**: No errors detected in `stderr`.

### 2. Qualitative LLM Assessment (5 Points)
An LLM judges the quality of the generated code and execution logs:
* **Relevance (2 pts)**: Did the code import and use the core project library?
* **Clarity (2 pts)**: Is the code logic clear and professional?
* **Completeness (1 pt)**: Did the code mock required data or call necessary setup steps?

---

## Installation & Setup

### Prerequisites
* Python 3.8+
* Git
* Docker (recommended)

### Dependencies
Install the required packages using the provided requirements file:
```bash
pip install -r requirements.txt