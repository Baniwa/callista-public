from datetime import date, datetime

import pytest

from tests.fakes.repos import FakeProjetoLeiRepo
from tests.fakes.senado import FakeSenado, FakeSenadoVazio
from src.application.use_cases.rastrear_pl import RastrearPLInput, RastrearPLUseCase
from src.domain.entities.projeto_lei import ProjetoLei


def _pl(
    id_senado: int = 8503515,
    identificacao: str = "PEC 45/2019",
    sigla: str = "PEC",
    numero: int = 45,
    ano: int = 2019,
    situacao_atual: str = "TRANSFORMADA EM NORMA JURÍDICA",
    tramitando: bool = False,
) -> ProjetoLei:
    return ProjetoLei(
        id=None,
        id_senado=id_senado,
        identificacao=identificacao,
        sigla=sigla,
        numero=numero,
        ano=ano,
        ementa="Altera o Sistema Tributário Nacional.",
        tramitando=tramitando,
        situacao_atual=situacao_atual,
        sigla_situacao="TNJR",
        dat_situacao=date(2023, 12, 20),
        url_documento="https://legis.senado.gov.br/sdleg-getter/documento?dm=123",
        autoria="Câmara dos Deputados",
        dat_ultima_atualizacao=datetime(2024, 1, 5, 10, 0, 0),
    )


def test_rastrear_pl_novo_salva_e_retorna():
    pl = _pl()
    uc = RastrearPLUseCase(
        senado=FakeSenado(pl),
        pl_repo=FakeProjetoLeiRepo(),
    )
    resultado = uc.executar(RastrearPLInput(sigla="PEC", numero=45, ano=2019))
    assert resultado.id_senado == 8503515
    assert resultado.identificacao == "PEC 45/2019"
    assert resultado.id is not None


def test_rastrear_pl_atualiza_snapshot_existente():
    pl_antigo = _pl(situacao_atual="EM TRAMITAÇÃO")
    pl_antigo.id = 1
    repo = FakeProjetoLeiRepo([pl_antigo])

    pl_novo = _pl(situacao_atual="APROVADO")
    uc = RastrearPLUseCase(
        senado=FakeSenado(pl_novo),
        pl_repo=repo,
    )
    resultado = uc.executar(RastrearPLInput(sigla="PEC", numero=45, ano=2019))

    assert resultado.id == 1
    assert resultado.situacao_atual == "APROVADO"


def test_rastrear_pl_vincula_demanda():
    uc = RastrearPLUseCase(
        senado=FakeSenado(_pl()),
        pl_repo=FakeProjetoLeiRepo(),
    )
    resultado = uc.executar(RastrearPLInput(sigla="PEC", numero=45, ano=2019, demanda_id=7))
    assert resultado.demanda_id == 7


def test_rastrear_pl_sem_demanda_nao_vincula():
    uc = RastrearPLUseCase(
        senado=FakeSenado(_pl()),
        pl_repo=FakeProjetoLeiRepo(),
    )
    resultado = uc.executar(RastrearPLInput(sigla="PEC", numero=45, ano=2019))
    assert resultado.demanda_id is None


def test_pl_nao_encontrado_lanca_erro():
    uc = RastrearPLUseCase(
        senado=FakeSenadoVazio(),
        pl_repo=FakeProjetoLeiRepo(),
    )
    with pytest.raises(ValueError, match="PEC 45/2019"):
        uc.executar(RastrearPLInput(sigla="PEC", numero=45, ano=2019))


def test_listar_pls_por_demanda():
    pl1 = _pl(id_senado=1)
    pl1.demanda_id = 10
    pl1.id = 1
    pl2 = _pl(id_senado=2)
    pl2.demanda_id = 99
    pl2.id = 2
    repo = FakeProjetoLeiRepo([pl1, pl2])
    resultado = repo.listar_por_demanda(10)
    assert len(resultado) == 1
    assert resultado[0].id_senado == 1
