# Adapters Django ORM

Esta seção documenta a Fase 2 do CALLISTA: a implementação dos **adapters de persistência** que conectam as interfaces de repositório do domínio ao banco de dados via Django ORM.

---

## 1. O Papel dos Adapters

Na Clean Architecture, os adapters são a camada que "traduz" entre o mundo externo (banco de dados, APIs, HTTP) e a linguagem do domínio. O adapter não contém lógica de negócio — ele apenas converte dados.

```
DemandaRepository (Protocol)    ←  interface que o domínio define
        ↑ implementa
DjangoDemandaRepository         ←  adapter que conhece Django ORM
        ↑ usa
DemandaModel (Django Model)     ←  representação no banco de dados
```

O domínio nunca importa nada de `src/adapters/`. Os adapters importam do domínio — a dependência só flui para dentro.

---

## 2. Modelos Django ORM

**Localização:** `src/adapters/django_orm/models.py`

Os modelos Django são um detalhe de infraestrutura. Eles existem apenas para persistência e não carregam lógica de negócio.

| Model Django | Entidade de Domínio | Tabela no BD |
|---|---|---|
| `UsuarioModel` | `Usuario` | `callista_usuario` |
| `FeriadoModel` | `Feriado` | `callista_feriado` |
| `AfastamentoModel` | `Afastamento` | `callista_afastamento` |
| `DemandaModel` | `Demanda` | `callista_demanda` |
| `RespostaModel` | `Resposta` | `callista_resposta` |

### Diferenças entre Model e Entidade

A entidade `Demanda` carrega um `Prazo` (value object). O `DemandaModel` armazena apenas `dias_prazo: int`. O adapter faz a conversão:

```python
# Model -> Entidade
prazo=Prazo(dias_uteis=obj.dias_prazo)

# Entidade -> Model
dias_prazo=demanda.prazo.dias_uteis
```

O `StatusDemanda` é armazenado como string de 2 caracteres (`"PR"`, `"PF"`, `"PE"`, `"C"`), compatível com o schema do sistema legado.

---

## 3. Adapters de Repositório

### DjangoDemandaRepository

**Localização:** `src/adapters/django_orm/demanda_repo.py`

Implementa todos os métodos de `DemandaRepository`, incluindo os de contagem para o sorteio:

```python
def contar_respostas_no_mes(self, usuario_id: int, mes: int, ano: int) -> int:
    return DemandaModel.objects.filter(
        relator_id=usuario_id,
        dat_chegada__month=mes,
        dat_chegada__year=ano,
        status__in=["PF", "C"],
    ).count()
```

A query conta apenas demandas em que o relator já entregou a resposta (status `PF` ou `C`).

### DjangoAfastamentoRepository

**Localização:** `src/adapters/django_orm/afastamento_repo.py`

A query filtra por `dat_final >= data` para capturar afastamentos que **possam** cobrir a data. A lógica de antecipação de 2 dias úteis fica na entidade `Afastamento.cobre_data()` — não no adapter:

```python
def listar_ativos_na_data(self, data: date) -> Sequence[Afastamento]:
    return [
        self._to_entity(obj)
        for obj in AfastamentoModel.objects.filter(dat_final__gte=data)
    ]
```

O use case `AtribuirRelatorUseCase` chama `cobre_data()` em cada afastamento retornado.

---

## 4. Container de Injeção de Dependências

**Localização:** `src/infrastructure/container/__init__.py`

O container monta os use cases com suas dependências concretas. Cada função retorna um use case completamente wired:

```python
def build_atribuir_relator() -> AtribuirRelatorUseCase:
    return AtribuirRelatorUseCase(
        demanda_repo=DjangoDemandaRepository(),
        usuario_repo=DjangoUsuarioRepository(),
        afastamento_repo=DjangoAfastamentoRepository(),
        feriado_repo=DjangoFeriadoRepository(),
        sorteio=SorteioJustoService(),
    )
```

As views Django chamam `build_atribuir_relator().executar(dto)` — sem saber que existem repositórios ou banco de dados por baixo.

!!! note "Sem dependency-injector"
    O pacote `dependency-injector` não compilou no Python 3.14. A injeção manual via funções factory é suficiente para este estágio e mais fácil de depurar.

---

## 5. Settings por Ambiente

**Localização:** `src/infrastructure/settings/`

| Arquivo | Ambiente | Banco | DEBUG |
|---|---|---|---|
| `base.py` | — | — (sem DB) | — |
| `development.py` | Local | SQLite | `True` |
| `production.py` | Produção | PostgreSQL | `False` |

O arquivo `development.py` é o default do `manage.py`. Para produção, defina `DJANGO_SETTINGS_MODULE=src.infrastructure.settings.production`.

Variáveis sensíveis são lidas via `python-decouple` do arquivo `.env`:

```python
SECRET_KEY = config("SECRET_KEY")
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
```

---

## 6. Seed de Dados

**Uso:**

```bash
# Inserir dados fictícios
python manage.py seed_data

# Limpar tudo e reinserir
python manage.py seed_data --limpar
```

**O que é inserido:**

| Tipo | Quantidade | Detalhes |
|---|---|---|
| Usuários | 6 | 5 pesquisadores + 1 admin oculto |
| Feriados | 12 | Feriados nacionais de 2026 |
| Demandas | 12 | Mix de SGM, LAI, IMP, INT — em vários status |
| Respostas | 9 | Para demandas com status `PF` ou `C` |
| Afastamentos | 1 | Bruno Carvalho: julho/2026 |

**Status das demandas geradas:**
- 3 demandas `C` (concluídas, com relator e revisor)
- 6 demandas `PF` (respondidas, aguardando revisão)
- 3 demandas `PR` (novas, sem atribuição)

---

## 7. Rodando Localmente

```bash
# 1. Migrations
python manage.py migrate

# 2. Seed
python manage.py seed_data

# 3. Criar superusuário para o admin
python manage.py createsuperuser

# 4. Subir o servidor
python manage.py runserver

# Admin disponível em: http://127.0.0.1:8000/admin/
```
