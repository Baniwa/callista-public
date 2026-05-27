from typing import Protocol, Sequence

from src.domain.entities.historico_atribuicao import HistoricoAtribuicao


class HistoricoAtribuicaoRepository(Protocol):
    def salvar(self, historico: HistoricoAtribuicao) -> HistoricoAtribuicao: ...
    def listar_por_demanda(self, demanda_id: int) -> Sequence[HistoricoAtribuicao]: ...
