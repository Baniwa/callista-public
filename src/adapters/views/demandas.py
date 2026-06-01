from datetime import date
from src.adapters.views.mixins import usuario_ativo_required
from django.core.paginator import Paginator
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


def _paginar(lista, request, por_pagina=20):
    p = Paginator(lista, por_pagina)
    return p.get_page(request.GET.get("pagina", 1))


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


@usuario_ativo_required
def lista(request: HttpRequest) -> HttpResponse:
    demanda_repo = DjangoDemandaRepository()
    usuario_repo = DjangoUsuarioRepository()
    hoje = date.today()
    status_filtro = request.GET.get("status", "")

    q = request.GET.get("q", "").strip()
    valores_validos = {s.value for s in StatusDemanda}

    if q:
        demandas = demanda_repo.buscar_por_texto(q)
    elif status_filtro in valores_validos:
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
        "q": q,
    })


@usuario_ativo_required
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


@usuario_ativo_required
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


@usuario_ativo_required
def minhas_demandas(request: HttpRequest) -> HttpResponse:
    usuario_repo = DjangoUsuarioRepository()
    demanda_repo = DjangoDemandaRepository()
    hoje = date.today()

    meu_usuario = usuario_repo.buscar_por_email(request.user.email)
    tab = request.GET.get("tab", "todas")

    if meu_usuario:
        todas = demanda_repo.listar_por_usuario(meu_usuario.id)
        if tab == "responder":
            demandas = [d for d in todas if d.status == StatusDemanda.PENDENTE_RESPOSTA and d.id_relator == meu_usuario.id]
        elif tab == "revisar":
            demandas = [d for d in todas if d.status == StatusDemanda.PENDENTE_REVISAO and d.id_revisor == meu_usuario.id]
        else:
            demandas = list(todas)
        contagens = {
            "responder": sum(1 for d in todas if d.status == StatusDemanda.PENDENTE_RESPOSTA and d.id_relator == meu_usuario.id),
            "revisar": sum(1 for d in todas if d.status == StatusDemanda.PENDENTE_REVISAO and d.id_revisor == meu_usuario.id),
            "todas": len(list(todas)),
        }
    else:
        demandas = []
        contagens = {"responder": 0, "revisar": 0, "todas": 0}

    rows = _build_rows(demandas, usuario_repo, hoje)
    page_obj = _paginar(rows, request)

    return render(request, "demandas/minhas_demandas.html", {
        "page_obj": page_obj,
        "tab": tab,
        "contagens": contagens,
        "meu_usuario": meu_usuario,
    })


@usuario_ativo_required
def equipe(request: HttpRequest) -> HttpResponse:
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
    page_obj = _paginar(rows, request)

    return render(request, "demandas/equipe.html", {
        "page_obj": page_obj,
        "status_filtro": status_filtro,
        "status_opcoes": STATUS_OPCOES,
    })


@usuario_ativo_required
def pesquisa(request: HttpRequest) -> HttpResponse:
    demanda_repo = DjangoDemandaRepository()
    usuario_repo = DjangoUsuarioRepository()
    origem_repo = DjangoOrigemDemandaRepository()
    hoje = date.today()

    origens = origem_repo.listar()
    usuarios = usuario_repo.listar_ativos_visiveis()

    q = request.GET.get("q", "").strip()
    origem = request.GET.get("origem", "").strip()
    status_valor = request.GET.get("status", "")
    relator_id_raw = request.GET.get("relator", "")
    revisor_id_raw = request.GET.get("revisor", "")
    dat_ini_raw = request.GET.get("dat_ini", "")
    dat_fim_raw = request.GET.get("dat_fim", "")

    pesquisou = any([q, origem, status_valor, relator_id_raw, revisor_id_raw, dat_ini_raw, dat_fim_raw])
    rows = []
    page_obj = None

    if pesquisou:
        relator_id = int(relator_id_raw) if relator_id_raw.isdigit() else None
        revisor_id = int(revisor_id_raw) if revisor_id_raw.isdigit() else None
        try:
            dat_inicial = date.fromisoformat(dat_ini_raw) if dat_ini_raw else None
            dat_final = date.fromisoformat(dat_fim_raw) if dat_fim_raw else None
        except ValueError:
            dat_inicial = dat_final = None

        demandas = demanda_repo.listar_com_filtros(
            texto=q,
            origem=origem,
            status_valor=status_valor,
            relator_id=relator_id,
            revisor_id=revisor_id,
            dat_inicial=dat_inicial,
            dat_final=dat_final,
        )
        rows = _build_rows(demandas, usuario_repo, hoje)
        page_obj = _paginar(rows, request)

    return render(request, "demandas/pesquisa.html", {
        "page_obj": page_obj,
        "rows": rows,
        "origens": origens,
        "usuarios": usuarios,
        "status_opcoes": STATUS_OPCOES,
        "pesquisou": pesquisou,
        "q": q,
        "origem_sel": origem,
        "status_sel": status_valor,
        "relator_sel": relator_id_raw,
        "revisor_sel": revisor_id_raw,
        "dat_ini": dat_ini_raw,
        "dat_fim": dat_fim_raw,
    })
