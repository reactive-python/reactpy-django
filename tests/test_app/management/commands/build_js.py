import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand

HERE = Path(__file__).parent
JS_DIR = HERE.parent.parent.parent / "js"


class Command(BaseCommand):
    help = "Build javascript source for test app"

    def handle(self, *args, **options):
        subprocess.run(["npm", "install"], cwd=JS_DIR, check=True)
        subprocess.run(["npm", "run", "build"], cwd=JS_DIR, check=True)
