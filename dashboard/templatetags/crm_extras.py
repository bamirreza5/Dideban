from django import template


register = template.Library()


@register.filter
def money(value):
    """Format integer amounts with thousands separators."""

    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "۰"


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """Keep current filters while replacing one or more query parameters."""

    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return query.urlencode()
