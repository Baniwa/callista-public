from dataclasses import dataclass

from src.domain.entities.demanda import Demanda
from src.domain.entities.revisao import Revisao
from src.domain.repositories.demanda_repository import DemandaRepository
from src.domain.repositories.revisao_repository import RevisaoRepository


@dataclass
class RevisarDemandaInput:
    demanda_id: int
    usuario_id: int
    texto: str


class RevisarDemandaUseCase:
    def __init__(
        self,
        demanda_repo: DemandaRepository,
        revisao_repo: RevisaoRepository,
    ) -> None:
        self._demanda_repo = demanda_repo
        self._revisao_repo = revisao_repo

    def executar(self, dto: RevisarDemandaInput) -> Demanda:
        demanda = self._demanda_repo.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")
        if demanda.id_revisor != dto.usuario_id:
            raise ValueError("Usuário não é o revisor desta demanda")

        demanda.marcar_concluida()

        self._revisao_repo.salvar(
            Revisao(id=None, demanda_id=dto.demanda_id, usuario_id=dto.usuario_id, texto=dto.texto)
        )

        return self._demanda_repo.salvar(demanda)
