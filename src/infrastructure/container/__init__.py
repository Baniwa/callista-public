from src.adapters.django_orm.afastamento_repo import DjangoAfastamentoRepository
from src.adapters.django_orm.demanda_repo import DjangoDemandaRepository
from src.adapters.django_orm.feriado_repo import DjangoFeriadoRepository
from src.adapters.django_orm.resposta_repo import DjangoRespostaRepository
from src.adapters.django_orm.usuario_repo import DjangoUsuarioRepository
from src.domain.services.sorteio_justo import SorteioJustoService
from src.application.use_cases.atribuir_relator import AtribuirRelatorUseCase
from src.application.use_cases.cadastrar_demanda import CadastrarDemandaUseCase
from src.application.use_cases.responder_demanda import ResponderDemandaUseCase
from src.application.use_cases.revisar_demanda import RevisarDemandaUseCase


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
        revisao_repo=DjangoRespostaRepository(),
    )
