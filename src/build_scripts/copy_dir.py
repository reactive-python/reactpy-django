# ruff: noqa: INP001
import shutil
import sys
from pathlib import Path


def copy_files(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()

    for file in source.iterdir():
        if file.is_file():
            shutil.copy(file, destination / file.name)
        else:
            copy_files(file, destination / file.name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    root_dir = Path(__file__).parent.parent.parent
    src = Path(root_dir / sys.argv[1])
    dest = Path(root_dir / sys.argv[2])

    if not src.exists():
        sys.exit(1)

    copy_files(src, dest)
