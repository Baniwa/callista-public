# Máquina de Estados da Demanda

A entidade `Demanda` implementa uma **máquina de estados finita** com transições controladas por métodos explícitos. Nenhum código externo pode alterar o status diretamente — todas as transições passam pela entidade.

---

## 1. Estados

| Estado | Código | Descrição |
|---|---|---|
| **Pendente de Resposta** | `PR` | Estado inicial. Demanda cadastrada, aguarda resposta do relator. |
| **Pendente de Revisão** | `PF` | Relator submeteu resposta. Aguarda revisão do revisor. |
| **Pendente Externa** | `PE` | Demanda aguarda informação de órgão externo. Desvio temporário. |
| **Concluída** | `C` | Revisor homologou. Ciclo encerrado. |

---

## 2. Diagrama de Transições

```
                  ┌───────────────────────────────────────────┐
                  │                                           │
   cadastrar()    │         marcar_respondida()               │
  ─────────────▶  PR  ──────────────────────────▶  PF        │
                  │                                │           │
                  │  registrar_pendencia_externa() │           │
                  ├─────────────────────▶ PE       │           │
                  │                      │         │           │
                  │   resolver_externa() │         │ marcar_   │
                  │ ◀────────────────────┘         │ concluida │
                  │                                ▼           │
                  │                                C  ─────────┘
                  │                           (estado final)
                  │
              (estado inicial)
```

!!! note "Estado PE"
    `PENDENTE_EXTERNA` é um desvio temporário: a demanda retorna para `PR` quando a pendência é resolvida. Essa transição ainda não está implementada no domínio atual (prevista na Fase 2).

---

## 3. Implementação

```python
# src/domain/entities/demanda.py

def marcar_respondida(self) -> None:
    if self.status != StatusDemanda.PENDENTE_RESPOSTA:
        raise ValueError("Demanda não está pendente de resposta")
    self.status = StatusDemanda.PENDENTE_REVISAO

def marcar_concluida(self) -> None:
    if self.status != StatusDemanda.PENDENTE_REVISAO:
        raise ValueError("Demanda não está pendente de revisão")
    self.status = StatusDemanda.CONCLUIDA
```

Cada método de transição:
1. **Valida** o estado atual antes de transitar
2. **Lança `ValueError`** em caso de transição inválida
3. **Muta o estado** apenas se a pré-condição for satisfeita

---

## 4. Transições Válidas e Inválidas

| De | Para | Método | Válida? |
|---|---|---|---|
| `PR` | `PF` | `marcar_respondida()` | ✅ |
| `PF` | `C` | `marcar_concluida()` | ✅ |
| `PR` | `PE` | `registrar_pendencia_externa()` | ✅ (Fase 2) |
| `PE` | `PR` | `resolver_pendencia_externa()` | ✅ (Fase 2) |
| `PF` | `PF` | `marcar_respondida()` | ❌ `ValueError` |
| `PR` | `C` | `marcar_concluida()` | ❌ `ValueError` |
| `C` | qualquer | qualquer | ❌ `ValueError` |

---

## 5. Propriedades Derivadas

Duas propriedades de conveniência evitam verificações repetidas de status no código cliente:

```python
@property
def respondida(self) -> bool:
    return self.status in (StatusDemanda.PENDENTE_REVISAO, StatusDemanda.CONCLUIDA)

@property
def concluida(self) -> bool:
    return self.status == StatusDemanda.CONCLUIDA
```

**Uso nos use cases:**

```python
# ResponderDemandaUseCase — verifica se já respondida antes de aceitar nova resposta
if demanda.respondida:
    raise ValueError("Demanda já possui resposta")

# RevisarDemandaUseCase — usa marcar_concluida() que valida internamente
demanda.marcar_concluida()  # lança ValueError se status != PF
```

---

## 6. Por que Proteger as Transições na Entidade?

A alternativa seria verificar o status nos use cases:

```python
# Abordagem ingênua — frágil
if dto.status == "PR":
    demanda.status = "PF"  # atribuição direta — sem proteção
```

O problema: qualquer código que receba a demanda pode atribuir qualquer status a qualquer momento. Uma validação esquecida num use case futuro corromperia o estado da entidade silenciosamente.

Ao encapsular as transições na própria entidade, a regra de negócio ("você só pode concluir uma demanda que foi respondida") está **no único lugar onde ela deve estar**: a entidade de domínio. Esse princípio é chamado de **Tell, Don't Ask** (Fowler, 2002): você diz à entidade o que fazer, não pergunta seu estado para decidir o que fazer com ela.

---

## 7. Cobertura de Testes

Todos os cenários de transição estão cobertos em `tests/unit/domain/test_demanda.py`:

```
✅ test_demanda_criada_com_status_pendente
✅ test_marcar_respondida_muda_status
✅ test_marcar_concluida_muda_status
✅ test_marcar_respondida_sem_estar_pendente_levanta_erro
✅ test_marcar_concluida_sem_revisao_levanta_erro
```
