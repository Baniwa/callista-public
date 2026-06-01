"""
Limpa todos os dados de demonstração do banco, preservando:
- Feriados (dados reais, não fictícios)
- Origens de Demanda (configuração do sistema)
- Superusuários do Django Admin

Use para preparar o ambiente antes de cadastrar usuários reais.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from src.adapters.django_orm.models import (
    AfastamentoModel,
    DemandaModel,
    HistoricoAtribuicaoModel,
    PendenciaExternaModel,
    RespostaModel,
    RevisaoModel,
    UsuarioModel,
)


class Command(BaseCommand):
    help = "Remove todos os dados fictícios. Preserva feriados, origens e superusuários."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Necessário para executar. Sem esta flag, apenas mostra o que seria removido.",
        )

    def handle(self, *args, **options):
        confirmar = options["confirmar"]

        contagens = {
            "Demandas": DemandaModel.objects.count(),
            "Respostas": RespostaModel.objects.count(),
            "Revisões": RevisaoModel.objects.count(),
            "Histórico de atribuições": HistoricoAtribuicaoModel.objects.count(),
            "Pendências externas": PendenciaExternaModel.objects.count(),
            "Afastamentos": AfastamentoModel.objects.count(),
            "Usuários Callista": UsuarioModel.objects.count(),
            "Usuários Django (não superusuários)": User.objects.filter(is_superuser=False).count(),
        }

        self.stdout.write("\nDados que serão removidos:")
        for nome, qtd in contagens.items():
            self.stdout.write(f"  {nome}: {qtd}")

        preservados = {
            "Feriados": "preservados",
            "Origens de Demanda": "preservadas",
            "Superusuários Django": str(User.objects.filter(is_superuser=True).count()),
        }
        self.stdout.write("\nDados preservados:")
        for nome, info in preservados.items():
            self.stdout.write(f"  {nome}: {info}")

        if not confirmar:
            self.stdout.write(
                self.style.WARNING(
                    "\nExecute com --confirmar para apagar os dados acima."
                )
            )
            return

        # Apaga na ordem correta para respeitar FKs
        HistoricoAtribuicaoModel.objects.all().delete()
        PendenciaExternaModel.objects.all().delete()
        RevisaoModel.objects.all().delete()
        RespostaModel.objects.all().delete()
        DemandaModel.objects.all().delete()
        AfastamentoModel.objects.all().delete()
        UsuarioModel.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("\nDados fictícios removidos com sucesso."))
        self.stdout.write("Próximos passos:")
        self.stdout.write("  1. Acesse /cadastrar/ e crie sua conta com o código de setor.")
        self.stdout.write("  2. No Admin (/admin/), defina is_staff=True se precisar de acesso ao painel.")
