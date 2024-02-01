from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manually clean ReactPy data."

    def handle(self, **options):
        from reactpy_django.clean import clean_all

        no_session = options.get("no_session", False)
        no_user_data = options.get("no_user_data", False)
        verbosity = options.get("verbosity", 1)

        clean_all(
            immediate=True,
            no_session=no_session,
            no_user_data=no_user_data,
            verbosity=verbosity,
        )

        if verbosity >= 1:
            print("ReactPy data has been cleaned!")

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-session",
            action="store_true",
            help="Prevent ReactPy from cleaning session data.",
        )
        parser.add_argument(
            "--no-user-data",
            action="store_true",
            help="Prevent ReactPy from cleaning user data.",
        )
