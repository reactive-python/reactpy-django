from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

os.chdir(Path(__file__).parent.parent.parent)


@pytest.fixture(autouse=True, scope="session")
def install_playwright():
    subprocess.run(["playwright", "install", "chromium"], check=True)
