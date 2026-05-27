from datetime import date

import pytest

from src.application.use_cases.revisar_demanda import RevisarDemandaInput, RevisarDemandaUseCase
from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda
from tests.fakes.repos import FakeDemandaRepo, FakeRevisaoRepo


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

    assert repo_revisao._revisao is not None
    assert repo_revisao._revisao.texto == "Minha revisão"


def test_usuario_errado_levanta_erro():
    demanda = _demanda_respondida(id_revisor=2)
    uc = RevisarDemandaUseCase(FakeDemandaRepo([demanda]), FakeRevisaoRepo())

    with pytest.raises(ValueError, match="não é o revisor"):
        uc.executar(RevisarDemandaInput(demanda_id=1, usuario_id=99, texto="Texto"))


def test_demanda_inexistente_levanta_erro():
    uc = RevisarDemandaUseCase(FakeDemandaRepo([]), FakeRevisaoRepo())

    with pytest.raises(ValueError, match="não encontrada"):
        uc.executar(RevisarDemandaInput(demanda_id=99, usuario_id=2, texto="Texto"))
