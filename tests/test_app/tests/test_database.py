from time import sleep
from typing import Any
from uuid import uuid4

import dill as pickle
from django.test import TransactionTestCase
from reactpy_django import utils
from reactpy_django.models import ComponentSession
from reactpy_django.types import ComponentParams


class RoutedDatabaseTests(TransactionTestCase):
    from reactpy_django import config

    databases = {config.REACTPY_DATABASE}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        utils.delete_expired_sessions(immediate=True)

    def test_component_params(self):
        # Make sure the ComponentParams table is empty
        self.assertEqual(ComponentSession.objects.count(), 0)
        params_1 = self._save_params_to_db(1)

        # Check if a component params are in the database
        self.assertEqual(ComponentSession.objects.count(), 1)
        self.assertEqual(
            pickle.loads(ComponentSession.objects.first().params), params_1  # type: ignore
        )

        # Force `params_1` to expire
        from reactpy_django import config

        config.REACTPY_SESSION_MAX_AGE = 1
        sleep(config.REACTPY_SESSION_MAX_AGE + 0.1)

        # Create a new, non-expired component params
        params_2 = self._save_params_to_db(2)
        self.assertEqual(ComponentSession.objects.count(), 2)

        # Delete the first component params based on expiration time
        utils.delete_expired_sessions()  # Don't use `immediate` to test timestamping logic

        # Make sure `params_1` has expired
        self.assertEqual(ComponentSession.objects.count(), 1)
        self.assertEqual(
            pickle.loads(ComponentSession.objects.first().params), params_2  # type: ignore
        )

    def _save_params_to_db(self, value: Any) -> ComponentParams:
        db = list(self.databases)[0]
        param_data = ComponentParams((value,), {"test_value": value})
        model = ComponentSession(uuid4().hex, params=pickle.dumps(param_data))
        model.clean_fields()
        model.clean()
        model.save(using=db)

        return param_data
