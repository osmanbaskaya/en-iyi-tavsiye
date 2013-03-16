from django import template
import os

register = template.Library()
context = os.path.basename(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

@register.filter
def subtract(value, arg):
    return int(value) - arg

@register.filter
def dthumanize(value):
    import humanize
    return humanize.naturaltime(value)

#@register.simple_tag
#def get_context():
    #return context

register.filter('subtract', subtract)
register.filter('dthumanize',dthumanize)


