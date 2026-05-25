from datetime import date

import pytest

from tests.fakes.ia import FakeIA, FakeIAVazia
from tests.fakes.repos import FakeDemandaRepo
from src.application.use_cases.gerar_resumo import GerarResumoInput, GerarResumoUseCase
from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda


def _demanda(id: int = 1, texto: str = "Levantamento sobre PLs de criptoativos.") -> Demanda:
    return Demanda(
        id=id,
        origem="LAI",
        num_origem=None,
        texto=texto,
        dat_chegada=date(2026, 3, 10),
        prazo=Prazo(dias_uteis=20),
        status=StatusDemanda.PENDENTE_RESPOSTA,
    )


def test_gerar_resumo_retorna_output_com_texto():
    demanda = _demanda(id=1, texto="Quórum para aprovação de PEC?")
    uc = GerarResumoUseCase(repository=FakeDemandaRepo([demanda]), ia=FakeIA())
    output = uc.executar(GerarResumoInput(demanda_id=1))
    assert "Quórum para aprovação de PEC?" in output.resumo


def test_gerar_resumo_demanda_inexistente_lanca_erro():
    uc = GerarResumoUseCase(repository=FakeDemandaRepo(), ia=FakeIA())
    with pytest.raises(ValueError, match="42"):
        uc.executar(GerarResumoInput(demanda_id=42))


def test_gerar_resumo_ia_vazia_retorna_string_vazia():
    demanda = _demanda(id=1)
    uc = GerarResumoUseCase(repository=FakeDemandaRepo([demanda]), ia=FakeIAVazia())
    output = uc.executar(GerarResumoInput(demanda_id=1))
    assert output.resumo == ""
