import re

from django.test import TestCase

from reactpy_django.utils import COMMENT_REGEX, COMPONENT_REGEX


class RegexTests(TestCase):
    def test_component_regex(self):
        # Real component matches
        assert re.search(COMPONENT_REGEX, '{%component "my.component"%}')
        assert re.search(COMPONENT_REGEX, '{%component  "my.component"%}')
        assert re.search(COMPONENT_REGEX, "{%component 'my.component'%}")
        assert re.search(COMPONENT_REGEX, '{% component "my.component" %}')
        assert re.search(COMPONENT_REGEX, "{% component 'my.component' %}")
        assert re.search(COMPONENT_REGEX, '{% component "my.component" class="my_thing" %}')
        assert re.search(COMPONENT_REGEX, '{% component "my.component" class="my_thing" attr="attribute" %}')
        assert re.search(
            COMPONENT_REGEX,
            '{%\n            component\n            "my.component"\n            class="my_thing"\n            attr="attribute"\n\n        %}',
        )
        assert re.search(COMPONENT_REGEX, '{% component "my.component" my_object %}')
        assert re.search(COMPONENT_REGEX, '{% component "my.component" class="example-cls" x=123 y=456 %}')
        assert re.search(COMPONENT_REGEX, '{% component "my.component" class = "example-cls" %}')

        # Fake component matches
        assert not re.search(COMPONENT_REGEX, '{% not_a_real_thing "my.component" %}')
        assert not re.search(COMPONENT_REGEX, "{% component my.component %}")
        assert not re.search(COMPONENT_REGEX, "{% component 'my.component\" %}")
        assert not re.search(COMPONENT_REGEX, '{ component "my.component" }')
        assert not re.search(COMPONENT_REGEX, '{{ component "my.component" }}')
        assert not re.search(COMPONENT_REGEX, "component")
        assert not re.search(COMPONENT_REGEX, "{%%}")
        assert not re.search(COMPONENT_REGEX, " ")
        assert not re.search(COMPONENT_REGEX, "")
        assert not re.search(COMPONENT_REGEX, '{% component " my.component " %}')
        assert not re.search(COMPONENT_REGEX, '{% component "my.component\n                         " %}')
        assert not re.search(COMPONENT_REGEX, '{{ component """ }}')
        assert not re.search(COMPONENT_REGEX, '{{ component "" }}')

        # Make sure back-to-back components are not merged into one match
        double_component_match = COMPONENT_REGEX.search(
            r'{% component "my.component" %} {% component "my.component" %}'
        )
        assert double_component_match[0] == '{% component "my.component" %}'

    def test_comment_regex(self):
        # Real comment matches
        assert re.search(COMMENT_REGEX, "<!-- comment -->")
        assert re.search(COMMENT_REGEX, "<!-- comment\n        -->")
        assert re.search(COMMENT_REGEX, "<!--\n            comment -->")
        assert re.search(COMMENT_REGEX, "<!--\n        comment\n        -->")
        assert re.search(
            COMMENT_REGEX, "<!--\n        a comment\n        another comments\n        drink some cement\n        -->"
        )

        # Fake comment matches
        assert not re.search(COMMENT_REGEX, "<!-- a comment ")
        assert not re.search(COMMENT_REGEX, "another comment -->")
        assert not re.search(COMMENT_REGEX, "<! - - comment - - >")
        assert not re.search(COMMENT_REGEX, '{% component "my.component" %}')

        # Components surrounded by comments
        assert (
            COMMENT_REGEX.sub("", '{% component "my.component" %} <!-- comment -->').strip()
            == '{% component "my.component" %}'
        )
        assert (
            COMMENT_REGEX.sub("", '<!-- comment --> {% component "my.component" %}').strip()
            == '{% component "my.component" %}'
        )
        assert (
            COMMENT_REGEX.sub("", '<!-- comment --> {% component "my.component" %} <!-- comment -->').strip()
            == '{% component "my.component" %}'
        )
        assert (
            COMMENT_REGEX.sub(
                "",
                '<!-- comment\n                    --> {% component "my.component" %}\n                    <!-- comment -->\n                <!--\n                comment -->',
            ).strip()
            == '{% component "my.component" %}'
        )

        # Components surrounded by comments
        assert COMMENT_REGEX.sub("", '<!-- {% component "my.component" %} -->') == ""
        assert (
            COMMENT_REGEX.sub(
                "",
                '<!--\n            {% component "my.component" %}\n            {% component "my.component" %}\n            -->',
            )
            == ""
        )

    def test_offline_component_regex(self):
        regex = re.compile(COMPONENT_REGEX)
        # Check if "offline_path" group is present and equals to "my_offline_path"
        search = regex.search(r'{% component "my.component" offline="my_offline_path" %}')
        assert search["offline_path"] == '"my_offline_path"'

        search = regex.search(r'{% component "my.component" arg_1="1" offline="my_offline_path" arg_2="2" %}')
        assert search["offline_path"] == '"my_offline_path"'

        search = regex.search(r'{% component "my.component" offline="my_offline_path" arg_2="2" %}')

        assert search["offline_path"] == '"my_offline_path"'
        search = regex.search(r'{% component "my.component" arg_1="1" offline="my_offline_path" %}')
        assert search["offline_path"] == '"my_offline_path"'
