# Referência de Endpoints

> Documentação em construção. Os endpoints serão documentados conforme implementação.

## Demandas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/demandas/` | Lista demandas ativas |
| `POST` | `/demandas/` | Cadastra nova demanda |
| `GET` | `/demandas/{id}/` | Detalhe da demanda |
| `POST` | `/demandas/{id}/atribuir/` | Atribui relator/revisor |
| `POST` | `/demandas/{id}/responder/` | Registra resposta |
| `POST` | `/demandas/{id}/revisar/` | Registra revisão |

## IA

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/ia/fontes/` | Busca fontes oficiais para um texto |
| `POST` | `/ia/resumo/` | Gera resumo de uma demanda |

## PLs

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/pls/` | Busca PLs via API do Senado |
| `GET` | `/pls/{sigla}/{numero}/{ano}/` | Detalhe e tramitação do PL |
