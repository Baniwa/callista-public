"""
Management command para popular o banco com dados fictícios de demonstração.
Todos os dados são inventados — nenhuma relação com dados reais do Senado Federal.

Uso:
    python manage.py seed_data
    python manage.py seed_data --limpar   # apaga tudo antes de inserir
"""
from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from src.adapters.django_orm.models import (
    AfastamentoModel,
    DemandaModel,
    FeriadoModel,
    RespostaModel,
    UsuarioModel,
)


USUARIOS = [
    {"nome": "Ana Luísa Figueiredo", "email": "ana.figueiredo@callista.demo", "matricula": "100001", "cargo": "Analista Legislativa Sênior"},
    {"nome": "Bruno Carvalho Matos", "email": "bruno.matos@callista.demo", "matricula": "100002", "cargo": "Analista Legislativo"},
    {"nome": "Carla Drummond Silva", "email": "carla.silva@callista.demo", "matricula": "100003", "cargo": "Analista Legislativa"},
    {"nome": "Diego Santana Reis", "email": "diego.reis@callista.demo", "matricula": "100004", "cargo": "Analista Legislativo Júnior"},
    {"nome": "Erica Tavares Nunes", "email": "erica.nunes@callista.demo", "matricula": "100005", "cargo": "Coordenadora de Pesquisa", "is_oculto": False},
    {"nome": "Admin Sistema", "email": "admin@callista.demo", "matricula": "999999", "cargo": "Administrador", "is_oculto": True},
]

FERIADOS_2026 = [
    (date(2026, 1, 1),  "Confraternização Universal"),
    (date(2026, 2, 16), "Carnaval (segunda-feira)"),
    (date(2026, 2, 17), "Carnaval (terça-feira)"),
    (date(2026, 4, 3),  "Sexta-Feira Santa"),
    (date(2026, 4, 21), "Tiradentes"),
    (date(2026, 5, 1),  "Dia do Trabalho"),
    (date(2026, 6, 4),  "Corpus Christi"),
    (date(2026, 9, 7),  "Independência do Brasil"),
    (date(2026, 10, 12),"Nossa Senhora Aparecida"),
    (date(2026, 11, 2), "Finados"),
    (date(2026, 11, 15),"Proclamação da República"),
    (date(2026, 12, 25),"Natal"),
]

DEMANDAS_FICTICIAS = [
    {"origem": "SGM",  "num_origem": 202601, "dias_prazo": 3,  "texto": "Qual o histórico de votações nominais em matérias de reforma tributária na última legislatura?"},
    {"origem": "SGM",  "num_origem": 202602, "dias_prazo": 5,  "texto": "Há precedente regimental para votação de MPV em sessão conjunta do Congresso Nacional?"},
    {"origem": "LAI",  "num_origem": None,   "dias_prazo": 20, "texto": "Solicitação de informação sobre o número de PLs apresentados por senadores do estado do Pará entre 2019 e 2022."},
    {"origem": "LAI",  "num_origem": None,   "dias_prazo": 20, "texto": "Quais foram os gastos com passagens aéreas da assessoria no primeiro semestre de 2025?"},
    {"origem": "IMP",  "num_origem": None,   "dias_prazo": 2,  "texto": "Pedido de nota técnica sobre o PL 1234/2025 — reforma do Código Eleitoral."},
    {"origem": "SGM",  "num_origem": 202603, "dias_prazo": 3,  "texto": "Levantamento dos PLs que tratam de regulamentação de criptoativos apresentados desde 2020."},
    {"origem": "IMP",  "num_origem": None,   "dias_prazo": 2,  "texto": "Quais senadores integram a Comissão de Ciência e Tecnologia na atual legislatura?"},
    {"origem": "SGM",  "num_origem": 202604, "dias_prazo": 5,  "texto": "Há jurisprudência do STF sobre a constitucionalidade de MPs que versam sobre matéria tributária estadual?"},
    {"origem": "INT",  "num_origem": None,   "dias_prazo": 10, "texto": "Consolidação das normas sobre afastamento de senadores para missões oficiais no exterior."},
    {"origem": "LAI",  "num_origem": None,   "dias_prazo": 20, "texto": "Solicito cópia das atas das reuniões da Mesa Diretora do Senado no exercício de 2024."},
    {"origem": "SGM",  "num_origem": 202605, "dias_prazo": 3,  "texto": "Quorum necessário para aprovação de emenda constitucional em sessão extraordinária?"},
    {"origem": "IMP",  "num_origem": None,   "dias_prazo": 2,  "texto": "Nota sobre tramitação do PEC 45/2024 e posição atual na Comissão de Constituição e Justiça."},
]

