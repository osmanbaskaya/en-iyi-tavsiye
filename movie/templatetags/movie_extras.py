from django import template
from movie.models import *

register = template.Library()

@register.filter
def subtract(value, arg):
    return int(value) - arg

@register.filter
def dthumanize(value):
    import humanize
    return humanize.naturaltime(value)

register.filter('subtract', subtract)
register.filter('dthumanize',dthumanize)


