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

## Navegação

| Seção | Descrição |
|-------|-----------|
| [Arquitetura](architecture/overview.md) | Visão geral das camadas e responsabilidades |
| [Fluxo de Dados](architecture/data-flow.md) | Como uma demanda percorre o sistema |
| [ADR-001](adr/ADR-001-clean-architecture.md) | Decisão arquitetural: Clean Architecture |
| [API](api/endpoints.md) | Referência dos endpoints REST |