TEXTOS_RESPOSTA = [
    "Após análise da legislação vigente e do Regimento Interno do Senado Federal, verificou-se que...",
    "Com base no levantamento realizado nas bases de dados legislativos, identificaram-se os seguintes precedentes...",
    "A pesquisa realizada no sistema de tramitação do Senado Federal indica que...",
    "Consultando os Diários do Senado Federal e as atas disponíveis, constatou-se que...",
]


class Command(BaseCommand):
    help = "Popula o banco de dados com dados fictícios para demonstração"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga todos os dados antes de inserir",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["limpar"]:
            self._limpar()

        usuarios = self._criar_usuarios()
        self._criar_feriados()
        demandas = self._criar_demandas(usuarios)
        self._criar_respostas(demandas, usuarios)
        self._criar_afastamentos(usuarios)

        self.stdout.write(self.style.SUCCESS(
            f"\nSeed concluido: {len(usuarios)} usuarios, "
            f"{len(FERIADOS_2026)} feriados, "
            f"{len(demandas)} demandas"
        ))

    def _limpar(self):
        RespostaModel.objects.all().delete()
        DemandaModel.objects.all().delete()
        AfastamentoModel.objects.all().delete()
        FeriadoModel.objects.all().delete()
        UsuarioModel.objects.all().delete()
        self.stdout.write("  -> Dados anteriores removidos")

    def _criar_usuarios(self):
        criados = []
        for dados in USUARIOS:
            obj, novo = UsuarioModel.objects.get_or_create(
                matricula=dados["matricula"],
                defaults=dados,
            )
            criados.append(obj)
            status = "criado" if novo else "já existe"
            self.stdout.write(f"  -> Usuário {obj.nome} ({status})")
        return criados

    def _criar_feriados(self):
        for data, nome in FERIADOS_2026:
            FeriadoModel.objects.get_or_create(data=data, defaults={"nome": nome})
        self.stdout.write(f"  -> {len(FERIADOS_2026)} feriados de 2026 inseridos")

    def _criar_demandas(self, usuarios):
        visiveis = [u for u in usuarios if not u.is_oculto]
        demandas = []
        base = date(2026, 3, 1)

        for i, dados in enumerate(DEMANDAS_FICTICIAS):
            dat_chegada = base + timedelta(days=i * 4)
            relator = random.choice(visiveis)
            revisor = random.choice([u for u in visiveis if u != relator])

            # Últimas 3 demandas ficam pendentes (sem relator/revisor atribuído)
            if i >= len(DEMANDAS_FICTICIAS) - 3:
                status, relator_id, revisor_id = "PR", None, None
            elif i >= len(DEMANDAS_FICTICIAS) - 6:
                status, relator_id, revisor_id = "PF", relator.id, revisor.id
            else:
                status, relator_id, revisor_id = "C", relator.id, revisor.id

            obj = DemandaModel.objects.create(
                origem=dados["origem"],
                num_origem=dados.get("num_origem"),
                texto=dados["texto"],
                dat_chegada=dat_chegada,
                dias_prazo=dados["dias_prazo"],
                status=status,
                relator_id=relator_id,
                revisor_id=revisor_id,
            )
            demandas.append(obj)

        self.stdout.write(f"  -> {len(demandas)} demandas criadas")
        return demandas

    def _criar_respostas(self, demandas, usuarios):
        concluidas = [d for d in demandas if d.status in ("PF", "C")]
        for demanda in concluidas:
            if not RespostaModel.objects.filter(demanda=demanda).exists():
                RespostaModel.objects.create(
                    demanda=demanda,
                    usuario_id=demanda.relator_id,
                    texto=random.choice(TEXTOS_RESPOSTA),
                )
        self.stdout.write(f"  -> {len(concluidas)} respostas criadas")

    def _criar_afastamentos(self, usuarios):
        visiveis = [u for u in usuarios if not u.is_oculto]
        if len(visiveis) >= 2:
            AfastamentoModel.objects.get_or_create(
                usuario=visiveis[1],
                dat_inicial=date(2026, 7, 1),
                dat_final=date(2026, 7, 15),
                defaults={"motivo": "Férias"},
            )
            self.stdout.write(f"  -> 1 afastamento criado para {visiveis[1].nome}")
