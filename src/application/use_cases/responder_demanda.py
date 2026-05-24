from dataclasses import dataclass

from src.domain.entities.demanda import Demanda
from src.domain.entities.resposta import Resposta
from src.domain.repositories.demanda_repository import DemandaRepository
from src.domain.repositories.resposta_repository import RespostaRepository


@dataclass
class ResponderDemandaInput:
    demanda_id: int
    usuario_id: int
    texto: str


class ResponderDemandaUseCase:
    def __init__(
        self,
        demanda_repo: DemandaRepository,
        resposta_repo: RespostaRepository,
    ) -> None:
        self._demanda_repo = demanda_repo
        self._resposta_repo = resposta_repo

    def executar(self, dto: ResponderDemandaInput) -> Demanda:
        demanda = self._demanda_repo.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")
        if demanda.id_relator != dto.usuario_id:
            raise ValueError("Usuário não é o relator desta demanda")

        demanda.marcar_respondida()

        self._resposta_repo.salvar(
            Resposta(id=None, demanda_id=dto.demanda_id, usuario_id=dto.usuario_id, texto=dto.texto)
        )

        return self._demanda_repo.salvar(demanda)
