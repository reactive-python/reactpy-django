from typing import Literal

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manually clean ReactPy data. When using this command without args, it will perform all cleaning operations."

    def handle(self, **options):
        from reactpy_django.clean import clean

        verbosity = options.get("verbosity", 1)

        cleaning_args: set[Literal["all", "sessions", "user_data"]] = set()
        if options.get("sessions"):
            cleaning_args.add("sessions")
        if options.get("user_data"):
            cleaning_args.add("user_data")
        if not cleaning_args:
            cleaning_args = {"all"}

        clean(*cleaning_args, immediate=True, verbosity=verbosity)

        if verbosity >= 1:
            print("ReactPy data has been cleaned!")

    def add_arguments(self, parser):
        parser.add_argument(
            "--sessions",
            action="store_true",
            help="Clean session data. This value can be combined with other cleaning options.",
        )
        parser.add_argument(
            "--user-data",
            action="store_true",
            help="Clean user data. This value can be combined with other cleaning options.",
        )
