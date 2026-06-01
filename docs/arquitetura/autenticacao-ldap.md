# Migração para Autenticação LDAP/AD — Estudo de Caso para Deploy no Senado Federal

> **Contexto:** Este documento descreve o caminho técnico para substituir o mecanismo
> provisório de código de setor (ver [ADR-005](../adr/ADR-005-autenticacao-codigo-setor.md))
> por autenticação integrada ao Active Directory do Senado Federal, caso o CALLISTA
> seja adotado como sistema oficial.

---

## Como Funciona a Autenticação em Intranets Governamentais

Órgãos do Poder Legislativo federal — Senado, Câmara, Congresso Nacional — operam
intranets baseadas em **Microsoft Active Directory (AD)** integrado ao **LDAP**
(Lightweight Directory Access Protocol).

Na prática, isso significa:

- Cada servidor tem uma **conta única na rede** (login de rede + senha)
- Essa mesma conta dá acesso ao Windows, ao email institucional (@senado.leg.br),
  ao SEI, ao SIGEPE e a todos os sistemas internos
- O servidor **nunca precisa criar uma senha separada** para cada sistema
- A TI do órgão gerencia o ciclo de vida das contas (admissão, afastamento, exoneração)
  em um único lugar

```
Usuário → Login com matrícula + senha da rede
       → Sistema consulta AD/LDAP
       → AD confirma: "é servidor ativo, lotado na SEPEL"
       → Sistema cria sessão autenticada
```

Nenhuma senha é armazenada no banco do CALLISTA. O banco de dados institucional do
Senado é a fonte de verdade de identidade.

---

## O que Muda no CALLISTA

A autenticação LDAP substitui **apenas a camada de autenticação** — a lógica de negócio,
os models de domínio e os repositórios não são afetados. Isso é exatamente o que a
[Clean Architecture](../adr/ADR-001-clean-architecture.md) garante: infraestrutura é
detalhe substituível.

| Componente | Situação atual | Com LDAP |
|---|---|---|
| `UsuarioModel` | Criado no cadastro (`/cadastrar/`) | Criado automaticamente no primeiro login via signal |
| `django.contrib.auth.User` | Criado no cadastro | Criado pelo `django-auth-ldap` no primeiro login |
| Senha | Armazenada no banco (hash bcrypt) | **Nunca armazenada** — autenticada no AD |
| `/cadastrar/` | Único caminho de acesso | Removida (ou restrita a superusuários locais) |
| Django Admin | `is_staff` manual | `is_staff` mapeado de grupo AD (ex: `SEPEL-Gestores`) |

---

## Implementação Passo a Passo

### 1. Instalar o pacote

```bash
pip install django-auth-ldap
```

Adicionar ao `requirements/base.txt`:

```
django-auth-ldap>=4.8
```

### 2. Configurar o backend em `settings/production.py`

```python
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# ── Conexão com o servidor AD do Senado ──────────────────────────────────────
AUTH_LDAP_SERVER_URI = "ldap://ad.senado.leg.br"

# Conta de serviço (read-only) para consultar o AD — nunca use admin
AUTH_LDAP_BIND_DN = "CN=svc-callista,OU=ServiceAccounts,DC=senado,DC=leg,DC=br"
AUTH_LDAP_BIND_PASSWORD = config("LDAP_BIND_PASSWORD")

# ── Onde buscar usuários ──────────────────────────────────────────────────────
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "OU=Servidores,DC=senado,DC=leg,DC=br",
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)",  # login por matrícula
)

# ── Mapeamento de atributos AD → User Django ──────────────────────────────────
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name":  "sn",
    "email":      "mail",
}

# ── Grupos AD → permissões Django ────────────────────────────────────────────
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "OU=Grupos,DC=senado,DC=leg,DC=br",
    ldap.SCOPE_SUBTREE,
    "(objectClass=group)",
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    # Membros do grupo SEPEL-Gestores viram is_staff automaticamente
    "is_staff": "CN=SEPEL-Gestores,OU=Grupos,DC=senado,DC=leg,DC=br",
}

# Atualiza atributos do User a cada login (reflete mudanças no AD)
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# ── Backends de autenticação ──────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django_auth_ldap.backend.LDAPBackend",
    "django.contrib.auth.backends.ModelBackend",  # fallback para superusuários locais
]
```

