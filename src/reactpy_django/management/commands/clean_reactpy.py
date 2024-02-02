from typing import Literal

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manually clean ReactPy data."

    def handle(self, **options):
        from reactpy_django.clean import clean

        verbosity = options.get("verbosity", 1)

        cleaning_args: set[Literal["all", "session", "user_data"]] = set()
        if options.get("session"):
            cleaning_args.add("session")
        if options.get("user_data"):
            cleaning_args.add("user_data")
        if not cleaning_args:
            cleaning_args = {"all"}

        clean(*cleaning_args, immediate=True, verbosity=verbosity)

        if verbosity >= 1:
            print("ReactPy data has been cleaned!")

    def add_arguments(self, parser):
        parser.add_argument(
            "--session",
            action="store_true",
            help="Configure this clean to only clean session data (and other configured cleaning options).",
        )
        parser.add_argument(
            "--user-data",
            action="store_true",
            help="Configure this clean to only clean user data (and other configured cleaning options).",
        )
