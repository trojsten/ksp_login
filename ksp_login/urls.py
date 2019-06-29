from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from ksp_login import views
from ksp_login.forms import PasswordResetForm

urlpatterns = [
    url(r'^login/$', views.login, name='account_login'),
    url(r'^$', views.settings, name='account_settings'),
    url(r'^logout/$', views.logout, name='account_logout'),
    url(r'^register/$', views.register, name='account_register'),
    url(r'^disconnect/(?P<backend>[^/]+)/(?P<association_id>[^/]+)/$',
        views.disconnect, name='account_disconnect'),
    url(r'^password/$', views.password, name='account_password'),

    url(r'^password-reset/$', auth_views.PasswordResetView.as_view(
        template_name='ksp_login/password_reset_form.html',
        email_template_name='ksp_login/password_reset_email.txt',
        subject_template_name='ksp_login/password_reset_subject.txt',
        form_class=PasswordResetForm, ), name='password_reset'),
    url(r'^password-reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='ksp_login/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='ksp_login/password_reset_confirm.html', ),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='ksp_login/password_reset_complete.html'),
        name='password_reset_complete'),

    url(r'', include('social_django.urls', namespace='social')),
    url(r'^settings/', RedirectView.as_view(pattern_name='account_settings',
                                            permanent=True)),
]
