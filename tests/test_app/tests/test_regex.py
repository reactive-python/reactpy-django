from django.test import TestCase

from django_idom.utils import COMPONENT_REGEX


class RegexTests(TestCase):
    def test_component_regex(self):
        for component in {
            r'{%component "my.component"%}',
            r'{%component  "my.component"%}',
            r"{%component 'my.component'%}",
            r'{% component "my.component" %}',
            r"{% component 'my.component' %}",
            r'{% component "my.component" class="my_thing" %}',
            r'{% component "my.component" class="my_thing" attr="attribute" %}',
            r"""{%

                component   
                "my.component"  
                class="my_thing"  
                attr="attribute"  

            %}""",  # noqa: W291
        }:
            self.assertRegex(component, COMPONENT_REGEX)

        for fake_component in {
            r'{% not_a_real_thing "my.component" %}',
            r"{% component my.component %}",
            r"""{% component 'my.component" %}""",
            r'{ component "my.component" }',
            r'{{ component "my.component" }}',
            r"component",
            r"{%%}",
            r" ",
            r"",
            r'{% component " my.component " %}',
            r"""{% component "my.component
                        " %}""",
            r'{{ component """ }}',
            r'{{ component "" }}',
        }:
            self.assertNotRegex(fake_component, COMPONENT_REGEX)
