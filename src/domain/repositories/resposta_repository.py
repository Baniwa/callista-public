from typing import Optional, Protocol

from src.domain.entities.resposta import Resposta


class RespostaRepository(Protocol):
    def salvar(self, resposta: Resposta) -> Resposta: ...
    def buscar_por_demanda(self, demanda_id: int) -> Optional[Resposta]: ...
