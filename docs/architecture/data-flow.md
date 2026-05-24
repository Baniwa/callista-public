# Fluxo de Dados — Ciclo de uma Demanda

## Do HTTP ao Domínio

```
1. HTTP POST /demandas/
        │
        ▼
2. Django View (adapter)
   └── valida campos HTTP
   └── chama CadastrarDemandaUseCase(dto)
        │
        ▼
3. CadastrarDemandaUseCase (application)
   └── instancia entidade Demanda (domínio)
   └── chama AtribuirRelatorUseCase
   └── chama DemandaRepository.salvar()
        │
        ▼
4. DjangoDemandaRepository (adapter)
   └── persiste via Django ORM
        │
        ▼
5. Banco de Dados
```

## Com Assistente de IA

```
Relator abre a demanda
        │
        ▼
Django View chama BuscarFontesOficiaisUseCase(demanda_id)
        │
        ▼
BuscarFontesOficiaisUseCase
   └── chama IAPort.buscar_fontes(texto)   ← interface (Port)
        │
        ▼
ClaudeAIAdapter (implementa IAPort)
   └── envia prompt para Claude API
   └── retorna lista de FonteOficial
        │
        ▼
View renderiza painel lateral com fontes verificadas
```

## Status da Demanda

```
PENDENTE_RESPOSTA  →  PENDENTE_REVISÃO  →  CONCLUÍDA
      (PR)                  (PF)               (C)
                    ↘
              PENDENTE_EXTERNA
                    (PE)
```
