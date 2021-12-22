from django.test import TestCase

from django_idom.utils import COMPONENT_REGEX


class RegexTests(TestCase):
    def test_component_regex(self):
        for component in {
            r'{%idom_component "my.component"%}',
            r"{%idom_component 'my.component'%}",
            r'{% idom_component "my.component" %}',
            r"{% idom_component 'my.component' %}",
            r'{% idom_component "my.component" class="my_thing" %}',
            r'{% idom_component "my.component" class="my_thing" attr="attribute" %}',
        }:
            self.assertRegex(component, COMPONENT_REGEX)

        for fake_component in {
            r'{% not_a_real_thing "my.component" %}',
            r"{% idom_component my.component %}",
            r"""{% idom_component 'my.component" %}""",
            r'{ idom_component "my.component" }',
            r'{{ idom_component "my.component" }}',
            r"idom_component",
            r"{%%}",
            r" ",
            r"",
        }:
            self.assertNotRegex(fake_component, COMPONENT_REGEX)
