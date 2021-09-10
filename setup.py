from __future__ import print_function

import pipes
import shutil
import subprocess
import sys
import traceback
from distutils import log
from distutils.command.build import build  # type: ignore
from distutils.command.sdist import sdist  # type: ignore
from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.develop import develop


if sys.platform == "win32":
    from subprocess import list2cmdline
else:

    def list2cmdline(cmd_list):
        return " ".join(map(pipes.quote, cmd_list))


# the name of the project
name = "django_idom"

# basic paths used to gather files
root_dir = Path(__file__).parent
src_dir = root_dir / "src"
package_dir = src_dir / name


# -----------------------------------------------------------------------------
# Package Definition
# -----------------------------------------------------------------------------


package = {
    "name": name,
    "python_requires": ">=3.7",
    "packages": find_packages(str(src_dir)),
    "package_dir": {"": "src"},
    "description": "Control the web with Python",
    "author": "Ryan Morshead",
    "author_email": "ryan.morshead@gmail.com",
    "url": "https://github.com/idom-team/django-idom",
    "license": "MIT",
    "platforms": "Linux, Mac OS X, Windows",
    "keywords": ["interactive", "widgets", "DOM", "React"],
    "include_package_data": True,
    "zip_safe": False,
    "classifiers": [
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Graphics",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
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
    print("No version found in %s/__init__.py" % package_dir)
    sys.exit(1)


# -----------------------------------------------------------------------------
# Requirements
# -----------------------------------------------------------------------------


requirements = []
with (root_dir / "requirements" / "pkg-deps.txt").open() as f:
    for line in map(str.strip, f):
        if not line.startswith("#"):
            requirements.append(line)
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
            log.info("Installing Javascript...")
            try:
                js_dir = str(src_dir / "js")
                npm = shutil.which("npm")  # this is required on windows
                if npm is None:
                    raise RuntimeError("NPM is not installed.")

                # Required on when using NPM >3
                log.info(f"> Installing rollup, react, and react-dom")
                subprocess.run(f"{npm} install rollup".split(), cwd=js_dir, check=True)
                subprocess.run(f"{npm} install react".split(), cwd=js_dir, check=True)
                subprocess.run(
                    f"{npm} install react-dom".split(), cwd=js_dir, check=True
                )

                for args in (f"{npm} install", f"{npm} run build"):
                    args_list = args.split()
                    log.info(f"> {list2cmdline(args_list)}")
                    subprocess.run(args_list, cwd=js_dir, check=True)
            except Exception:
                log.error("Failed to install Javascript")
                log.error(traceback.format_exc())
                raise
            else:
                log.info("Successfully installed Javascript")
            super().run()

    return Command


package["cmdclass"] = {
    "sdist": build_javascript_first(sdist),
    "build": build_javascript_first(build),
    "develop": build_javascript_first(develop),
}


# -----------------------------------------------------------------------------
# Install It
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    setup(**package)
