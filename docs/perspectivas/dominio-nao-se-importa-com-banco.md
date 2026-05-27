# O domínio não se importa com o banco de dados

> Post publicado no LinkedIn ao final da Fase 2 — Django ORM Adapters.

---

Shipped the ORM layer for CALLISTA today.

The interesting part: the domain entities never changed. Not a single line.

That's the core promise of Clean Architecture, and the Fase 2 of this project was the first real test of it.

---

## O problema que a arquitetura resolve

Quando você começa um projeto Django, o instinto natural é ir direto nos models. Você pensa: "preciso de uma tabela de demandas, então vou criar `class Demanda(models.Model)`".

O problema é que você acabou de amarrar sua lógica de negócio a uma tecnologia de persistência. Se um dia você mudar de PostgreSQL para outra coisa — ou quiser testar sua lógica de negócio sem banco — você vai sentir a dor disso.

No CALLISTA, a entidade `Demanda` existe em `src/domain/entities/demanda.py` como um simples `@dataclass`. Sem `models.Model`. Sem `Meta`. Sem nenhuma importação do Django.

```python
@dataclass
class Demanda:
    id: Optional[int]
    origem: str
    texto: str
    dat_chegada: date
    prazo: Prazo
    status: StatusDemanda = StatusDemanda.PENDENTE_RESPOSTA
    id_relator: Optional[int] = None
```

Esse é o objeto que o domínio conhece. É nele que a regra de negócio vive — o método `marcar_respondida()` que valida a transição de status, o `marcar_concluida()` que exige que a demanda esteja em revisão antes de concluir.

---

## O que o adapter faz

O `DjangoDemandaRepository` vive em `src/adapters/django_orm/`. Ele conhece o Django. Ele conhece o ORM. Mas o domínio não sabe que ele existe.

```python
class DjangoDemandaRepository:
    def salvar(self, demanda: Demanda) -> Demanda:
        obj = DemandaModel.objects.create(
            origem=demanda.origem,
            texto=demanda.texto,
            # ...
        )
        return self._to_entity(obj)
```

O método `_to_entity` é o ponto central: ele traduz um `DemandaModel` (objeto do ORM, com todas as dependências do Django) em uma `Demanda` (objeto do domínio, sem dependência nenhuma). É uma fronteira explícita.

---

## Por que isso importa na prática

Durante a Fase 1, escrevi 42 testes unitários para o domínio. Nenhum deles usou banco de dados. Nenhum precisou de `pytest-django` ou de fixtures. Eles rodaram em 0.14 segundos.

Quando cheguei na Fase 2 e implementei o ORM, esses 42 testes continuaram passando sem nenhuma mudança. O domínio não sabia — e não precisava saber — que agora havia um banco real atrás.

Isso é o que a separação de camadas compra: **a lógica de negócio é testável, modificável e compreensível sem nenhuma infraestrutura**.

---

## O que foi implementado na Fase 2

```
src/adapters/django_orm/
├── models.py              ← DemandaModel, UsuarioModel, RespostaModel...
├── demanda_repo.py        ← Implementa DemandaRepository (Protocol)
├── usuario_repo.py        ← Implementa UsuarioRepository
├── resposta_repo.py       ← Implementa RespostaRepository
├── afastamento_repo.py    ← Implementa AfastamentoRepository
└── feriado_repo.py        ← Implementa FeriadoRepository
```

Cada adapter implementa uma interface definida no domínio (um `Protocol` do Python). O domínio define *o que* precisa. O adapter define *como* entrega.

---

## Estado do projeto após a Fase 2

| Componente | Status |
|---|---|
| Domínio (entidades, serviços, use cases) | Completo |
| Repository interfaces (Protocol) | Completo |
| ORM Models (Django) | Completo |
| Adapters de repositório (5 entidades) | Completo |
| Seed de dados fictícios | Completo |
| Testes unitários | 42 passando, sem banco |

Próxima fase: **Assistente de IA** — um adapter para o Gemini que o domínio também não vai conhecer.
