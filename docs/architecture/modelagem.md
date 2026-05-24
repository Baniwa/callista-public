# Modelagem do Domínio

Esta seção documenta as entidades, value objects e interfaces de repositório da camada `src/domain/`, com suas invariantes, atributos e relacionamentos.

---

## 1. Conceitos de Modelagem (DDD)

O CALLISTA utiliza os seguintes padrões do Domain-Driven Design (Evans, 2003):

| Padrão | Descrição | Exemplos no CALLISTA |
|---|---|---|
| **Entity** | Objeto com identidade própria e ciclo de vida | `Demanda`, `Usuario`, `Afastamento` |
| **Value Object** | Objeto sem identidade, definido apenas por seus atributos, imutável | `Prazo`, `StatusDemanda`, `Feriado` |
| **Domain Service** | Lógica que não pertence naturalmente a nenhuma entidade | `SorteioJustoService` |
| **Repository** | Interface (Protocol) para acesso a entidades persistidas | `DemandaRepository`, `UsuarioRepository` |
| **Use Case** | Caso de uso da camada Application que orquestra domínio | `CadastrarDemandaUseCase`, `AtribuirRelatorUseCase` |

---

## 2. Entidades

### 2.1 Demanda

Entidade central do sistema. Representa uma solicitação de pesquisa legislativa em seu ciclo de vida completo.

**Localização:** `src/domain/entities/demanda.py`

| Atributo | Tipo | Descrição |
|---|---|---|
| `id` | `Optional[int]` | Identificador único (None antes de persistir) |
| `origem` | `str` | Sigla do órgão requisitante (ex.: "SGM", "LAI") |
| `num_origem` | `Optional[int]` | Número da demanda no sistema de origem |
| `texto` | `str` | Enunciado completo da demanda |
| `dat_chegada` | `date` | Data de recebimento (base para cálculo de prazo) |
| `prazo` | `Prazo` | Value object com prazo em dias úteis |
| `status` | `StatusDemanda` | Estado atual na máquina de estados |
| `id_relator` | `Optional[int]` | ID do pesquisador responsável pela resposta |
| `id_revisor` | `Optional[int]` | ID do pesquisador responsável pela revisão |
| `dat_cadastro` | `datetime` | Timestamp de criação no sistema |

**Invariantes:**
- `status` só pode transitar via métodos (`marcar_respondida`, `marcar_concluida`), nunca diretamente
- `marcar_respondida()` só é válido em status `PENDENTE_RESPOSTA`
- `marcar_concluida()` só é válido em status `PENDENTE_REVISAO`

---

### 2.2 Usuario

Representa um pesquisador ou gestor da assessoria.

**Localização:** `src/domain/entities/usuario.py`

| Atributo | Tipo | Padrão | Descrição |
|---|---|---|---|
| `id` | `Optional[int]` | — | Identificador único |
| `nome` | `str` | — | Nome completo |
| `email` | `str` | — | E-mail institucional |
| `matricula` | `str` | — | Matrícula no órgão |
| `cargo` | `str` | `""` | Cargo (para relatórios) |
| `is_ativo` | `bool` | `True` | Se False, não aparece no sistema |
| `is_oculto` | `bool` | `False` | Se True, não recebe demandas (ex.: conta de admin) |

**Propriedade derivada:**
```python
@property
def elegivel_para_demandas(self) -> bool:
    return self.is_ativo and not self.is_oculto
```

**Invariante:** Um usuário só participa do sorteio de atribuição se `elegivel_para_demandas is True`.

---

### 2.3 Afastamento

Representa um período de indisponibilidade de um usuário.

**Localização:** `src/domain/entities/afastamento.py`

| Atributo | Tipo | Descrição |
|---|---|---|
| `id` | `Optional[int]` | Identificador único |
| `usuario_id` | `int` | FK para Usuario |
| `dat_inicial` | `date` | Início do afastamento |
| `dat_final` | `date` | Fim do afastamento (inclusive) |
| `motivo` | `str` | Descrição (férias, licença, treinamento...) |

**Método central — `cobre_data(data, feriados)`:**

Retorna `True` se uma demanda com `dat_chegada = data` deve considerar este membro como ausente. A lógica antecipa o início em **2 dias úteis** para proteger contra atribuições que seriam abandonadas:

```python
inicio_efetivo = dat_inicial - 2_dias_uteis(feriados)
return inicio_efetivo <= data <= dat_final
```

---

### 2.4 Resposta

Registra o texto elaborado pelo relator ou revisor. Desacoplada de `Demanda` para preservar histórico de edições.

**Localização:** `src/domain/entities/resposta.py`

