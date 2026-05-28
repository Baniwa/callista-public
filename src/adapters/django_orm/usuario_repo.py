from typing import Optional, Sequence

from src.domain.entities.usuario import Usuario
from .models import UsuarioModel


class DjangoUsuarioRepository:
    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        try:
            return self._to_entity(UsuarioModel.objects.get(pk=id))
        except UsuarioModel.DoesNotExist:
            return None

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        try:
            return self._to_entity(UsuarioModel.objects.get(email=email))
        except UsuarioModel.DoesNotExist:
            return None

    def listar_ativos_visiveis(self) -> Sequence[Usuario]:
        return [
            self._to_entity(obj)
            for obj in UsuarioModel.objects.filter(is_ativo=True, is_oculto=False)
        ]

    def salvar(self, usuario: Usuario) -> Usuario:
        dados = {
            "nome": usuario.nome,
            "email": usuario.email,
            "matricula": usuario.matricula,
            "cargo": usuario.cargo,
            "is_ativo": usuario.is_ativo,
            "is_oculto": usuario.is_oculto,
        }
        if usuario.id is None:
            obj = UsuarioModel.objects.create(**dados)
        else:
            UsuarioModel.objects.filter(pk=usuario.id).update(**dados)
            obj = UsuarioModel.objects.get(pk=usuario.id)
        return self._to_entity(obj)

    def _to_entity(self, obj: UsuarioModel) -> Usuario:
        return Usuario(
            id=obj.id,
            nome=obj.nome,
            email=obj.email,
            matricula=obj.matricula,
            cargo=obj.cargo,
            is_ativo=obj.is_ativo,
            is_oculto=obj.is_oculto,
        )
