# CALLISTA — Sistema de Gestão de Pesquisa Legislativa

Sistema de gestão de demandas para assessorias de pesquisa legislativa, com assistente de IA integrado para busca de fontes oficiais e sugestão de rascunhos.

Desenvolvido como evolução de um sistema real implantado em assessoria do Senado Federal, reimplementado com arquitetura limpa para uso público.

---

## Funcionalidades

- Gestão do ciclo de vida de demandas (recebimento → resposta → revisão)
- Distribuição justa de demandas entre membros da equipe (algoritmo ponderado por carga e metas)
- Controle de prazos em dias úteis com calendário de feriados e afastamentos
- **Assistente de IA**: resumo de demandas e busca de fontes oficiais verificadas
- **Rastreador de PLs**: acompanhamento de tramitação via API aberta do Senado Federal
- Documentação técnica navegável (MkDocs)

---

## Arquitetura

Clean Architecture + Domain-Driven Design. Leia a [documentação completa](docs/architecture/overview.md) ou rode localmente:

```bash
mkdocs serve
# acesse http://localhost:8001
```

---

## Instalação

```bash
git clone https://github.com/Baniwa/callista-public.git
cd callista-public

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements/development.txt

cp .env.example .env
# edite .env com suas chaves

python manage.py migrate
python manage.py seed_data   # popula com dados fictícios para demo
python manage.py runserver
```

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5.x + Django REST Framework |
| Frontend | HTMX + Alpine.js + Tailwind CSS |
| IA | Claude API (Anthropic) |
| Dados legislativos | API Aberta do Senado Federal |
| Documentação | MkDocs + Material Theme |
| Testes | pytest + pytest-django |

---

## Estrutura do Projeto

```
src/
├── domain/          # Entidades, Value Objects, Serviços de domínio
├── application/     # Casos de uso e ports (interfaces)
├── adapters/        # Django ORM, Claude AI, API do Senado
└── infrastructure/  # Configurações, injeção de dependência

docs/                # Documentação técnica (MkDocs)
tests/               # Testes unitários e de integração
```

---

## Licença

MIT License — livre para uso, modificação e distribuição.
