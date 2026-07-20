"""
Development/debug script to run Django's development server in the local environment.
You should run the `install_deps.py` script before this to ensure all dependencies are installed.
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Run server and pass through any additional command line arguments (e.g. for specifying a different port)
    subprocess.run(
        [sys.executable, "manage.py", "runserver", *sys.argv[1:]],
        check=True,
        cwd=Path(__file__).parent.parent.parent / "tests",
    )
