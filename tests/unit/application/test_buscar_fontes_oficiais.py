from datetime import date

import pytest

from tests.fakes.ia import FakeIA, FakeIAEspiao, FakeIAVazia
from tests.fakes.repos import FakeDemandaRepo
from src.application.use_cases.buscar_fontes_oficiais import (
    BuscarFontesInput,
    BuscarFontesOficiaisUseCase,
)
from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda


def _demanda(id: int = 1, texto: str = "Qual o quórum para aprovação de PEC?") -> Demanda:
    return Demanda(
        id=id,
        origem="SGM",
        num_origem=202601,
        texto=texto,
        dat_chegada=date(2026, 3, 1),
        prazo=Prazo(dias_uteis=3),
        status=StatusDemanda.PENDENTE_RESPOSTA,
    )


def test_busca_fontes_para_demanda_existente():
    demanda = _demanda(id=1)
    uc = BuscarFontesOficiaisUseCase(
        repository=FakeDemandaRepo([demanda]),
        ia=FakeIA(),
    )
    fontes = uc.executar(BuscarFontesInput(demanda_id=1))
    assert len(fontes) == 1
    assert fontes[0].titulo == "Regimento Interno do Senado Federal"
    assert fontes[0].orgao == "Senado Federal"


def test_busca_fontes_passa_texto_da_demanda_para_ia():
    """O use case deve repassar o texto da demanda, não o ID."""
    demanda = _demanda(id=5, texto="Quórum para aprovação de emenda constitucional?")
    ia = FakeIAEspiao()
    uc = BuscarFontesOficiaisUseCase(
        repository=FakeDemandaRepo([demanda]),
        ia=ia,
    )
    uc.executar(BuscarFontesInput(demanda_id=5))
    assert ia.textos_busca == ["Quórum para aprovação de emenda constitucional?"]


def test_demanda_nao_encontrada_lanca_erro():
    uc = BuscarFontesOficiaisUseCase(
        repository=FakeDemandaRepo(),
        ia=FakeIA(),
    )
    with pytest.raises(ValueError, match="99"):
        uc.executar(BuscarFontesInput(demanda_id=99))


def test_ia_sem_fontes_retorna_lista_vazia():
    demanda = _demanda(id=1)
    uc = BuscarFontesOficiaisUseCase(
        repository=FakeDemandaRepo([demanda]),
        ia=FakeIAVazia(),
    )
    fontes = uc.executar(BuscarFontesInput(demanda_id=1))
    assert fontes == []
