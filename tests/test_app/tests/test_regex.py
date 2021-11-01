from django.test import TestCase

from django_idom.utils import COMPONENT_REGEX


class RegexTests(TestCase):
    def test_component_regex(self):
        self.assertRegex(r'{%idom_component "my.component"%}', COMPONENT_REGEX)
        self.assertRegex(r"{%idom_component 'my.component'%}", COMPONENT_REGEX)
        self.assertRegex(r'{% idom_component "my.component" %}', COMPONENT_REGEX)
        self.assertRegex(r"{% idom_component 'my.component' %}", COMPONENT_REGEX)
        self.assertRegex(
            r'{% idom_component "my.component" class="my_thing" %}',
            COMPONENT_REGEX,
        )
        self.assertRegex(
            r'{% idom_component "my.component" class="my_thing" attr="attribute" %}',
            COMPONENT_REGEX,
        )
        self.assertNotRegex(r'{% not_a_real_thing "my.component" %}', COMPONENT_REGEX)
        self.assertNotRegex(r"{% idom_component my.component %}", COMPONENT_REGEX)
        self.assertNotRegex(r"""{% idom_component 'my.component" %}""", COMPONENT_REGEX)
        self.assertNotRegex(r'{ idom_component "my.component" }', COMPONENT_REGEX)
        self.assertNotRegex(r'{{ idom_component "my.component" }}', COMPONENT_REGEX)
        self.assertNotRegex(r"idom_component", COMPONENT_REGEX)
        self.assertNotRegex(r"{%%}", COMPONENT_REGEX)
        self.assertNotRegex(r"", COMPONENT_REGEX)
