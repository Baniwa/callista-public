# Apresentação e Motivação

## 1. Contexto

O CALLISTA é um sistema de gestão de demandas de pesquisa legislativa desenvolvido como projeto de portfólio público, com código aberto, inspirado em um sistema homônimo implantado na Assessoria de Pesquisa Legislativa do Senado Federal brasileiro.

O sistema original — aqui chamado de CALLISTA 1.x — foi construído como um monólito Django funcional e operou em produção em ambiente real. O presente projeto reimplementa suas regras de negócio do zero, utilizando **Clean Architecture** e princípios de **Domain-Driven Design (DDD)**, com o objetivo duplo de:

1. Demonstrar como lógica de negócio complexa pode ser modelada independentemente de frameworks;
2. Servir como material de estudo e referência para sistemas de informação no setor público.

!!! info "Sobre os dados"
    Este repositório não contém dados reais do Senado Federal. Todos os dados são fictícios e gerados para fins de demonstração.

---

## 2. O Problema

### 2.1 Fluxo manual e suscetível a erros

Assessorias de pesquisa legislativa recebem demandas de múltiplos órgãos — como a Secretaria-Geral da Mesa (SGM), a imprensa credenciada e solicitações via Lei de Acesso à Informação (LAI). Sem um sistema centralizado, a gestão ocorre por e-mail e planilhas, gerando:

- Perda de rastreabilidade (quem recebeu, quem respondeu, quando)
- Distribuição desigual de trabalho entre os membros da equipe
- Dificuldade em controlar prazos em **dias úteis**, respeitando feriados nacionais e afastamentos individuais
- Ausência de histórico auditável de respostas e revisões

### 2.2 O problema de distribuição justa

Um dos desafios centrais identificados no sistema original é a **atribuição equitativa de demandas**. Em equipes pequenas (5–15 pesquisadores), a distribuição manual tende a favorecer membros mais visíveis ou disponíveis no momento, ignorando quem está mais atrasado em relação à meta mensal.

O CALLISTA resolve esse problema com um **algoritmo de sorteio ponderado pela meta**, detalhado na seção [Algoritmo de Sorteio Justo](../architecture/sorteio-justo.md).

### 2.3 A fragilidade arquitetural do sistema original

O CALLISTA 1.x foi construído seguindo o padrão Django convencional: lógica de negócio em `models.py`, consultas de banco em `views.py`, e regras de validação em `forms.py`. Essa abordagem, embora produtiva no curto prazo, gerou acoplamento que dificultava:

- Testar regras de negócio sem configurar banco de dados
- Substituir componentes (ex.: migrar de SQLite para PostgreSQL)
- Auditar o comportamento do sistema sem entender ORM

---

## 3. Objetivos

| # | Objetivo | Indicador de Alcance |
|---|---|---|
| 1 | Modelar o domínio legislativo de forma testável e independente de framework | 100% dos testes de domínio rodam sem banco de dados |
| 2 | Implementar o algoritmo de distribuição justa de demandas | `SorteioJustoService` com testes de fairness |
| 3 | Demonstrar Clean Architecture aplicada ao setor público | Camadas `domain`, `application`, `adapters` sem violação de dependência |
| 4 | Integrar assistente de IA para pesquisa de fontes oficiais | Adapter Claude API desacoplado do domínio |
| 5 | Rastrear tramitação de Projetos de Lei em tempo real | Adapter API Aberta do Senado Federal |
| 6 | Servir como referência educacional documentada | Wiki técnica com fundamentação arquitetural |

---

## 4. Escopo

### O que o CALLISTA é

- Sistema de gestão do ciclo de vida de demandas de pesquisa legislativa
- Motor de distribuição justa de trabalho baseado em metas mensais
- Plataforma de integração com IA para pesquisa de fontes e geração de rascunhos
- Rastreador de tramitação de Projetos de Lei via API oficial do Senado

### O que o CALLISTA não é

- Um sistema de e-mail ou protocolo oficial
- Uma plataforma de publicação de respostas legislativas
- Um substituto para sistemas de protocolo como o SIGAD ou e-SIC
- Um produto com dados reais — é 100% fictício para fins educacionais

---

## 5. Motivação Acadêmica

Este projeto situa-se na intersecção de três áreas:

**Engenharia de Software Aplicada ao Setor Público**
A literatura identifica desafios recorrentes em sistemas governamentais: alta rotatividade de equipe, mudanças frequentes de requisito por alteração legislativa, obrigações de auditabilidade e restrições de orçamento para manutenção (Pressman & Maxim, 2016). A Clean Architecture endereça diretamente esses pontos ao isolar lógica de negócio de dependências tecnológicas.

**Domain-Driven Design em Domínios Regulados**
O domínio legislativo possui linguagem específica (relator, revisor, prazo, plenário), regras de negócio não-triviais (dias úteis, afastamentos, metas proporcionais) e invariantes que devem ser preservados em qualquer estado do sistema. O DDD (Evans, 2003) provê as ferramentas conceituais para modelar esse domínio com fidelidade.

**Inteligência Artificial como Ferramenta de Suporte Legislativo**
O uso de modelos de linguagem de grande escala (LLMs) para pesquisa de fontes normativas e redação de rascunhos é uma fronteira emergente no setor público. O CALLISTA modela a IA como um **adapter externo** — um detalhe de infraestrutura — preservando a possibilidade de substituição por qualquer outro modelo sem alterar o domínio.

---

## 6. Referências

- MARTIN, Robert C. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall, 2017.
- EVANS, Eric. *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley, 2003.
- FOWLER, Martin. *Patterns of Enterprise Application Architecture*. Addison-Wesley, 2002.
- PRESSMAN, Roger S.; MAXIM, Bruce R. *Engenharia de Software: Uma Abordagem Profissional*. 8. ed. McGraw-Hill, 2016.
- SENADO FEDERAL. *API de Dados Abertos Legislativos*. Disponível em: dados.senado.leg.br.
