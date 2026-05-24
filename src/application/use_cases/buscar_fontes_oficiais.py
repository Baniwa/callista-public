from dataclasses import dataclass
from typing import Sequence

from src.application.ports.ai_port import FonteOficial, IAPort
from src.domain.repositories.demanda_repository import DemandaRepository


@dataclass
class BuscarFontesInput:
    demanda_id: int


class BuscarFontesOficiaisUseCase:
    def __init__(self, repository: DemandaRepository, ia: IAPort) -> None:
        self._repository = repository
        self._ia = ia

    def executar(self, dto: BuscarFontesInput) -> Sequence[FonteOficial]:
        demanda = self._repository.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")
        return self._ia.buscar_fontes(demanda.texto)
