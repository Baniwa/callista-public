from dataclasses import dataclass

from src.application.ports.ai_port import IAPort
from src.domain.repositories.demanda_repository import DemandaRepository


@dataclass
class GerarResumoInput:
    demanda_id: int


@dataclass
class GerarResumoOutput:
    resumo: str


class GerarResumoUseCase:
    def __init__(self, repository: DemandaRepository, ia: IAPort) -> None:
        self._repository = repository
        self._ia = ia

    def executar(self, dto: GerarResumoInput) -> GerarResumoOutput:
        demanda = self._repository.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")
        resumo = self._ia.gerar_resumo(demanda.texto)
        return GerarResumoOutput(resumo=resumo)
