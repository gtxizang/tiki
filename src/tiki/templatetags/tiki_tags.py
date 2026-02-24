import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def jsonld_pretty(value):
    """Pretty-print a JSON-LD dict."""
    if isinstance(value, dict):
        return mark_safe(json.dumps(value, indent=2, ensure_ascii=False))
    return value
