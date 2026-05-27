# Domínio Legislativo

Esta seção descreve o contexto institucional e as regras do domínio que o CALLISTA modela. Compreender o domínio é pré-requisito para entender as decisões de modelagem do sistema.

---

## 1. O que é uma Assessoria de Pesquisa Legislativa

Casas legislativas brasileiras (Senado Federal, Câmara dos Deputados, Assembleias Estaduais) mantêm assessorias especializadas em pesquisa legislativa. Essas equipes são responsáveis por:

- Responder a demandas de informação de outros órgãos internos
- Produzir notas técnicas e pareceres sobre matérias em tramitação
- Rastrear o andamento de Projetos de Lei de interesse institucional
- Atender solicitações via Lei de Acesso à Informação (LAI)

A equipe é tipicamente composta por pesquisadores com formação jurídica ou em ciências sociais, coordenados por um gestor que distribui e acompanha as demandas.

---

## 2. O Ciclo de Vida de uma Demanda

Uma demanda nasce quando um órgão requisitante (origem) envia uma solicitação de pesquisa. O fluxo típico é:

```
Órgão Requisitante
       │
       │ envia demanda
       ▼
Assessoria recebe e cadastra
       │
       │ atribui relator + revisor (via sorteio justo)
       ▼
Relator elabora resposta
       │
       │ submete resposta
       ▼
Revisor lê e homologa (ou devolve)
       │
       │ revisão aprovada
       ▼
Demanda concluída — resposta enviada ao requisitante
```

Em casos especiais, a demanda pode ser transferida para **pendência externa**, quando a resposta depende de informação de outro órgão (ex.: a própria SGM, em situação de consulta circular).

---

## 3. Origens de Demanda

| Sigla | Órgão | Característica |
|---|---|---|
| **SGM** | Secretaria-Geral da Mesa | Alta prioridade, prazos curtos (3–5 dias úteis) |
| **LAI** | Lei de Acesso à Informação | Prazo legal de 20 dias (prorrogável) |
| **IMP** | Imprensa credenciada | Prazo variável |
| **INT** | Demanda interna | Sem prazo fixo |

Cada origem pode ter um prazo padrão configurado. O prazo é sempre contado em **dias úteis**, excluindo fins de semana e feriados nacionais.

---

## 4. Papéis no Sistema

### Relator
Pesquisador responsável por **elaborar a resposta** a uma demanda. É sorteado automaticamente pelo sistema no momento do cadastro, levando em conta:
- Disponibilidade (não estar afastado)
- Equilíbrio de carga (quem está mais atrás na meta mensal)
- Preferências configuradas por órgão de origem

### Revisor
Pesquisador responsável por **revisar e homologar** a resposta do relator antes de enviá-la ao requisitante. Também é sorteado automaticamente, sempre diferente do relator da mesma demanda.

### Gestor
Administrador da assessoria. Pode:
- Configurar preferências de atribuição por órgão
- Substituir atribuições do sorteio
- Gerir períodos de afastamento
- Acessar relatórios e planos de gestão

---

## 5. Regras de Negócio Centrais

### 5.1 Cálculo de Prazo em Dias Úteis

O prazo de uma demanda é definido em **dias úteis** a partir da data de chegada. O sistema avança dia a dia a partir da `dat_chegada`, contando apenas dias que não sejam:
- Sábado ou domingo
- Feriado nacional cadastrado no sistema

```python
# Exemplo: demanda que chega na sexta-feira com prazo de 1 dia útil
dat_chegada = date(2026, 5, 22)  # sexta
prazo = Prazo(dias_uteis=1)
data_limite = prazo.data_limite(dat_chegada)
# → date(2026, 5, 25) — segunda-feira
```

### 5.2 Regra de Afastamento com Antecipação

Um membro afastado não recebe novas demandas. A regra, replicada do sistema original do Senado, é mais conservadora: um membro é considerado **indisponível** a partir de **2 dias úteis antes** do início formal do afastamento.

Essa antecipação evita que uma demanda longa seja atribuída a alguém que sairá de férias antes de poder concluí-la.

```
Afastamento: 16/06/2026 a 30/06/2026 (segunda a segunda)
Início efetivo para sorteio: 12/06/2026 (quinta) — 2 dias úteis antes
```

### 5.3 Distribuição Proporcional à Meta

A meta mensal individual é calculada **proporcionalmente** ao número de dias trabalhados no mês:

```
meta_proporcional = meta_base × (dias_trabalhados / dias_úteis_no_mês)
```

Se um pesquisador tirou 5 dias de licença em um mês com 20 dias úteis, sua meta individual cai de 12 para 9 demandas. Isso garante que o sorteio compare percentuais relativos, não números absolutos.

---

## 6. Glossário

| Termo | Definição |
|---|---|
| **Demanda** | Solicitação de pesquisa legislativa recebida de um órgão requisitante |
| **Relator** | Pesquisador responsável por elaborar a resposta |
| **Revisor** | Pesquisador responsável por revisar e homologar a resposta |
| **Prazo** | Número de dias úteis para resposta, contado a partir da data de chegada |
| **Feriado** | Data excluída do cômputo de dias úteis |
| **Afastamento** | Período em que um membro está indisponível (férias, licença, treinamento) |
| **Sorteio Justo** | Algoritmo de distribuição de demandas ponderado pela meta mensal |
| **Meta Mensal** | Número de demandas respondidas/revisadas esperado por mês |
| **Plano de Gestão (PG)** | Período de avaliação (anual, subdividido em trimestres) com pontuação por demanda respondida/revisada — gera relatório formal de desempenho da equipe |
| **Troca de demanda** | Redistribuição negociada de uma demanda entre membros, registrada com histórico |
| **SGM** | Secretaria-Geral da Mesa — principal órgão requisitante |
| **LAI** | Lei de Acesso à Informação (Lei nº 12.527/2011) |
| **PL** | Projeto de Lei — matéria legislativa rastreável via API do Senado |
| **Pendência Externa** | Estado em que a demanda aguarda informação de órgão externo |
| **PR** | Status: Pendente de Resposta (estado inicial) |
| **PF** | Status: Pendente de Revisão (relator respondeu) |
| **PE** | Status: Pendente Externa (aguardando informação externa) |
| **C** | Status: Concluída (revisor homologou) |

---

## 7. Analogia com Sistemas Similares

Para leitores de outras áreas, o CALLISTA é análogo a sistemas de **ticketing** (como Jira ou Zendesk), mas com particularidades do setor público:

- Prazos em dias úteis com feriados dinâmicos (ao contrário de SLAs em horas corridas)
- Distribuição automática por sorteio ponderado (ao contrário de fila FIFO ou atribuição manual)
- Ciclo obrigatório de revisão antes do fechamento (quatro olhos)
- Geração de relatórios de desempenho para prestação de contas institucional
