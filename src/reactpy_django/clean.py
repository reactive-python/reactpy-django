from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.utils import timezone

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from reactpy_django.models import Config

CLEAN_NEEDED_BY: datetime = datetime(year=1, month=1, day=1)


def clean_all(
    immediate: bool = False,
    no_session: bool = False,
    no_user_data: bool = False,
    verbosity: int = 1,
):
    from reactpy_django.config import (
        REACTPY_CLEAN_SESSIONS,
        REACTPY_CLEAN_USER_DATA,
    )
    from reactpy_django.models import Config

    config = Config.load()
    if immediate or is_clean_needed(config):
        config.cleaned_at = timezone.now()
        config.save()

        if no_session or REACTPY_CLEAN_SESSIONS:
            clean_sessions(verbosity)
        if no_user_data or REACTPY_CLEAN_USER_DATA:
            clean_user_data(verbosity)


def clean_sessions(verbosity: int = 1):
    """Deletes expired component sessions from the database.
    As a performance optimization, this is only run once every REACTPY_SESSION_MAX_AGE seconds.
    """
    from reactpy_django.config import REACTPY_DEBUG_MODE, REACTPY_SESSION_MAX_AGE
    from reactpy_django.models import ComponentSession

    if verbosity >= 1:
        print("Cleaning ReactPy component sessions...")

    start_time = timezone.now()
    expiration_date = timezone.now() - timedelta(seconds=REACTPY_SESSION_MAX_AGE)
    ComponentSession.objects.filter(last_accessed__lte=expiration_date).delete()

    if REACTPY_DEBUG_MODE or verbosity >= 2:
        inspect_clean_duration(start_time, "component sessions", verbosity)


def clean_user_data(verbosity: int = 1):
    """Delete any user data that is not associated with an existing `User`.
    This is a safety measure to ensure that we don't have any orphaned data in the database.

    Our `UserDataModel` is supposed to automatically get deleted on every `User` delete signal.
    However, we can't use Django to enforce this relationship since ReactPy can be configured to
    use any database.
    """
    from reactpy_django.config import REACTPY_DEBUG_MODE
    from reactpy_django.models import UserDataModel

    if verbosity >= 1:
        print("Cleaning ReactPy user data...")

    start_time = timezone.now()
    user_model = get_user_model()
    all_users = user_model.objects.all()
    all_user_pks = all_users.values_list(user_model._meta.pk.name, flat=True)  # type: ignore
    if user_model.objects.db != UserDataModel.objects.db:
        all_user_pks = list(all_user_pks)  # type: ignore
    UserDataModel.objects.exclude(user_pk__in=all_user_pks).delete()

    if REACTPY_DEBUG_MODE or verbosity >= 2:
        inspect_clean_duration(start_time, "user data", verbosity)


def is_clean_needed(config: Config | None = None) -> bool:
    """Check if a clean is needed. This function avoids unnecessary database reads by caching the
    CLEAN_NEEDED_BY date."""
    from reactpy_django.config import REACTPY_CLEAN_INTERVAL
    from reactpy_django.models import Config

    global CLEAN_NEEDED_BY

    if REACTPY_CLEAN_INTERVAL == 0:
        return False

    if CLEAN_NEEDED_BY.year == 1 or timezone.now() >= CLEAN_NEEDED_BY:
        config = config or Config.load()
        CLEAN_NEEDED_BY = config.cleaned_at + timedelta(seconds=REACTPY_CLEAN_INTERVAL)

    return timezone.now() >= CLEAN_NEEDED_BY


def inspect_clean_duration(start_time: datetime, task_name: str, verbosity: int):
    clean_duration = timezone.now() - start_time

    if verbosity >= 3:
        print(
            f"Cleaned ReactPy {task_name} in {clean_duration.total_seconds()} seconds."
        )

    if clean_duration.total_seconds() > 1:
        _logger.warning(
            "ReactPy has taken %s seconds to clean %s. "
            "This may indicate a performance issue with your system, cache, or database.",
            clean_duration.total_seconds(),
            task_name,
        )
