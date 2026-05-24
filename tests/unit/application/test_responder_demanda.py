from datetime import date
from typing import Optional, Sequence

import pytest

from src.domain.entities.demanda import Demanda
from src.domain.entities.resposta import Resposta
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda
from src.application.use_cases.responder_demanda import ResponderDemandaInput, ResponderDemandaUseCase


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


class FakeRespostaRepo:
    def __init__(self):
        self.salvas: list[Resposta] = []

    def salvar(self, resposta: Resposta) -> Resposta:
        self.salvas.append(resposta)
        return resposta

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Resposta]:
        return next((r for r in self.salvas if r.demanda_id == demanda_id), None)


def _demanda(id_relator: int = 1, id_revisor: int = 2) -> Demanda:
    return Demanda(
        id=1, origem="SGM", num_origem=None,
        texto="Teste", dat_chegada=date(2026, 5, 26),
        prazo=Prazo(5), id_relator=id_relator, id_revisor=id_revisor,
    )


def test_responder_muda_status_para_pendente_revisao():
    demanda = _demanda()
    repo_resposta = FakeRespostaRepo()
    uc = ResponderDemandaUseCase(FakeDemandaRepo([demanda]), repo_resposta)

    resultado = uc.executar(ResponderDemandaInput(demanda_id=1, usuario_id=1, texto="Resposta aqui"))

    assert resultado.status == StatusDemanda.PENDENTE_REVISAO


def test_responder_salva_texto_da_resposta():
    demanda = _demanda()
    repo_resposta = FakeRespostaRepo()
    uc = ResponderDemandaUseCase(FakeDemandaRepo([demanda]), repo_resposta)

    uc.executar(ResponderDemandaInput(demanda_id=1, usuario_id=1, texto="Minha resposta"))

    assert len(repo_resposta.salvas) == 1
    assert repo_resposta.salvas[0].texto == "Minha resposta"


def test_usuario_errado_levanta_erro():
    demanda = _demanda(id_relator=1)
    uc = ResponderDemandaUseCase(FakeDemandaRepo([demanda]), FakeRespostaRepo())

    with pytest.raises(ValueError, match="não é o relator"):
        uc.executar(ResponderDemandaInput(demanda_id=1, usuario_id=99, texto="Texto"))


def test_demanda_inexistente_levanta_erro():
    uc = ResponderDemandaUseCase(FakeDemandaRepo([]), FakeRespostaRepo())

    with pytest.raises(ValueError, match="não encontrada"):
        uc.executar(ResponderDemandaInput(demanda_id=99, usuario_id=1, texto="Texto"))
