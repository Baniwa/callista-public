# Migração do Callista 1.0 → 2.0

Esta seção documenta o processo de análise comparativa entre as duas versões do sistema, as lacunas identificadas e as decisões de implementação para garantir que nenhum dado histórico seja perdido na migração.

---

## 1. Contexto

O Callista 1.0 é um sistema Django monolítico em produção na CEPEL (Senado Federal), desenvolvido de forma incremental ao longo de vários ciclos. O Callista 2.0 (este repositório) foi construído do zero com Clean Architecture, usando o 1.0 como referência de regras de negócio — mas não como referência de schema.

O objetivo desta fase é **preparar o 2.0 para receber todos os dados históricos do 1.0** sem perda de informação.

---

## 2. Metodologia de Análise

O processo de análise seguiu três etapas:

### 2.1 Levantamento do schema do 1.0

Leitura direta dos arquivos `models.py` de cada app Django:

```
D:\Projetos\callista\
├── configuracoes\models.py   → Feriado, MotivoAfastamento, Afastamento
├── demandas\models.py        → OrigemDemanda, CadastroDemanda, RespostaDemanda,
│                               FeedbackDemandas, ArqDemandas, ArqFeedbacks,
│                               HistoricoAtribuicao, TrocaAtribuicao,
│                               Preferencia, PendenciaExterna
├── usuarios\models.py        → UserProfile (extensão do django.auth.User)
└── plano_gestao\models.py    → PlanoGestao, PeriodoPlanoGestao
```

### 2.2 Mapeamento campo a campo

Cada tabela do 1.0 foi comparada com o equivalente no 2.0 (ou a ausência dele), campo por campo, tipo por tipo.

### 2.3 Classificação das lacunas

As lacunas foram classificadas por impacto na migração:

| Prioridade | Critério |
|---|---|
| **Crítico** | Dados seriam perdidos irreversivelmente |
| **Importante** | Funcionalidades do 1.0 não reproduzíveis |
| **Futuro** | Pode ser implementado em fases posteriores |

---

## 3. Comparativo Completo de Schemas

### 3.1 Usuários

| Campo no 1.0 (UserProfile) | Campo no 2.0 (UsuarioModel) | Situação |
|---|---|---|
| `User.first_name` + `User.last_name` | `nome` CharField(200) | Requer concatenação na importação |
| `User.email` | `email` EmailField unique | OK |
| `UserProfile.matricula` IntegerField | `matricula` CharField(20) unique | Tipo diferente — compatível via str() |
| `UserProfile.cargo` CharField(50) | `cargo` CharField(100) | OK |
| `User.is_active` | `is_ativo` BooleanField | OK |
| `UserProfile.is_hidden` | `is_oculto` BooleanField | OK |

**Decisão:** Importar `first_name + " " + last_name` como `nome`. Converter `matricula` para string.

---

### 3.2 Origens das Demandas

| Campo no 1.0 (OrigemDemanda) | Campo no 2.0 | Situação |
|---|---|---|
| `id_origem` AutoField PK | — | Não existe |
| `nom_origem` CharField(255) | `origem` CharField(50) na demanda | **Só o nome, sem tabela própria** |
| `tmp_resposta` DurationField (prazo padrão) | — | **Perdido** |
| `ind_origem` BooleanField (tem número?) | — | **Perdido** |

**Lacuna crítica:** `OrigemDemanda` é uma entidade com comportamento no 1.0 — o prazo padrão é herdado pela demanda se não especificado manualmente. No 2.0, `origem` é apenas uma string.

**Decisão:** Criar `OrigemDemandaModel`. Manter `origem` CharField em `DemandaModel` para compatibilidade retroativa, e adicionar FK opcional `origem_ref`.

---

### 3.3 Demandas

