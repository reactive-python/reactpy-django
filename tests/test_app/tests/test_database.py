# ruff: noqa: RUF012
import asyncio
from time import sleep
from typing import Any
from uuid import uuid4

import dill
from django.test import TransactionTestCase

from reactpy_django import tasks
from reactpy_django.models import ComponentSession, SessionStateModel, UserDataModel
from reactpy_django.types import ComponentParams


class RoutedDatabaseTests(TransactionTestCase):
    """Database tests that should only exclusively access the ReactPy database."""

    from reactpy_django import config

    databases = {config.REACTPY_DATABASE}

    def test_component_params(self):
        from reactpy_django import config

        initial_clean_interval = config.REACTPY_CLEAN_INTERVAL
        initial_session_max_age = config.REACTPY_SESSION_MAX_AGE
        initial_clean_user_data = config.REACTPY_CLEAN_USER_DATA
        config.REACTPY_CLEAN_INTERVAL = 1
        config.REACTPY_SESSION_MAX_AGE = 1
        config.REACTPY_CLEAN_USER_DATA = False

        try:
            tasks.clean(immediate=True)

            # Make sure the ComponentParams table is empty
            assert ComponentSession.objects.count() == 0
            params_1 = self._save_params_to_db(1)

            # Check if a component params are in the database
            assert ComponentSession.objects.count() == 1
            assert dill.loads(ComponentSession.objects.first().params) == params_1

            # Force `params_1` to expire
            sleep(config.REACTPY_CLEAN_INTERVAL)

            # Create a new, non-expired component params
            params_2 = self._save_params_to_db(2)
            assert ComponentSession.objects.count() == 2

            # Try to delete the `params_1` via cleaning (it should be expired)
            # Note: We don't use `immediate` here in order to test timestamping logic
            tasks.clean()

            # Make sure `params_1` has expired, but `params_2` is still there
            assert ComponentSession.objects.count() == 1
            assert dill.loads(ComponentSession.objects.first().params) == params_2
        finally:
            config.REACTPY_CLEAN_INTERVAL = initial_clean_interval
            config.REACTPY_SESSION_MAX_AGE = initial_session_max_age
            config.REACTPY_CLEAN_USER_DATA = initial_clean_user_data

    def test_session_state_roundtrip_and_cleanup(self):
        from reactpy_django import config
        from reactpy_django.hooks import _get_session_state, _set_session_state

        initial_clean_session_state = config.REACTPY_CLEAN_SESSION_STATE
        initial_session_state_max_age = config.REACTPY_SESSION_STATE_MAX_AGE
        config.REACTPY_CLEAN_SESSION_STATE = False
        config.REACTPY_SESSION_STATE_MAX_AGE = 1

        try:
            scope_id = f"tab:{uuid4()}"
            key = "my_state"

            # No state exists yet, so the default is returned
            assert asyncio.run(_get_session_state(scope_id, key, default="default")) == "default"

            # Persist some state and read it back
            state = {"count": 1, "items": [1, 2, 3]}
            asyncio.run(_set_session_state(scope_id, key, state))
            assert SessionStateModel.objects.filter(scope_id=scope_id, key=key).count() == 1
            assert asyncio.run(_get_session_state(scope_id, key, default="default")) == state

            # Persisting the same scope+key updates the existing row (no duplicate)
            asyncio.run(_set_session_state(scope_id, key, {"count": 2}))
            assert SessionStateModel.objects.filter(scope_id=scope_id, key=key).count() == 1
            assert asyncio.run(_get_session_state(scope_id, key, default="default")) == {"count": 2}

            # Let the first state row age past the expiry threshold
            sleep(config.REACTPY_SESSION_STATE_MAX_AGE)

            # A freshly-written (non-expired) entry should survive cleaning
            fresh_scope = f"tab:{uuid4()}"
            asyncio.run(_set_session_state(fresh_scope, "other", "keep-me"))
            assert SessionStateModel.objects.count() == 2
            tasks.clean_session_state()
            assert SessionStateModel.objects.count() == 1
            assert asyncio.run(_get_session_state(fresh_scope, "other", default="default")) == "keep-me"
        finally:
            config.REACTPY_CLEAN_SESSION_STATE = initial_clean_session_state
            config.REACTPY_SESSION_STATE_MAX_AGE = initial_session_state_max_age

    def _save_params_to_db(self, value: Any) -> ComponentParams:
        db = next(iter(self.databases))
        param_data = ComponentParams((value,), {"test_value": value})
        model = ComponentSession(str(uuid4()), params=dill.dumps(param_data))
        model.clean_fields()
        model.clean()
        model.save(using=db)

        return param_data


class MultiDatabaseTests(TransactionTestCase):
    """Database tests that need to access both the default and ReactPy databases."""

    from reactpy_django import config

    databases = {"default", config.REACTPY_DATABASE}

    def test_user_data_cleanup(self):
        from django.contrib.auth.models import User

        # Create UserData for real user #1
        user = User.objects.create_user(username=str(uuid4()), password=str(uuid4()))
        user_data = UserDataModel(user_pk=user.pk)
        user_data.save()

        # Create UserData for real user #2
        user = User.objects.create_user(username=str(uuid4()), password=str(uuid4()))
        user_data = UserDataModel(user_pk=user.pk)
        user_data.save()

        # Store the initial amount of UserData objects
        initial_count = UserDataModel.objects.count()

        # Create UserData for a user that doesn't exist (effectively orphaned)
        user_data = UserDataModel(user_pk=str(uuid4()))
        user_data.save()

        # Make sure the orphaned user data object is deleted
        assert UserDataModel.objects.count() == initial_count + 1
        tasks.clean_user_data()
        assert UserDataModel.objects.count() == initial_count

        # Check if deleting a user deletes the associated UserData
        user.delete()
        assert UserDataModel.objects.count() == initial_count - 1

        # Make sure one user data object remains
        assert UserDataModel.objects.count() == 1
