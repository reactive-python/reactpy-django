import shutil
import subprocess
from pathlib import Path

# Make sure the JS is always re-built before running the tests
js_dir = Path(__file__).parent.parent.parent / "src" / "js"
static_dir = (
    Path(__file__).parent.parent.parent
    / "src"
    / "reactpy_django"
    / "static"
    / "reactpy_django"
)
assert subprocess.run(["bun", "install"], cwd=str(js_dir), check=True).returncode == 0
assert (
    subprocess.run(
        ["bun", "build", "./src/index.tsx", "--outfile", str(static_dir / "client.js")],
        cwd=str(js_dir),
        check=True,
    ).returncode
    == 0
)

# Make sure the current PyScript distribution is always available
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

# Make sure the current Morphdom distrubiton is always available
morphdom_dist = js_dir / "node_modules" / "morphdom" / "dist"
morphdom_static_dir = (
    Path(__file__).parent.parent.parent
    / "src"
    / "reactpy_django"
    / "static"
    / "reactpy_django"
    / "morphdom"
)
if not morphdom_static_dir.exists():
    morphdom_static_dir.mkdir()
for file in morphdom_dist.iterdir():
    shutil.copy(file, morphdom_static_dir / file.name)
