# ADR-004 — Django Admin como painel de gestão SEPEL

| Campo | Valor |
|-------|-------|
| **Status** | Aceito |
| **Data** | 2026-06-01 |
| **Decisores** | Equipe CALLISTA |

## Contexto

Com a Fase 5 concluída, a interface do sistema atendia bem os pesquisadores. Faltava, porém,
uma forma de o **gestor da equipe SEPEL** administrar o sistema: cadastrar novos membros,
ajustar prazos de origens de demanda, registrar feriados e monitorar o histórico de atribuições.

Duas abordagens foram consideradas (ver Alternativas).

A decisão precisava levar em conta o princípio já estabelecido em [ADR-001](ADR-001-clean-architecture.md):
o sistema deve evitar reescrever infraestrutura que já existe quando ela resolve o problema.

## Decisão

Usar o **Django Admin** (`/admin/`) como interface de gestão, configurado com `ModelAdmin`
customizados para cada entidade relevante.

O Admin foi registrado em `src/adapters/django_orm/admin.py` — camada de adapters, o lugar
correto segundo a Regra de Dependência. Ele acessa diretamente os models ORM sem passar
pelos casos de uso, o que é aceitável para operações administrativas fora do fluxo normal
do sistema.

## Consequências

**Positivas:**

- Zero código de view, template ou URL para a interface de gestão
- Filtros, busca, paginação e edição inline disponíveis imediatamente
- Controle de acesso via `is_staff` do Django Auth — sem implementação extra
- Auditabilidade: o Admin registra quem alterou o quê via `LogEntry`

**Negativas:**

- UX diferente da interface principal do CALLISTA (sem Tailwind, sem dark mode)
- Gestores precisam de `is_staff=True` no Django Auth — acoplamento ao modelo de
  autenticação do Django
- Não é adequado para fluxos complexos de negócio (ex: atribuição automática de relator)
  — esses continuam como use cases com suas próprias views

## O que foi configurado

| Model | Ações disponíveis no Admin |
|-------|---------------------------|
| `OrigemDemandaModel` | CRUD completo; edição inline de prazo e ativo na listagem |
| `UsuarioModel` | Ativar/desativar, ocultar do sorteio, editar cargo |
| `AfastamentoModel` | CRUD com autocomplete de usuário |
| `FeriadoModel` | CRUD com hierarquia de datas |
| `DemandaModel` | Visualização e reatribuição; `dat_cadastro` somente leitura |
| `RespostaModel` / `RevisaoModel` | Consulta e auditoria |
| `HistoricoAtribuicaoModel` | Consulta do histórico de atribuições |
| `ProjetoLeiModel` | Visualização de PLs rastreados |

A origem de demanda, que era hardcoded em `origem_demanda_repo.py`, foi migrada para
`OrigemDemandaModel` — um model de BD com migration de dados inicial (ver
[Depuração e Migração](../desenvolvimento/admin-e-depuracao.md)).

## Alternativas Consideradas

| Alternativa | Por que rejeitada |
|-------------|------------------|
| Painel de gestão nativo com views Tailwind | Semanas de desenvolvimento para replicar o que o Admin oferece gratuitamente; escopo fora da Fase 5 |
| Manter origens hardcoded | O gestor não teria como adicionar uma nova origem sem mexer no código e fazer deploy |
| Usar ferramenta externa (ex: Retool, Metabase) | Dependência externa desnecessária para um conjunto simples de operações CRUD |

## Referências

- [ADR-001 — Clean Architecture](ADR-001-clean-architecture.md): o Admin fica na camada de adapters
- [ADR-002 — Django 6](ADR-002-django6-python314.md): versão do Django usada
- [Django Admin documentation](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/)
- [Depuração: erros de import e migrations](../desenvolvimento/admin-e-depuracao.md)
