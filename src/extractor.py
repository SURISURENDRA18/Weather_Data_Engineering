from pathlib import Path
import sys

# Run src/extract.py
extract_path = Path(__file__).parent / "extract.py"
with open(extract_path, "r", encoding="utf-8") as f:
    exec(f.read())