| Atributo | Tipo | Descrição |
|---|---|---|
| `id` | `Optional[int]` | Identificador único |
| `demanda_id` | `int` | FK para Demanda |
| `usuario_id` | `int` | ID de quem elaborou |
| `texto` | `str` | Conteúdo da resposta ou revisão |
| `dat_resposta` | `datetime` | Timestamp de submissão |
| `editado` | `bool` | Indica se houve edição posterior |

---

## 3. Value Objects

### 3.1 Prazo

Encapsula a lógica de cálculo de data-limite em dias úteis. É **imutável** (`frozen=True`).

**Localização:** `src/domain/value_objects/prazo.py`

```python
@dataclass(frozen=True)
class Prazo:
    dias_uteis: int  # deve ser > 0

    def data_limite(self, a_partir_de: date, feriados: Sequence[date] = ()) -> date:
        # avança dia a dia, contando apenas dias úteis
        ...
```

**Invariante:** `dias_uteis > 0` — validado em `__post_init__`.

**Por que Value Object e não int simples?**
Um `int` puro não carrega o significado de "dias úteis" nem a lógica de cálculo. `Prazo` encapsula ambos, tornando o código autodescritivo e o comportamento testável de forma isolada.

---

### 3.2 StatusDemanda

Enumeração tipada dos estados possíveis de uma demanda.

**Localização:** `src/domain/value_objects/status.py`

```python
class StatusDemanda(str, Enum):
    PENDENTE_RESPOSTA = "PR"
    PENDENTE_REVISAO  = "PF"
    PENDENTE_EXTERNA  = "PE"
    CONCLUIDA         = "C"
```

Herdando de `str`, o enum serializa diretamente para o banco de dados como string de 2 caracteres — compatível com o esquema do sistema legado.

---

### 3.3 Feriado

Value object simples que nomeia uma data de feriado.

**Localização:** `src/domain/entities/feriado.py`

```python
@dataclass(frozen=True)
class Feriado:
    data: date
    nome: str
```

Embora conceitualmente simples, modelar `Feriado` como tipo explícito (ao invés de `list[date]`) permite:
- Serialização com nome para exibição
- Filtragem por tipo (nacional, estadual, municipal) em versões futuras

---

## 4. Interfaces de Repositório (Protocol)

Repositórios são definidos como `Protocol` do Python (PEP 544), não como classes abstratas. A diferença é crucial: qualquer classe que implemente os métodos corretos satisfaz a interface, sem necessidade de herança explícita.

Isso permite que os fakes de teste sejam criados sem importar nada de Django ou ORM.

### Repositórios disponíveis

| Interface | Localização | Implementações previstas |
|---|---|---|
| `DemandaRepository` | `repositories/demanda_repository.py` | Django ORM (Fase 2) |
| `UsuarioRepository` | `repositories/usuario_repository.py` | Django ORM (Fase 2) |
| `AfastamentoRepository` | `repositories/afastamento_repository.py` | Django ORM (Fase 2) |
| `FeriadoRepository` | `repositories/feriado_repository.py` | Django ORM (Fase 2) |
| `RespostaRepository` | `repositories/resposta_repository.py` | Django ORM (Fase 2) |

### Por que Protocol ao invés de ABC?

```python
# Com ABC: acoplamento por herança
class DemandaRepository(ABC):
    @abstractmethod
    def salvar(self, demanda: Demanda) -> Demanda: ...

class FakeDemandaRepo(DemandaRepository):  # herança obrigatória
    ...

# Com Protocol: duck typing verificado estaticamente
class DemandaRepository(Protocol):
    def salvar(self, demanda: Demanda) -> Demanda: ...

class FakeDemandaRepo:  # zero herança — apenas implementa os métodos
    def salvar(self, demanda): ...
```

A vantagem: os fakes de teste não precisam importar a interface. Qualquer classe que tenha os métodos certos "satisfaz" o protocolo — verificado em tempo de análise estática (mypy/pyright), não em runtime.

---

## 5. Diagrama de Relacionamentos

```
┌─────────────────────────────────────────────┐
│                  DOMAIN                      │
│                                              │
│  ┌──────────┐     ┌──────────┐              │
│  │  Demanda │────▶│  Prazo   │ (value obj)  │
│  │ (entity) │     └──────────┘              │
│  │          │────▶│  Status  │ (value obj)  │
│  └──────────┘     └──────────┘              │
│       │                                      │
│       │ id_relator / id_revisor              │
│       ▼                                      │
│  ┌──────────┐     ┌─────────────┐           │
│  │ Usuario  │────▶│ Afastamento │           │
│  │ (entity) │     │  (entity)   │           │
│  └──────────┘     └─────────────┘           │
│                                              │
│  ┌──────────────────────────────────┐       │
│  │     DemandaRepository (Protocol) │       │
│  │     UsuarioRepository (Protocol) │       │
│  │  AfastamentoRepository (Protocol)│       │
│  └──────────────────────────────────┘       │
└─────────────────────────────────────────────┘
```
