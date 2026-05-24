from datetime import date
import pytest

from src.domain.entities.afastamento import Afastamento


def _afastamento(ini: date, fim: date) -> Afastamento:
    return Afastamento(id=None, usuario_id=1, dat_inicial=ini, dat_final=fim, motivo="Férias")


def test_cobre_data_dentro_do_periodo():
    af = _afastamento(date(2026, 6, 10), date(2026, 6, 20))
    assert af.cobre_data(date(2026, 6, 15)) is True


def test_cobre_data_no_fim_do_periodo():
    af = _afastamento(date(2026, 6, 10), date(2026, 6, 20))
    assert af.cobre_data(date(2026, 6, 20)) is True


def test_nao_cobre_data_apos_periodo():
    af = _afastamento(date(2026, 6, 10), date(2026, 6, 20))
    assert af.cobre_data(date(2026, 6, 21)) is False


def test_cobre_data_antecipando_2_dias_uteis():
    # Afastamento inicia na quarta 2026-06-10
    # 2 dias úteis antes = segunda 2026-06-08
    af = _afastamento(date(2026, 6, 10), date(2026, 6, 20))
    assert af.cobre_data(date(2026, 6, 8)) is True


def test_nao_cobre_data_3_dias_uteis_antes_do_inicio():
    # 3 dias úteis antes da quarta 06-10 = sexta 06-05
    af = _afastamento(date(2026, 6, 10), date(2026, 6, 20))
    assert af.cobre_data(date(2026, 6, 5)) is False


def test_antecipacao_pula_fim_de_semana():
    # Afastamento inicia na segunda 2026-06-15
    # 2 dias úteis antes pulando fim de semana (sáb/dom) = quinta 2026-06-11
    af = _afastamento(date(2026, 6, 15), date(2026, 6, 25))
    assert af.cobre_data(date(2026, 6, 11)) is True
    assert af.cobre_data(date(2026, 6, 10)) is False


def test_antecipacao_pula_feriado():
    feriados = [date(2026, 6, 11)]  # quinta é feriado
    # Afastamento inicia na segunda 2026-06-15
    # Com feriado na quinta: 2 dias úteis antes = quarta 2026-06-10
    af = _afastamento(date(2026, 6, 15), date(2026, 6, 25))
    assert af.cobre_data(date(2026, 6, 10), feriados) is True
    assert af.cobre_data(date(2026, 6, 9), feriados) is False
