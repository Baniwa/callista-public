from django.urls import path
from . import dashboard

app_name = "callista"

urlpatterns = [
    path("", dashboard.dashboard, name="dashboard"),
]
