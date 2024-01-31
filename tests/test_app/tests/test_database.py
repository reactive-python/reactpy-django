from time import sleep
from typing import Any
from uuid import uuid4

import dill as pickle
from django.test import TransactionTestCase
from reactpy_django import clean
from reactpy_django.models import ComponentSession, UserDataModel
from reactpy_django.types import ComponentParams


class RoutedDatabaseTests(TransactionTestCase):
    from reactpy_django import config

    databases = {config.REACTPY_DATABASE}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        clean.clean_sessions(immediate=True)

    def test_component_params(self):
        # Make sure the ComponentParams table is empty
        self.assertEqual(ComponentSession.objects.count(), 0)
        params_1 = self._save_params_to_db(1)

        # Check if a component params are in the database
        self.assertEqual(ComponentSession.objects.count(), 1)
        self.assertEqual(
            pickle.loads(ComponentSession.objects.first().params), params_1
        )

        # Force `params_1` to expire
        from reactpy_django import config

        config.REACTPY_SESSION_MAX_AGE = 1
        sleep(config.REACTPY_SESSION_MAX_AGE + 0.1)

        # Create a new, non-expired component params
        params_2 = self._save_params_to_db(2)
        self.assertEqual(ComponentSession.objects.count(), 2)

        # Delete the first component params based on expiration time
        clean.clean_sessions()  # Don't use `immediate` to test timestamping logic

        # Make sure `params_1` has expired
        self.assertEqual(ComponentSession.objects.count(), 1)
        self.assertEqual(
            pickle.loads(ComponentSession.objects.first().params), params_2
        )

    def test_user_data_cleanup(self):
        from django.contrib.auth.models import User

        # Create UserData for real user #1
        user = User.objects.create_user(username=uuid4().hex, password=uuid4().hex)
        user_data = UserDataModel(user_pk=user.pk)
        user_data.save()

        # Create UserData for real user #2
        user = User.objects.create_user(username=uuid4().hex, password=uuid4().hex)
        user_data = UserDataModel(user_pk=user.pk)
        user_data.save()

        # Keep track of the count of UserData objects
        original_count = UserDataModel.objects.count()

        # Create UserData for a fake user (orphaned)
        user_data = UserDataModel(user_pk=uuid4().hex)
        user_data.save()

        # Make sure the orphaned user data object is deleted
        self.assertNotEqual(UserDataModel.objects.count(), original_count)
        clean.clean_user_data()
        self.assertEqual(UserDataModel.objects.count(), original_count)

        # Check if deleting a user deletes the associated UserData
        user.delete()
        self.assertEqual(UserDataModel.objects.count(), original_count - 1)

    def _save_params_to_db(self, value: Any) -> ComponentParams:
        db = list(self.databases)[0]
        param_data = ComponentParams((value,), {"test_value": value})
        model = ComponentSession(uuid4().hex, params=pickle.dumps(param_data))
        model.clean_fields()
        model.clean()
        model.save(using=db)

        return param_data
