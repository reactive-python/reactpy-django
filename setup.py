from __future__ import print_function

import pipes
import shutil
import subprocess
import sys
import traceback
from distutils import log
from logging import StreamHandler, getLogger
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.sdist import sdist


if sys.platform == "win32":
    from subprocess import list2cmdline
else:

    def list2cmdline(cmd_list):
        return " ".join(map(pipes.quote, cmd_list))


log = getLogger()
log.addHandler(StreamHandler(sys.stdout))


# -----------------------------------------------------------------------------
# Basic Constants
# -----------------------------------------------------------------------------


# the name of the project
name = "reactpy_django"

# basic paths used to gather files
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
package_dir = src_dir / name


# -----------------------------------------------------------------------------
# Package Definition
# -----------------------------------------------------------------------------


package = {
    "name": name,
    "python_requires": ">=3.8",
    "packages": find_packages(str(src_dir)),
    "package_dir": {"": "src"},
    "description": "Control the web with Python",
    "author": "Ryan Morshead",
    "author_email": "ryan.morshead@gmail.com",
    "url": "https://github.com/reactive-python/reactpy-django",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": ["interactive", "widgets", "DOM", "React"],
    "include_package_data": True,
    "zip_safe": False,
    "classifiers": [
        "Framework :: Django",
        "Framework :: Django :: 4.0",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
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


requirements = []
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


def build_javascript_first(cls):
    class Command(cls):
        def run(self):
            js_dir = str(src_dir / "js")
            npm = shutil.which("npm")  # this is required on windows
            if npm is None:
                raise RuntimeError("NPM is not installed.")

            log.info("Updating NPM...")
            try:
                args_list = [npm, "install", "-g", "npm@latest"]
                log.info(f"> {list2cmdline(args_list)}")
                subprocess.run(args_list, cwd=js_dir, check=True)
            except Exception:
                log.error("Failed to update NPM")
                log.error(traceback.format_exc())
                raise

            log.info("Installing Javascript...")
            try:
                args_list = [npm, "install"]
                log.info(f"> {list2cmdline(args_list)}")
                subprocess.run(args_list, cwd=js_dir, check=True)
            except Exception:
                log.error("Failed to install Javascript")
                log.error(traceback.format_exc())
                raise

            log.info("Building Javascript...")
            try:
                args_list = [npm, "run", "build"]
                log.info(f"> {list2cmdline(args_list)}")
                subprocess.run(args_list, cwd=js_dir, check=True)
            except Exception:
                log.error("Failed to build Javascript")
                log.error(traceback.format_exc())
                raise

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
# Install It
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    setup(**package)
