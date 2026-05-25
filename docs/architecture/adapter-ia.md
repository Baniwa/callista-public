# Adapter de Inteligência Artificial

Esta seção documenta a Fase 3 do CALLISTA: a integração com um provedor de IA generativa para busca de fontes, geração de resumos e sugestão de rascunhos de resposta.

---

## 1. O Contrato: IAPort

Antes de existir qualquer adapter, o domínio define o que espera de um serviço de IA. Isso é feito através de um `Protocol` Python em `src/application/ports/ai_port.py`:

```python
class IAPort(Protocol):
    def buscar_fontes(self, texto: str) -> Sequence[FonteOficial]: ...
    def gerar_resumo(self, texto: str) -> str: ...
    def sugerir_rascunho(self, texto_demanda: str, respostas_anteriores: Sequence[str]) -> str: ...
```

O domínio e os use cases só enxergam esse contrato. Não existe nenhuma importação de `google`, `anthropic`, ou qualquer SDK externo dentro de `src/domain/` ou `src/application/`.

### FonteOficial — o objeto de retorno

```python
@dataclass
class FonteOficial:
    titulo: str
    url: str
    orgao: str
    resumo_trecho: str
```

Esse dataclass também vive em `src/application/ports/ai_port.py` — é a linguagem que o domínio usa para representar uma fonte de pesquisa. O adapter é responsável por traduzir a resposta da API para esse formato.

---

## 2. O Adapter: GeminiAdapter

**Localização:** `src/adapters/ai/gemini_adapter.py`

O `GeminiAdapter` implementa o `IAPort` usando o modelo `gemini-2.0-flash` (Google). Ele é responsável por:

1. Formatar os prompts específicos para pesquisa legislativa
2. Chamar a API Gemini
3. Parsear a resposta (JSON para `buscar_fontes`, texto para os demais)
4. Devolver objetos do domínio (`FonteOficial`, `str`)

```
IAPort (Protocol)          ← contrato que o domínio define
        ↑ implementa
GeminiAdapter              ← adapter que conhece a API Gemini
        ↑ usa
google.genai.Client        ← SDK do provedor externo
```

### Por que Gemini 2.0 Flash?

| Critério | Decisão |
|---|---|
| Custo | Tier gratuito: 1.500 requisições/dia |
| Latência | Flash é otimizado para respostas rápidas |
| Qualidade | Adequado para sumarização e pesquisa de fontes legislativas |
| Modelo | `gemini-2.0-flash` — estável e disponível globalmente |

---

## 3. Prompts como Detalhe de Implementação

Os prompts ficam **dentro do adapter**, não nos use cases. Isso é deliberado: o prompt é um detalhe do provedor. Se o Callista migrar para Claude ou GPT-4, os prompts mudam no adapter — nenhum use case é tocado.

### buscar_fontes — JSON estruturado

O adapter solicita resposta em `application/json` diretamente via `response_mime_type`:

```python
config=types.GenerateContentConfig(
    response_mime_type="application/json",
    temperature=0.2,
)
```

O prompt instrui o modelo a retornar um array de objetos com os campos `titulo`, `url`, `orgao` e `resumo_trecho` — exatamente o formato de `FonteOficial`. O adapter então parseia com `json.loads()` e mapeia campo a campo.

### Tratamento de falhas

Se o JSON vier malformado ou a chamada falhar, o adapter captura a exceção, registra em log e retorna lista vazia / string vazia. O use case não sabe que houve falha — ele só recebe um resultado vazio.

!!! note "Por que não lançar exceção?"
    Para um sistema institucional, uma busca de fontes sem resultado é melhor que uma tela de erro. A falha silenciosa com log permite que o pesquisador continue seu trabalho manualmente.

---

## 4. Use Cases de IA

Três use cases consomem o `IAPort`:

| Use Case | Entrada | Saída | Método IAPort |
|---|---|---|---|
| `BuscarFontesOficiaisUseCase` | `demanda_id` | `Sequence[FonteOficial]` | `buscar_fontes()` |
| `GerarResumoUseCase` | `demanda_id` | `GerarResumoOutput` | `gerar_resumo()` |
| `SugerirRascunhoUseCase` | `demanda_id` | `SugerirRascunhoOutput` | `sugerir_rascunho()` |

Todos seguem o mesmo padrão:

```
1. Busca a demanda pelo ID no repositório
2. Lança ValueError se não encontrada
3. Extrai o texto da demanda
4. Repassa ao adapter de IA
5. Devolve o resultado
```

O use case não sabe se está falando com Gemini, Claude ou um fake de testes.

---

## 5. Container — montando com Gemini

**Localização:** `src/infrastructure/container/__init__.py`

```python
def _gemini() -> GeminiAdapter:
    return GeminiAdapter(api_key=config("GEMINI_API_KEY"))

def build_buscar_fontes_oficiais() -> BuscarFontesOficiaisUseCase:
    return BuscarFontesOficiaisUseCase(
        repository=DjangoDemandaRepository(),
        ia=_gemini(),
    )
```

Para migrar para outro provedor no Callista 2.0:

```python
# Antes
ia=GeminiAdapter(api_key=config("GEMINI_API_KEY"))

# Depois (exemplo hipotético)
ia=ClaudeAdapter(api_key=config("ANTHROPIC_API_KEY"))
```

Nada mais muda. Os use cases, entidades e testes permanecem intactos.

---

## 6. Testes — Fakes Centralizados

**Localização:** `tests/fakes/ia.py`

Os testes unitários nunca chamam a API real. Em vez disso, usam adapters de teste (fakes) que implementam o mesmo `IAPort`:

| Classe | Comportamento |
|---|---|
| `FakeIA` | Retorna dados fixos e previsíveis |
| `FakeIAVazia` | Retorna listas e strings vazias (simula falha silenciosa) |
| `FakeIAEspiao` | Registra todas as chamadas recebidas para verificação |

```python
# Qualquer implementação de IAPort funciona aqui:
uc = BuscarFontesOficiaisUseCase(
    repository=FakeDemandaRepo([demanda]),
    ia=FakeIA(),          # ← pode ser GeminiAdapter, ClaudeAdapter, FakeIA...
)
```

Essa organização deixa explícito que `FakeIA` e `GeminiAdapter` são **implementações intercambiáveis** do mesmo contrato — o mesmo princípio que guiará a criação de um `ClaudeAdapter` em versões futuras.

---

## 7. Configuração

Adicione ao seu `.env` (veja `.env.example`):

```
GEMINI_API_KEY=sua-chave-aqui
```

Obtenha sua chave gratuitamente em [Google AI Studio](https://aistudio.google.com/app/apikey).

O tier gratuito do Gemini 2.0 Flash oferece **1.500 requisições/dia** — suficiente para desenvolvimento e demonstração do sistema.
