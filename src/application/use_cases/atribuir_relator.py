from dataclasses import dataclass, field
from datetime import date
from typing import Sequence

from src.domain.entities.demanda import Demanda
from src.domain.repositories.afastamento_repository import AfastamentoRepository
from src.domain.repositories.demanda_repository import DemandaRepository
from src.domain.repositories.feriado_repository import FeriadoRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.services.sorteio_justo import CandidatoSorteio, SorteioJustoService


@dataclass
class AtribuirRelatorInput:
    demanda_id: int
    meta_mensal_respostas: int = 12
    meta_mensal_revisoes: int = 12


class AtribuirRelatorUseCase:
    """
    Atribui automaticamente relator e revisor a uma demanda via sorteio justo.

    O sorteio prioriza membros que estão mais atrás na meta mensal e exclui
    quem está afastado (ou prestes a se afastar) na data de chegada da demanda.
    """

    def __init__(
        self,
        demanda_repo: DemandaRepository,
        usuario_repo: UsuarioRepository,
        afastamento_repo: AfastamentoRepository,
        feriado_repo: FeriadoRepository,
        sorteio: SorteioJustoService,
    ) -> None:
        self._demanda_repo = demanda_repo
        self._usuario_repo = usuario_repo
        self._afastamento_repo = afastamento_repo
        self._feriado_repo = feriado_repo
        self._sorteio = sorteio

    def executar(self, dto: AtribuirRelatorInput) -> Demanda:
        demanda = self._demanda_repo.buscar_por_id(dto.demanda_id)
        if demanda is None:
            raise ValueError(f"Demanda {dto.demanda_id} não encontrada")

        feriados = [f.data for f in self._feriado_repo.listar()]
        afastamentos = self._afastamento_repo.listar_ativos_na_data(demanda.dat_chegada)
        afastados_ids = {
            a.usuario_id
            for a in afastamentos
            if a.cobre_data(demanda.dat_chegada, feriados)
        }

        disponiveis = [
            u for u in self._usuario_repo.listar_ativos_visiveis()
            if u.id not in afastados_ids
        ]

        if not disponiveis:
            raise ValueError("Nenhum membro disponível para atribuição na data da demanda")

        mes, ano = demanda.dat_chegada.month, demanda.dat_chegada.year

        candidatos_relator = [
            CandidatoSorteio(
                usuario_id=u.id,
                percentual_meta=self._demanda_repo.contar_respostas_no_mes(u.id, mes, ano)
                / dto.meta_mensal_respostas,
            )
            for u in disponiveis
        ]
        demanda.id_relator = self._sorteio.selecionar(candidatos_relator)

        candidatos_revisor = [
            CandidatoSorteio(
                usuario_id=u.id,
                percentual_meta=self._demanda_repo.contar_revisoes_no_mes(u.id, mes, ano)
                / dto.meta_mensal_revisoes,
            )
            for u in disponiveis
            if u.id != demanda.id_relator
        ]

        if candidatos_revisor:
            demanda.id_revisor = self._sorteio.selecionar(candidatos_revisor)

        return self._demanda_repo.salvar(demanda)
