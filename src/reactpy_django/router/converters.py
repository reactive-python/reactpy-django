from django.urls.converters import get_converters
from reactpy_router.types import ConversionInfo

CONVERTERS: dict[str, ConversionInfo] = {
    name: {"regex": converter.regex, "func": converter.to_python} for name, converter in get_converters().items()
}
CONVERTERS["any"] = {"regex": r".*", "func": str}
