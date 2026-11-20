import os
import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
    frontend_dir = Path(__file__).resolve().parent / "frontend"
    sys.path.insert(0, str(frontend_dir))
    os.chdir(frontend_dir)
    runpy.run_path(str(frontend_dir / "main.py"), run_name="__main__")
