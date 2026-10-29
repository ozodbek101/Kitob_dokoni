from django import template

register = template.Library()


@register.filter
def som(value):
    """69000 -> '69 000 so‘m'"""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value
    return f"{value:,}".replace(",", "\u00a0") + "\u00a0so‘m"


@register.filter
def initials(text):
    return "".join(w[0] for w in str(text).split()[:2]).upper()


@register.simple_tag(takes_context=True)
def query_with(context, **kwargs):
    """Joriy GET parametrlarini saqlagan holda bittasini almashtiradi."""
    params = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v in (None, ""):
            params.pop(k, None)
        else:
            params[k] = v
    return "?" + params.urlencode() if params else "?"


@register.filter
def get_item(mapping, key):
    return mapping.get(key) if hasattr(mapping, "get") else None


@register.filter
def phone(value):
    """+998901234567 -> '+998 90 123 45 67'"""
    v = str(value)
    if len(v) == 13 and v.startswith("+998"):
        return f"{v[:4]} {v[4:6]} {v[6:9]} {v[9:11]} {v[11:]}"
    return v
