from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal

from django.contrib.auth import get_user_model
from django.utils import timezone

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from reactpy_django.models import Config

CLEAN_NEEDED_BY: datetime = datetime(year=1, month=1, day=1, tzinfo=timezone.now().tzinfo)
CleaningArgs = Literal["all", "sessions", "auth_tokens", "user_data"]


def clean(*args: CleaningArgs, immediate: bool = False, verbosity: int = 1):
    from reactpy_django.config import (
        REACTPY_CLEAN_AUTH_TOKENS,
        REACTPY_CLEAN_SESSIONS,
        REACTPY_CLEAN_USER_DATA,
    )
    from reactpy_django.models import Config

    config = Config.load()
    if immediate or clean_is_needed(config):
        config.cleaned_at = timezone.now()
        config.save()

        # If no args are provided, use the default settings.
        sessions = REACTPY_CLEAN_SESSIONS
        auth_tokens = REACTPY_CLEAN_AUTH_TOKENS
        user_data = REACTPY_CLEAN_USER_DATA

        if args:
            sessions = any(value in args for value in ("sessions", "all"))
            auth_tokens = any(value in args for value in ("auth_tokens", "all"))
            user_data = any(value in args for value in ("user_data", "all"))

        if sessions:
            clean_component_sessions(verbosity)
        if auth_tokens:
            clean_auth_tokens(verbosity)
        if user_data:
            clean_user_data(verbosity)


def clean_component_sessions(verbosity: int = 1):
    """Deletes expired component sessions from the database.
    As a performance optimization, this is only run once every REACTPY_SESSION_MAX_AGE seconds.
    """

    from reactpy_django.config import DJANGO_DEBUG, REACTPY_SESSION_MAX_AGE
    from reactpy_django.models import ComponentSession

    if verbosity >= 2:
        _logger.info("Cleaning ReactPy component sessions...")

    start_time = timezone.now()
    expiration_date = timezone.now() - timedelta(seconds=REACTPY_SESSION_MAX_AGE)
    session_objects = ComponentSession.objects.filter(last_accessed__lte=expiration_date)

    if verbosity >= 2:
        _logger.info("Deleting %d expired component sessions...", session_objects.count())

    session_objects.delete()

    if DJANGO_DEBUG or verbosity >= 2:
        inspect_clean_duration(start_time, "component sessions", verbosity)


def clean_auth_tokens(verbosity: int = 1):
    from reactpy_django.config import DJANGO_DEBUG, REACTPY_AUTH_TOKEN_MAX_AGE
    from reactpy_django.models import AuthToken

    if verbosity >= 2:
        _logger.info("Cleaning ReactPy auth tokens...")
    start_time = timezone.now()
    expiration_date = timezone.now() - timedelta(seconds=REACTPY_AUTH_TOKEN_MAX_AGE)
    synchronizer_objects = AuthToken.objects.filter(created_at__lte=expiration_date)

    if verbosity >= 2:
        _logger.info("Deleting %d expired auth token objects...", synchronizer_objects.count())

    synchronizer_objects.delete()

    if DJANGO_DEBUG or verbosity >= 2:
        inspect_clean_duration(start_time, "auth tokens", verbosity)


def clean_user_data(verbosity: int = 1):
    """Delete any user data that is not associated with an existing `User`.
    This is a safety measure to ensure that we don't have any orphaned data in the database.

    Our `UserDataModel` is supposed to automatically get deleted on every `User` delete signal.
    However, we can't use Django to enforce this relationship since ReactPy can be configured to
    use any database.
    """
    from reactpy_django.config import DJANGO_DEBUG
    from reactpy_django.models import UserDataModel

    if verbosity >= 2:
        _logger.info("Cleaning ReactPy user data...")

    start_time = timezone.now()
    user_model = get_user_model()
    all_users = user_model.objects.all()
    all_user_pks = all_users.values_list(user_model._meta.pk.name, flat=True)  # type: ignore

    # Django doesn't support using QuerySets as an argument with cross-database relations.
    if user_model.objects.db != UserDataModel.objects.db:
        all_user_pks = list(all_user_pks)

    user_data_objects = UserDataModel.objects.exclude(user_pk__in=all_user_pks)

    if verbosity >= 2:
        _logger.info("Deleting %d user data objects not associated with an existing user...", user_data_objects.count())

    user_data_objects.delete()

    if DJANGO_DEBUG or verbosity >= 2:
        inspect_clean_duration(start_time, "user data", verbosity)


def clean_is_needed(config: Config | None = None) -> bool:
    """Check if a clean is needed. This function avoids unnecessary database reads by caching the
    CLEAN_NEEDED_BY date."""
    from reactpy_django.config import REACTPY_CLEAN_INTERVAL
    from reactpy_django.models import Config

    global CLEAN_NEEDED_BY

    if REACTPY_CLEAN_INTERVAL is None:
        return False

    if timezone.now() >= CLEAN_NEEDED_BY:
        config = config or Config.load()
        CLEAN_NEEDED_BY = config.cleaned_at + timedelta(seconds=REACTPY_CLEAN_INTERVAL)

    return timezone.now() >= CLEAN_NEEDED_BY


def inspect_clean_duration(start_time: datetime, task_name: str, verbosity: int):
    clean_duration = timezone.now() - start_time

    if verbosity >= 3:
        _logger.info("Cleaned ReactPy %s in %s seconds.", task_name, clean_duration.total_seconds())

    if clean_duration.total_seconds() > 1:
        _logger.warning(
            "ReactPy has taken %s seconds to clean %s. "
            "This may indicate a performance issue with your system, cache, or database.",
            clean_duration.total_seconds(),
            task_name,
        )
