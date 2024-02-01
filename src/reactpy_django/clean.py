import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.utils import timezone

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from reactpy_django.models import Config


def clean_all(immediate: bool = False, ignore_config=False):
    from reactpy_django.config import (
        REACTPY_CLEAN_SESSIONS,
        REACTPY_CLEAN_USER_DATA,
    )
    from reactpy_django.models import Config

    config = Config.load()
    if immediate or is_clean_needed(config):
        if ignore_config or REACTPY_CLEAN_SESSIONS:
            clean_sessions()
        if ignore_config or REACTPY_CLEAN_USER_DATA:
            clean_user_data()
        config.cleaned_at = timezone.now()
        config.save()


def clean_sessions():
    """Deletes expired component sessions from the database.
    As a performance optimization, this is only run once every REACTPY_SESSION_MAX_AGE seconds.
    """
    from reactpy_django.config import REACTPY_DEBUG_MODE, REACTPY_SESSION_MAX_AGE
    from reactpy_django.models import ComponentSession

    start_time = timezone.now()
    expiration_date = timezone.now() - timedelta(seconds=REACTPY_SESSION_MAX_AGE)
    ComponentSession.objects.filter(last_accessed__lte=expiration_date).delete()

    if REACTPY_DEBUG_MODE:
        inspect_clean_duration(start_time, "component sessions")


def clean_user_data():
    """Delete any user data that is not associated with an existing `User`.
    This is a safety measure to ensure that we don't have any orphaned data in the database.

    Our `UserDataModel` is supposed to automatically get deleted on every `User` delete signal.
    However, we can't use Django to enforce this relationship since ReactPy can be configured to
    use any database.
    """
    from reactpy_django.config import REACTPY_DEBUG_MODE
    from reactpy_django.models import UserDataModel

    start_time = timezone.now()
    user_model = get_user_model()
    all_users = user_model.objects.all()
    all_user_pks = all_users.values_list(user_model._meta.pk.name, flat=True)  # type: ignore
    UserDataModel.objects.exclude(user_pk__in=all_user_pks).delete()

    if REACTPY_DEBUG_MODE:
        inspect_clean_duration(start_time, "user data")


def is_clean_needed(config: Config | None = None) -> bool:
    from reactpy_django.config import REACTPY_SESSION_MAX_AGE
    from reactpy_django.models import Config

    config = config or Config.load()
    cleaned_at = config.cleaned_at
    clean_needed_by = cleaned_at + timedelta(seconds=REACTPY_SESSION_MAX_AGE)

    return timezone.now() >= clean_needed_by


def inspect_clean_duration(start_time: datetime, task_name: str):
    clean_duration = timezone.now() - start_time
    if clean_duration.total_seconds() > 1:
        _logger.warning(
            "ReactPy has taken %s seconds to clean %s. "
            "This may indicate a performance issue with your system, cache, or database.",
            clean_duration.total_seconds(),
            task_name,
        )
