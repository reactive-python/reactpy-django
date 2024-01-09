from pathlib import Path

from nodejs import npm

# Make sure the JS is always re-built before running the tests
js_dir = Path(__file__).parent.parent.parent / "src" / "js"
assert npm.call(["install"], cwd=str(js_dir)) == 0
assert npm.call(["run", "build"], cwd=str(js_dir)) == 0
