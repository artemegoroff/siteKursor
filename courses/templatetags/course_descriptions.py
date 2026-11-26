"""Keep migration placeholders out of public course descriptions."""
from html import unescape

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter
def public_description(value):
    if not value:
        return ''
    text = ' '.join(unescape(strip_tags(str(value))).split()).rstrip('.')
    if text == 'Автоматически создано миграцией':
        return ''
    return value
