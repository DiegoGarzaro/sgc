from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_query(context):
    """Return existing query parameters excluding the page param."""
    request = context.get("request")
    if not request:
        return ""
    querydict = request.GET.copy()
    querydict.pop("page", None)
    query = querydict.urlencode()
    if query:
        return "&" + query
    return ""
