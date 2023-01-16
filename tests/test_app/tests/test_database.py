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

        # Add component params to the database
        params = ComponentParamData((1,), {"test_value": 1})
        model = ComponentParams(uuid4().hex, data=pickle.dumps(params))
        model.full_clean()
        model.save()

        # Check if a component params are in the database
        self.assertEqual(ComponentParams.objects.count(), 1)

        # Check if the data is the same
        self.assertEqual(pickle.loads(ComponentParams.objects.first().data), params)  # type: ignore

        # Check if the data is the same after a reload
        ComponentParams.objects.first().refresh_from_db()  # type: ignore
        self.assertEqual(pickle.loads(ComponentParams.objects.first().data), params)  # type: ignore

        # Force the data to expire
        from django_idom import config

        config.IDOM_RECONNECT_MAX = 0
        utils.db_cleanup()  # Don't use `immediate` to better simulate a real world scenario

        # Make sure the data is gone
        self.assertEqual(ComponentParams.objects.count(), 0)
