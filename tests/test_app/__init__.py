import shutil
from pathlib import Path

from nodejs import npm

# Make sure the JS is always re-built before running the tests
js_dir = Path(__file__).parent.parent.parent / "src" / "js"
assert npm.call(["install"], cwd=str(js_dir)) == 0
assert npm.call(["run", "build"], cwd=str(js_dir)) == 0

# Make sure the current PyScript distribution is available
pyscript_dist = js_dir / "node_modules" / "@pyscript" / "core" / "dist"
pyscript_static_dir = (
    Path(__file__).parent.parent.parent
    / "src"
    / "reactpy_django"
    / "static"
    / "reactpy_django"
    / "pyscript"
)
if not pyscript_static_dir.exists():
    pyscript_static_dir.mkdir()
for file in pyscript_dist.iterdir():
    shutil.copy(file, pyscript_static_dir / file.name)
