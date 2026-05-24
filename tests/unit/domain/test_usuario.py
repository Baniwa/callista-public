import pytest

from src.domain.entities.usuario import Usuario


def _usuario_base(**kwargs) -> Usuario:
    defaults = dict(id=1, nome="Ana Silva", email="ana@senado.leg.br", matricula="123456")
    return Usuario(**{**defaults, **kwargs})


def test_usuario_elegivel_por_padrao():
    u = _usuario_base()
    assert u.elegivel_para_demandas is True


def test_usuario_oculto_nao_e_elegivel():
    u = _usuario_base(is_oculto=True)
    assert u.elegivel_para_demandas is False


def test_usuario_inativo_nao_e_elegivel():
    u = _usuario_base(is_ativo=False)
    assert u.elegivel_para_demandas is False


def test_usuario_inativo_e_oculto_nao_e_elegivel():
    u = _usuario_base(is_ativo=False, is_oculto=True)
    assert u.elegivel_para_demandas is False


def test_usuario_cargo_default_vazio():
    u = _usuario_base()
    assert u.cargo == ""
