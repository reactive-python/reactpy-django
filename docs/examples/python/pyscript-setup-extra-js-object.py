from django.shortcuts import render
from django.templatetags.static import static


def index(request):
    return render(
        request,
        "my_template.html",
        context={"my_extra_js_object": {static("moment.js"): "moment"}},
    )
