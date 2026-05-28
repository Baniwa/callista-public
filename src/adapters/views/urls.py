from django.contrib.auth import views as auth_views
from django.urls import path
from . import dashboard, demandas

app_name = "callista"

urlpatterns = [
    path("", dashboard.dashboard, name="dashboard"),
    path("demandas/", demandas.lista, name="demanda_lista"),
    path("demandas/nova/", demandas.nova, name="demanda_nova"),
    path("demandas/<int:demanda_id>/", demandas.detalhe, name="demanda_detalhe"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
