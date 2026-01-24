import sys
from pathlib import Path

# Ensure `python/` is on sys.path so tests can import `tcs_exercises` without packaging.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

