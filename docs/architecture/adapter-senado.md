# Adapter da API do Senado Federal

Esta seção documenta a Fase 4 do CALLISTA: a integração com a API de Dados Abertos do Senado Federal para rastreamento de Projetos de Lei em tempo real.

---

## 1. O Contrato: SenadoPort

O domínio define o que espera de um serviço de dados legislativos via `Protocol` em `src/application/ports/senado_port.py`:

```python
class SenadoPort(Protocol):
    def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]: ...
    def buscar_por_id(self, id_senado: int) -> Optional[ProjetoLei]: ...
```

O use case `RastrearPLUseCase` só enxerga esse contrato. Nenhuma importação de `httpx`, URLs ou lógica de parsing existe fora do adapter.

---

## 2. A Entidade: ProjetoLei

**Localização:** `src/domain/entities/projeto_lei.py`

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
    sigla_situacao: str         # "AGDESP", "TNJR"...
    dat_situacao: date
    url_documento: str
    autoria: str
    dat_ultima_atualizacao: datetime
    demanda_id: Optional[int] = None
```

O campo `demanda_id` permite que um PL rastreado seja vinculado a uma demanda do CALLISTA — ligação bidirecional entre o fluxo interno de pesquisa e a tramitação legislativa externa.

---

## 3. O Adapter: SenadoAdapter

**Localização:** `src/adapters/senado_api/senado_adapter.py`

```
SenadoPort (Protocol)       ← contrato que o domínio define
        ↑ implementa
SenadoAdapter               ← adapter que conhece a API do Senado
        ↑ usa
httpx.Client                ← HTTP client (já em requirements)
```

### Endpoint ativo

O endpoint `/materia/pesquisa/lista` foi desativado em 01/02/2026. O adapter usa o substituto oficial:

```
GET https://legis.senado.leg.br/dadosabertos/processo?sigla=PEC&numero=45&ano=2019
GET https://legis.senado.leg.br/dadosabertos/processo/{id_senado}
```

### Estratégia de busca em dois passos

```python
def buscar_pl(self, sigla: str, numero: int, ano: int) -> Optional[ProjetoLei]:
    # 1. Busca por identificação → obtém o id_senado
    resp = self._client.get("/processo", params={"sigla": sigla, "numero": numero, "ano": ano})
    id_senado = resp.json()[0]["id"]
    # 2. Busca o detalhe completo pelo ID
    return self._buscar_detalhe(id_senado)
```

A busca por identificação retorna campos resumidos. O detalhe por ID traz o objeto completo (ementa, autoria, situação atual, URL do documento). O adapter sempre faz os dois passos para garantir dados completos.

### Parser defensivo

A API do Senado usa wrappers JSON variáveis dependendo do endpoint. O método `_extrair_lista()` navega a resposta tentando chaves comuns (`dados`, `Dados`, `processos`, `items`) antes de desistir:

```python
def _extrair_lista(self, dados: dict) -> list:
    if isinstance(dados, list):
        return dados
    for chave in ("dados", "Dados", "processos", "Processos", "items"):
        valor = dados.get(chave)
        if isinstance(valor, list):
            return valor
        # ... tenta sub-chaves
    return []
```

### Tratamento de falhas

Se qualquer chamada HTTP falhar (`httpx.HTTPError`), o adapter captura a exceção, registra em log e retorna `None`. O use case então lança `ValueError` com a identificação do PL, permitindo tratamento adequado na camada de apresentação.

!!! warning "Sub-recursos de tramitação"
    Os endpoints `/processo/{id}/tramitacao` e `/processo/{id}/eventos` retornam **404**.
    Não é possível obter o histórico completo de passos via API. O CALLISTA contorna isso
    salvando snapshots — a mudança de `situacao_atual` entre consultas é o sinal de progresso.

---

## 4. O Use Case: RastrearPLUseCase

**Localização:** `src/application/use_cases/rastrear_pl.py`

```python
class RastrearPLUseCase:
    def executar(self, dto: RastrearPLInput) -> ProjetoLei:
        pl = self._senado.buscar_pl(dto.sigla, dto.numero, dto.ano)
        if pl is None:
            raise ValueError(f"PL {dto.sigla} {dto.numero}/{dto.ano} não encontrado")

        existente = self._pl_repo.buscar_por_id_senado(pl.id_senado)
        if existente:
            pl.id = existente.id   # ← atualiza snapshot, mantém o ID interno

        if dto.demanda_id is not None:
            pl.demanda_id = dto.demanda_id

        return self._pl_repo.salvar(pl)
```

**Lógica de snapshot:** o use case verifica se o PL já foi rastreado antes (via `id_senado`). Se sim, preserva o ID interno e sobrescreve os dados — atualizando o snapshot. Isso permite detectar mudanças de status comparando `situacao_atual` antes e depois.

---

## 5. Persistência: ProjetoLeiModel

**Localização:** `src/adapters/django_orm/models.py`  
**Tabela:** `callista_projeto_lei`

| Campo | Tipo | Observação |
|-------|------|------------|
| `id_senado` | `IntegerField (unique)` | Chave de idempotência com a API |
| `identificacao` | `CharField` | "PL 8/2025" |
| `situacao_atual` | `CharField` | Comparado no próximo polling |
| `dat_ultima_atualizacao` | `DateTimeField` | Polling: só re-consulta se mudou |
| `dat_snapshot` | `DateTimeField (auto_now)` | Timestamp local do último rastreamento |
| `demanda` | `ForeignKey → DemandaModel` | Vínculo opcional |

O campo `dat_snapshot` (atualizado automaticamente a cada `salvar()`) permite saber quando o CALLISTA consultou a API pela última vez — útil para respeitar o cache de 30 minutos do servidor.

---

## 6. Testes — FakeSenado

**Localização:** `tests/fakes/senado.py`

| Classe | Comportamento |
|--------|---------------|
| `FakeSenado(pl)` | Retorna o `ProjetoLei` configurado |
| `FakeSenadoVazio` | Sempre retorna `None` — simula PL não encontrado |

```python
# Os testes nunca fazem chamadas HTTP:
uc = RastrearPLUseCase(
    senado=FakeSenado(pl),      # ← pode ser SenadoAdapter ou FakeSenado
    pl_repo=FakeProjetoLeiRepo(),
)
```

Seis testes cobrem: PL novo, atualização de snapshot existente, vínculo com demanda, ausência de vínculo, PL não encontrado e listagem por demanda.

---

## 7. Container — montando com SenadoAdapter

**Localização:** `src/infrastructure/container/__init__.py`

```python
def build_rastrear_pl() -> RastrearPLUseCase:
    return RastrearPLUseCase(
        senado=SenadoAdapter(),
        pl_repo=DjangoProjetoLeiRepository(),
    )
```

O `SenadoAdapter` não precisa de API key — a API do Senado é pública. Para trocar de provedor de dados legislativos, basta implementar `SenadoPort` em outro adapter e mudar esta linha.

---

## 8. Limites conhecidos da API

| Limitação | Impacto | Contorno |
|-----------|---------|----------|
| Cache server-side de 30 min | Não faz sentido consultar mais de 1x/30min | Respeitar `dat_snapshot` antes de re-consultar |
| Sem histórico de tramitação (`/tramitacao` → 404) | Não há histórico passo a passo | Comparar `situacao_atual` entre snapshots |
| Busca retorna apenas processos na casa revisora | Não lista todos os PLs do Brasil | Busca pontual por `sigla+numero+ano` é a abordagem correta |

Para contexto completo da exploração da API antes da implementação, veja [API do Senado Federal — Análise](senado-api.md).
