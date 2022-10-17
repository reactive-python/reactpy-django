from django.test import TestCase

from django_idom.utils import COMMENT_REGEX, COMPONENT_REGEX


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

    def test_comment_regex(self):
        for comment in {
            r"<!-- comment -->",
            r"""<!-- comment
            -->""",
            r"""<!--
             comment -->""",
            r"""<!--
            comment
            -->""",
            r"""<!-- 
            a comment
            another comments
            drink some cement 
            -->""",  # noqa: W291
        }:
            self.assertRegex(comment, COMMENT_REGEX)

        for fake_comment in {
            r"<!-- a comment ",
            r"another comment -->",
            r"<! - - comment - - >",
            r'{% component "my.component" %}',
        }:
            self.assertNotRegex(fake_comment, COMMENT_REGEX)

        for embedded_comment in {
            r'{% component "my.component" %} <!-- comment -->',
            r'<!-- comment --> {% component "my.component" %}',
            r'<!-- comment --> {% component "my.component" %} <!-- comment -->',
            r"""<!-- comment
                    --> {% component "my.component" %}
                    <!-- comment -->
                <!--
                comment -->""",
        }:  # noqa: W291
            text = COMMENT_REGEX.sub("", embedded_comment)
            if text.strip() != '{% component "my.component" %}':
                raise self.failureException(
                    f"Regex pattern {COMMENT_REGEX.pattern} failed to remove comment from {embedded_comment}"
                )
