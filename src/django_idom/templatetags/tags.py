from django import template
from django.urls import reverse


register = template.Library()

# Template tag that renders the IDOM scripts
@register.inclusion_tag("idom/head_content.html")
def idom_scripts():
    pass

# Template tag that renders an empty idom root object
@register.inclusion_tag("idom/root.html")
def idom_root(html_id):
    return {"html_id": html_id}
