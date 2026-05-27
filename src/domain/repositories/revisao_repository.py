from typing import Optional, Protocol

from src.domain.entities.revisao import Revisao


class RevisaoRepository(Protocol):
    def salvar(self, revisao: Revisao) -> Revisao: ...
    def buscar_por_demanda(self, demanda_id: int) -> Optional[Revisao]: ...
