from django import template

register = template.Library()

@register.filter(name='parsed')
def parsed(value):
    if value % 2 == 0:
        return True
    elif value % 2 != 0:
        return False
