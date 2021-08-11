from django.http import HttpRequest, HttpResponse
from idom.config import IDOM_WED_MODULES_DIR


def web_modules_file(request: HttpRequest, file: str) -> HttpResponse:
    file_path = IDOM_WED_MODULES_DIR.current.joinpath(*file.split("/"))
    return HttpResponse(file_path.read_text(), content_type="text/javascript")
