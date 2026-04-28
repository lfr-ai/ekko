# Developer setup (pip + venv)

Follow these steps to get a local development environment running.

1. Create and activate a virtual environment

   - Linux / macOS:
     - python -m venv .venv
     - source .venv/bin/activate

   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1

2. Install runtime and developer dependencies

   - pip install --upgrade pip
   - pip install -r requirements.txt
   - pip install -r requirements-dev.txt

3. Install pre-commit hooks

   - pre-commit install
   - pre-commit run --all-files

4. Run tests

   - pytest

5. Run the app (development)

   - python -m uvicorn voice.interaction.main:app --reload --host 127.0.0.1 --port 8000

Notes
- This repository previously used PDM; the project has been migrated toward a standard venv + pip workflow.
- If you need to recreate a pinned requirements.txt from pyproject.lock (if present), use your preferred tooling.
