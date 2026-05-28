# Fase 5 — Frontend: Arquitetura e Decisões

## Visão Geral

A Fase 5 implementou a interface completa do CALLISTA usando **Tailwind CSS v4**, **HTMX**,
**Alpine.js** e **Django Templates**. O objetivo foi criar uma UI profissional com identidade
visual do setor público brasileiro, dark mode e experiência de uso fluida — sem frameworks
JavaScript pesados.

---

## Stack Frontend

| Tecnologia | Versão | Papel |
|-----------|--------|-------|
| Tailwind CSS | v4.3.0 | Framework utilitário CSS, design tokens |
| django-tailwind | 4.4.2 | Integração Django ↔ PostCSS pipeline |
| HTMX | 2.0.4 | Interações sem full-page reload |
| Inter | Google Fonts | Tipografia do corpo |
| Playfair Display | Google Fonts | Logotipo e títulos de destaque |

---

## Paleta de Cores (Identidade Federal)

A paleta segue o Manual de Identidade Visual do Governo Federal Brasileiro:

| Nome | Hex | Uso |
|------|-----|-----|
| Azul Federal | `#1351B4` | Botões, links, ações primárias |
| Azul Profundo | `#071D41` | Sidebar, textos de cabeçalho |
| Azul Claro | `#DBE8FB` | Bordas, divisores, fundos secundários |
| Fundo | `#F0F4F8` | Background da aplicação (light mode) |
| Dourado | `#FFCD07` | Logotipo (planeta), estrelas |

---

## Estrutura de Templates

```
theme/templates/
├── base.html                    ← Layout principal: sidebar + header + conteúdo
├── dashboard.html               ← Pauta do dia: KPIs + tabela de demandas
├── registration/
│   └── login.html               ← Login standalone (não herda base.html)
├── demandas/
│   ├── lista.html               ← Lista geral com filtro por status
│   ├── detalhe.html             ← Detalhe de uma demanda
│   ├── nova.html                ← Formulário centralizado de cadastro
│   ├── minhas_demandas.html     ← Demandas do usuário logado, com abas
│   ├── equipe.html              ← Visão da equipe com paginação
│   └── pesquisa.html            ← Pesquisa avançada com 6 filtros
├── afastamentos/
│   └── lista.html               ← Cadastro e listagem de afastamentos
└── partials/
    ├── sidebar.html             ← Sidebar esquerda com navegação
    ├── tabela_demandas.html     ← Tabela reutilizável de demandas
    └── paginacao.html           ← Paginação reutilizável
```

### Princípio: templates finos

As views Django passam objetos já computados para os templates. **Templates não fazem
lógica de negócio** — apenas renderização condicional e iteração. O cálculo de `dias_restantes`,
nomes de relator/revisor e classificação de urgência é feito na view.

---

## Dark Mode

O dark mode usa uma **classe CSS no elemento raiz** (`html.dark`) combinada com seletores
CSS que sobrescrevem propriedades inline do Tailwind:

```css
/* styles.css */
html.dark .row-hover:hover { background-color: #1A3352 !important; }
html.dark .form-input { background-color: #0D1B2A; color: #e2e8f0; }
```

A preferência é salva em `localStorage` e aplicada **antes da renderização** para evitar
flash (FOUC — Flash of Unstyled Content):

```html
<!-- base.html, dentro do <head>, antes de qualquer CSS -->
<script>
  (function() {
    if (localStorage.getItem('callista-theme') === 'dark') {
      document.documentElement.classList.add('dark');
    }
  })();
</script>
```

### Botão de toggle animado

O botão mostra lua (light mode) ou sol (dark mode) com animação CSS pura — sem JavaScript
trocando ícones. Ambos os ícones estão no DOM, absolutamente posicionados, e a transição
é controlada apenas pela presença da classe `html.dark`:

```css
.icon-theme { position: absolute; inset: 0; transition: transform 0.4s, opacity 0.3s; }
#icon-moon  { transform: rotate(0deg) scale(1); opacity: 1; }
#icon-sun   { transform: rotate(90deg) scale(0.5); opacity: 0; }
html.dark #icon-moon { transform: rotate(-90deg) scale(0.5); opacity: 0; }
html.dark #icon-sun  { transform: rotate(0deg) scale(1); opacity: 1; }
```

---

## Paginação com Query String Preservada

A paginação precisa preservar filtros ativos na URL ao mudar de página
(ex: `/equipe/?status=PR&pagina=2`). Django Templates não manipulam query strings
nativamente, então foi criado um custom template tag:

```python
# theme/templatetags/callista_tags.py
@register.simple_tag(takes_context=True)
def querystring_replace(context, **kwargs):
    params = context.get("request").GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    return f"?{params.urlencode()}"
```

Uso no template:

```html
{% load callista_tags %}
<a href="{% querystring_replace pagina=page_obj.next_page_number %}">Próxima →</a>
```

---

## Página de Login

A página de login é um template **independente** (não herda `base.html`) com:

- **Carrossel de fotos** do Congresso Nacional desfocadas (`congresso1.jpg` a `congresso7.jpg`)
  com crossfade CSS de 2 segundos a cada 60 segundos, início aleatório
- **Starfield SVG** com ~21 estrelas animadas em branco, dourado e azul
- **Glassmorphism card**: `backdrop-filter: blur(32px)`, `background: rgba(5,18,45,0.72)`
- **Logotipo flutuante**: planeta SVG com animação float e glow dourado

### Técnica do carrossel

Dois `<div>` absolutamente posicionados e sobrepostos. O crossfade troca a opacidade de
um para o outro com `transition: opacity 2s ease-in-out`. A próxima foto é pré-carregada
com `new Image()` antes da troca para evitar flash de imagem:

```javascript
async function proximaFoto() {
  await preload(FOTOS[idx]);       // carrega antes de mostrar
  aplicarFoto(proximo, FOTOS[idx]);
  proximo.style.opacity = '1';
  atual.style.opacity   = '0';
}
```

---

## Segurança: `@login_required` em Todas as Views

Todas as views de aplicação foram protegidas com `@login_required`. Sem autenticação,
o usuário é redirecionado para `/login/?next=<url-original>`. Após login, Django redireciona
automaticamente para a URL original via o parâmetro `next`.

O logout redireciona para `/login/` (configurado em `settings/base.py`):

```python
LOGOUT_REDIRECT_URL = "/login/"
```

---

## Vinculação Usuário Django ↔ Entidade de Domínio

O Django Auth (`django.contrib.auth.User`) e a entidade `Usuario` do domínio são modelos
separados. A vinculação é feita por **email**:

```python
# views/demandas.py — Minhas Demandas
meu_usuario = usuario_repo.buscar_por_email(request.user.email)
```

Se o email do usuário autenticado não coincidir com nenhuma entidade `Usuario`, a view
"Minhas Demandas" exibe estado vazio com aviso explicativo. Isso permite que
administradores (superusuários do Django Admin) naveguem na aplicação sem erro.
