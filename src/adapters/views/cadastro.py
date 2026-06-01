from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from src.adapters.django_orm.models import UsuarioModel


@require_http_methods(["GET", "POST"])
def cadastro(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("callista:dashboard")

    erros = {}
    post = {}

    if request.method == "POST":
        post = request.POST
        nome = post.get("nome", "").strip()
        email = post.get("email", "").strip().lower()
        matricula = post.get("matricula", "").strip().upper()
        cargo = post.get("cargo", "").strip()
        codigo = post.get("codigo_setor", "").strip()
        senha = post.get("senha", "")
        senha2 = post.get("senha2", "")

        if not nome:
            erros["nome"] = "Nome é obrigatório."
        if not email:
            erros["email"] = "E-mail é obrigatório."
        elif User.objects.filter(email=email).exists():
            erros["email"] = "Este e-mail já está cadastrado."
        if not matricula:
            erros["matricula"] = "Matrícula é obrigatória."
        elif UsuarioModel.objects.filter(matricula=matricula).exists():
            erros["matricula"] = "Esta matrícula já está cadastrada."
        if codigo != settings.CALLISTA_CODIGO_SETOR:
            erros["codigo_setor"] = "Código de acesso inválido. Solicite ao gestor da equipe."
        if len(senha) < 8:
            erros["senha"] = "A senha deve ter no mínimo 8 caracteres."
        elif senha != senha2:
            erros["senha2"] = "As senhas não coincidem."

        if not erros:
            username = matricula.lower()
            if User.objects.filter(username=username).exists():
                username = email.split("@")[0]

            user = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=nome.split()[0],
                last_name=" ".join(nome.split()[1:]),
            )

            UsuarioModel.objects.create(
                nome=nome,
                email=email,
                matricula=matricula,
                cargo=cargo,
                is_ativo=True,
                is_oculto=False,
            )

            login(request, user)
            return redirect("callista:dashboard")

    return render(request, "registration/cadastro.html", {
        "erros": erros,
        "post": post,
    })