| Campo no 1.0 (CadastroDemanda) | Campo no 2.0 (DemandaModel) | Situação |
|---|---|---|
| `id_demanda` AutoField | `id` BigAutoField | OK |
| `num_origem` IntegerField null | `num_origem` IntegerField null | OK |
| `id_origem` FK → OrigemDemanda | `origem` CharField(50) | **Perde normalização** |
| `des_demanda` TextField | `texto` TextField | OK (renomeado) |
| `dat_chegada` DateField | `dat_chegada` DateField | OK |
| `prazo` DurationField | `dias_prazo` PositiveSmallIntegerField | Requer conversão `.days` |
| `usuario_resposta` FK → User | `relator` FK → UsuarioModel | OK |
| `data_atribuicao_resposta` DateTimeField null | — | **Faltando** |
| `usuario_revisao` FK → User | `revisor` FK → UsuarioModel | OK |
| `data_atribuicao_revisao` DateTimeField null | — | **Faltando** |
| `status` CharField(2) choices | `status` CharField(2) choices | OK (mesmos valores) |
| `id_usuario` FK → User (criador) | — | **Faltando** |
| `dat_cadastro` DateTimeField auto_now_add | `dat_cadastro` DateTimeField auto_now_add | OK |

**Campos faltando:** `data_atribuicao_relator`, `data_atribuicao_revisor`, `criador`.

---

### 3.4 Respostas

| Campo no 1.0 (RespostaDemanda) | Campo no 2.0 (RespostaModel) | Situação |
|---|---|---|
| `id_resposta` AutoField | `id` BigAutoField | OK |
| `des_resposta` TextField | `texto` TextField | OK (renomeado) |
| `id_demanda` **OneToOneField** CASCADE | `demanda` **ForeignKey** CASCADE | 1.0 = 1 resposta por demanda; 2.0 = N |
| `id_usuario` FK → User | `usuario` FK → UsuarioModel | OK |
| `dat_resposta` DateTimeField auto_now_add | `dat_resposta` DateTimeField auto_now_add | OK |
| `editado` BooleanField | `editado` BooleanField | OK |
| `dat_edicao` DateTimeField auto_now | — | **Faltando** |
| `id_usuario_edicao` FK → User null | — | **Faltando** |

---

### 3.5 Revisões (FeedbackDemandas no 1.0)

!!! warning "Lacuna crítica"
    No Callista 1.0, a revisão é uma **entidade separada** (`FeedbackDemandas`), distinta da resposta. No 2.0, o `RevisarDemandaUseCase` salva a revisão como um `RespostaModel` — colapsando as duas em uma única tabela sem distinção.

| Campo no 1.0 (FeedbackDemandas) | Campo no 2.0 | Situação |
|---|---|---|
| `id_feedback` AutoField | — | Colapsado em RespostaModel |
| `des_feedback` TextField | `texto` (RespostaModel) | Indistinguível |
| `id_resposta` OneToOneField → RespostaDemanda | — | **Relação perdida** |
| `id_usuario` FK → User | `usuario` (RespostaModel) | OK |
| `dat_feedback` DateTimeField auto_now_add | `dat_resposta` (RespostaModel) | OK |
| `editado` BooleanField | `editado` (RespostaModel) | OK |
| `dat_edicao` DateTimeField auto_now | — | **Faltando** |
| `id_usuario_edicao` FK → User null | — | **Faltando** |

**Decisão:** Criar `RevisaoModel` e `Revisao` entity separados. Atualizar `RevisarDemandaUseCase` para usar o repositório correto.

---

### 3.6 Histórico de Atribuições

| Campo no 1.0 (HistoricoAtribuicao) | Campo no 2.0 | Situação |
|---|---|---|
| `id_demanda` FK | — | **Não existe** |
| `id_usuario` FK | — | **Não existe** |
| `tipo_atribuicao` CharField ('RES'/'REV') | — | **Não existe** |
| `data_atribuicao` DateTimeField auto_now_add | — | **Não existe** |
| `atribuicao_valida` BooleanField | — | **Não existe** |

**Impacto:** Sem este histórico, não é possível saber quem foi atribuído originalmente a uma demanda quando houve troca posterior.

**Decisão:** Criar `HistoricoAtribuicaoModel`.

---

### 3.7 Pendência Externa

