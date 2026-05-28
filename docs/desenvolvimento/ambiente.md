# Configuração do Ambiente de Desenvolvimento

## 1. Pré-requisitos

| Ferramenta | Versão mínima | Observação |
|---|---|---|
| Python | 3.11+ | Testado em 3.14 — ver [ADR-002](../adr/ADR-002-django6-python314.md) |
| Node.js | 18+ | Necessário para compilar o Tailwind CSS v4 |
| npm | 9+ | Vem com Node.js |
| Git | 2.x | Qualquer versão recente |
| pip | 23+ | `pip install --upgrade pip` |

O projeto **não requer Docker** para desenvolvimento local. Docker é previsto para deploy (Fase 6).

!!! info "Por que Node.js?"
    A partir da Fase 5, o projeto usa **Tailwind CSS v4** com pipeline PostCSS. O comando
    `python manage.py tailwind build` chama o compilador Node.js internamente via
    `django-tailwind`. Sem Node.js instalado, o CSS não é compilado e a interface não
    carrega estilos. Ver [Fase 5 — Frontend](../fase5/frontend.md) para detalhes.

---

## 2. Clonando o Repositório

```bash
git clone https://github.com/Baniwa/callista-public.git
cd callista-public
```

---

## 3. Ambiente Virtual

É fortemente recomendado usar um ambiente virtual para isolar as dependências:

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

---

## 4. Instalando Dependências

```bash
# Dependências de desenvolvimento (inclui testes e documentação)
pip install -r requirements/development.txt
```

O arquivo `requirements/development.txt` inclui:
- `requirements/base.txt` (Django, DRF, Anthropic SDK, httpx)
- pytest + pytest-django
- factory-boy
- coverage
- mkdocs + mkdocs-material

---

## 5. Variáveis de Ambiente

Copie o arquivo de exemplo e edite com seus valores:

```bash
cp .env.example .env
```

Abra `.env` e configure:

```env
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de dados (padrão: SQLite para desenvolvimento)
DATABASE_URL=sqlite:///db.sqlite3

# Claude API (obrigatório para use cases de IA)
ANTHROPIC_API_KEY=sk-ant-...

# API Senado (não requer autenticação)
SENADO_API_BASE_URL=https://legis.senado.leg.br/dadosabertos
```

!!! warning "Nunca commite o .env"
    O arquivo `.env` está no `.gitignore`. Ele contém credenciais reais e **nunca deve ser versionado**.

---

## 6. Rodando os Testes

Os testes do domínio não requerem banco de dados nem variáveis de ambiente:

```bash
# Todos os testes unitários
python -m pytest tests/unit/ -v

# Apenas o domínio
python -m pytest tests/unit/domain/ -v

# Apenas os use cases
python -m pytest tests/unit/application/ -v

# Com cobertura
python -m pytest tests/unit/ --cov=src --cov-report=term-missing
```

---

## 7. Compilando o CSS (Tailwind)

A partir da Fase 5, os estilos da interface são gerados pelo Tailwind CSS v4 via PostCSS.
É necessário compilar o CSS **antes de rodar o servidor** em desenvolvimento:

```bash
# Compilação única (suficiente para desenvolvimento)
python manage.py tailwind build

# Modo watch — recompila automaticamente ao salvar arquivos CSS
python manage.py tailwind start
```

O arquivo gerado é `theme/static/css/dist/styles.css`. Ele está incluído no repositório
para que o deploy não dependa de Node.js em produção.

!!! warning "npm install na primeira vez"
    Na primeira vez (ou após `git clone`), o Tailwind precisa instalar seus pacotes:
    ```bash
    python manage.py tailwind install
    ```

---

## 8. Rodando a Documentação (Wiki)

```bash
python -m mkdocs serve --dev-addr 127.0.0.1:8001
```

Acesse: [http://127.0.0.1:8001](http://127.0.0.1:8001)

---

## 9. Estrutura de Branches

```
main        ← produção. Nunca altere diretamente.
develop     ← integração. Base de todos os features.
feature/*   ← toda mudança nova parte daqui.
```

Fluxo para contribuir:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/minha-funcionalidade

# ... desenvolva, teste, commite ...

git push origin feature/minha-funcionalidade
# Abra PR: feature/minha-funcionalidade → develop
```

---

## 10. Convenções de Commit

O projeto usa **Conventional Commits** em português, no imperativo:

```
feat: adiciona entidade PL com rastreamento de tramitação
fix: corrige cálculo de prazo em feriados que caem na sexta
test: cobre caso de afastamento com feriado no período
refactor: extrai lógica de elegibilidade para método privado
docs: documenta algoritmo de sorteio justo
chore: atualiza dependências do requirements/base.txt
```

!!! danger "Sem assinatura de IA"
    Commits neste projeto **nunca** incluem `Co-Authored-By: Claude` ou metadados de IA. Os commits devem ser rastreáveis apenas pelo desenvolvedor.
