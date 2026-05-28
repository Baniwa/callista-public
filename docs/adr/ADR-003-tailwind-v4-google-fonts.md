# ADR-003 — Google Fonts via `<link>` HTML, não `@import` CSS, com Tailwind v4

| Campo | Valor |
|-------|-------|
| **Status** | Aceito |
| **Data** | 2026-05-28 |
| **Decisores** | Equipe CALLISTA |

## Contexto

A Fase 5 introduziu Tailwind CSS v4 com pipeline PostCSS via `django-tailwind`. A
abordagem comum de carregar fontes Google é via `@import` no início do arquivo CSS:

```css
/* ❌ NÃO FUNCIONA com Tailwind v4 + PostCSS */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&...');
```

Com Tailwind v4, o PostCSS processa o arquivo CSS em um único passo de compilação. O
`@import url(...)` para domínios externos **não é resolvido** — o PostCSS tenta resolver
importações como arquivos locais e falha silenciosamente ou ignora a regra, resultando
em fontes que nunca são carregadas.

Além disso, o bloco `@theme` do Tailwind v4 substitui o `tailwind.config.js` para
definir design tokens. A declaração de fontes no CSS é necessária para os tokens, mas
o carregamento da fonte em si deve acontecer antes do CSS ser aplicado.

## Decisão

Carregar fontes Google **exclusivamente via `<link>` no `<head>` dos templates HTML**,
removendo qualquer `@import` de URL externa do CSS compilado.

```html
<!-- ✅ templates base.html e login.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap">
```

O CSS do projeto continua referenciando as famílias por nome nos design tokens:

```css
/* styles.css — referencia a família, não carrega a fonte */
@theme {
  --font-display: 'Playfair Display', serif;
  --font-sans: 'Inter', sans-serif;
}
```

## Consequências

**Positivas:**

- Fontes carregam corretamente em todos os ambientes (desenvolvimento e produção)
- Separação clara de responsabilidades: HTML gerencia recursos externos, CSS define tokens
- O `rel="preconnect"` melhora a performance de carregamento da fonte
- Pipeline PostCSS não precisa de configuração especial para fontes externas

**Negativas:**

- A declaração da fonte fica em dois lugares (token no CSS, `<link>` no HTML) — pode
  parecer redundante, mas é necessário por limitação do PostCSS
- Templates que herdam de `base.html` recebem as fontes automaticamente, mas templates
  independentes (ex: `login.html`) precisam incluir o `<link>` manualmente

## Alternativas Consideradas

| Alternativa | Por que rejeitada |
|-------------|------------------|
| `@import` no CSS | Não funciona com PostCSS do Tailwind v4 para URLs externas |
| Self-host das fontes (servir do próprio servidor) | Resolve o problema técnico, mas adiciona manutenção de atualização das fontes e peso no repositório |
| Usar fontes do sistema (sem Google Fonts) | Perderia a identidade visual com Playfair Display para o logotipo |

## Referências

- [Tailwind CSS v4 — Using CSS Variables](https://tailwindcss.com/docs/v4-beta)
- [PostCSS `@import` documentation](https://github.com/postcss/postcss-import)
- Discussões na comunidade Django-Tailwind sobre fontes externas com v4
