"""test_app URL Configuration

Examples:

Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.base_template),
    path("port/<int:port>/", views.host_port_template),
    path(
        "roundrobin/<int:port1>/<int:port2>/<int:count>/",
        views.host_port_roundrobin_template,
    ),
    path("errors/", views.errors_template),
    path("", include("test_app.prerender.urls")),
    path("", include("test_app.performance.urls")),
    path("", include("test_app.router.urls")),
    path("", include("test_app.offline.urls")),
    path("reactpy/", include("reactpy_django.http.urls")),
    path("admin/", admin.site.urls),
]
