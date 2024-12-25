from logging import getLogger

from django.core.management.base import BaseCommand

_logger = getLogger(__name__)


class Command(BaseCommand):
    help = "Manually clean ReactPy data. When using this command without args, it will perform all cleaning operations."

    def handle(self, *_args, **options):
        from reactpy_django.tasks import CleaningArgs, clean

        verbosity = options.pop("verbosity", 1)
        valid_args: set[CleaningArgs] = {"all", "sessions", "auth_tokens", "user_data"}
        cleaning_args: set[CleaningArgs] = {arg for arg in options if arg in valid_args and options[arg]} or {"all"}

        clean(*cleaning_args, immediate=True, verbosity=verbosity)

        if verbosity >= 1:
            _logger.info("ReactPy data has been cleaned!")

    def add_arguments(self, parser):
        parser.add_argument(
            "--sessions",
            action="store_true",
            help="Clean component session data. This value can be combined with other cleaning options.",
        )
        parser.add_argument(
            "--user-data",
            action="store_true",
            help="Clean user data. This value can be combined with other cleaning options.",
        )
        parser.add_argument(
            "--auth-tokens",
            action="store_true",
            help="Clean authentication tokens. This value can be combined with other cleaning options.",
        )
