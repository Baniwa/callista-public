from dataclasses import dataclass
from typing import Optional

from src.application.ports.senado_port import SenadoPort
from src.domain.entities.projeto_lei import ProjetoLei
from src.domain.repositories.projeto_lei_repository import ProjetoLeiRepository


@dataclass
class RastrearPLInput:
    sigla: str
    numero: int
    ano: int
    demanda_id: Optional[int] = None


class RastrearPLUseCase:
    def __init__(self, senado: SenadoPort, pl_repo: ProjetoLeiRepository) -> None:
        self._senado = senado
        self._pl_repo = pl_repo

    def executar(self, dto: RastrearPLInput) -> ProjetoLei:
        pl = self._senado.buscar_pl(dto.sigla, dto.numero, dto.ano)
        if pl is None:
            raise ValueError(
                f"PL {dto.sigla} {dto.numero}/{dto.ano} não encontrado na API do Senado"
            )

        existente = self._pl_repo.buscar_por_id_senado(pl.id_senado)
        if existente:
            pl.id = existente.id

        if dto.demanda_id is not None:
            pl.demanda_id = dto.demanda_id

        return self._pl_repo.salvar(pl)
