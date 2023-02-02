from time import sleep
from typing import Any
from uuid import uuid4

import dill as pickle
from django.test import TransactionTestCase

from django_idom import utils
from django_idom.models import ComponentParams
from django_idom.types import ComponentParamData


class DatabaseTests(TransactionTestCase):
    def test_component_params(self):
        # Make sure the ComponentParams table is empty
        self.assertEqual(ComponentParams.objects.count(), 0)
        params_1 = self._save_params_to_db(1)

        # Check if a component params are in the database
        self.assertEqual(ComponentParams.objects.count(), 1)
        self.assertEqual(pickle.loads(ComponentParams.objects.first().data), params_1)  # type: ignore

        # Force `params_1` to expire
        from django_idom import config

        config.IDOM_RECONNECT_MAX = 1
        sleep(config.IDOM_RECONNECT_MAX + 0.1)

        # Create a new, non-expired component params
        params_2 = self._save_params_to_db(2)
        self.assertEqual(ComponentParams.objects.count(), 2)

        # Delete the first component params based on expiration time
        utils.db_cleanup()  # Don't use `immediate` to test cache timestamping logic

        # Make sure `params_1` has expired
        self.assertEqual(ComponentParams.objects.count(), 1)
        self.assertEqual(pickle.loads(ComponentParams.objects.first().data), params_2)  # type: ignore

    def _save_params_to_db(self, value: Any) -> ComponentParamData:
        param_data = ComponentParamData((value,), {"test_value": value})
        model = ComponentParams(uuid4().hex, data=pickle.dumps(param_data))
        model.full_clean()
        model.save()

        return param_data
