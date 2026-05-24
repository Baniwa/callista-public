# Convenções de Teste

## 1. Filosofia

O CALLISTA segue a **pirâmide de testes** com ênfase na base:

```
        ▲
       /E2E\          ← raros (Fase 5+)
      /──────\
     /Integração\     ← médio volume (Fase 2+)
    /────────────\
   / Unitários    \   ← maioria (agora)
  /────────────────\
```

A camada `src/domain/` é testável **sem banco de dados, sem Django, sem rede**. Isso é uma propriedade arquitetural intencional — não um detalhe de implementação.

---

## 2. Estrutura de Testes

```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_demanda.py        # máquina de estados
│   │   ├── test_prazo.py          # cálculo de dias úteis
│   │   ├── test_usuario.py        # elegibilidade
│   │   ├── test_afastamento.py    # cobre_data() com antecipação
│   │   └── test_sorteio_justo.py  # algoritmo de distribuição
│   └── application/
│       ├── test_atribuir_relator.py   # orquestração do sorteio
│       ├── test_responder_demanda.py  # transição PR → PF
│       └── test_revisar_demanda.py    # transição PF → C
└── integration/                       # (Fase 2 — com banco de dados)
```

---

## 3. Fakes vs Mocks

O projeto usa **fakes** (implementações in-memory simples) ao invés de **mocks** (objetos simulados com verificação de chamadas).

**Por quê?**

Mocks acoplam o teste à implementação interna (verificam *como* o código é chamado, não *o que* ele produz). Fakes testam o comportamento visível — que é o que importa.

```python
# ❌ Mock frágil — testa implementação, não comportamento
mock_repo = MagicMock()
mock_repo.buscar_por_id.return_value = demanda
uc.executar(dto)
mock_repo.salvar.assert_called_once_with(demanda)  # quebra se refatorarmos

# ✅ Fake robusto — testa resultado
class FakeDemandaRepo:
    def __init__(self, demandas):
        self._store = {d.id: d for d in demandas}

    def buscar_por_id(self, id): return self._store.get(id)
    def salvar(self, d): self._store[d.id] = d; return d
    ...

resultado = uc.executar(dto)
assert resultado.status == StatusDemanda.PENDENTE_REVISAO  # testa comportamento
```

---

## 4. Convenções de Nomenclatura

### Funções de teste

```python
# Padrão: test_<o_que_faz>_<condição>_<resultado_esperado>
def test_marcar_respondida_sem_estar_pendente_levanta_erro(): ...
def test_afastamento_antecipa_2_dias_uteis_no_sorteio(): ...
def test_sorteio_exclui_membro_com_percentual_acima_do_limite(): ...
```

### Helpers de fixture

Funções prefixadas com `_` retornam objetos de domínio prontos para uso nos testes:

```python
def _demanda_base() -> Demanda:
    return Demanda(id=1, origem="SGM", ...)

def _usuario(id: int, **kwargs) -> Usuario:
    return Usuario(id=id, nome=f"Usuario {id}", ...)
```

---

## 5. Cobertura Atual

Execute para ver a cobertura detalhada:

```bash
python -m pytest tests/unit/ --cov=src --cov-report=term-missing
```

| Módulo | Cobertura | Status |
|---|---|---|
| `src/domain/entities/` | ~95% | ✅ |
| `src/domain/value_objects/` | 100% | ✅ |
| `src/domain/services/` | 100% | ✅ |
| `src/application/use_cases/` | ~90% | ✅ |
| `src/adapters/` | 0% | ⏳ Fase 2 |
| `src/infrastructure/` | 0% | ⏳ Fase 2 |

**Meta:** ≥ 80% em `domain/` e `application/` — conforme especificado no CLAUDE.md.

---

## 6. Rodando um Teste Específico

```bash
# Um arquivo
python -m pytest tests/unit/domain/test_sorteio_justo.py -v

# Uma função
python -m pytest tests/unit/domain/test_sorteio_justo.py::test_todos_acima_90_sorteia_abaixo_da_media -v

# Por palavra-chave
python -m pytest -k "sorteio" -v

# Com output de print (útil para depuração)
python -m pytest tests/unit/ -v -s
```

---

## 7. Antes de Todo Commit

```bash
# Execute sempre antes de commitar
python -m pytest tests/unit/

# Se qualquer teste falhar → não commite
# Se todos passarem → pode commitar
```

Esse comando deve levar **menos de 1 segundo** — porque nenhum teste de domínio acessa banco ou rede. Se algum teste estiver lento, investigue: provavelmente há um acesso externo indevido.
