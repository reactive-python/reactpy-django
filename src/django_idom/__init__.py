from logging import getLogger

from django_idom import components, decorators, hooks, types, utils
from django_idom.websocket.paths import IDOM_WEBSOCKET_PATH


logger = getLogger(__name__)

print("WARNING: django-idom has been renamed to reactpy-django.")
logger.warning("django-idom has been renamed to reactpy-django.")

__version__ = "3.0.1"
__all__ = [
    "IDOM_WEBSOCKET_PATH",
    "hooks",
    "components",
    "decorators",
    "types",
    "utils",
]
