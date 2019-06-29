from django import template
from django.contrib.auth.forms import AuthenticationForm


register = template.Library()

@register.simple_tag(takes_context=True)
def ksp_login_next(context):
    request = context['request']
    if 'next' in context:
        next_page = context['next']
    elif 'next' in request.GET:
        next_page = request.GET['next']
    elif 'next' in request.POST:
        next_page = request.POST['next']
    else:
        next_page = request.get_full_path()

    return next_page


@register.simple_tag(takes_context=True)
def ksp_login_auth_form(context, id_prefix=None):
    if id_prefix:
        return AuthenticationForm(auto_id=id_prefix+'_%s')
    return AuthenticationForm()
