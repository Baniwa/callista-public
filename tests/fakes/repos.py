"""
Implementações fake dos repositórios do domínio para uso em testes unitários.

Cada classe aqui é um adapter de teste — armazena dados em memória e segue
o mesmo contrato (Protocol) dos adapters reais (DjangoDemandaRepository, etc.).
Nenhum banco de dados é necessário.
"""
from typing import Optional, Sequence

from src.domain.entities.afastamento import Afastamento
from src.domain.entities.demanda import Demanda
from src.domain.entities.feriado import Feriado
from src.domain.entities.resposta import Resposta
from src.domain.entities.revisao import Revisao
from src.domain.entities.usuario import Usuario
from src.domain.value_objects.status import StatusDemanda


class FakeDemandaRepo:
    def __init__(self, demandas: list[Demanda] | None = None) -> None:
        self._demandas: dict[int, Demanda] = {d.id: d for d in (demandas or [])}

    def buscar_por_id(self, id: int) -> Optional[Demanda]:
        return self._demandas.get(id)

    def salvar(self, demanda: Demanda) -> Demanda:
        self._demandas[demanda.id] = demanda
        return demanda

    def listar_ativas(self) -> Sequence[Demanda]:
        return list(self._demandas.values())

    def listar_por_status(self, status: StatusDemanda) -> Sequence[Demanda]:
        return [d for d in self._demandas.values() if d.status == status]

    def contar_respostas_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return sum(
            1 for d in self._demandas.values()
            if d.id_relator == usuario_id
            and d.dat_chegada.month == mes
            and d.dat_chegada.year == ano
            and d.status in (StatusDemanda.PENDENTE_REVISAO, StatusDemanda.CONCLUIDA)
        )

    def contar_revisoes_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
        return sum(
            1 for d in self._demandas.values()
            if d.id_revisor == usuario_id
            and d.dat_chegada.month == mes
            and d.dat_chegada.year == ano
            and d.status == StatusDemanda.CONCLUIDA
        )


class FakeRespostaRepo:
    def __init__(self, resposta: Optional[Resposta] = None) -> None:
        self._resposta = resposta

    def salvar(self, resposta: Resposta) -> Resposta:
        self._resposta = resposta
        return resposta

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Resposta]:
        return self._resposta


class FakeUsuarioRepo:
    def __init__(self, usuarios: list[Usuario] | None = None) -> None:
        self._usuarios: dict[int, Usuario] = {u.id: u for u in (usuarios or [])}

    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        return self._usuarios.get(id)

    def listar_ativos_visiveis(self) -> Sequence[Usuario]:
        return [u for u in self._usuarios.values() if u.elegivel_para_demandas]

    def salvar(self, usuario: Usuario) -> Usuario:
        self._usuarios[usuario.id] = usuario
        return usuario


class FakeRevisaoRepo:
    def __init__(self, revisao: Optional[Revisao] = None) -> None:
        self._revisao = revisao

    def salvar(self, revisao: Revisao) -> Revisao:
        self._revisao = revisao
        return revisao

    def buscar_por_demanda(self, demanda_id: int) -> Optional[Revisao]:
        if self._revisao and self._revisao.demanda_id == demanda_id:
            return self._revisao
        return None


class FakeAfastamentoRepo:
    def __init__(self, afastamentos: list[Afastamento] | None = None) -> None:
        self._afastamentos = afastamentos or []

    def listar_ativos_na_data(self, data) -> Sequence[Afastamento]:
        return self._afastamentos


class FakeFeriadoRepo:
    def __init__(self, feriados: list[Feriado] | None = None) -> None:
        self._feriados = feriados or []

    def listar(self) -> Sequence[Feriado]:
        return self._feriados
