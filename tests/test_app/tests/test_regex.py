import re

from django.test import TestCase
from reactpy_django.utils import COMMENT_REGEX, COMPONENT_REGEX


class RegexTests(TestCase):
    def test_component_regex(self):
        # Real component matches
        self.assertRegex(r'{%component "my.component"%}', COMPONENT_REGEX)
        self.assertRegex(r'{%component  "my.component"%}', COMPONENT_REGEX)
        self.assertRegex(r"{%component 'my.component'%}", COMPONENT_REGEX)
        self.assertRegex(r'{% component "my.component" %}', COMPONENT_REGEX)
        self.assertRegex(r"{% component 'my.component' %}", COMPONENT_REGEX)
        self.assertRegex(
            r'{% component "my.component" class="my_thing" %}', COMPONENT_REGEX
        )
        self.assertRegex(
            r'{% component "my.component" class="my_thing" attr="attribute" %}',
            COMPONENT_REGEX,
        )
        self.assertRegex(
            r"""{%
            component   
            "my.component"  
            class="my_thing"  
            attr="attribute"  

        %}""",  # noqa: W291
            COMPONENT_REGEX,
        )
        self.assertRegex(r'{% component "my.component" my_object %}', COMPONENT_REGEX)
        self.assertRegex(
            r'{% component "my.component" class="example-cls" x=123 y=456 %}',
            COMPONENT_REGEX,
        )
        self.assertRegex(
            r'{% component "my.component" class = "example-cls" %}',
            COMPONENT_REGEX,
        )

        # Fake component matches
        self.assertNotRegex(r'{% not_a_real_thing "my.component" %}', COMPONENT_REGEX)
        self.assertNotRegex(r"{% component my.component %}", COMPONENT_REGEX)
        self.assertNotRegex(r"""{% component 'my.component" %}""", COMPONENT_REGEX)
        self.assertNotRegex(r'{ component "my.component" }', COMPONENT_REGEX)
        self.assertNotRegex(r'{{ component "my.component" }}', COMPONENT_REGEX)
        self.assertNotRegex(r"component", COMPONENT_REGEX)
        self.assertNotRegex(r"{%%}", COMPONENT_REGEX)
        self.assertNotRegex(r" ", COMPONENT_REGEX)
        self.assertNotRegex(r"", COMPONENT_REGEX)
        self.assertNotRegex(r'{% component " my.component " %}', COMPONENT_REGEX)
        self.assertNotRegex(
            r"""{% component "my.component
                         " %}""",
            COMPONENT_REGEX,
        )
        self.assertNotRegex(r'{{ component """ }}', COMPONENT_REGEX)
        self.assertNotRegex(r'{{ component "" }}', COMPONENT_REGEX)

        # Make sure back-to-back components are not merged into one match
        double_component_match = COMPONENT_REGEX.search(
            r'{% component "my.component" %} {% component "my.component" %}'
        )
        self.assertTrue(double_component_match[0] == r'{% component "my.component" %}')  # type: ignore

    def test_comment_regex(self):
        # Real comment matches
        self.assertRegex(r"<!-- comment -->", COMMENT_REGEX)
        self.assertRegex(
            r"""<!-- comment
        -->""",
            COMMENT_REGEX,
        )
        self.assertRegex(
            r"""<!--
            comment -->""",
            COMMENT_REGEX,
        )
        self.assertRegex(
            r"""<!--
        comment
        -->""",
            COMMENT_REGEX,
        )
        self.assertRegex(
            r"""<!-- 
        a comment
        another comments
        drink some cement 
        -->""",  # noqa: W291
            COMMENT_REGEX,
        )

        # Fake comment matches
        self.assertNotRegex(r"<!-- a comment ", COMMENT_REGEX)
        self.assertNotRegex(r"another comment -->", COMMENT_REGEX)
        self.assertNotRegex(r"<! - - comment - - >", COMMENT_REGEX)
        self.assertNotRegex(r'{% component "my.component" %}', COMMENT_REGEX)

        # Components surrounded by comments
        self.assertEqual(
            COMMENT_REGEX.sub(
                "", r'{% component "my.component" %} <!-- comment -->'
            ).strip(),
            '{% component "my.component" %}',
        )
        self.assertEqual(
            COMMENT_REGEX.sub(
                "", r'<!-- comment --> {% component "my.component" %}'
            ).strip(),
            '{% component "my.component" %}',
        )
        self.assertEqual(
            COMMENT_REGEX.sub(
                "", r'<!-- comment --> {% component "my.component" %} <!-- comment -->'
            ).strip(),
            '{% component "my.component" %}',
        )
        self.assertEqual(
            COMMENT_REGEX.sub(
                "",
                r"""<!-- comment
                    --> {% component "my.component" %}
                    <!-- comment -->
                <!--
                comment -->""",
            ).strip(),
            '{% component "my.component" %}',
        )

        # Components surrounded by comments
        self.assertEqual(
            COMMENT_REGEX.sub("", r'<!-- {% component "my.component" %} -->'),
            "",
        )
        self.assertEqual(
            COMMENT_REGEX.sub(
                "",
                r"""<!--
            {% component "my.component" %} 
            {% component "my.component" %} 
            -->""",  # noqa: W291
            ),
            "",
        )

    def test_offline_component_regex(self):
        regex = re.compile(COMPONENT_REGEX)
        # Check if "offline_path" group is present and equals to "my_offline_path"
        search = regex.search(
            r'{% component "my.component" offline="my_offline_path" %}'
        )
        self.assertTrue(search["offline_path"] == '"my_offline_path"')  # type: ignore

        search = regex.search(
            r'{% component "my.component" arg_1="1" offline="my_offline_path" arg_2="2" %}'
        )
        self.assertTrue(search["offline_path"] == '"my_offline_path"')  # type: ignore

        search = regex.search(
            r'{% component "my.component" offline="my_offline_path" arg_2="2" %}'
        )

        self.assertTrue(search["offline_path"] == '"my_offline_path"')  # type: ignore
        search = regex.search(
            r'{% component "my.component" arg_1="1" offline="my_offline_path" %}'
        )
        self.assertTrue(search["offline_path"] == '"my_offline_path"')  # type: ignore
