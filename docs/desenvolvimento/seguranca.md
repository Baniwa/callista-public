# Análise de Segurança — CALLISTA

> Revisão realizada em 2026-06-01. Perspectiva: hardening para deploy institucional
> (intranet Senado Federal). Referência: OWASP Top 10, CIS Controls, práticas RedHat.

---

## Falhas Críticas — Corrigidas

### 1. Timing Attack na comparação do código de setor

**Risco:** A comparação direta `codigo != settings.CALLISTA_CODIGO_SETOR` permite que
um atacante meça o tempo de resposta para inferir caracteres corretos do código.

**Onde era:** `src/adapters/views/cadastro.py`

**Correção aplicada:**
```python
import hmac

def _codigo_valido(informado: str) -> bool:
    return hmac.compare_digest(informado.strip(), settings.CALLISTA_CODIGO_SETOR)
```

`hmac.compare_digest` garante tempo constante independente de quantos caracteres coincidem.

---

### 2. Código de setor exposto no repositório público

**Risco:** O valor padrão `SFSEPEL26` estava no `.env.example` — versionado e público.
Qualquer pessoa com acesso ao repositório poderia criar conta no sistema.

**Correção aplicada:** `.env.example` agora contém apenas o placeholder
`defina-um-codigo-secreto-aqui`. O valor real nunca deve entrar no git.

---

### 3. Colisão de username sem fallback seguro

**Risco:** Se `matricula.lower()` já existia como username Django, o código tentava
`email.split("@")[0]` — que também poderia colidir, lançando `IntegrityError` não
tratado (erro 500 exposto ao usuário).

**Correção aplicada:**
```python
def _gerar_username(matricula, email):
    for candidato in [matricula.lower(), email.split("@")[0].lower()]:
        if not User.objects.filter(username=candidato).exists():
            return candidato
    return f"{matricula.lower()}-{uuid.uuid4().hex[:6]}"  # sempre único
```

---

### 4. Usuário desativado no Callista mantinha acesso HTTP

**Risco:** O gestor desativava um pesquisador no Admin (`is_ativo=False` no
`UsuarioModel`), mas a conta Django Auth permanecia válida — o usuário continuava
logando normalmente.

**Correção aplicada:** Substituição de `@login_required` por `@usuario_ativo_required`
em todas as views de aplicação (`src/adapters/views/mixins.py`). Ao detectar
`is_ativo=False`, a view faz logout imediato e redireciona para `/login/`.

Superusuários Django passam sem checagem (acesso administrativo de emergência).

---

### 5. Headers de segurança ausentes em produção

**Risco:** Sem HSTS com subdomínios, sem `X-Frame-Options: DENY`, sem
`X-Content-Type-Options`, o sistema era vulnerável a clickjacking, MIME sniffing
e downgrade de protocolo.

**Correção aplicada em `settings/production.py`:**
```python
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
```

---

## Riscos Residuais — Documentados para Fase 6

### Rate Limiting (médio)

Nem `/login/` nem `/cadastrar/` têm limitação de requisições. Um atacante pode
tentar combinações de senha ou código de setor indefinidamente.

**Solução recomendada:** `django-ratelimit` ou `django-axes` (bloqueia IPs após N
tentativas falhas). Implementar na Fase 6 com deploy.

```python
# Exemplo com django-axes
INSTALLED_APPS += ["axes"]
AUTHENTICATION_BACKENDS = ["axes.backends.AxesStandaloneBackend", ...]
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hora
```

---

### Content Security Policy — CSP (médio)

Não há header `Content-Security-Policy`. Se um XSS for introduzido, scripts
injetados rodam sem restrição.

**Solução recomendada:** `django-csp` com política restritiva:
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_SCRIPT_SRC = ("'self'", "unpkg.com")  # htmx
CSP_IMG_SRC = ("'self'", "data:")
```

---

### Sem auditoria de acesso (médio)

Não há logging de: logins bem-sucedidos, tentativas falhas, criação/exclusão de
demandas, ou ações no Admin. Em ambiente governamental, isso é obrigação legal
(LAI, CGU).

**Solução recomendada:** Configurar `LOGGING` no Django para arquivo + syslog:
```python
LOGGING = {
    "version": 1,
    "handlers": {
        "file": {"class": "logging.FileHandler", "filename": "/var/log/callista/access.log"},
    },
    "loggers": {
        "django.security": {"handlers": ["file"], "level": "INFO"},
        "django.request": {"handlers": ["file"], "level": "WARNING"},
    },
}
```

---

### Ausência de RBAC (baixo — contexto atual)

Todos os usuários autenticados têm o mesmo nível de acesso. Um pesquisador pode
excluir afastamentos de outro membro, ver dados de toda a equipe, etc.

Para a equipe atual (~6 pessoas), isso é aceitável. Para escala ou múltiplos
setores, implementar `django-guardian` ou perfis (`SEPEL-Gestor`, `SEPEL-Pesquisador`).

---

### `SECRET_KEY` com valor default inseguro (baixo)

`settings/base.py` tem `default="django-insecure-dev-key-troque-em-producao"`.
Se o `.env` de produção não definir `SECRET_KEY`, o sistema sobe com essa chave
conhecida — sessions e CSRF ficam comprometidos.

**Solução:** Fazer `SECRET_KEY` obrigatório em produção (sem default):
```python
# settings/production.py
SECRET_KEY = config("SECRET_KEY")  # sem default — falha rápido se não configurado
```

---

## O que o Django já protege automaticamente

| Vetor | Proteção |
|-------|---------|
| SQL Injection | ORM parametrizado — imune por design |
| XSS | Templates auto-escapam `{{ variavel }}` |
| CSRF | `CsrfViewMiddleware` em todos os POSTs |
| Clickjacking | `XFrameOptionsMiddleware` |
| Senhas | `PBKDF2` com salt (Django Auth padrão) |
| Path traversal | `ALLOWED_HOSTS` + `DEBUG=False` em produção |

---

## Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/6.0/topics/security/)
- [CIS Controls v8](https://www.cisecurity.org/controls/v8)
- [ADR-005 — Autenticação](../adr/ADR-005-autenticacao-codigo-setor.md)
- [Migração LDAP/AD](../arquitetura/autenticacao-ldap.md)
