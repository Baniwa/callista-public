from datetime import date

import pytest

from tests.fakes.ia import FakeIAEspiao, FakeIA
from tests.fakes.repos import FakeDemandaRepo, FakeRespostaRepo
from src.application.use_cases.sugerir_rascunho import (
    SugerirRascunhoInput,
    SugerirRascunhoUseCase,
)
from src.domain.entities.demanda import Demanda
from src.domain.entities.resposta import Resposta
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda


def _demanda(id: int = 1) -> Demanda:
    return Demanda(
        id=id,
        origem="IMP",
        num_origem=None,
        texto="Nota técnica sobre o PL 1234/2025.",
        dat_chegada=date(2026, 4, 1),
        prazo=Prazo(dias_uteis=2),
        status=StatusDemanda.PENDENTE_RESPOSTA,
    )


def test_sugerir_rascunho_sem_resposta_anterior():
    demanda = _demanda(id=1)
    ia = FakeIAEspiao()
    uc = SugerirRascunhoUseCase(
        demanda_repo=FakeDemandaRepo([demanda]),
        resposta_repo=FakeRespostaRepo(resposta=None),
        ia=ia,
    )
    output = uc.executar(SugerirRascunhoInput(demanda_id=1))
    assert output.rascunho == "Rascunho do espião."
    assert ia.contextos_rascunho[0] == []


def test_sugerir_rascunho_com_resposta_anterior_como_contexto():
    demanda = _demanda(id=1)
    resposta_existente = Resposta(
        id=10,
        demanda_id=1,
        usuario_id=2,
        texto="Conforme análise realizada, verificou-se que...",
    )
    ia = FakeIAEspiao()
    uc = SugerirRascunhoUseCase(
        demanda_repo=FakeDemandaRepo([demanda]),
        resposta_repo=FakeRespostaRepo(resposta=resposta_existente),
        ia=ia,
    )
    uc.executar(SugerirRascunhoInput(demanda_id=1))
    assert ia.contextos_rascunho[0] == ["Conforme análise realizada, verificou-se que..."]


def test_sugerir_rascunho_demanda_inexistente_lanca_erro():
    ia = FakeIAEspiao()
    uc = SugerirRascunhoUseCase(
        demanda_repo=FakeDemandaRepo(),
        resposta_repo=FakeRespostaRepo(),
        ia=ia,
    )
    with pytest.raises(ValueError, match="77"):
        uc.executar(SugerirRascunhoInput(demanda_id=77))


def test_sugerir_rascunho_passa_texto_da_demanda_para_ia():
    demanda = _demanda(id=1)
    ia = FakeIAEspiao()
    uc = SugerirRascunhoUseCase(
        demanda_repo=FakeDemandaRepo([demanda]),
        resposta_repo=FakeRespostaRepo(),
        ia=ia,
    )
    uc.executar(SugerirRascunhoInput(demanda_id=1))
    assert ia.textos_rascunho[0] == "Nota técnica sobre o PL 1234/2025."
