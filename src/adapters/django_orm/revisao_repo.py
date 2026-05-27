from typing import Optional

from src.domain.entities.revisao import Revisao
from .models import RevisaoModel


class DjangoRevisaoRepository:
    def salvar(self, revisao: Revisao) -> Revisao:
        if revisao.id is None:
            obj = RevisaoModel.objects.create(
                demanda_id=revisao.demanda_id,
                usuario_id=revisao.usuario_id,
                texto=revisao.texto,
                editado=revisao.editado,
                editado_por_id=revisao.editado_por_id,
                dat_edicao=revisao.dat_edicao,
            )
        else:
            RevisaoModel.objects.filter(pk=revisao.id).update(
                texto=revisao.texto,
                editado=revisao.editado,
                editado_por_id=revisao.editado_por_id,
                dat_edicao=revisao.dat_edicao,
            )
            obj = RevisaoModel.objects.get(pk=revisao.id)
        return self._to_entity(obj)

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Revisao]:
        try:
            return self._to_entity(RevisaoModel.objects.get(demanda_id=demanda_id))
        except RevisaoModel.DoesNotExist:
            return None

    def _to_entity(self, obj: RevisaoModel) -> Revisao:
        return Revisao(
            id=obj.id,
            demanda_id=obj.demanda_id,
            usuario_id=obj.usuario_id,
            texto=obj.texto,
            dat_revisao=obj.dat_revisao,
            editado=obj.editado,
            editado_por_id=obj.editado_por_id,
            dat_edicao=obj.dat_edicao,
        )
