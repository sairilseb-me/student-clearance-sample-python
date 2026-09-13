from django.contrib import admin
from django.urls import include, path

from accounts import urls as accounts_urls
from clearance.root_views import root

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root, name="root"),
    path("", include(accounts_urls)),
    path("", include("clearance.urls")),
    path("assistant/", include("assistant.urls")),
]
