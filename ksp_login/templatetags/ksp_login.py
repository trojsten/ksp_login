from django import template
from django.contrib.auth.forms import AuthenticationForm


register = template.Library()

@register.simple_tag(takes_context=True)
def ksp_login_next(context):
    request = context['request']
    if 'next' in context:
        next_page = context['next']
    elif 'next' in request.REQUEST:
        next_page = request.REQUEST['next']
    else:
        next_page = request.get_full_path()

    return next_page

@register.assignment_tag(takes_context=True)
def ksp_login_auth_form(context):
    return AuthenticationForm
