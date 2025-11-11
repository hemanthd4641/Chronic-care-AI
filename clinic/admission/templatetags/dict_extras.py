from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(dictionary, key):
    """Template filter to lookup a value in a dictionary by key"""
    return dictionary.get(key)

