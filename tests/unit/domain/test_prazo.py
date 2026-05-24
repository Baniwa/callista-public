from datetime import date
import pytest

from src.domain.value_objects.prazo import Prazo


def test_prazo_calcula_data_limite_em_dias_uteis():
    prazo = Prazo(dias_uteis=5)
    # Segunda-feira + 5 dias úteis = segunda-feira seguinte
    resultado = prazo.data_limite(a_partir_de=date(2026, 5, 25))
    assert resultado == date(2026, 6, 1)


def test_prazo_pula_fins_de_semana():
    prazo = Prazo(dias_uteis=1)
    # Sexta-feira + 1 dia útil = segunda-feira
    resultado = prazo.data_limite(a_partir_de=date(2026, 5, 29))
    assert resultado == date(2026, 6, 1)


def test_prazo_pula_feriados():
    prazo = Prazo(dias_uteis=1)
    feriados = [date(2026, 5, 26)]
    # Segunda + feriado na terça → próximo dia útil = quarta
    resultado = prazo.data_limite(a_partir_de=date(2026, 5, 25), feriados=feriados)
    assert resultado == date(2026, 5, 27)


def test_prazo_invalido_levanta_erro():
    with pytest.raises(ValueError):
        Prazo(dias_uteis=0)
