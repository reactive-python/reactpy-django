from django.test import TestCase

from django_idom.utils import get_component


class RegexTests(TestCase):
    def test_get_component(self):
        real_component = get_component("test_app.components.HelloWorld")
        self.assertIsNotNone(real_component)
        self.assertEqual(getattr(real_component, "__name__", None), "HelloWorld")

        fake_component = get_component("test_app.components.FakeComponent")
        self.assertIsNone(fake_component)

