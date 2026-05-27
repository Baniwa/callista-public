from typing import Optional

from src.domain.entities.resposta import Resposta
from .models import RespostaModel


class DjangoRespostaRepository:
    def salvar(self, resposta: Resposta) -> Resposta:
        if resposta.id is None:
            obj = RespostaModel.objects.create(
                demanda_id=resposta.demanda_id,
                usuario_id=resposta.usuario_id,
                texto=resposta.texto,
                editado=resposta.editado,
                editado_por_id=resposta.editado_por_id,
                dat_edicao=resposta.dat_edicao,
            )
        else:
            RespostaModel.objects.filter(pk=resposta.id).update(
                texto=resposta.texto,
                editado=resposta.editado,
                editado_por_id=resposta.editado_por_id,
                dat_edicao=resposta.dat_edicao,
            )
            obj = RespostaModel.objects.get(pk=resposta.id)
        return self._to_entity(obj)

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Resposta]:
        obj = RespostaModel.objects.filter(demanda_id=demanda_id).order_by("dat_resposta").first()
        return self._to_entity(obj) if obj else None

    def _to_entity(self, obj: RespostaModel) -> Resposta:
        return Resposta(
            id=obj.id,
            demanda_id=obj.demanda_id,
            usuario_id=obj.usuario_id,
            texto=obj.texto,
            dat_resposta=obj.dat_resposta,
            editado=obj.editado,
            editado_por_id=obj.editado_por_id,
            dat_edicao=obj.dat_edicao,
        )
