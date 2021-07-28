from uuid import uuid4

from django import template

from django_idom.app_settings import IDOM_WEBSOCKET_URL, TEMPLATE_FILE_PATHS


register = template.Library()


# Template tag that renders the IDOM scripts
@register.inclusion_tag(TEMPLATE_FILE_PATHS["head_content"])
def idom_head():
    pass


@register.inclusion_tag(TEMPLATE_FILE_PATHS["view"])
def idom_view(view_id, view_params=""):
    return {
        "idom_websocket_url": IDOM_WEBSOCKET_URL,
        "idom_mount_uuid": uuid4().hex,
        "idom_view_id": view_id,
        "idom_view_params": view_params,
    }
