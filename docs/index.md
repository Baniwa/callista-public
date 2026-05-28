# CALLISTA

Sistema de gestão de demandas para assessorias de pesquisa legislativa, com assistente de IA integrado.

## Início Rápido

```bash
pip install -r requirements/development.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## Início Rápido (com Frontend)

```bash
pip install -r requirements/development.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data

# Compilar o CSS (necessário desde a Fase 5)
python manage.py tailwind install  # apenas na primeira vez
python manage.py tailwind build

python manage.py runserver
```

## Fases Implementadas

| Fase | Descrição | Status |
|------|-----------|--------|
| 0 | Design e planejamento | ✅ Concluída |
| 1 | Domínio + Testes (42 testes unitários) | ✅ Concluída |
| 2 | Django + Adapters ORM | ✅ Concluída |
| 3 | Assistente de IA — Gemini (53 testes) | ✅ Concluída |
| 4 | Rastreador de PLs — API do Senado | ⏳ Pendente |
| 5 | Frontend — Tailwind v4 + dark mode + login | ✅ Concluída |
| 6 | Documentação completa + Docker + Deploy | ⏳ Pendente |

## Navegação

| Seção | Descrição |
|-------|-----------|
| [Arquitetura](architecture/overview.md) | Visão geral das camadas e responsabilidades |
| [Fluxo de Dados](architecture/data-flow.md) | Como uma demanda percorre o sistema |
| [Frontend — Fase 5](fase5/frontend.md) | Tailwind v4, dark mode, login, paginação |
| [ADR-001](adr/ADR-001-clean-architecture.md) | Decisão: Clean Architecture |
| [ADR-002](adr/ADR-002-django6-python314.md) | Decisão: Django 6.x por incompatibilidade com Python 3.14 |
| [ADR-003](adr/ADR-003-tailwind-v4-google-fonts.md) | Decisão: Google Fonts via `<link>`, não `@import` |
| [API](api/endpoints.md) | Referência dos endpoints REST |
