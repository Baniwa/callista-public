from dataclasses import dataclass
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from src.adapters.django_orm.afastamento_repo import DjangoAfastamentoRepository
from src.adapters.django_orm.usuario_repo import DjangoUsuarioRepository
from src.domain.entities.afastamento import Afastamento


MOTIVOS = [
    "Férias",
    "Licença médica",
    "Licença maternidade/paternidade",
    "Capacitação",
    "Missão oficial",
    "Outros",
]


@dataclass
class AfastamentoRow:
    afastamento: Afastamento
    usuario_nome: str
    estado: str


def _classificar(af: Afastamento, hoje: date) -> str:
    if af.dat_final < hoje:
        return "finalizado"
    if af.dat_inicial > hoje:
        return "futuro"
    return "ativo"


@login_required
def lista(request: HttpRequest) -> HttpResponse:
    repo = DjangoAfastamentoRepository()
    usuario_repo = DjangoUsuarioRepository()
    hoje = date.today()

    if request.method == "POST":
        acao = request.POST.get("acao")
        if acao == "excluir":
            af_id = int(request.POST.get("af_id", 0))
            if af_id:
                repo.excluir(af_id)
            return redirect("callista:afastamentos")

        try:
            usuario_id = int(request.POST["usuario_id"])
            af = Afastamento(
                id=None,
                usuario_id=usuario_id,
                dat_inicial=date.fromisoformat(request.POST["dat_inicial"]),
                dat_final=date.fromisoformat(request.POST["dat_final"]),
                motivo=request.POST["motivo"].strip(),
            )
            repo.salvar(af)
            return redirect("callista:afastamentos")
        except (KeyError, ValueError) as e:
            erro = str(e)
        usuarios = usuario_repo.listar_ativos_visiveis()
        return render(request, "afastamentos/lista.html", {
            "erro": erro,
            "usuarios": usuarios,
            "motivos": MOTIVOS,
            "hoje": hoje.isoformat(),
            "rows": _build_rows(repo.listar_todos(), usuario_repo, hoje),
            "tab": "ativo",
        })

    usuarios = usuario_repo.listar_ativos_visiveis()
    tab = request.GET.get("tab", "ativo")
    todos = repo.listar_todos()
    rows = _build_rows(todos, usuario_repo, hoje)

    return render(request, "afastamentos/lista.html", {
        "rows": rows,
        "tab": tab,
        "usuarios": usuarios,
        "motivos": MOTIVOS,
        "hoje": hoje.isoformat(),
    })


def _build_rows(afastamentos, usuario_repo, hoje):
    cache = {}
    rows = []
    for af in afastamentos:
        if af.usuario_id not in cache:
            u = usuario_repo.buscar_por_id(af.usuario_id)
            cache[af.usuario_id] = u.nome if u else "—"
        rows.append(AfastamentoRow(
            afastamento=af,
            usuario_nome=cache[af.usuario_id],
            estado=_classificar(af, hoje),
        ))
    return rows
