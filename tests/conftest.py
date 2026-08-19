import os
import sys
from pathlib import Path

# Make `app.*` importable when pytest is run from the repo root.
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("HF_API_TOKEN", "dummy-token-for-tests")
