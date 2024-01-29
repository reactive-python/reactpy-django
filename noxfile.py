from __future__ import annotations

from glob import glob
from pathlib import Path

from nox import Session, session

ROOT_DIR = Path(__file__).parent


@session(tags=["test"])
def test_python(session: Session) -> None:
    """Run the Python-based test suite"""
    install_requirements_file(session, "test-env")
    session.install(".[all]")
    session.chdir(ROOT_DIR / "tests")
    session.env["REACTPY_DEBUG_MODE"] = "1"

    posargs = session.posargs[:]
    if "--headless" in posargs:
        posargs.remove("--headless")
        session.env["PLAYWRIGHT_HEADLESS"] = "1"

    if "--no-debug-mode" not in posargs:
        posargs.append("--debug-mode")

    session.run("playwright", "install", "chromium")

    # Run tests for each settings file (tests/test_app/settings_*.py)
    settings_glob = "test_app/settings_*.py"
    settings_files = glob(settings_glob)
    assert settings_files, f"No Django settings files found at '{settings_glob}'!"
    for settings_file in settings_files:
        settings_module = settings_file.strip(".py").replace("/", ".").replace("\\", ".")
        session.run(
            "python",
            "manage.py",
            "test",
            *posargs,
            "-v",
            "2",
            "--settings",
            settings_module,
        )


@session(tags=["test"])
def test_types(session: Session) -> None:
    install_requirements_file(session, "check-types")
    install_requirements_file(session, "pkg-deps")
    session.run("mypy", "--show-error-codes", "src/reactpy_django", "tests/test_app")


@session(tags=["test"])
def test_style(session: Session) -> None:
    """Check that style guidelines are being followed"""
    install_requirements_file(session, "check-style")
    session.run("ruff", "check", ".")


@session(tags=["test"])
def test_javascript(session: Session) -> None:
    install_requirements_file(session, "test-env")
    session.chdir(ROOT_DIR / "src" / "js")
    session.run("python", "-m", "nodejs.npm", "install", external=True)
    session.run("python", "-m", "nodejs.npm", "run", "check")


def install_requirements_file(session: Session, name: str) -> None:
    session.install("--upgrade", "pip", "setuptools", "wheel")
    file_path = ROOT_DIR / "requirements" / f"{name}.txt"
    assert file_path.exists(), f"requirements file {file_path} does not exist"
    session.install("-r", str(file_path))
