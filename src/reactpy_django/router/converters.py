from django.urls.converters import (
    IntConverter,
    PathConverter,
    SlugConverter,
    StringConverter,
    UUIDConverter,
)
from reactpy_router.simple import ConversionInfo

CONVERTERS: dict[str, ConversionInfo] = {
    "int": {
        "regex": IntConverter().regex,
        "func": IntConverter().to_python,
    },
    "path": {
        "regex": PathConverter().regex,
        "func": PathConverter().to_python,
    },
    "slug": {
        "regex": SlugConverter().regex,
        "func": SlugConverter().to_python,
    },
    "str": {
        "regex": StringConverter().regex,
        "func": StringConverter().to_python,
    },
    "uuid": {
        "regex": UUIDConverter().regex,
        "func": UUIDConverter().to_python,
    },
}
