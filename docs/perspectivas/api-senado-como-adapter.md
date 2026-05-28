# O governo já tem a API. Você só precisa conectar.

> Post publicado no LinkedIn ao final da Fase 4 — Rastreador de PLs.

---

Wired the Brazilian Senate's public API into CALLISTA today.

The domain still doesn't know it exists.

The use case calls `senado.buscar_pl("PEC", 45, 2019)` and gets back a `ProjetoLei` entity. It has no idea whether that data came from an HTTP request, a database cache, or a hardcoded fake in a test file.

---

## Por que isso importa

O Senado Federal mantém uma API pública em `legis.senado.leg.br/dadosabertos`. Sem autenticação. Sem chave de API. Com cache de 30 minutos no servidor.

Para o CALLISTA, isso significa que qualquer pesquisador legislativo pode rastrear a tramitação de um PL de interesse — PEC 45/2019, PL 8/2025, qualquer matéria identificável por sigla + número + ano — sem sair do sistema.

```
GET /processo?sigla=PEC&numero=45&ano=2019
→ situacaoAtual: "TRANSFORMADA EM NORMA JURÍDICA"
→ normaGerada: "Emenda Constitucional nº 132 de 20/12/2023"
```

---

## A pegadinha da API

Fui implementar histórico de tramitação.

```
GET /processo/8503515/tramitacao
→ 404
```

O endpoint não existe. A API expõe apenas o snapshot atual — não o histórico de passos. Isso muda o design: o CALLISTA não pode mostrar "o PL passou pela comissão X no dia Y". Ele pode mostrar "o status mudou desde a última consulta".

Não é o ideal. É o disponível. E é suficiente para o caso de uso real.

---

## O que foi implementado

```
SenadoPort (Protocol)        ← o domínio define o que precisa
SenadoAdapter (httpx)        ← implementa consultando a API pública
FakeSenado (in-memory)       ← implementa para os testes, sem rede
```

O `RastrearPLUseCase` detecta snapshots existentes pelo `id_senado` e atualiza em vez de duplicar. O vínculo com a demanda é opcional — um PL pode ser rastreado independentemente ou associado a uma demanda específica.

---

## Estado do projeto após a Fase 4

| Componente | Status |
|---|---|
| Domínio (entidades, serviços, use cases) | Completo |
| ORM Models + Adapters de repositório | Completo |
| Adapter Gemini (IAPort) | Completo |
| Use cases de IA (buscar, resumir, rascunho) | Completo |
| Adapter Senado (SenadoPort) | Completo |
| RastrearPLUseCase | Completo |
| Testes unitários | 59 passando |

Próxima fase: **Frontend** — HTMX + Tailwind CSS + paleta federal.
