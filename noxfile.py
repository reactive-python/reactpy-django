from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

import nox
from nox.sessions import Session


HERE = Path(__file__).parent
POSARGS_PATTERN = re.compile(r"^(\w+)\[(.+)\]$")


@nox.session(reuse_venv=True)
def format(session: Session) -> None:
    install_requirements_file(session, "check-style")
    session.run("black", ".")
    session.run("isort", ".")


@nox.session
def test(session: Session) -> None:
    """Run the complete test suite"""
    session.install("--upgrade", "pip", "setuptools", "wheel")
    test_suite(session)
    test_style(session)


@nox.session
def test_suite(session: Session) -> None:
    """Run the Python-based test suite"""
    session.env["IDOM_DEBUG_MODE"] = "1"
    install_requirements_file(session, "test-env")
    session.install(".[all]")
    session.run("figure-it-out")


@nox.session
def test_style(session: Session) -> None:
    """Check that style guidelines are being followed"""
    install_requirements_file(session, "check-style")
    session.run("flake8", "src/django_idom", "tests")
    black_default_exclude = r"\.eggs|\.git|\.hg|\.mypy_cache|\.nox|\.tox|\.venv|\.svn|_build|buck-out|build|dist"
    session.run(
        "black",
        ".",
        "--check",
        "--exclude",
        rf"/({black_default_exclude}|venv|node_modules)/",
    )
    session.run("isort", ".", "--check-only")


def install_requirements_file(session: Session, name: str) -> None:
    file_path = HERE / "requirements" / (name + ".txt")
    assert file_path.exists(), f"requirements file {file_path} does not exist"
    session.install("-r", str(file_path))
