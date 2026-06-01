from django.db import migrations

ORIGENS = [
    {"sigla": "SGM", "nome": "Secretaria-Geral da Mesa",   "prazo_padrao_dias": 5,  "tem_numero": True,  "ativo": True},
    {"sigla": "LAI", "nome": "Lei de Acesso à Informação", "prazo_padrao_dias": 20, "tem_numero": False, "ativo": True},
    {"sigla": "IMP", "nome": "Imprensa",                   "prazo_padrao_dias": 2,  "tem_numero": False, "ativo": True},
    {"sigla": "INT", "nome": "Demanda Interna",            "prazo_padrao_dias": 10, "tem_numero": False, "ativo": True},
]


def seed_origens(apps, schema_editor):
    OrigemDemandaModel = apps.get_model("django_orm", "OrigemDemandaModel")
    for dados in ORIGENS:
        OrigemDemandaModel.objects.get_or_create(sigla=dados["sigla"], defaults=dados)


def desfazer_seed(apps, schema_editor):
    OrigemDemandaModel = apps.get_model("django_orm", "OrigemDemandaModel")
    OrigemDemandaModel.objects.filter(sigla__in=[o["sigla"] for o in ORIGENS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("django_orm", "0005_adiciona_origem_demanda_model"),
    ]

    operations = [
        migrations.RunPython(seed_origens, desfazer_seed),
    ]
