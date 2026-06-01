# Fase 7 — Módulo Relatórios e Plano de Gestão (PG)

> **Status:** Pendente. Esta página documenta o escopo da próxima fase e as perguntas
> de negócio que precisam ser respondidas antes da implementação.

---

## O que é o Plano de Gestão (PG)

O **Plano de Gestão** é o instrumento formal pelo qual a SEPEL acompanha o desempenho
individual dos pesquisadores. Cada pesquisador tem uma **meta de pontos** por período;
as demandas concluídas geram pontos; ao final do período, o gestor emite um relatório
oficial comparando pontuação obtida × meta.

No Callista 1.0 em produção, o módulo exibia:

```
Erika Alves      8100 de 6645 pontos  (121,90%)   ✅ acima da meta
Allan Anjos      4200 de 6645 pontos  ( 63,20%)   ❌ abaixo da meta
```

A meta é **proporcional ao tempo trabalhado** — descontando afastamentos registrados.

---

## Componentes previstos

| Tela | Descrição |
|------|-----------|
| **Contagem de pontos** | Ranking individual no período atual: pontos obtidos, meta proporcional, % atingimento |
| **Desempenho PG** | Histórico de períodos anteriores por pesquisador; gráfico de evolução |
| **Relatório PG** | Exportação do documento formal `.docx` com tabela de desempenho para arquivo institucional |
| **Planilha** | Exportação `.xlsx` de todas as demandas do período com dados de autoria e prazo |

---

## Perguntas de negócio a responder antes de implementar

### Estrutura do Plano de Gestão

1. **Quantos períodos tem um PG?**
   O Callista 1.0 tinha 3 períodos por ano (quadrimestral). Continua assim?
   ```
   PG 2026/2027
   ├── 1º período: ago/2026 – out/2026
   ├── 2º período: nov/2026 – jan/2027
   └── 3º período: fev/2027 – abr/2027
   ```

2. **As datas dos períodos são fixas ou configuráveis pelo gestor?**
   O gestor deve conseguir criar um novo período via Admin?

3. **O PG se aplica a todos os pesquisadores ou apenas aos "ativos no período"?**
   Como tratar alguém que entrou na equipe no meio do período?

---

### Sistema de pontuação

4. **Como é calculada a pontuação de uma demanda?**
   - Valor fixo por demanda (ex: toda demanda = 100 pontos)?
   - Valor proporcional ao prazo (demanda de 2 dias = menos pontos que demanda de 20 dias)?
   - Existe bônus por demanda concluída antes do prazo?
   - Demanda concluída como **relator** vale diferente de **revisor**?

5. **O pontuador é relator, revisor, ou ambos?**
   Se uma demanda tem relator + revisor, cada um ganha pontos?

6. **Demandas canceladas ou pendente externa contam pontos?**

---

### Meta individual

7. **A meta é igual para todos os pesquisadores?**
   Ou varia por cargo/nível?

8. **Como a meta é descontada por afastamento?**
   Fórmula exata:
   ```
   meta_proporcional = meta_total × (dias_úteis_trabalhados / dias_úteis_periodo)
   ```
   Essa fórmula está correta?

9. **Afastamento no meio de um período retroage?**
   Se o pesquisador registra um afastamento do mês passado hoje, a meta é
   recalculada retroativamente?

---

### Exportações

10. **O Relatório PG (`.docx`) tem um template fixo?**
    Existe um modelo Word aprovado pelo Senado que deve ser preenchido?
    Ou o sistema gera o formato livremente?

11. **A Planilha (`.xlsx`) deve ter abas separadas por pesquisador ou uma única tabela?**
    Quais colunas são obrigatórias?

12. **As exportações ficam salvas no servidor ou são geradas sob demanda?**

---

### Dados históricos

13. **Os PGs anteriores devem ser consultáveis?**
    O gestor precisa ver o desempenho de 2024/2025 em 2027?

14. **O que acontece com as demandas de um período fechado?**
    Ficam imutáveis (snapshot) ou continuam editáveis?

---

## Impacto no modelo de dados

Para implementar o módulo, serão necessários novos models:

```python
class PeriodoPGModel(models.Model):
    nome = models.CharField(max_length=100)       # "1º Período 2026/2027"
    dat_inicio = models.DateField()
    dat_fim = models.DateField()
    meta_pontos = models.PositiveIntegerField()   # meta total do período

class PontuacaoPesquisadorModel(models.Model):
    periodo = models.ForeignKey(PeriodoPGModel, ...)
    usuario = models.ForeignKey(UsuarioModel, ...)
    pontos_obtidos = models.PositiveIntegerField(default=0)
    meta_proporcional = models.FloatField()       # calculada com base nos afastamentos
```

Além de um novo campo `pontos` em `DemandaModel` (ou calculado dinamicamente).

---

## Referências

- [Callista 1.0 — Referência de UI](../projeto/callista1-referencia-ui.md): seção 7 — Módulo PG
- [Segurança](../desenvolvimento/seguranca.md): RBAC necessário antes de expor relatórios
- [ADR-004 — Django Admin](../adr/ADR-004-django-admin-gestao.md): gestão de períodos via Admin
