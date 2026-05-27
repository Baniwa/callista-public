from typing import Sequence

from src.domain.entities.historico_atribuicao import HistoricoAtribuicao, TipoAtribuicao
from .models import HistoricoAtribuicaoModel


class DjangoHistoricoAtribuicaoRepository:
    def salvar(self, historico: HistoricoAtribuicao) -> HistoricoAtribuicao:
        obj = HistoricoAtribuicaoModel.objects.create(
            demanda_id=historico.demanda_id,
            usuario_id=historico.usuario_id,
            tipo=historico.tipo.value,
            valido=historico.valido,
        )
        return self._to_entity(obj)

    def listar_por_demanda(self, demanda_id: int) -> Sequence[HistoricoAtribuicao]:
        return [
            self._to_entity(obj)
            for obj in HistoricoAtribuicaoModel.objects.filter(demanda_id=demanda_id)
        ]

    def _to_entity(self, obj: HistoricoAtribuicaoModel) -> HistoricoAtribuicao:
        return HistoricoAtribuicao(
            id=obj.id,
            demanda_id=obj.demanda_id,
            usuario_id=obj.usuario_id,
            tipo=TipoAtribuicao(obj.tipo),
            data_atribuicao=obj.data_atribuicao,
            valido=obj.valido,
        )
