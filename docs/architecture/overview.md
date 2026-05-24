# Visão Geral da Arquitetura

O CALLISTA adota **Clean Architecture** (Robert C. Martin, 2017) com táticas de **Domain-Driven Design** (Eric Evans, 2003).

## Princípio Central

> A regra de negócio não conhece o banco de dados, o framework web, nem o provedor de IA.  
> Esses são detalhes de infraestrutura — substituíveis sem reescrever o domínio.

## Camadas

```
┌─────────────────────────────────────────┐
│           INFRASTRUCTURE                │  Django config, wiring, migrations
├─────────────────────────────────────────┤
│             ADAPTERS                    │  Django ORM, Claude API, Senado API
├─────────────────────────────────────────┤
│            APPLICATION                  │  Casos de uso, orquestração
├─────────────────────────────────────────┤
│              DOMAIN                     │  Entidades, regras, serviços puros
└─────────────────────────────────────────┘
        ↑ dependências apontam para dentro
```

### Domain (`src/domain/`)

Núcleo do sistema. **Zero dependências externas** — nem Django, nem banco de dados.

- `entities/` — `Demanda`, `Usuario`, `PL`
- `value_objects/` — `Prazo`, `StatusDemanda`, `OrigemDemanda`
- `services/` — `SorteioJustoService`, `CalculoPrazoService`
- `repositories/` — interfaces (`Protocol`) que os adapters implementam

### Application (`src/application/`)

Casos de uso que orquestram o domínio. Não conhecem Django.

- `CadastrarDemandaUseCase`
- `AtribuirRelatorUseCase`
- `BuscarFontesOficiaisUseCase`
- `GerarResumoIAUseCase`
- `RastrearPLUseCase`

### Adapters (`src/adapters/`)

Traduzem o mundo externo para a linguagem do domínio.

- `django_orm/` — implementações dos repositórios usando ORM
- `ai/` — adapter para a Claude API (Anthropic)
- `senado_api/` — adapter para `legis.senado.leg.br/dadosabertos`
- `views/` — Django Views finas (só HTTP, delegam ao use case)

### Infrastructure (`src/infrastructure/`)

Configuração, injeção de dependência e wiring geral.

## Referências

- Martin, R.C. *Clean Architecture* (2017) — caps. 17–22
- Evans, E. *Domain-Driven Design* (2003)
- Vernon, V. *Implementing Domain-Driven Design* (2013)
