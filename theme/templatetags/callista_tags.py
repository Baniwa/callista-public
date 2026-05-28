from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def querystring_replace(context, **kwargs):
    """Substitui parâmetros na query string atual preservando os demais."""
    request = context.get("request")
    if request is None:
        params = {}
    else:
        params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    qs = params.urlencode()
    return f"?{qs}" if qs else "?"
