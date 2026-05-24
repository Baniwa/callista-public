from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.domain.entities.demanda import Demanda
from src.domain.repositories.demanda_repository import DemandaRepository
from src.domain.value_objects.prazo import Prazo


@dataclass
class CadastrarDemandaInput:
    origem: str
    texto: str
    dat_chegada: date
    dias_prazo: int
    id_usuario_criacao: int
    num_origem: Optional[int] = None


class CadastrarDemandaUseCase:
    def __init__(self, repository: DemandaRepository) -> None:
        self._repository = repository

    def executar(self, dto: CadastrarDemandaInput) -> Demanda:
        demanda = Demanda(
            id=None,
            origem=dto.origem,
            num_origem=dto.num_origem,
            texto=dto.texto,
            dat_chegada=dto.dat_chegada,
            prazo=Prazo(dias_uteis=dto.dias_prazo),
        )
        return self._repository.salvar(demanda)
