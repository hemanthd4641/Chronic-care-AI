from django import template

register = template.Library()


@register.filter(name='mul')
def multiply(value, arg):
    """Multiply numeric value by arg. Safely handles non-numeric inputs."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return 0



