import shutil
import subprocess
from pathlib import Path

# Make sure the JS is always re-built before running the tests
js_dir = Path(__file__).parent.parent.parent / "src" / "js"
static_dir = Path(__file__).parent.parent.parent / "src" / "reactpy_django" / "static" / "reactpy_django"

# Check if bun is available; if so, rebuild the JS. If not, assume artifacts exist.
_bun_available = shutil.which("bun") is not None
if _bun_available:
    subprocess.run(["bun", "install"], cwd=str(js_dir), check=True)
    subprocess.run(
        ["bun", "build", "./src/index.ts", f"--outdir={static_dir}", "--sourcemap=linked"],
        cwd=str(js_dir),
        check=True,
    )
else:
    # Verify that JS artifacts already exist so we don't silently skip a needed build
    if not (static_dir / "index.js").exists():
        raise RuntimeError(
            "bun is not installed and JS artifacts are missing. "
            f"Run 'bun install && bun build' in {js_dir} first."
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
