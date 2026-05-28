# A interface também é um detalhe

> Post publicado no LinkedIn ao final da Fase 5 — Frontend com Tailwind CSS v4 e HTMX.

---

Shipped the frontend for CALLISTA today.

The domain still doesn't know it exists.

A view Django recebe um `HttpRequest`, chama um repositório, monta um contexto e devolve HTML renderizado. Em nenhum momento ela importa algo de `src/domain/`. Ela consome objetos que o domínio já produziu — e o template apenas os exibe.

Essa é a Regra de Dependência aplicada até a última camada: o HTML é o anel externo. Ele depende de tudo, e nada depende dele.

---

## O que isso significa na prática

A Fase 5 adicionou seis novas views, oito templates, paginação, dark mode e uma página de login com carrossel de fotos do Congresso.

Nenhuma linha dessas adições tocou em `src/domain/` ou `src/application/`.

As views são finas por design. Uma view que fica grande está fazendo trabalho demais — está virando um use case disfarçado de HTTP handler. No CALLISTA, quando isso acontecia, era sinal de que a lógica pertencia a um use case ou a um método de domínio, não à view.

---

## A paleta federal não é opcional

Comecei a Fase 5 com uma decisão que parece estética mas é política: usar a paleta de cores do Manual de Identidade Visual do Governo Federal Brasileiro.

```
Azul Federal:   #1351B4  ← botões, links, ações primárias
Azul Profundo:  #071D41  ← sidebar, cabeçalhos
Fundo:          #F0F4F8  ← background da aplicação
Dourado:        #FFCD07  ← logotipo
```

Sistemas públicos têm uma identidade visual institucional por uma razão: o cidadão precisa reconhecer que está num serviço oficial. Um sistema de pesquisa legislativa que parece um SaaS genérico perde contexto. A paleta federal não é engessamento — é respeito pelo usuário institucional.

---

## A decisão técnica que mais me ensinou

Tentei carregar as fontes Google via `@import` no CSS:

```css
/* ❌ silenciosamente ignorado pelo PostCSS do Tailwind v4 */
@import url('https://fonts.googleapis.com/css2?...');
```

Não funcionou. O PostCSS do Tailwind v4 resolve `@import` como arquivos locais — URLs externas são descartadas sem aviso de erro. Levei alguns minutos para perceber que a fonte Inter que eu via era a do sistema operacional, não a carregada.

A solução é simples, mas o raciocínio importa: **HTML gerencia recursos externos, CSS define tokens**. O `<link>` no `<head>` é o lugar certo para buscar uma fonte da internet. O CSS é o lugar certo para nomear essa fonte como `--font-sans`. São responsabilidades distintas.

```html
<!-- ✅ base.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap">
```

---

## O login como vitrine

A página de login é a única tela que um visitante vê sem autenticar. Decidi que ela deveria comunicar o propósito do sistema imediatamente.

Sete fotos do Congresso Nacional em crossfade lento, desfocadas com `filter: blur(5px)`, servem de fundo. Um card com `backdrop-filter: blur(32px)` flutua sobre elas. O logotipo é um planeta dourado com animação.

Isso não é frescura de design. É curadoria de primeira impressão para um portfólio que vai ser avaliado por recrutadores e avaliadores acadêmicos que julgam em segundos.

Tecnicamente: dois `<div>` sobrepostos com `transition: opacity 2s ease-in-out`, um `preload()` via `new Image()` antes de cada troca, e início aleatório para evitar que todo visitante veja sempre a mesma foto.

---

## Dark mode sem FOUC

O dark mode aplica a classe `html.dark` **antes** de qualquer CSS ser carregado:

```html
<script>
  (function() {
    if (localStorage.getItem('callista-theme') === 'dark') {
      document.documentElement.classList.add('dark');
    }
  })();
</script>
```

Esse bloco vai no `<head>`, antes do `<link>` do Tailwind. Se fosse depois, o browser renderizaria a página em light mode por um frame antes de corrigir — o Flash of Unstyled Content que transforma dark mode numa experiência ruim.

O toggle usa dois ícones absolutamente posicionados com `transition: transform + opacity` controlados por CSS puro. Zero JavaScript trocando elementos — só a classe `html.dark` determinando qual ícone está visível.

---

## Estado do projeto após a Fase 5

| Componente | Status |
|---|---|
| Domínio (entidades, serviços, use cases) | Completo |
| ORM Models + Adapters de repositório | Completo |
| Adapter Gemini (IAPort) | Completo |
| Adapter Senado (SenadoPort) | Completo |
| Frontend — 8 páginas com dark mode | Completo |
| Página de login com carrossel | Completo |
| Paginação com filtros preservados | Completo |
| Testes unitários | 59 passando |

Próxima fase: **Deploy** — Docker, documentação final e README com screenshots.

---

*O frontend é o anel mais externo da cebola. Ele muda a cada sprint de design. O domínio não mudou uma linha desde a Fase 1.*
