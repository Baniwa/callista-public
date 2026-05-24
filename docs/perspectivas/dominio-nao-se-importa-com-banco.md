# O domínio não se importa com o banco de dados

> Post publicado no LinkedIn ao final da Fase 2 — Django ORM adapters.

---

I finally wired my domain layer to a real database today.

The fun part? The domain didn't care at all.

That's the whole point of writing framework-agnostic business logic — when you eventually plug in Django ORM, you just write a thin translator. The rules stay exactly where they were.

The less exciting part: one dependency I listed in requirements didn't compile on Python 3.14. Manual dependency injection it is. Sometimes the boring solution is the right one.

---

## O que aconteceu por baixo

Na Fase 2 do CALLISTA, conectamos o domínio ao banco de dados sem tocar em uma linha de lógica de negócio.

O fluxo completo ficou assim:

```
View Django (HTTP)
    ↓
build_cadastrar_demanda()      ← container monta o use case
    ↓
CadastrarDemandaUseCase        ← domínio puro, sem Django
    ↓
DjangoDemandaRepository        ← adapter: traduz para ORM
    ↓
DemandaModel.objects.create()  ← banco de dados
```

Cada camada só conhece a camada imediatamente abaixo. O domínio não sabe que existe SQLite. O banco não sabe que existe um algoritmo de sorteio justo.

---

## O problema com o dependency-injector

O pacote `dependency-injector` — que seria responsável por montar automaticamente as dependências — não compilou no Python 3.14 (extensão C sem suporte ainda).

Solução: injeção manual com funções factory.

```python
# src/infrastructure/container/__init__.py

def build_atribuir_relator() -> AtribuirRelatorUseCase:
    return AtribuirRelatorUseCase(
        demanda_repo=DjangoDemandaRepository(),
        usuario_repo=DjangoUsuarioRepository(),
        afastamento_repo=DjangoAfastamentoRepository(),
        feriado_repo=DjangoFeriadoRepository(),
        sorteio=SorteioJustoService(),
    )
```

Verboso? Sim. Legível? Muito. Depurável sem framework? Completamente.

Às vezes a solução chata é a correta.

---

## Estado do projeto após a Fase 2

| Componente | Status |
|---|---|
| Domínio (entidades, serviços, use cases) | Completo |
| ORM Models (5 tabelas) | Completo |
| Adapters de repositório (5) | Completo |
| Settings por ambiente (dev/prod) | Completo |
| Seed de dados fictícios | Completo |
| Testes unitários | 42 passando |

Próxima fase: **Assistente de IA** — adapter para Claude API integrado ao `BuscarFontesOficiaisUseCase`.
