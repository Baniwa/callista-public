# A IA é só mais um detalhe de infraestrutura

> Post publicado no LinkedIn ao final da Fase 3 — Assistente de IA com Gemini.

---

Wired an AI assistant into CALLISTA today.

The funny part? The domain still doesn't know it exists.

I added Gemini 2.0 Flash as the AI provider. The use cases call `ia.buscar_fontes(texto)` and get back a list of official legislative sources. They have no idea whether that list came from Gemini, Claude, or a hardcoded fake in a test file.

That's the whole point of the Port pattern.

The `IAPort` Protocol defines *what* the domain needs. `GeminiAdapter` defines *how* Gemini delivers it. If we migrate to Claude tomorrow, we write one new file and change one line in the dependency container. Zero use cases touched.

---

## O que foi implementado

Três novos use cases, todos consumindo a mesma interface:

```
BuscarFontesOficiaisUseCase  →  ia.buscar_fontes(demanda.texto)
GerarResumoUseCase           →  ia.gerar_resumo(demanda.texto)
SugerirRascunhoUseCase       →  ia.sugerir_rascunho(texto, contexto)
```

O adapter formata os prompts, chama a API, parseia o JSON de resposta e devolve objetos do domínio. Todo o trabalho sujo fica isolado em `src/adapters/ai/gemini_adapter.py`.

---

## Por que Gemini e não Claude?

Honestidade: custo. O tier gratuito do Gemini 2.0 Flash oferece 1.500 requisições/dia — suficiente para desenvolvimento e portfólio. Claude tem um nível de qualidade excelente para tarefas legislativas (e foi meu copiloto neste projeto inteiro), mas para demonstração pública, gratuito ganha.

A arquitetura não tem preferência. Amanhã posso adicionar um `ClaudeAdapter` e oferecer os dois como opção no container.

---

## O detalhe que mudou a estrutura dos testes

Quando fui escrever os testes, percebi que os fakes estavam duplicados em cada arquivo. Extraí para `tests/fakes/ia.py` — três classes: `FakeIA`, `FakeIAVazia`, `FakeIAEspiao`.

Isso não é só organização. É comunicação: fica explícito que `FakeIA` e `GeminiAdapter` são implementações intercambiáveis do mesmo contrato. Qualquer desenvolvedor que entrar no projeto vê isso imediatamente.

---

## Estado do projeto após a Fase 3

| Componente | Status |
|---|---|
| Domínio (entidades, serviços, use cases) | Completo |
| ORM Models + Adapters de repositório | Completo |
| Adapter Gemini (IAPort) | Completo |
| Use cases de IA (buscar, resumir, rascunho) | Completo |
| Testes unitários | 53 passando |

Próxima fase: **Rastreador de PLs** — adapter para a API Aberta do Senado Federal.
