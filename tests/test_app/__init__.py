import shutil
import subprocess
from pathlib import Path

# Make sure the JS is always re-built before running the tests
js_dir = Path(__file__).parent.parent.parent / "src" / "js"
static_dir = Path(__file__).parent.parent.parent / "src" / "reactpy_django" / "static" / "reactpy_django"
assert subprocess.run(["bun", "install"], cwd=str(js_dir), check=True).returncode == 0
assert (
    subprocess.run(
        ["bun", "build", "./src/index.ts", "--outfile", str(static_dir / "client.js")],
        cwd=str(js_dir),
        check=True,
    ).returncode
    == 0
)


# Make sure the test environment is always using the latest JS
def copy_js_files(source_dir: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()

    for file in source_dir.iterdir():
        if file.is_file():
            shutil.copy(file, destination / file.name)
        else:
            copy_js_files(file, destination / file.name)


# Copy PyScript
copy_js_files(
    js_dir / "node_modules" / "@pyscript" / "core" / "dist",
    Path(__file__).parent.parent.parent / "src" / "reactpy_django" / "static" / "reactpy_django" / "pyscript",
)


# Copy MorphDOM
copy_js_files(
    js_dir / "node_modules" / "morphdom" / "dist",
    Path(__file__).parent.parent.parent / "src" / "reactpy_django" / "static" / "reactpy_django" / "morphdom",
)
