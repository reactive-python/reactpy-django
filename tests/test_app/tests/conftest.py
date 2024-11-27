from __future__ import annotations

import os
from pathlib import Path

import pytest

os.chdir(Path(__file__).parent.parent.parent)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
