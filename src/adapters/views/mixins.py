from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from src.adapters.django_orm.models import UsuarioModel


def usuario_ativo_required(view_func):
    """
    Exige autenticação E is_ativo=True no UsuarioModel.
    Superusuários Django passam sem checagem (acesso administrativo).
    Usuários desativados pelo gestor no Admin são deslogados imediatamente.
    """
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_superuser:
            ativo = UsuarioModel.objects.filter(
                email=request.user.email, is_ativo=True
            ).exists()
            if not ativo:
                logout(request)
                return redirect("/login/?msg=inativo")
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
