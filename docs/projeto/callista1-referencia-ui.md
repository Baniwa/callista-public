# Callista 1.0 — Referência de Interface para a Fase 5

Esta página documenta a interface do sistema original (Callista 1.0, implantado na SEPEL/Senado Federal) como referência de design para a Fase 5 do CALLISTA. As informações foram extraídas da documentação oficial do sistema em produção.

!!! info "Propósito"
    Esta não é uma especificação. É um mapa de referência fiel ao que foi validado em uso real. O frontend do CALLISTA pode divergir em tecnologia (HTMX/Tailwind vs. o sistema original), mas deve preservar a lógica de navegação e os dados exibidos.

---

## 1. Tema e Layout Geral

O sistema original usa **tema escuro** com sidebar lateral fixa. O logo exibe o nome "Callista" acompanhado de um ícone de olho — referência ao caráter investigativo da pesquisa legislativa.

```
┌─────────────────────────────────────────────────────────┐
│  👁 Callista   │              Conteúdo                   │
│                │                                         │
│  DEMANDAS      │  [Dashboard / Tabela / Formulário]      │
│  RELATÓRIOS    │                                         │
│  CADASTRAR     │                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Estrutura do Sidebar

### DEMANDAS
| Item | Descrição |
|------|-----------|
| Minhas demandas | Demandas onde o usuário logado é relator ou revisor |
| Demandas da equipe | Visão geral de todas as demandas ativas |
| Pesquisa de demandas | Busca com filtros (1361 registros em produção) |
| Trocas de demandas | Solicitações de redistribuição entre membros |

### RELATÓRIOS
| Item | Descrição |
|------|-----------|
| Contagem de pontos | Pontuação individual no período atual |
| Desempenho PG | Gráfico/tabela de atingimento de meta por membro |
| Relatório PG | Geração do documento formal do Plano de Gestão |
| Planilha | Exportação em `.xlsx` das demandas do período |

### CADASTRAR
| Item | Descrição |
|------|-----------|
| Demandas | Formulário de nova demanda |
| Preferências | Configuração de atribuição preferencial por órgão |
| Afastamentos | Registro e consulta de períodos de ausência |

---

## 3. Dashboard — KPIs

A tela inicial exibe cards de resumo para o usuário logado:

| KPI | Significado |
|-----|-------------|
| Demandas em Aberto | Total de demandas ativas (não concluídas) |
| Para Responder | Demandas onde o usuário é relator e ainda não respondeu |
| Para Revisar | Demandas onde o usuário é revisor e aguardam revisão |
| Atrasadas | Demandas com prazo vencido |
| Finalizadas Hoje | Demandas concluídas no dia corrente |

---

## 4. Tabela de Demandas

Colunas exibidas na listagem de demandas:

| Coluna | Tipo | Observação |
|--------|------|------------|
| `#` | Número | ID sequencial da demanda |
| `Texto` | String | Descrição resumida da demanda |
| `Órgão` | String | Sigla da origem (SGM, LAI, IMP...) |
| `Chegada` | Data | Data de chegada no formato `DD/MM/AAAA` |
| `Deadline` | Data | Data-limite calculada em dias úteis |
| `Prazo` | Inteiro | Dias restantes — **negativo em vermelho** quando vencido |
| `Relator` | String | Nome do membro responsável pela resposta |
| `Revisor` | String | Nome do membro responsável pela revisão |

**Status labels (texto completo, exibidos como badge):**

| Status | Código interno |
|--------|----------------|
| Pendente de resposta | PR |
| Pendente de revisão | PF |
| Pendente de resposta externa | PE |
| Concluída | C |

---

## 5. Formulário de Cadastro de Demanda

```
Texto da demanda     [_________________________________]
Origem               [Dropdown: SGM / LAI / IMP / ...]
Número na origem     [____]
Data de chegada      [DD/MM/AAAA]

           "Relator, revisor e data para conclusão serão
            definidos automaticamente pelo sistema."
```

O sistema não expõe os campos de atribuição no formulário — reforçando a imutabilidade do sorteio justo para o usuário comum.

---

## 6. Tela de Afastamentos

```
[Formulário: novo afastamento]
  Membro:    [dropdown]
  Início:    [data]
  Fim:       [data]
  Motivo:    [dropdown]

Ativos (3)  |  Futuros (2)  |  Finalizados (15)
[tabela com afastamentos da aba selecionada]
```

Abas com contagem por status. O número de ativos impacta diretamente o sorteio.

---

## 7. Módulo Plano de Gestão (PG)

### Estrutura de períodos

```
Plano de Gestão 2025/2026
└── 01/08/2025 a 31/07/2026
    ├── 1º período  01/08/2025 a 31/10/2025
    ├── 2º período  01/11/2025 a 31/01/2026
    └── 3º período  01/02/2026 a 30/04/2026
```

### Pontuação individual

Cada pesquisador tem uma pontuação acumulada exibida como:

```
8100 de 6645 (121,90%)   ← verde: acima da meta
4200 de 6645 (63,20%)    ← vermelho: abaixo da meta
```

O numerador é a pontuação obtida; o denominador é a meta proporcional ao período trabalhado (descontados afastamentos). O percentual indica o atingimento.

### Exportação

O módulo gera:
- **Relatório PG** — documento `.docx` formal com tabela de desempenho individual
- **Planilha** — arquivo `.xlsx` com detalhamento de demandas do período

---

## 8. Convenções de Usuário

O sistema original usa o formato `primeiro.ultimo` para identificar membros — sem maiúsculas, sem acentos:

```
erika.alves
allan.anjos
rafhael.rezende
vanessa.francisca
leonardo.darosa
bruno.hayashi
```

A exibição no frontend usa o nome formatado (e.g., "Erika Alves"), mas o identificador de sistema segue o padrão.

---

## 9. Escala em Produção

| Métrica | Valor observado |
|---------|-----------------|
| Total de demandas | 1.361 registros |
| Registros por página (pesquisa) | 20 |
| Membros ativos | ~6 pesquisadores |

Esses números orientam decisões de UX: paginação é obrigatória desde o início, e filtros de busca precisam ser rápidos.
