from typing import Optional, Protocol

from src.domain.entities.pendencia_externa import PendenciaExterna


class PendenciaExternaRepository(Protocol):
    def salvar(self, pendencia: PendenciaExterna) -> PendenciaExterna: ...
    def buscar_por_demanda(self, demanda_id: int) -> Optional[PendenciaExterna]: ...
