import hmac
import uuid

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from src.adapters.django_orm.models import UsuarioModel


def _codigo_valido(informado: str) -> bool:
    # hmac.compare_digest evita timing attack na comparação do código de setor
    return hmac.compare_digest(
        informado.strip(),
        settings.CALLISTA_CODIGO_SETOR,
    )


def _gerar_username(matricula: str, email: str) -> str:
    candidatos = [matricula.lower(), email.split("@")[0].lower()]
    for candidato in candidatos:
        if not User.objects.filter(username=candidato).exists():
            return candidato
    # fallback único se ambos existirem
    return f"{matricula.lower()}-{uuid.uuid4().hex[:6]}"


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
        codigo = post.get("codigo_setor", "")
        senha = post.get("senha", "")
        senha2 = post.get("senha2", "")

        if not nome or len(nome.split()) < 2:
            erros["nome"] = "Informe nome e sobrenome."
        if not email:
            erros["email"] = "E-mail é obrigatório."
        elif User.objects.filter(email=email).exists():
            erros["email"] = "Este e-mail já está cadastrado."
        if not matricula:
            erros["matricula"] = "Matrícula é obrigatória."
        elif UsuarioModel.objects.filter(matricula=matricula).exists():
            erros["matricula"] = "Esta matrícula já está cadastrada."
        if not _codigo_valido(codigo):
            erros["codigo_setor"] = "Código de acesso inválido. Solicite ao gestor da equipe."
        if len(senha) < 8:
            erros["senha"] = "A senha deve ter no mínimo 8 caracteres."
        elif senha != senha2:
            erros["senha2"] = "As senhas não coincidem."

        if not erros:
            partes = nome.split()
            user = User.objects.create_user(
                username=_gerar_username(matricula, email),
                email=email,
                password=senha,
                first_name=partes[0],
                last_name=" ".join(partes[1:]),
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
