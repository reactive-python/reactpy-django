from django import template

from django_idom.app_settings import IDOM_WEBSOCKET_URL


register = template.Library()


# Template tag that renders the IDOM scripts
@register.inclusion_tag("idom/head_content.html")
def idom_scripts():
    pass


@register.inclusion_tag("idom/view.html")
def idom_view(view_id):
    return {"idom_websocket_url": IDOM_WEBSOCKET_URL, "view_id": view_id}