!!! warning "Conta de serviço"
    A conta `svc-callista` precisa de permissão de leitura no AD. **Nunca use uma conta
    administrativa** como conta de serviço. A senha vai para o `.env` de produção,
    nunca para o repositório.

### 3. Criar o UsuarioModel automaticamente no primeiro login

O `django-auth-ldap` cria o `User` do Django automaticamente. Mas o `UsuarioModel`
do domínio precisa ser criado também. Isso é feito via **signal**:

```python
# src/adapters/django_orm/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from src.adapters.django_orm.models import UsuarioModel


@receiver(post_save, sender=User)
def sincronizar_usuario_callista(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_superuser:
        return  # superusuários locais não viram UsuarioModel

    # Extrai a matrícula do username (padrão AD: sAMAccountName)
    matricula = instance.username.upper()

    UsuarioModel.objects.get_or_create(
        email=instance.email,
        defaults={
            "nome": instance.get_full_name() or instance.username,
            "matricula": matricula,
            "cargo": "",
            "is_ativo": True,
            "is_oculto": False,
        },
    )
```

Registrar o signal no `AppConfig`:

```python
# src/adapters/django_orm/apps.py
from django.apps import AppConfig

class DjangoOrmConfig(AppConfig):
    name = "src.adapters.django_orm"

    def ready(self):
        import src.adapters.django_orm.signals  # noqa: F401
```

### 4. Variáveis de ambiente adicionais (`.env` de produção)

```env
# Conta de serviço LDAP (read-only no AD)
LDAP_BIND_PASSWORD=senha-da-conta-de-servico

# URI do servidor AD (confirmar com TI do Senado)
# AUTH_LDAP_SERVER_URI é definida em settings/production.py
```

### 5. Testar a conexão LDAP antes de ir para produção

```bash
# Verificar conectividade com o servidor AD
python -c "
import ldap
conn = ldap.initialize('ldap://ad.senado.leg.br')
conn.simple_bind_s('CN=svc-callista,...', 'senha')
result = conn.search_s('OU=Servidores,...', ldap.SCOPE_SUBTREE, '(sAMAccountName=12345)')
print(result)
"
```

---

## O que a TI do Senado Precisa Fornecer

Para viabilizar a integração, a equipe de TI do Senado precisa fornecer:

| Informação | Descrição |
|------------|-----------|
| URI do servidor AD | ex: `ldap://ad.senado.leg.br` ou `ldaps://` para TLS |
| Base DN dos servidores | ex: `OU=Servidores,DC=senado,DC=leg,DC=br` |
| Base DN dos grupos | ex: `OU=Grupos,DC=senado,DC=leg,DC=br` |
| Nome do grupo SEPEL | ex: `CN=SEPEL,OU=Grupos,...` |
| Conta de serviço | Login + senha com permissão de leitura no AD |
| Atributo de matrícula | Geralmente `sAMAccountName` ou `employeeID` |

---

## Comparação dos Cenários

| Critério | Código de setor (atual) | LDAP/AD (produção) |
|----------|------------------------|--------------------|
| Infraestrutura necessária | Nenhuma | Servidor AD + conta de serviço |
| Senha armazenada no banco | Sim (hash) | Não |
| Gestão de contas | Manual (Admin) | Automática via AD |
| Single Sign-On | Não | Sim |
| Auditoria TCU/CGU | Parcial | Completa |
| Adequado para portfólio | ✅ | — |
| Adequado para produção real | ⚠️ provisório | ✅ |

---

## Referências

- [ADR-005 — Código de Setor (decisão atual)](../adr/ADR-005-autenticacao-codigo-setor.md)
- [ADR-001 — Clean Architecture](../adr/ADR-001-clean-architecture.md)
- [django-auth-ldap — Documentação oficial](https://django-auth-ldap.readthedocs.io/)
- [Microsoft: Understanding LDAP](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc961766(v=technet.10))
- [Senado Federal — Portal de Dados Abertos](https://dados.senado.leg.br/)
- [GOV.BR — Para sistemas com acesso externo](https://www.gov.br/governodigital/pt-br/acesso-governo/login-govbr)
