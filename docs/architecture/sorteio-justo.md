# Algoritmo de Sorteio Justo

O `SorteioJustoService` é o coração operacional do CALLISTA. Resolve o problema de **distribuição equitativa de carga de trabalho** entre pesquisadores, levando em conta a meta mensal individual de cada membro.

---

## 1. O Problema

Dada uma equipe de *n* pesquisadores com diferentes históricos de demandas respondidas no mês corrente, **a quem atribuir a próxima demanda** de forma que a distribuição seja justa ao longo do tempo?

A solução trivial — atribuição aleatória uniforme — falha em dois cenários:

1. **Membros atrasados não são priorizados.** Quem respondeu 0 demandas tem a mesma chance de quem respondeu 11.
2. **Membros adiantados não são protegidos.** Quem está com 15 demandas (superando a meta de 12) continua sendo sorteado igualmente.

O algoritmo do CALLISTA, replicado do sistema original implantado no Senado Federal, resolve ambos.

---

## 2. Definições Formais

Seja:

- **M** — meta mensal individual de respostas (padrão: 12)
- **dᵢ** — número de demandas respondidas pelo membro *i* no mês corrente
- **pᵢ = dᵢ / M** — percentual da meta atingido pelo membro *i*
- **C** — conjunto de candidatos disponíveis (ativos, não ocultos, não afastados)

---

## 3. O Algoritmo

O algoritmo opera em dois modos, determinados pela situação coletiva da equipe:

### Modo A — Todos acima de 90% da meta

**Condição:** ∀ *i* ∈ C, pᵢ ≥ 0.9

Neste caso, toda a equipe está próxima ou acima da meta. O critério de desempate é a **média do grupo**:

```
E = { i ∈ C | pᵢ < média(C) }
Se E = ∅ → E = C   (todos empatados na média)
```

**Selecionar** aleatoriamente um membro de **E** (distribuição uniforme).

### Modo B — Algum membro abaixo de 90%

**Condição:** ∃ *i* ∈ C, pᵢ < 0.9

O sistema identifica quem está mais atrás e limita a 10 pontos percentuais acima do mínimo:

```
mín = min{ pᵢ | i ∈ C }
E = { i ∈ C | pᵢ ≤ mín + 0.10 }
```

**Selecionar** aleatoriamente um membro de **E** (distribuição uniforme).

---

## 4. Implementação

**Localização:** `src/domain/services/sorteio_justo.py`

```python
@dataclass(frozen=True)
class CandidatoSorteio:
    usuario_id: int
    percentual_meta: float  # dᵢ / M

class SorteioJustoService:
    def selecionar(self, candidatos: Sequence[CandidatoSorteio]) -> int:
        if not candidatos:
            raise ValueError("Nenhum candidato disponível para o sorteio")

        percentuais = [c.percentual_meta for c in candidatos]
        todos_acima_90 = all(p >= 0.9 for p in percentuais)

        if todos_acima_90:
            media = sum(percentuais) / len(percentuais)
            elegiveis = [c for c in candidatos if c.percentual_meta < media]
            if not elegiveis:
                elegiveis = list(candidatos)
        else:
            minimo = min(percentuais)
            elegiveis = [c for c in candidatos if c.percentual_meta <= minimo + 0.10]

        return random.choice(elegiveis).usuario_id
```

---

## 5. Exemplos Numéricos

### Exemplo 1 — Equipe equilibrada, ninguém acima de 90%

| Membro | Demandas respondidas | pᵢ (meta=12) |
|---|---|---|
| Ana | 4 | 33% |
| Bruno | 5 | 42% |
| Carla | 6 | 50% |

**Modo B** (nem todos ≥ 90%)  
mín = 33%, limite = 43%  
**Elegíveis: Ana (33%) e Bruno (42%)**  
Carla (50%) fica fora — está 17 p.p. acima do mínimo.

---

### Exemplo 2 — Equipe adiantada, todos acima de 90%

| Membro | Demandas respondidas | pᵢ (meta=12) |
|---|---|---|
| Ana | 11 | 92% |
| Bruno | 12 | 100% |
| Carla | 13 | 108% |

**Modo A** (todos ≥ 90%)  
média = (92 + 100 + 108) / 3 = 100%  
**Elegíveis: Ana (92%)** — abaixo da média  
Bruno e Carla ficam de fora até Ana alcançar a média.

---

### Exemplo 3 — Empate geral acima de 90%

| Membro | pᵢ |
|---|---|
| Ana | 100% |
| Bruno | 100% |
| Carla | 100% |

**Modo A** — média = 100%, ninguém abaixo da média → `E = C`  
Sorteio uniforme entre todos os três.

---

## 6. Propriedades do Algoritmo

| Propriedade | Descrição |
|---|---|
| **Fairness** | Membros com menor percentual de meta têm prioridade garantida por construção |
| **Aleatoriedade** | Dentro dos elegíveis, a seleção é uniformemente aleatória — sem favorecimento |
| **Tolerância** | A janela de 10 p.p. (Modo B) evita que um único atraso monopolize todas as demandas |
| **Determinismo do conjunto** | O conjunto elegível é determinístico dado o estado atual — apenas o sorteio é aleatório |
| **Composabilidade** | O serviço recebe candidatos prontos — não consulta repositórios diretamente |

---

## 7. Separação de Responsabilidades

O `SorteioJustoService` recebe **apenas** uma lista de `CandidatoSorteio`. Ele não sabe:

- Quem está afastado (responsabilidade do `AtribuirRelatorUseCase`)
- Quantas demandas cada membro respondeu (responsabilidade do `DemandaRepository`)
- Qual é a meta mensal (responsabilidade da configuração injetada no use case)

Essa separação é fundamental para testabilidade: o serviço pode ser testado com listas simples, sem banco de dados ou configuração de contexto.

```python
# Teste direto do algoritmo — puro Python, sem dependências
def test_todos_acima_90_sorteia_abaixo_da_media():
    servico = SorteioJustoService()
    candidatos = [
        CandidatoSorteio(usuario_id=1, percentual_meta=0.90),
        CandidatoSorteio(usuario_id=2, percentual_meta=1.00),
    ]
    for _ in range(20):
        assert servico.selecionar(candidatos) == 1  # Ana sempre escolhida
```

---

## 8. Referência ao Sistema Original

Este algoritmo é fiel à implementação original do `atribuir_demanda()` em `demandas/models.py` do CALLISTA 1.x, que operou em produção no Senado Federal. As diferenças são apenas de estrutura:

| CALLISTA 1.x | CALLISTA (este projeto) |
|---|---|
| Método de instância em `CadastroDemanda` | Serviço de domínio isolado `SorteioJustoService` |
| Acessa banco de dados diretamente | Recebe dados já calculados como parâmetro |
| Sem testes automatizados | 7 testes unitários cobrindo todos os cenários |
| Acoplado ao Django ORM | Zero dependências externas |
