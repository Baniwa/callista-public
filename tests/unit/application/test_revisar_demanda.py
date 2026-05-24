from datetime import date
from typing import Optional, Sequence

import pytest

from src.domain.entities.demanda import Demanda
from src.domain.entities.resposta import Resposta
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda
from src.application.use_cases.revisar_demanda import RevisarDemandaInput, RevisarDemandaUseCase


class FakeDemandaRepo:
    def __init__(self, demandas: list[Demanda]):
        self._demandas = {d.id: d for d in demandas}

    def buscar_por_id(self, id: int) -> Optional[Demanda]:
        return self._demandas.get(id)

    def salvar(self, demanda: Demanda) -> Demanda:
        self._demandas[demanda.id] = demanda
        return demanda

    def listar_por_status(self, status) -> Sequence[Demanda]: return []
    def listar_ativas(self) -> Sequence[Demanda]: return []
    def contar_respostas_no_mes(self, *_) -> int: return 0
    def contar_revisoes_no_mes(self, *_) -> int: return 0


class FakeRevisaoRepo:
    def __init__(self):
        self.salvas: list[Resposta] = []

    def salvar(self, revisao: Resposta) -> Resposta:
        self.salvas.append(revisao)
        return revisao

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Resposta]:
        return next((r for r in self.salvas if r.demanda_id == demanda_id), None)


def _demanda_respondida(id_revisor: int = 2) -> Demanda:
    d = Demanda(
        id=1, origem="SGM", num_origem=None,
        texto="Teste", dat_chegada=date(2026, 5, 26),
        prazo=Prazo(5), id_relator=1, id_revisor=id_revisor,
    )
    d.marcar_respondida()
    return d


def test_revisar_muda_status_para_concluida():
    demanda = _demanda_respondida()
    repo_revisao = FakeRevisaoRepo()
    uc = RevisarDemandaUseCase(FakeDemandaRepo([demanda]), repo_revisao)

    resultado = uc.executar(RevisarDemandaInput(demanda_id=1, usuario_id=2, texto="Revisão ok"))

    assert resultado.status == StatusDemanda.CONCLUIDA


def test_revisar_salva_texto_da_revisao():
    demanda = _demanda_respondida()
    repo_revisao = FakeRevisaoRepo()
    uc = RevisarDemandaUseCase(FakeDemandaRepo([demanda]), repo_revisao)

    uc.executar(RevisarDemandaInput(demanda_id=1, usuario_id=2, texto="Minha revisão"))

    assert len(repo_revisao.salvas) == 1
    assert repo_revisao.salvas[0].texto == "Minha revisão"


def test_usuario_errado_levanta_erro():
    demanda = _demanda_respondida(id_revisor=2)
    uc = RevisarDemandaUseCase(FakeDemandaRepo([demanda]), FakeRevisaoRepo())

    with pytest.raises(ValueError, match="não é o revisor"):
        uc.executar(RevisarDemandaInput(demanda_id=1, usuario_id=99, texto="Texto"))


def test_demanda_inexistente_levanta_erro():
    uc = RevisarDemandaUseCase(FakeDemandaRepo([]), FakeRevisaoRepo())

    with pytest.raises(ValueError, match="não encontrada"):
        uc.executar(RevisarDemandaInput(demanda_id=99, usuario_id=2, texto="Texto"))
