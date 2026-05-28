from datetime import date
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from src.adapters.django_orm.demanda_repo import DjangoDemandaRepository
from src.adapters.django_orm.origem_demanda_repo import DjangoOrigemDemandaRepository
from src.adapters.django_orm.resposta_repo import DjangoRespostaRepository
from src.adapters.django_orm.usuario_repo import DjangoUsuarioRepository
from src.application.use_cases.cadastrar_demanda import CadastrarDemandaInput
from src.domain.value_objects.status import StatusDemanda
from src.infrastructure.container import build_cadastrar_demanda

from .dashboard import DemandaRow


def _build_rows(demandas, usuario_repo, hoje):
    rows = []
    for demanda in demandas:
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
    return rows


STATUS_OPCOES = [
    {"value": "", "label": "Ativas"},
    {"value": "PR", "label": "Para Responder"},
    {"value": "PF", "label": "Para Revisar"},
    {"value": "PE", "label": "Pendente Externa"},
    {"value": "C", "label": "Concluídas"},
    {"value": "all", "label": "Todas"},
]


def lista(request: HttpRequest) -> HttpResponse:
    demanda_repo = DjangoDemandaRepository()
    usuario_repo = DjangoUsuarioRepository()
    hoje = date.today()
    status_filtro = request.GET.get("status", "")

    valores_validos = {s.value for s in StatusDemanda}
    if status_filtro in valores_validos:
        demandas = demanda_repo.listar_por_status(StatusDemanda(status_filtro))
    elif status_filtro == "all":
        demandas = list(demanda_repo.listar_ativas()) + list(
            demanda_repo.listar_por_status(StatusDemanda.CONCLUIDA)
        )
    else:
        demandas = demanda_repo.listar_ativas()

    rows = _build_rows(demandas, usuario_repo, hoje)

    return render(request, "demandas/lista.html", {
        "rows": rows,
        "status_filtro": status_filtro,
        "status_opcoes": STATUS_OPCOES,
    })


def detalhe(request: HttpRequest, demanda_id: int) -> HttpResponse:
    demanda_repo = DjangoDemandaRepository()
    usuario_repo = DjangoUsuarioRepository()
    resposta_repo = DjangoRespostaRepository()
    hoje = date.today()

    demanda = demanda_repo.buscar_por_id(demanda_id)
    if demanda is None:
        raise Http404

    data_limite = demanda.prazo.data_limite(demanda.dat_chegada)
    dias_restantes = (data_limite - hoje).days

    relator = usuario_repo.buscar_por_id(demanda.id_relator) if demanda.id_relator else None
    revisor = usuario_repo.buscar_por_id(demanda.id_revisor) if demanda.id_revisor else None
    resposta = resposta_repo.buscar_por_demanda(demanda_id)

    return render(request, "demandas/detalhe.html", {
        "demanda": demanda,
        "data_limite": data_limite,
        "dias_restantes": dias_restantes,
        "relator": relator,
        "revisor": revisor,
        "resposta": resposta,
    })


def nova(request: HttpRequest) -> HttpResponse:
    origem_repo = DjangoOrigemDemandaRepository()
    origens = origem_repo.listar()

    if request.method == "POST":
        usuario_repo = DjangoUsuarioRepository()
        usuarios = usuario_repo.listar_ativos_visiveis()
        criador_id = usuarios[0].id if usuarios else 1

        try:
            num_origem_raw = request.POST.get("num_origem", "").strip()
            dto = CadastrarDemandaInput(
                origem=request.POST["origem"],
                texto=request.POST["texto"].strip(),
                dat_chegada=date.fromisoformat(request.POST["dat_chegada"]),
                dias_prazo=int(request.POST["dias_prazo"]),
                id_usuario_criacao=criador_id,
                num_origem=int(num_origem_raw) if num_origem_raw else None,
            )
            demanda = build_cadastrar_demanda().executar(dto)
            return redirect("callista:demanda_detalhe", demanda_id=demanda.id)
        except (KeyError, ValueError) as e:
            return render(request, "demandas/nova.html", {
                "origens": origens,
                "erro": str(e),
                "post": request.POST,
                "hoje": date.today().isoformat(),
            })

    return render(request, "demandas/nova.html", {
        "origens": origens,
        "hoje": date.today().isoformat(),
    })
