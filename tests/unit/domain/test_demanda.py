from datetime import date
import pytest

from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda


def _demanda_base() -> Demanda:
    return Demanda(
        id=None,
        origem="SGM",
        num_origem=1847,
        texto="Texto da demanda de teste",
        dat_chegada=date(2026, 5, 24),
        prazo=Prazo(dias_uteis=5),
    )


def test_demanda_criada_com_status_pendente():
    demanda = _demanda_base()
    assert demanda.status == StatusDemanda.PENDENTE_RESPOSTA
    assert not demanda.respondida
    assert not demanda.concluida


def test_marcar_respondida_muda_status():
    demanda = _demanda_base()
    demanda.marcar_respondida()
    assert demanda.status == StatusDemanda.PENDENTE_REVISAO
    assert demanda.respondida


def test_marcar_concluida_muda_status():
    demanda = _demanda_base()
    demanda.marcar_respondida()
    demanda.marcar_concluida()
    assert demanda.status == StatusDemanda.CONCLUIDA
    assert demanda.concluida


def test_marcar_respondida_sem_estar_pendente_levanta_erro():
    demanda = _demanda_base()
    demanda.marcar_respondida()
    with pytest.raises(ValueError):
        demanda.marcar_respondida()


def test_marcar_concluida_sem_revisao_levanta_erro():
    demanda = _demanda_base()
    with pytest.raises(ValueError):
        demanda.marcar_concluida()
