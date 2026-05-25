from dataclasses import dataclass

from src.application.ports.ai_port import IAPort
from src.domain.repositories.demanda_repository import DemandaRepository
from src.domain.repositories.resposta_repository import RespostaRepository


@dataclass
class SugerirRascunhoInput:
    demanda_id: int


@dataclass
class SugerirRascunhoOutput:
    rascunho: str


class SugerirRascunhoUseCase:
    def __init__(
        self,
        demanda_repo: DemandaRepository,
        resposta_repo: RespostaRepository,
        ia: IAPort,
    ) -> None:
        self._demanda_repo = demanda_repo
        self._resposta_repo = resposta_repo
        self._ia = ia

    def executar(self, dto: SugerirRascunhoInput) -> SugerirRascunhoOutput:
        demanda = self._demanda_repo.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")

        resposta_existente = self._resposta_repo.buscar_por_demanda(dto.demanda_id)
        textos_anteriores = [resposta_existente.texto] if resposta_existente else []

        rascunho = self._ia.sugerir_rascunho(demanda.texto, textos_anteriores)
        return SugerirRascunhoOutput(rascunho=rascunho)
