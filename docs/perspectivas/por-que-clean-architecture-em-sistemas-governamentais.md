# Por que o domínio de um sistema governamental não pode depender do seu banco de dados?

> Post publicado no LinkedIn. Perspectiva de Engenheiro Principal em infraestrutura pública digital.

---

Nos últimos meses trabalhei na reimplementação de um sistema real de gestão de demandas legislativas — inspirado na plataforma operada pela assessoria de pesquisa do Senado Federal. O código é público, o aprendizado é o projeto.

A decisão arquitetural mais importante que tomei foi a primeira: **o núcleo de negócio não conhece Django, não conhece PostgreSQL, não conhece a AWS. Ele não sabe que existe uma internet.**

Isso se chama Clean Architecture (Robert C. Martin, 2017). Mas deixa eu traduzir para o mundo real de governo digital.

---

## O problema clássico em sistemas públicos

Sistemas governamentais costumam nascer como um script, virar um monolito acoplado ao banco, e ser reescritos do zero a cada mudança de gestão — não por falta de orçamento, mas porque a lógica de negócio está enterrada em queries SQL e models de ORM.

Quando a regra muda ("o prazo agora é em dias corridos"), você não sabe onde mexer. Quando o banco muda (PostgreSQL → Oracle por licitação), você reescreve metade da aplicação.

---

## A solução: dependências apontam para dentro

```
domain/      ← zero dependências externas
application/ ← conhece o domínio, não conhece Django
adapters/    ← traduz HTTP, ORM e APIs externas para a linguagem do domínio
```

O algoritmo de sorteio justo de demandas — que garante distribuição equitativa entre pesquisadores segundo metas mensais — vive em `SorteioJustoService`, um arquivo Python puro. Sem decorators de framework. Sem imports de ORM.

Ele pode ser testado em milissegundos com dados em memória, auditado por qualquer pessoa com conhecimento básico de Python, e substituído sem tocar em uma linha de infraestrutura.

---

## Por que isso importa em escala governamental

Um sistema que vai para produção num órgão federal carrega consigo:

- **Auditabilidade** — obrigação legal perante CGU, TCU e LAI
- **Sem vendor lock-in** em componentes críticos de negócio
- **Testes automatizados** antes de toda implantação
- **Longevidade** — o sistema precisa sobreviver a 3 mandatos, 5 times e 2 migrações de infraestrutura

!!! note "Clean Architecture não é perfeccionismo acadêmico"
    É engenharia de sobrevivência institucional.

---

## O que está no repositório hoje

42 testes unitários. Zero banco de dados. Domínio completo:

| Componente | Descrição |
|---|---|
| `Demanda` | Máquina de estados (PR → PF → C) |
| `Prazo` | Cálculo em dias úteis com feriados |
| `Afastamento` | Regra de antecipação de 2 dias úteis |
| `SorteioJustoService` | Distribuição proporcional por meta mensal |
| `AtribuirRelatorUseCase` | Orquestra sorteio excluindo indisponíveis |
| `ResponderDemandaUseCase` | Transita PR → PF, persiste texto |
| `RevisarDemandaUseCase` | Transita PF → C, persiste texto |

Próxima fase: Django como detalhe de infraestrutura. Claude API como adapter de IA.

---

*Arquitetura limpa não é sobre elegância. É sobre o que acontece quando o sistema precisa mudar — e ele sempre vai precisar.*
