# ADR-002 — Upgrade para Django 6.0.5 por incompatibilidade com Python 3.14

| Campo | Valor |
|-------|-------|
| **Status** | Aceito |
| **Data** | 2026-05-28 |
| **Decisores** | Equipe CALLISTA |

## Contexto

O projeto usava Django 5.0.6. Ao rodar em **Python 3.14**, o servidor falha imediatamente
com o seguinte traceback:

```
TypeError: cannot pickle 'property' object
  File "django/template/context.py", line ..., in __copy__
```

O método `__copy__` de `django.template.context.BaseContext` tenta fazer pickle de
`property` objects — algo que passou a falhar com a nova semântica de cópia do Python 3.14.

Essa incompatibilidade está documentada no issue tracker do Django e foi corrigida apenas
na série 5.2+ / 6.x.

## Decisão

Atualizar Django de **5.0.6 → 6.0.5**.

Ao mesmo tempo, o pacote `django-browser-reload` — que adiciona recarga automática do
navegador em desenvolvimento — foi **removido**, pois estava causando erros secundários
durante o diagnóstico e não é necessário em produção. O benefício (recarregar o navegador
automaticamente) não justifica a complexidade extra de manutenção.

## Consequências

**Positivas:**

- Python 3.14 funciona sem nenhuma modificação no código da aplicação
- Django 6.x traz melhorias de desempenho no ORM e suporte mais longo (LTS)
- Menos dependências desnecessárias (`django-browser-reload` removido)

**Negativas:**

- Django 6.x é uma major version; breaking changes potenciais precisam ser revisados
  (não foram identificados impactos neste projeto no momento do upgrade)
- Perda da recarga automática do navegador em desenvolvimento (tradeoff aceitável)

## Alternativas Consideradas

| Alternativa | Por que rejeitada |
|-------------|------------------|
| Manter Django 5.0.6 e usar Python 3.12 | Forçaria todos os desenvolvedores a instalar uma versão Python específica; inflexível |
| Usar Django 5.2 (LTS) | Testado, mas o mesmo bug se manifestava — a correção definitiva foi na série 6.x |
| Patch manual de `context.py` | Frágil; seria sobrescrito em qualquer upgrade de dependência |

## Referências

- Django Issue: `django.template.context.__copy__` quebra com Python 3.14
- [Django 6.0 Release Notes](https://docs.djangoproject.com/en/6.0/releases/6.0/)
- [Python 3.14 What's New](https://docs.python.org/3.14/whatsnew/3.14.html)
