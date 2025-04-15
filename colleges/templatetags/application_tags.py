from django import template

register = template.Library()

@register.filter
def filter(queryset, arg):
    key, value = arg.split(':')
    return queryset.filter(**{key: value})