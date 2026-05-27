from django import template

register = template.Library()

@register.filter
def split(value, key):
    return value.split(key)

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)