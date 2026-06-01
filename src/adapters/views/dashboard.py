from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.adapters.views.mixins import usuario_ativo_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from src.adapters.django_orm.demanda_repo import DjangoDemandaRepository
from src.adapters.django_orm.usuario_repo import DjangoUsuarioRepository
from src.domain.entities.demanda import Demanda
from src.domain.value_objects.prazo import Prazo
from src.domain.value_objects.status import StatusDemanda


@dataclass
class DemandaRow:
    demanda: Demanda
    data_limite: date
    dias_restantes: int
    relator: Optional[str]
    revisor: Optional[str]


@dataclass
class KPIs:
    em_aberto: int
    para_responder: int
    para_revisar: int
    atrasadas: int
    finalizadas_hoje: int


@usuario_ativo_required
def dashboard(request: HttpRequest) -> HttpResponse:
    demanda_repo = DjangoDemandaRepository()
    usuario_repo = DjangoUsuarioRepository()
    hoje = date.today()

    ativas = demanda_repo.listar_ativas()

    rows = []
    for demanda in ativas:
        data_limite = demanda.prazo.data_limite(demanda.dat_chegada)
        dias_restantes = (data_limite - hoje).days

        relator = None
        revisor = None
        if demanda.id_relator:
            u = usuario_repo.buscar_por_id(demanda.id_relator)
            relator = u.nome if u else None
        if demanda.id_revisor:
            u = usuario_repo.buscar_por_id(demanda.id_revisor)
            revisor = u.nome if u else None

        rows.append(DemandaRow(
            demanda=demanda,
            data_limite=data_limite,
            dias_restantes=dias_restantes,
            relator=relator,
            revisor=revisor,
        ))

    rows.sort(key=lambda r: r.dias_restantes)

    finalizadas_hoje = len([
        d for d in demanda_repo.listar_por_status(StatusDemanda.CONCLUIDA)
        if hasattr(d, 'dat_cadastro') and d.dat_cadastro and d.dat_cadastro.date() == hoje
    ])

    kpis = KPIs(
        em_aberto=len(ativas),
        para_responder=sum(1 for r in rows if r.demanda.status == StatusDemanda.PENDENTE_RESPOSTA),
        para_revisar=sum(1 for r in rows if r.demanda.status == StatusDemanda.PENDENTE_REVISAO),
        atrasadas=sum(1 for r in rows if r.dias_restantes < 0),
        finalizadas_hoje=finalizadas_hoje,
    )

    aba = request.GET.get("aba", "recentes")
    if aba == "atrasadas":
        demandas_exibir = [r for r in rows if r.dias_restantes < 0]
    else:
        demandas_exibir = rows[:20]

    return render(request, "dashboard.html", {
        "kpis": kpis,
        "demandas": demandas_exibir,
        "aba": aba,
    })
