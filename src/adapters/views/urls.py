from django.contrib.auth import views as auth_views
from django.urls import path
from . import afastamentos, dashboard, demandas

app_name = "callista"

urlpatterns = [
    path("", dashboard.dashboard, name="dashboard"),

    # Demandas
    path("demandas/", demandas.lista, name="demanda_lista"),
    path("demandas/nova/", demandas.nova, name="demanda_nova"),
    path("demandas/<int:demanda_id>/", demandas.detalhe, name="demanda_detalhe"),
    path("minhas-demandas/", demandas.minhas_demandas, name="minhas_demandas"),
    path("equipe/", demandas.equipe, name="equipe"),
    path("pesquisa/", demandas.pesquisa, name="pesquisa"),

    # Cadastros
    path("afastamentos/", afastamentos.lista, name="afastamentos"),

    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
