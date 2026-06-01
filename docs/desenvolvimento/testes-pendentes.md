# Testes Pendentes

> Estado atual: **59 testes unitários** passando em `tests/unit/` (domínio + casos de uso).
> Cobertura de views e adapters ORM: **zero**.

---

## Testes críticos ausentes

### 1. View de cadastro — `src/adapters/views/cadastro.py`

A view mais sensível do sistema (cria usuários) não tem nenhum teste.

```python
# tests/integration/views/test_cadastro.py

class TestCadastroView:
    def test_cadastro_valido_cria_user_e_usuario_model(self, client):
        """POST com dados válidos + código correto cria User Django e UsuarioModel."""

    def test_codigo_setor_invalido_rejeita(self, client):
        """Código errado retorna erro no campo codigo_setor."""

    def test_email_duplicado_rejeita(self, client, user_existente):
        """E-mail já cadastrado retorna erro no campo email."""

    def test_matricula_duplicada_rejeita(self, client, usuario_model_existente):
        """Matrícula já cadastrada retorna erro."""

    def test_senhas_divergentes_rejeita(self, client):
        """senha != senha2 retorna erro no campo senha2."""

    def test_nome_sem_sobrenome_rejeita(self, client):
        """Nome com uma única palavra é rejeitado."""

    def test_usuario_autenticado_e_redirecionado(self, client, usuario_logado):
        """Usuário já logado vai para o dashboard sem ver o form."""

    def test_timing_attack_codigo_invalido(self, client):
        """Tempo de resposta para código inválido não varia com prefixo correto."""
        # Verifica que hmac.compare_digest está sendo usado (mock ou timing check)

    def test_username_fallback_uuid_quando_colisao(self, client, users_conflitantes):
        """Quando matricula e email já existem como username, gera UUID."""
```

---

### 2. Mixin `usuario_ativo_required` — `src/adapters/views/mixins.py`

```python
# tests/integration/views/test_mixins.py

class TestUsuarioAtivoRequired:
    def test_usuario_ativo_acessa_normalmente(self, client, usuario_ativo):
        """Usuário com is_ativo=True acessa view protegida."""

    def test_usuario_inativo_e_deslogado(self, client, usuario_inativo):
        """Usuário com is_ativo=False é deslogado e redirecionado ao login."""

    def test_superuser_passa_sem_usuario_model(self, client, superuser):
        """Superuser Django acessa sem precisar de UsuarioModel."""

    def test_usuario_sem_usuario_model_e_deslogado(self, client, user_sem_model):
        """User Django sem UsuarioModel correspondente é deslogado."""
```

---

### 3. Repositórios ORM (adapters) — sem nenhum teste de integração

```python
# tests/integration/adapters/test_origem_demanda_repo.py

class TestDjangoOrigemDemandaRepository:
    def test_listar_retorna_apenas_ativos(self, db, origem_inativa):
        """listar() exclui origens com ativo=False."""

    def test_buscar_por_sigla_existente(self, db):
        """buscar_por_sigla('SGM') retorna a origem correta."""

    def test_buscar_por_sigla_inexistente_retorna_none(self, db):
        """buscar_por_sigla('XXX') retorna None sem exceção."""

    def test_buscar_por_sigla_inativa_retorna_none(self, db, origem_inativa):
        """Origem desativada não é retornada por buscar_por_sigla."""


# tests/integration/adapters/test_historico_atribuicao_repo.py

class TestDjangoHistoricoAtribuicaoRepository:
    def test_registrar_cria_historico(self, db, demanda, usuario):
        """registrar() cria HistoricoAtribuicaoModel com os dados corretos."""

    def test_listar_por_demanda_retorna_apenas_da_demanda(self, db):
        """listar_por_demanda() não mistura histórico de demandas diferentes."""
```

---

### 4. Testes unitários de domínio faltando

```python
# tests/unit/domain/test_prazo.py (verificar se está completo)
# Caso ausente:

def test_prazo_negativo_quando_vencido():
    """dias_restantes retorna valor negativo quando data_limite < hoje."""

def test_prazo_zero_no_dia_do_vencimento():
    """dias_restantes == 0 quando data_limite == hoje."""
```

---

## Como rodar os testes existentes

```bash
# Unitários (sem banco)
python -m pytest tests/unit/ -v

# Com cobertura
python -m pytest tests/unit/ --cov=src --cov-report=term-missing

# Quando os de integração forem criados (precisam de banco)
python -m pytest tests/integration/ -v --reuse-db
```

---

## Infraestrutura de testes de integração a criar

Para os testes de view e adapter, será necessário:

```bash
pip install pytest-django factory-boy  # já no requirements/development.txt
```

```python
# tests/conftest.py
import pytest
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def codigo_setor_valido(settings):
    settings.CALLISTA_CODIGO_SETOR = "TESTE-123"
    return "TESTE-123"
```

```ini
# pytest.ini (ou pyproject.toml)
[pytest]
DJANGO_SETTINGS_MODULE = src.infrastructure.settings.development
```

---

## Prioridade de implementação

| Prioridade | Teste | Motivo |
|------------|-------|--------|
| 🔴 Alta | `TestCadastroView` | View mais crítica — cria usuários sem testes |
| 🔴 Alta | `TestUsuarioAtivoRequired` | Segurança — proteção de acesso |
| 🟡 Média | `TestDjangoOrigemDemandaRepository` | Mudou de hardcoded para BD sem testes |
| 🟡 Média | `TestDjangoHistoricoAtribuicaoRepository` | Novo repo sem cobertura |
| 🟢 Baixa | Prazo edge cases | Domínio já bem coberto, completar gaps |

---

## Referências

- [Configuração do Ambiente](ambiente.md): como rodar os testes
- [Segurança](seguranca.md): testes de segurança têm alta prioridade
- [Convenções de Teste](testes.md): padrões do projeto
