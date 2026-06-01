# Django Admin e Depuração de Imports/Migrations

Esta página documenta dois processos relacionados que surgiram juntos durante o
desenvolvimento: a construção do painel Admin e a resolução dos erros de import e
migration que o antecederam.

---

## 1. Erros de Import: repositórios faltando

Ao subir o servidor pela primeira vez após o rebase da Fase 5, o Django falhou
imediatamente com:

```
ModuleNotFoundError: No module named 'src.adapters.django_orm.origem_demanda_repo'
```

A causa: durante o rebase que integrou as branches de Fase 3, 4 e 5, alguns arquivos
de repositório foram referenciados em `views/urls.py` e `container/__init__.py` mas
**nunca chegaram a existir no repositório** — eram imports que ficaram como dívida
técnica do histórico de desenvolvimento.

### Como localizar todos os imports quebrados

Antes de criar qualquer arquivo, o diagnóstico correto é mapear **todos** os imports
ausentes de uma vez:

```bash
# Importar as URLs valida a cadeia de imports inteira
python -c "
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'src.infrastructure.settings.development'
django.setup()
from src.adapters.views.urls import urlpatterns
print('OK —', len(urlpatterns), 'urls')
"
```

Se esse comando passa sem erro, o servidor vai subir. Se quebra, o traceback aponta
exatamente qual módulo está faltando.

### O que foi criado

Dois repositórios estavam ausentes:

**`src/adapters/django_orm/origem_demanda_repo.py`**

