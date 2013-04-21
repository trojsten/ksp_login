from django import template


register = template.Library()

@register.simple_tag(takes_context=True)
def ksp_login_next(context):
    request = context['request']
    if 'next' in request.REQUEST:
        next_page = request.REQUEST['next']
    else:
        next_page = request.get_full_path()

    return next_page
