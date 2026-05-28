from decouple import config

from src.adapters.ai.gemini_adapter import GeminiAdapter
from src.adapters.django_orm.afastamento_repo import DjangoAfastamentoRepository
from src.adapters.django_orm.demanda_repo import DjangoDemandaRepository
from src.adapters.django_orm.feriado_repo import DjangoFeriadoRepository
from src.adapters.django_orm.historico_atribuicao_repo import DjangoHistoricoAtribuicaoRepository
from src.adapters.django_orm.origem_demanda_repo import DjangoOrigemDemandaRepository
from src.adapters.django_orm.projeto_lei_repo import DjangoProjetoLeiRepository
from src.adapters.django_orm.resposta_repo import DjangoRespostaRepository
from src.adapters.django_orm.revisao_repo import DjangoRevisaoRepository
from src.adapters.django_orm.usuario_repo import DjangoUsuarioRepository
from src.adapters.senado_api.senado_adapter import SenadoAdapter
from src.application.use_cases.atribuir_relator import AtribuirRelatorUseCase
from src.application.use_cases.buscar_fontes_oficiais import BuscarFontesOficiaisUseCase
from src.application.use_cases.cadastrar_demanda import CadastrarDemandaUseCase
from src.application.use_cases.gerar_resumo import GerarResumoUseCase
from src.application.use_cases.rastrear_pl import RastrearPLUseCase
from src.application.use_cases.responder_demanda import ResponderDemandaUseCase
from src.application.use_cases.revisar_demanda import RevisarDemandaUseCase
from src.application.use_cases.sugerir_rascunho import SugerirRascunhoUseCase
from src.domain.services.sorteio_justo import SorteioJustoService


def _gemini() -> GeminiAdapter:
    return GeminiAdapter(api_key=config("GEMINI_API_KEY"))


def build_cadastrar_demanda() -> CadastrarDemandaUseCase:
    return CadastrarDemandaUseCase(repository=DjangoDemandaRepository())


def build_atribuir_relator() -> AtribuirRelatorUseCase:
    return AtribuirRelatorUseCase(
        demanda_repo=DjangoDemandaRepository(),
        usuario_repo=DjangoUsuarioRepository(),
        afastamento_repo=DjangoAfastamentoRepository(),
        feriado_repo=DjangoFeriadoRepository(),
        sorteio=SorteioJustoService(),
    )


def build_responder_demanda() -> ResponderDemandaUseCase:
    return ResponderDemandaUseCase(
        demanda_repo=DjangoDemandaRepository(),
        resposta_repo=DjangoRespostaRepository(),
    )


def build_revisar_demanda() -> RevisarDemandaUseCase:
    return RevisarDemandaUseCase(
        demanda_repo=DjangoDemandaRepository(),
        revisao_repo=DjangoRevisaoRepository(),
    )


def build_buscar_fontes_oficiais() -> BuscarFontesOficiaisUseCase:
    return BuscarFontesOficiaisUseCase(
        repository=DjangoDemandaRepository(),
        ia=_gemini(),
    )


def build_gerar_resumo() -> GerarResumoUseCase:
    return GerarResumoUseCase(
        repository=DjangoDemandaRepository(),
        ia=_gemini(),
    )


def build_sugerir_rascunho() -> SugerirRascunhoUseCase:
    return SugerirRascunhoUseCase(
        demanda_repo=DjangoDemandaRepository(),
        resposta_repo=DjangoRespostaRepository(),
        ia=_gemini(),
    )


def build_origem_demanda_repo() -> DjangoOrigemDemandaRepository:
    return DjangoOrigemDemandaRepository()


def build_revisao_repo() -> DjangoRevisaoRepository:
    return DjangoRevisaoRepository()


def build_historico_atribuicao_repo() -> DjangoHistoricoAtribuicaoRepository:
    return DjangoHistoricoAtribuicaoRepository()


def build_rastrear_pl() -> RastrearPLUseCase:
    return RastrearPLUseCase(
        senado=SenadoAdapter(),
        pl_repo=DjangoProjetoLeiRepository(),
    )