| Campo no 1.0 (PendenciaExterna) | Campo no 2.0 | Situação |
|---|---|---|
| `id_demanda` OneToOneField | — | Status `PE` existe, mas sem dados |
| `justificativa` TextField | — | **Perdido** |
| `data_inicio` DateTimeField auto_now_add | — | **Perdido** |
| `data_fim` DateTimeField null | — | **Perdido** |
| `id_usuario_criacao` FK | — | **Perdido** |

**Decisão:** Criar `PendenciaExternaModel`.

---

### 3.8 Tabelas para Fases Futuras (fora do escopo desta migração)

| Tabela no 1.0 | Motivo do adiamento |
|---|---|
| `TrocaAtribuicao` | Funcionalidade de UI ainda não implementada no 2.0 |
| `Preferencia` (titular/substituto) | Requer mudança no algoritmo de sorteio |
| `ArqDemandas` / `ArqFeedbacks` | Requer suporte a upload de arquivos (Fase 5) |
| `PlanoGestao` / `PeriodoPlanoGestao` | Módulo de gestão separado (fase futura) |
| `MotivoAfastamento` | Normalização menor; CharField mantido por ora |

---

## 4. Decisões de Implementação

### 4.1 Compatibilidade retroativa

Todas as mudanças de schema são **aditivas** — nenhum campo existente é removido ou alterado. Novos campos são `null=True` para não quebrar registros existentes. Isso garante que:

- A migration pode ser aplicada sem downtime
- O seed de dados fictícios continua funcionando
- Os 53 testes unitários permanecem válidos

### 4.2 Origem como FK opcional

`DemandaModel.origem` (CharField) é mantido. Um novo campo `origem_ref` (FK nullable para `OrigemDemandaModel`) é adicionado. Durante a importação, ambos são preenchidos. No futuro, `origem` pode ser deprecado.

### 4.3 Separação Resposta / Revisão

`RespostaModel` continua como está. Uma nova tabela `callista_revisao` é criada com o mesmo schema, mas como entidade própria. O `RevisarDemandaUseCase` é atualizado para usar `RevisaoRepository`.

### 4.4 Histórico de atribuições gerado na importação

O `HistoricoAtribuicaoModel` é criado, e o comando de importação preenche um registro por demanda para cada atribuição existente (`relator` e `revisor`).

---

## 5. Schema Final após a Migração

```
callista_usuario            (existente — sem mudanças)
callista_feriado            (existente — sem mudanças)
callista_afastamento        (existente — sem mudanças)

callista_origem_demanda     ← NOVO
callista_demanda            (atualizado: +criador, +dat_atribuicao_relator,
                                         +dat_atribuicao_revisor, +origem_ref)
callista_resposta           (atualizado: +dat_edicao, +editado_por)
callista_revisao            ← NOVO
callista_historico_atrib    ← NOVO
callista_pendencia_externa  ← NOVO
```

---

## 6. Comando de Importação

**Uso:**

```bash
python manage.py importar_callista1 \
    --db-path D:\Projetos\callista\db.sqlite3 \
    --dry-run        # opcional: simula sem salvar
```

**Ordem de importação** (respeitando FKs):

```
1. OrigemDemanda     → callista_origem_demanda
2. Feriados          → callista_feriado (get_or_create)
3. Usuários          → callista_usuario
4. Afastamentos      → callista_afastamento
5. Demandas          → callista_demanda
6. Respostas         → callista_resposta
7. Revisões          → callista_revisao
8. HistoricoAtrib.   → callista_historico_atrib
9. PendênciaExterna  → callista_pendencia_externa
```

**Tratamento de conflitos:** O comando usa `get_or_create` onde possível e emite warnings para registros com dados inconsistentes (ex.: demanda com status `PF` mas sem resposta).

---

## 7. Verificação pós-migração

Após executar o comando, verificar:

```bash
# Contagem de registros importados
python manage.py shell -c "
from src.adapters.django_orm.models import *
print('Usuarios:', UsuarioModel.objects.count())
print('Demandas:', DemandaModel.objects.count())
print('Respostas:', RespostaModel.objects.count())
print('Revisoes:', RevisaoModel.objects.count())
print('Historico:', HistoricoAtribuicaoModel.objects.count())
"
```

Comparar com contagens diretas no banco SQLite do 1.0.
