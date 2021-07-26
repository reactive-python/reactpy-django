from django import template


register = template.Library()


# Template tag that renders the IDOM scripts
@register.inclusion_tag("idom/head_content.html")
def idom_scripts():
    pass


# Template tag that renders an empty idom root object
@register.inclusion_tag("idom/root.html")
def idom_view(html_id):
    return {"html_id": html_id}
