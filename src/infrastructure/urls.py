from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("src.adapters.views.urls")),
    path("", include(("src.adapters.views.urls", "callista"), namespace="callista")),
]
