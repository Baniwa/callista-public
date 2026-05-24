# ADR-001 — Adoção de Clean Architecture

| Campo | Valor |
|-------|-------|
| **Status** | Aceito |
| **Data** | 2026-05-24 |
| **Decisores** | Equipe CALLISTA |

## Contexto

O CALLISTA 1.x era um monólito Django com lógica de negócio misturada em `models.py` e `views.py`. O algoritmo de sorteio, as regras de prazo e as validações residiam diretamente nos modelos — tornando testes unitários impossíveis sem banco de dados e impedindo a substituição de componentes (ex: trocar provedor de IA).

## Decisão

Adotar **Clean Architecture** (Robert C. Martin, 2017) com separação em quatro camadas concêntricas, com **inversão de dependência** via `Protocol` do Python. Django permanece como detalhe de infraestrutura.

## Consequências

**Positivas:**
- Lógica de domínio testável com `pytest` puro — sem banco, sem Django
- Provedor de IA substituível sem alterar casos de uso
- Auditabilidade clara: cada camada tem responsabilidade única
- Evolução futura para microserviços sem reescrever o domínio

**Negativas:**
- Mais arquivos e indireção inicial
- Curva de aprendizado para desenvolvedores acostumados com "fat models" do Django

## Alternativas Consideradas

| Alternativa | Por que rejeitada |
|-------------|------------------|
| Microserviços imediatos | Overhead desnecessário para equipe pequena (< 10 pessoas) |
| Manter monólito Django puro | Impossibilita testes unitários do domínio e troca de infraestrutura |

## Referências

- Martin, R.C. *Clean Architecture: A Craftsman's Guide* (2017) — ISBN 978-0-13-468599-1
- Evans, E. *Domain-Driven Design* (2003) — ISBN 978-0-321-12521-7
- Fowler, M. "Hexagonal Architecture" — martinfowler.com/bliki/HexagonalArchitecture.html
