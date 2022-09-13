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
def manage(session: Session) -> None:
    """Run a manage.py command for tests/test_app"""
    session.install("-r", "requirements/test-env.txt")
    session.install("idom[stable]")
    session.install("-e", ".")
    session.chdir("tests")
    session.run("python", "manage.py", *session.posargs)


@nox.session(reuse_venv=True)
def format(session: Session) -> None:
    """Run automatic code formatters"""
    install_requirements_file(session, "check-style")
    session.run("black", ".")
    session.run("isort", ".")


@nox.session
def test(session: Session) -> None:
    """Run the complete test suite"""
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.notify("test_suite", posargs=session.posargs)
    session.notify("test_types")
    session.notify("test_style")


@nox.session
def test_suite(session: Session) -> None:
    """Run the Python-based test suite"""
    install_requirements_file(session, "test-env")
    session.install(".[all]")

    session.chdir(HERE / "tests")
    session.env["IDOM_DEBUG_MODE"] = "1"

    posargs = session.posargs[:]
    if "--headless" in posargs:
        posargs.remove("--headless")
        session.env["SELENIUM_HEADLESS"] = "1"

    if "--no-debug-mode" not in posargs:
        posargs.append("--debug-mode")

    session.run("python", "manage.py", "test", *posargs)


@nox.session
def test_types(session: Session) -> None:
    install_requirements_file(session, "check-types")
    install_requirements_file(session, "pkg-deps")
    session.run("mypy", "--show-error-codes", "src/django_idom", "tests/test_app")


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
