# API Aberta do Senado Federal — Análise para a Fase 4

## Contexto

Antes de implementar o Rastreador de PLs (Fase 4), exploramos a API de Dados Abertos do Senado Federal para entender o que está disponível, quais endpoints são ativos, quais campos são úteis e onde estão as limitações. Esta página documenta esse processo de descoberta.

---

## O que foi feito

1. Tentativa de acesso à documentação Swagger (`/dadosabertos/docs/`) — interface carrega mas não é indexável programaticamente
2. Chamada ao endpoint histórico `/materia/pesquisa/lista` — retornou metadados de depreciação
3. Exploração do endpoint substituto `/processo`
4. Testes de busca, detalhe e sub-recursos

---

## Endpoint ativo: `/processo`

O endpoint `/materia/pesquisa/lista` foi **descontinuado em 18/03/2025 e desativado em 01/02/2026**. O substituto oficial é:

```
https://legis.senado.leg.br/dadosabertos/processo
```

### Operações disponíveis

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `GET` | `/processo?sigla=PL&numero=8&ano=2025` | Busca por identificação |
| `GET` | `/processo?sigla=PEC&ano=2019` | Listagem por tipo e ano |
| `GET` | `/processo/{id}` | Detalhe completo pelo ID interno |

### Parâmetros de busca confirmados

| Parâmetro | Exemplo | Descrição |
|-----------|---------|-----------|
| `sigla` | `PL`, `PEC`, `PLP` | Tipo do projeto |
| `numero` | `8` | Número da matéria |
| `ano` | `2025` | Ano de apresentação |
| `tramitando` | `Sim` / `Não` | Filtro por situação |

---

## Estrutura da resposta

### Lista (`/processo?...`)

```json
{
  "id": 8783695,
  "identificacao": "PL 8/2025",
  "ementa": "Altera o Decreto-Lei nº 2.848...",
  "autoria": "Câmara dos Deputados",
  "tramitando": "Sim",
  "situacaoAtual": "AGUARDANDO DESPACHO",
  "dataSituacaoAtual": "2025-02-03",
  "dataUltimaAtualizacao": "2026-01-28T00:48:44.83",
  "urlDocumento": "https://legis.senado.gov.br/sdleg-getter/documento?dm=...",
  "tipoDocumento": "Projeto de Lei Ordinária"
}
```

### Detalhe (`/processo/{id}`)

Além dos campos acima, inclui:

```json
{
  "sigla": "PL",
  "numero": "8",
  "ano": 2025,
  "conteudo": {
    "ementa": "Altera o Decreto-Lei..."
  },
  "documento": {
    "url": "https://legis.senado.gov.br/sdleg-getter/documento?dm=...",
    "dataApresentacao": "2025-02-03",
    "autoria": [...],
    "resumoAutoria": "Câmara dos Deputados"
  },
  "autoriaIniciativa": [
    {
      "autor": "Nome do Parlamentar",
      "siglaPartido": "MDB",
      "cargo": "Deputado Federal"
    }
  ],
  "classificacoes": [
    {
      "descricao": "Finanças Públicas",
      "descricaoHierarquia": "Economia e Desenvolvimento / Finanças Públicas"
    }
  ],
  "processosApensados": [...],
  "siglaSituacaoAtual": "AGDESP",
  "dataSituacaoAtual": "2025-02-03",
  "dthUltimaAtualizacao": "2026-01-28T00:48:44.830000"
}
```

---

## Campos mapeados para o domínio Callista

| Campo da API | Campo do domínio | Uso |
|---|---|---|
| `id` | `id_senado` | Chave para chamadas subsequentes |
| `identificacao` | `identificacao` | Exibição para o usuário ("PL 8/2025") |
| `sigla` / `numero` / `ano` | `sigla`, `numero`, `ano` | Busca e referência |
| `conteudo.ementa` | `ementa` | Descrição da matéria |
| `tramitando` | `tramitando` | Flag booleano |
| `situacaoAtual` | `situacao_atual` | Status atual — comparado com snapshot anterior para detectar mudança |
| `siglaSituacaoAtual` | `sigla_situacao` | Código da situação (ex: `AGDESP`, `TNJR`) |
| `dataSituacaoAtual` | `dat_situacao` | Data da última mudança de status |
| `dthUltimaAtualizacao` | `dat_ultima_atualizacao` | Timestamp para polling — só re-consulta se mudou |
| `documento.url` | `url_documento` | Link para o texto original |
| `documento.resumoAutoria` | `autoria` | Autoria resumida |

---

## O que NÃO existe na API

!!! warning "Sub-recursos de tramitação"
    Os endpoints `/processo/{id}/tramitacao` e `/processo/{id}/eventos` retornam **404**.
    A API não expõe o histórico passo a passo de tramitação.

Isso impacta o design: **não é possível obter o histórico completo de passos**, apenas o snapshot do estado atual. A lógica de "detectar mudança de status" no Callista vai comparar o `situacaoAtual` salvo anteriormente com o valor retornado pela API.

---

## Volumes observados

| Consulta | Resultado |
|---|---|
| `?sigla=PL&ano=2025` | **849 registros** (PLs na casa revisora) |
| `?sigla=PEC&numero=45&ano=2019` | 1 registro (PEC 45/2019 — Reforma Tributária) |

A listagem por ano retorna todos os processos na casa revisora (Senado), não todos os PLs do Brasil. Busca pontual por `sigla+numero+ano` é a abordagem correta para o rastreio de uma matéria específica.

---

## Autenticação

A API é pública. Nenhuma chave ou token é necessário. Os headers observados:

```
access-control-allow-origin: *
cache-control: max-age=1800, s-maxage=1800
```

Cache de 30 minutos no servidor. O polling do Callista deve respeitar isso — não faz sentido consultar mais de uma vez a cada 30 minutos.

---

## Design da Fase 4

Com base nessa exploração, a implementação seguirá o mesmo padrão Port/Adapter das fases anteriores:

### `SenadoPort` (interface — `src/application/ports/`)

```python
class SenadoPort(Protocol):
    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]: ...
    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]: ...
```

### `ProjetoLei` (entidade — `src/domain/entities/`)

```python
@dataclass
class ProjetoLei:
    id: Optional[int]           # ID interno do Callista
    id_senado: int              # ID do /processo na API
    identificacao: str          # "PL 8/2025"
    sigla: str                  # "PL", "PEC", "PLP"
    numero: int
    ano: int
    ementa: str
    tramitando: bool
    situacao_atual: str
    sigla_situacao: str
    dat_situacao: date
    url_documento: str
    autoria: str
    dat_ultima_atualizacao: datetime
```

### `RastrearPLUseCase`

Receberá um `demanda_id` e um identificador de PL (`sigla`, `numero`, `ano`), consultará a API via `SenadoPort`, salvará o snapshot no banco e vinculará à demanda.

### `SenadoAdapter` (`src/adapters/senado_api/`)

Implementará `SenadoPort` fazendo chamadas HTTP a `legis.senado.leg.br/dadosabertos/processo`.

### `FakeSenado` (`tests/fakes/`)

Implementação in-memory do `SenadoPort` para testes unitários — o domínio não precisa saber que existe uma API externa.

---

## Exemplo testado ao vivo

**PEC 45/2019 — Reforma Tributária:**

```
GET /processo?sigla=PEC&numero=45&ano=2019
→ id: 8503515
→ situacaoAtual: "TRANSFORMADA EM NORMA JURÍDICA"
→ normaGerada: "Emenda Constitucional nº 132 de 20/12/2023"
→ tramitando: "Não"
```

A API retornou dados completos sem autenticação em menos de 1 segundo.