Usado pelas views `nova` e `pesquisa` para popular o `<select>` de origens.
Inicialmente implementado com dados hardcoded; depois migrado para consultar
`OrigemDemandaModel` no banco (ver [Seção 3](#3-migrando-origens-para-o-banco)).

```python
from src.adapters.django_orm.models import OrigemDemandaModel

class DjangoOrigemDemandaRepository:
    def listar(self):
        return list(OrigemDemandaModel.objects.filter(ativo=True))

    def buscar_por_sigla(self, sigla):
        return OrigemDemandaModel.objects.filter(sigla=sigla, ativo=True).first()
```

**`src/adapters/django_orm/historico_atribuicao_repo.py`**

Referenciado em `container/__init__.py` para `build_historico_atribuicao_repo()`.
O model `HistoricoAtribuicaoModel` já existia; só faltava o repositório:

```python
from src.adapters.django_orm.models import HistoricoAtribuicaoModel

class DjangoHistoricoAtribuicaoRepository:
    def registrar(self, demanda_id, usuario_id, tipo):
        HistoricoAtribuicaoModel.objects.create(
            demanda_id=demanda_id,
            usuario_id=usuario_id,
            tipo=tipo,
        )

    def listar_por_demanda(self, demanda_id):
        return list(
            HistoricoAtribuicaoModel.objects.filter(demanda_id=demanda_id)
            .select_related("usuario")
        )
```

---

## 2. Erros de Migration: dependências quebradas e tabelas já existentes

Após resolver os imports, o servidor falhou no `check_migrations`:

```
NodeNotFoundError: Migration django_orm.0003_adiciona_projeto_lei
dependencies reference nonexistent parent node ('django_orm', '0002_schema_migracao_v2')
```

A migration `0003` dependia de `0002_schema_migracao_v2` — uma migration que existia
em outra branch mas nunca foi incluída neste repositório. O rebase preservou a
dependência sem preservar o arquivo.

### Corrigir uma dependência quebrada

A solução é ajustar o `dependencies` da migration para apontar para a última que
realmente existe:

```python
# src/adapters/django_orm/migrations/0003_adiciona_projeto_lei.py
class Migration(migrations.Migration):
    dependencies = [
        # era: ('django_orm', '0002_schema_migracao_v2')  ← não existe
        ('django_orm', '0001_initial'),                   # ← corrigido
    ]
```

### Como identificar qual migration existe

```bash
python manage.py showmigrations django_orm
```

Isso lista todas as migrations e seu estado (aplicada ✓ ou pendente). Use essa saída
para confirmar a migration pai correta antes de editar.

### Tabelas já existentes: usar `--fake`

Após corrigir a dependência, o `migrate` gerou novas migrations para models que já
existiam no banco (criados por uma versão anterior do `0001_initial`):

```
django.db.utils.OperationalError: table "callista_historico_atrib" already exists
```

Quando o banco está à frente das migrations (as tabelas existem mas a migration
não foi registrada), use `--fake`:

```bash
# Marca a migration como aplicada sem executar o SQL
python manage.py migrate django_orm 0004 --fake
python manage.py migrate django_orm 0005 --fake
```

!!! warning "Quando usar --fake"
    `--fake` só é seguro quando você tem **certeza** que o schema do banco já corresponde
    ao que a migration criaria. Se houver divergência (ex: uma coluna nova que o banco
    não tem), o fake vai esconder o problema e causar erros em runtime.

### Coluna faltando após fake

No caso da coluna `ativo` de `OrigemDemandaModel`: a tabela existia sem essa coluna
(criada por uma versão mais antiga do model), mas a migration 0005 foi marcada como fake.
O banco ficou com schema desatualizado.

**Diagnóstico:**

```bash
python manage.py shell -c "
from django.db import connection
cols = connection.introspection.get_table_description(
    connection.cursor(), 'callista_origem_demanda'
)
for c in cols: print(c.name)
"
```

**Solução:** como o sistema de migrations já considerava 0005 aplicado, a coluna foi
adicionada diretamente via ORM — mais seguro do que SQL raw nesse contexto:

```python
# Executado uma única vez via python manage.py shell
from src.adapters.django_orm.models import OrigemDemandaModel
# O ORM passa a usar o model atualizado; o ALTER TABLE real foi feito
# por makemigrations + migrate após detectar a divergência
```

Na prática, o campo `ativo` foi adicionado com `DEFAULT 1` via SQL direto no SQLite,
e os dados foram inseridos via `update_or_create` do ORM.

---

## 3. Migrando Origens para o Banco

As origens de demanda (SGM, LAI, IMP, INT) eram hardcoded. Para que o gestor possa
gerenciá-las pelo Admin, elas foram movidas para `OrigemDemandaModel`.

### O novo model

```python
class OrigemDemandaModel(models.Model):
    sigla            = models.CharField(max_length=10, unique=True)
    nome             = models.CharField(max_length=100)
    prazo_padrao_dias = models.PositiveSmallIntegerField()
    tem_numero       = models.BooleanField(default=False)
    ativo            = models.BooleanField(default=True)

    class Meta:
        db_table = "callista_origem_demanda"
        verbose_name = "Origem de Demanda"
        verbose_name_plural = "Origens de Demanda"
```

### Migration de dados (data migration)

Os valores iniciais foram inseridos com uma `RunPython` migration — não no seed de
desenvolvimento, para que qualquer deploy novo receba as origens automaticamente:

```python
# migrations/0006_seed_origens_iniciais.py
ORIGENS = [
    {"sigla": "SGM", "nome": "Secretaria-Geral da Mesa",   "prazo_padrao_dias": 5,  ...},
    {"sigla": "LAI", "nome": "Lei de Acesso à Informação", "prazo_padrao_dias": 20, ...},
    ...
]

def seed_origens(apps, schema_editor):
    OrigemDemandaModel = apps.get_model("django_orm", "OrigemDemandaModel")
    for dados in ORIGENS:
        OrigemDemandaModel.objects.get_or_create(sigla=dados["sigla"], defaults=dados)
```

!!! note "Por que `get_or_create` e não `bulk_create`?"
    `get_or_create` é idempotente — pode ser executado múltiplas vezes sem duplicar
    dados. Se o ambiente já tiver origens (ex: banco de produção com dados reais),
    a migration não sobrescreve.

---

## 4. Construção do Django Admin

Com models e repositórios estabilizados, o Admin foi configurado em
`src/adapters/django_orm/admin.py`. A decisão de usar o Admin em vez de views
customizadas está documentada em [ADR-004](../adr/ADR-004-django-admin-gestao.md).

### Padrão de configuração

Cada model recebe uma classe `ModelAdmin` com:

- **`list_display`** — colunas visíveis na listagem
- **`list_editable`** — campos editáveis diretamente na listagem (sem abrir o formulário)
- **`search_fields`** — habilita a barra de busca; use `__` para seguir relações
- **`list_filter`** — painel de filtros lateral
- **`autocomplete_fields`** — substitui o `<select>` por campo de busca em FKs com muitos registros
- **`readonly_fields`** — campos gerados automaticamente (timestamps) que não devem ser editados
- **`fieldsets`** — agrupa campos no formulário de edição por contexto

### Exemplo: OrigemDemandaAdmin

```python
@admin.register(OrigemDemandaModel)
class OrigemDemandaAdmin(admin.ModelAdmin):
    list_display   = ("sigla", "nome", "prazo_padrao_dias", "tem_numero", "ativo")
    list_editable  = ("prazo_padrao_dias", "tem_numero", "ativo")
    search_fields  = ("sigla", "nome")
    list_filter    = ("ativo", "tem_numero")
```

O `list_editable` permite que o gestor ajuste o prazo padrão de uma origem diretamente
na tabela de listagem — sem precisar abrir cada registro individualmente.

### Personalizando o cabeçalho

```python
admin.site.site_header = "CALLISTA — Gestão SEPEL"
admin.site.site_title  = "CALLISTA Admin"
admin.site.index_title = "Painel de Administração"
```

Essas três linhas substituem o "Django administration" padrão pelo nome do sistema,
que aparece no `<title>` e no cabeçalho do Admin.

### Prerequisito: `is_staff = True`

Para acessar o Admin, o usuário Django Auth precisa de `is_staff=True`. Isso é
configurado no próprio Admin (seção **Autenticação e Autorização → Usuários**) ou via:

```bash
python manage.py shell -c "
from django.contrib.auth.models import User
u = User.objects.get(username='seu_usuario')
u.is_staff = True
u.save()
"
```

---

## Referências

- [ADR-001 — Clean Architecture](../adr/ADR-001-clean-architecture.md): por que o admin fica em `adapters/`
- [ADR-004 — Django Admin como painel de gestão](../adr/ADR-004-django-admin-gestao.md): a decisão
- [Configuração do Ambiente](ambiente.md): como subir o servidor em desenvolvimento
- [Django Admin — documentação oficial](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/)
- [Django Migrations — documentação oficial](https://docs.djangoproject.com/en/6.0/topics/migrations/)
