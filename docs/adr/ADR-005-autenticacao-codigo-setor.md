# ADR-005 — Autenticação por Código de Setor (provisório) com caminho documentado para LDAP

| Campo | Valor |
|-------|-------|
| **Status** | Aceito (provisório — ver caminho de evolução) |
| **Data** | 2026-06-01 |
| **Decisores** | Equipe CALLISTA |

## Contexto

O CALLISTA precisa de um mecanismo de cadastro para que novos membros da SEPEL criem
suas próprias contas — sem depender exclusivamente do gestor criar cada usuário manualmente
no Django Admin.

Ao mesmo tempo, o acesso não pode ser aberto: o sistema gerencia informações legislativas
internas e deve ser restrito à equipe autorizada.

O cenário de deploy atual é **desenvolvimento/portfólio**: sem Active Directory corporativo,
sem servidor SMTP configurado, sem infraestrutura de convites por email.

O cenário de deploy futuro, caso o sistema seja adotado pelo Senado Federal, é
**intranet institucional**: Active Directory já existente, autenticação SSO via LDAP.

Esta ADR documenta a decisão provisória e o caminho de evolução.

## Decisão

Implementar autenticação por **código de setor** como mecanismo provisório:

- Um código secreto configurável no `.env` (`CALLISTA_CODIGO_SETOR`, padrão `SFSEPEL26`)
- O gestor distribui o código pessoalmente a cada novo membro
- O membro acessa `/cadastrar/`, preenche seus dados e o código, e cria a própria conta
- O gestor pode revogar o acesso de um usuário via Django Admin (desativar `is_active`)
- O gestor pode trocar o código no `.env` a qualquer momento (não afeta contas já criadas)

O fluxo de cadastro cria simultaneamente:
1. Um `django.contrib.auth.User` — para autenticação HTTP
2. Um `UsuarioModel` — para participação no fluxo de demandas do domínio

## Consequências

**Positivas:**

- Zero dependência de infraestrutura externa (SMTP, AD, OAuth)
- Implementação em horas, não dias
- Adequado para equipes pequenas em ambiente controlado
- O código pode ser rotacionado sem impacto nas contas existentes

**Negativas:**

- O código pode ser compartilhado indevidamente — não há auditoria de quem o usou
- Não escala bem para equipes grandes ou ambientes com alta rotatividade
- Incompatível com requisitos de compliance de auditoria de acesso do TCU/CGU em produção real

## Caminho de Evolução: LDAP/AD

Quando o sistema evoluir para deploy institucional no Senado Federal, o mecanismo de
cadastro por código de setor deve ser **substituído** por autenticação LDAP/AD.

O impacto no código é mínimo:

1. Instalar `django-auth-ldap`
2. Configurar o backend em `settings/production.py`
3. Remover a view `/cadastrar/` (ou mantê-la apenas para superusuários criarem contas locais de emergência)
4. O `UsuarioModel` continua existindo — o sincronismo com o AD é feito via signal `post_save` do `User`

O guia técnico completo está em [Migração para LDAP/AD](../arquitetura/autenticacao-ldap.md).

## Alternativas Consideradas

| Alternativa | Por que rejeitada agora |
|-------------|------------------------|
| LDAP/AD direto | Sem infraestrutura disponível no contexto atual de portfólio |
| Convite por email | Requer SMTP configurado e aumenta complexidade sem benefício proporcional |
| Cadastro aberto (sem código) | Inaceitável — qualquer pessoa criaria conta |
| Apenas Django Admin | O gestor vira gargalo para cada novo membro |

## Referências

- [Guia técnico: Migração para LDAP/AD](../arquitetura/autenticacao-ldap.md)
- [ADR-001 — Clean Architecture](ADR-001-clean-architecture.md): autenticação fica em adapters/infrastructure
- [ADR-004 — Django Admin como painel de gestão](ADR-004-django-admin-gestao.md): gestão de usuários pelo Admin
- [django-auth-ldap documentation](https://django-auth-ldap.readthedocs.io/)
