from datetime import date
from typing import Optional, Sequence

import pytest

from src.domain.entities.afastamento import Afastamento
from src.domain.entities.demanda import Demanda
from src.domain.entities.feriado import Feriado
from src.domain.entities.usuario import Usuario
from src.domain.services.sorteio_justo import SorteioJustoService
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda
from src.application.use_cases.atribuir_relator import AtribuirRelatorInput, AtribuirRelatorUseCase


# --- Fakes de repositório (sem banco, sem Django) ---

class FakeDemandaRepo:
    def __init__(self, demandas: list[Demanda]):
        self._demandas = {d.id: d for d in demandas}

    def buscar_por_id(self, id: int) -> Optional[Demanda]:
        return self._demandas.get(id)

    def salvar(self, demanda: Demanda) -> Demanda:
        self._demandas[demanda.id] = demanda
        return demanda

    def listar_por_status(self, status: StatusDemanda) -> Sequence[Demanda]:
        return [d for d in self._demandas.values() if d.status == status]

    def listar_ativas(self) -> Sequence[Demanda]:
        return list(self._demandas.values())

    def contar_respostas_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return sum(
            1 for d in self._demandas.values()
            if d.id_relator == usuario_id
            and d.dat_chegada.month == mes
            and d.dat_chegada.year == ano
            and d.respondida
        )

    def contar_revisoes_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return sum(
            1 for d in self._demandas.values()
            if d.id_revisor == usuario_id
            and d.dat_chegada.month == mes
            and d.dat_chegada.year == ano
            and d.concluida
        )


class FakeUsuarioRepo:
    def __init__(self, usuarios: list[Usuario]):
        self._usuarios = usuarios

    def listar_ativos_visiveis(self) -> Sequence[Usuario]:
        return [u for u in self._usuarios if u.elegivel_para_demandas]

    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        return next((u for u in self._usuarios if u.id == id), None)

    def salvar(self, usuario: Usuario) -> Usuario:
        return usuario


class FakeAfastamentoRepo:
    def __init__(self, afastamentos: list[Afastamento] = None):
        self._afastamentos = afastamentos or []

    def listar_ativos_na_data(self, data: date) -> Sequence[Afastamento]:
        return [
            a for a in self._afastamentos
            if a.dat_inicial <= data <= a.dat_final
        ]


class FakeFeriadoRepo:
    def __init__(self, feriados: list[Feriado] = None):
        self._feriados = feriados or []

    def listar(self) -> Sequence[Feriado]:
        return self._feriados


# --- Fixtures ---

def _demanda(id: int, dat_chegada: date = date(2026, 5, 26)) -> Demanda:
    return Demanda(id=id, origem="SGM", num_origem=None, texto="Teste", dat_chegada=dat_chegada, prazo=Prazo(5))


def _usuario(id: int, **kwargs) -> Usuario:
    return Usuario(id=id, nome=f"Usuario {id}", email=f"u{id}@senado.leg.br", matricula=str(id), **kwargs)


def _use_case(demandas=None, usuarios=None, afastamentos=None, feriados=None):
    return AtribuirRelatorUseCase(
        demanda_repo=FakeDemandaRepo(demandas or []),
        usuario_repo=FakeUsuarioRepo(usuarios or []),
        afastamento_repo=FakeAfastamentoRepo(afastamentos),
        feriado_repo=FakeFeriadoRepo(feriados),
        sorteio=SorteioJustoService(),
    )


# --- Testes ---

def test_atribui_relator_e_revisor_diferentes():
    demanda = _demanda(id=1)
    usuarios = [_usuario(1), _usuario(2), _usuario(3)]
    uc = _use_case(demandas=[demanda], usuarios=usuarios)

    resultado = uc.executar(AtribuirRelatorInput(demanda_id=1))

    assert resultado.id_relator is not None
    assert resultado.id_revisor is not None
    assert resultado.id_relator != resultado.id_revisor


def test_demanda_inexistente_levanta_erro():
    uc = _use_case(demandas=[], usuarios=[_usuario(1)])
    with pytest.raises(ValueError, match="não encontrada"):
        uc.executar(AtribuirRelatorInput(demanda_id=99))


def test_sem_membros_disponiveis_levanta_erro():
    demanda = _demanda(id=1)
    uc = _use_case(demandas=[demanda], usuarios=[])
    with pytest.raises(ValueError, match="Nenhum membro disponível"):
        uc.executar(AtribuirRelatorInput(demanda_id=1))


def test_membro_afastado_excluido_do_sorteio():
    demanda = _demanda(id=1, dat_chegada=date(2026, 6, 15))
    usuarios = [_usuario(1), _usuario(2)]
    # usuario 1 está afastado na data da demanda
    afastamento = Afastamento(
        id=1, usuario_id=1,
        dat_inicial=date(2026, 6, 15), dat_final=date(2026, 6, 20),
        motivo="Férias"
    )
    uc = _use_case(demandas=[demanda], usuarios=usuarios, afastamentos=[afastamento])

    for _ in range(20):
        resultado = uc.executar(AtribuirRelatorInput(demanda_id=1))
        assert resultado.id_relator != 1


def test_membro_oculto_nao_participa_do_sorteio():
    demanda = _demanda(id=1)
    usuarios = [_usuario(1, is_oculto=True), _usuario(2)]
    uc = _use_case(demandas=[demanda], usuarios=usuarios)

    for _ in range(20):
        resultado = uc.executar(AtribuirRelatorInput(demanda_id=1))
        assert resultado.id_relator == 2


def test_com_unico_membro_disponivel_nao_atribui_revisor():
    demanda = _demanda(id=1)
    uc = _use_case(demandas=[demanda], usuarios=[_usuario(1)])

    resultado = uc.executar(AtribuirRelatorInput(demanda_id=1))

    assert resultado.id_relator == 1
    assert resultado.id_revisor is None
