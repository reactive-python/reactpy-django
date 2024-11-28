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
        print("Usage: python copy_dir.py <source_dir> <destination>")
        sys.exit(1)

    root_dir = Path(__file__).parent.parent.parent
    src = Path(root_dir / sys.argv[1])
    dest = Path(root_dir / sys.argv[2])

    if not src.exists():
        print(f"Source directory {src} does not exist")
        sys.exit(1)

    copy_files(src, dest)