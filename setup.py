from __future__ import annotations, print_function

import shutil
import subprocess
import sys
import traceback
from logging import getLogger
from pathlib import Path

from setuptools import find_namespace_packages, setup
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist

log = getLogger(__name__)

# -----------------------------------------------------------------------------
# Basic Constants
# -----------------------------------------------------------------------------
name = "reactpy_django"
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
js_dir = src_dir / "js"
package_dir = src_dir / name
static_dir = package_dir / "static" / name


# -----------------------------------------------------------------------------
# Package Definition
# -----------------------------------------------------------------------------
package = {
    "name": name,
    "python_requires": ">=3.9",
    "packages": find_namespace_packages(src_dir),
    "package_dir": {"": "src"},
    "description": "It's React, but in Python. Now with Django integration.",
    "author": "Mark Bakhit",
    "author_email": "archiethemonger@gmail.com",
    "url": "https://github.com/reactive-python/reactpy-django",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": [
        "interactive",
        "reactive",
        "widgets",
        "DOM",
        "React",
        "ReactJS",
        "ReactPy",
    ],
    "include_package_data": True,
    "zip_safe": False,
    "classifiers": [
        "Framework :: Django",
        "Framework :: Django :: 4.0",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Environment :: Web Environment",
    ],
}


# -----------------------------------------------------------------------------
# Library Version
# -----------------------------------------------------------------------------
for line in (package_dir / "__init__.py").read_text().split("\n"):
    if line.startswith("__version__ = "):
        package["version"] = eval(line.split("=", 1)[1])
        break
else:
    print(f"No version found in {package_dir}/__init__.py")
    sys.exit(1)


# -----------------------------------------------------------------------------
# Requirements
# -----------------------------------------------------------------------------
requirements: list[str] = []
with (root_dir / "requirements" / "pkg-deps.txt").open() as f:
    requirements.extend(line for line in map(str.strip, f) if not line.startswith("#"))
package["install_requires"] = requirements


# -----------------------------------------------------------------------------
# Library Description
# -----------------------------------------------------------------------------
with (root_dir / "README.md").open() as f:
    long_description = f.read()

package["long_description"] = long_description
package["long_description_content_type"] = "text/markdown"


# ----------------------------------------------------------------------------
# Build Javascript
# ----------------------------------------------------------------------------
def copy_js_files(source_dir: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()

    for file in source_dir.iterdir():
        if file.is_file():
            shutil.copy(file, destination / file.name)
        else:
            copy_js_files(file, destination / file.name)


def build_javascript_first(build_cls: type):
    class Command(build_cls):
        def run(self):

            log.info("Installing Javascript...")
            result = subprocess.run(
                ["bun", "install"], cwd=str(js_dir), check=True
            ).returncode
            if result != 0:
                log.error(traceback.format_exc())
                log.error("Failed to install Javascript")
                raise RuntimeError("Failed to install Javascript")

            log.info("Building Javascript...")
            result = subprocess.run(
                [
                    "bun",
                    "build",
                    "./src/index.tsx",
                    "--outfile",
                    str(static_dir / "client.js"),
                    "--minify",
                ],
                cwd=str(js_dir),
                check=True,
            ).returncode
            if result != 0:
                log.error(traceback.format_exc())
                log.error("Failed to build Javascript")
                raise RuntimeError("Failed to build Javascript")

            log.info("Copying @pyscript/core distribution")
            pyscript_dist = js_dir / "node_modules" / "@pyscript" / "core" / "dist"
            pyscript_static_dir = static_dir / "pyscript"
            copy_js_files(pyscript_dist, pyscript_static_dir)

            log.info("Copying Morphdom distribution")
            morphdom_dist = js_dir / "node_modules" / "morphdom" / "dist"
            morphdom_static_dir = static_dir / "morphdom"
            copy_js_files(morphdom_dist, morphdom_static_dir)

            log.info("Successfully built Javascript")
            super().run()

    return Command


package["cmdclass"] = {
    "sdist": build_javascript_first(sdist),
    "develop": build_javascript_first(develop),
}

if sys.version_info < (3, 10, 6):
    from distutils.command.build import build

    package["cmdclass"]["build"] = build_javascript_first(build)
else:
    from setuptools.command.build_py import build_py

    package["cmdclass"]["build_py"] = build_javascript_first(build_py)


# -----------------------------------------------------------------------------
# Installation
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    setup(**package)
