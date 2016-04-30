from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.core import mail
from django.db import models
from django.forms.fields import EmailField, IntegerField
from django.test import TestCase
from django.utils.encoding import force_text
from social.backends import utils

from ksp_login_tests.utils import IDAttributeCounter


class KspLoginTests(TestCase):
    def create_user(self):
        return User.objects.create_user('koniiiik', 'a@b.com', 'secret')

    def login(self):
        return self.client.login(username='koniiiik', password='secret')

    def social_testing_login(self, backend='test1', next=None, follow=True):
        url = '/account/login/%s/' % (backend,)
        if next is not None:
            url = '%s?%s' % (url, next)
        return self.client.get(url, follow=follow)

    def test_backend_order(self):
        """Verify the providers are displayed in correct order.
        """
        # The first three backends appear in the correct order in the
        # login box at the top of the page. Other backends only appear at
        # the bottom.
        response = self.client.get('/')

        match1 = re.search(
            br'<form action="/account/login/facebook/" method="get">',
            response.content,
        )
        match2 = re.search(
            br'<form action="/account/login/google/" method="get">',
            response.content,
        )
        match3 = re.search(
            br'<form action="/account/login/github/" method="get">',
            response.content,
        )
        match4 = re.search(b'More login options', response.content)
        match5 = re.search(
            br'<form action="/account/login/launchpad/" method="get">',
            response.content,
        )

        self.assertIsNotNone(match1)
        self.assertIsNotNone(match2)
        self.assertIsNotNone(match3)
        self.assertIsNotNone(match4)
        self.assertIsNotNone(match5)

        self.assertLess(match1.start(), match2.start())
        self.assertLess(match2.start(), match3.start())
        self.assertLess(match3.start(), match4.start())
        self.assertLess(match4.start(), match5.start())

        with self.settings(AUTHENTICATION_BACKENDS=(
            'ksp_login.backends.LaunchpadAuth',
            'social.backends.google.GoogleOpenId',
            'social.backends.github.GithubOAuth2',
            'social.backends.facebook.FacebookOAuth2',
            'social.backends.open_id.OpenIdAuth',
            'django.contrib.auth.backends.ModelBackend',
        ), AUTHENTICATION_PROVIDERS_BRIEF=2):
            # This time only Launchpad and Google are in the login box and
            # others appear only below.
            response = self.client.get('/')

            match1 = re.search(
                br'<form action="/account/login/launchpad/" method="get">',
                response.content,
            )
            match2 = re.search(
                br'<form action="/account/login/google/" method="get">',
                response.content,
            )
            match3 = re.search(b'More login options', response.content)
            match4 = re.search(
                br'<form action="/account/login/github/" method="get">',
                response.content,
            )
            match5 = re.search(
                br'<form action="/account/login/facebook/" method="get">',
                response.content,
            )

            self.assertIsNotNone(match1)
            self.assertIsNotNone(match2)
            self.assertIsNotNone(match3)
            self.assertIsNotNone(match4)
            self.assertIsNotNone(match5)

            self.assertLess(match1.start(), match2.start())
            self.assertLess(match2.start(), match3.start())
            self.assertLess(match3.start(), match4.start())
            self.assertLess(match4.start(), match5.start())

    def test_testing_backend(self):
        """Verify that the testing backend behaves as it should.

        That means, instead of redirecting to an external
        confirmation/login page, it redirects back to the URL where the
        auth process continues, assuming that the confirmation succeeded.
        Then the process is supposed to continue by redirecting to a login
        page.
        """
        response = self.social_testing_login(follow=False)
        self.assertRedirects(response,
                             'http://testserver/account/complete/test1/',
                             target_status_code=302)
        response = self.client.get('/account/complete/test1/')
        self.assertRedirects(response, '/account/register/')
        response = self.social_testing_login(follow=True)
        self.assertRedirects(response, '/account/register/')

    def test_registration_social(self):
        """Verify the registration process works with the social flow.

        When a user logs in for the first time using an unknown social
        account, she has to fill out the registration form before she is
        let in.
        """
        response = self.social_testing_login()
        # A registration form is displayed to the user.
        self.assertRedirects(response, '/account/register/')
        # The registration form is supposed to be filled in with values
        # retrieved from the auth provider.
        self.assertContains(
            response,
            b'<input id="id_username" maxlength="30" name="username" type="text" value="koniiiik" />',
            html=True,
        )
        self.assertContains(
            response,
            b'<input id="id_first_name" maxlength="30" name="first_name" type="text" value="Colleague" />',
            html=True,
        )
        self.assertContains(
            response,
            b'<input id="id_last_name" maxlength="30" name="last_name" type="text" value="Knuk" />',
            html=True,
        )
        # The type of an EmailInput has changed in 1.6, which means we
        # need to render it manually here. Also, EmailField.max_length
        # changed in 1.8.
        expected = EmailField().widget.render('email', 'b@a.com', {
            'maxlength': models.EmailField().max_length,
            'id': 'id_email'
        })
        self.assertContains(
            response,
            expected.encode('utf-8'),
            html=True,
        )
        # Submit the registration form...
        data = {
            'username': 'koniiiik',
            'email': 'b@a.com',
            'first_name': 'Colleague',
            'last_name': 'Knuk',
        }
        response = self.client.post('/account/register/', data,
                                    follow=True)
        # The redirect chain continues through the social:complete view
        # and lands at the LOGIN_URL destination.
        self.assertIn(tuple(response.redirect_chain),
                      [(('http://testserver/account/complete/test1/', 302),
                        ('http://testserver/account/', 302)),
                       (('/account/complete/test1/', 302),
                        ('/account/', 302))])
        # The resulting page shows the user logged in and with a social
        # association.
        self.assertIn(b'Logged in as', response.content)
        self.assertIn(b'<a href="/account/" class="navbar-link">koniiiik</a>', response.content)
        self.assertIn(b'Testing UID #1', response.content)

    def test_disassociate(self):
        """Verify social account disassociation works as intended.
        """
        user = self.create_user()
        self.login()
        response = self.social_testing_login()

        # There's a single social auth for the current user.
        self.assertContains(response, b'Testing UID #1')
        self.assertEqual(len(user.social_auth.all()), 1)
        auth = user.social_auth.get()
        self.assertEqual(auth.uid, 'Testing UID #1')

        # TODO: test that GET doesn't do anything

        # Disassociate the social auth.
        response = self.client.post('/account/disconnect/test1/%d/' % (auth.id,),
                                    follow=True)
        self.assertRedirects(response, '/account/')
        self.assertNotContains(response, b'Testing UID #1')
        self.assertContains(response, b"don't have any services associated")
        self.assertEqual(len(user.social_auth.all()), 0)

    def test_registration_details_form(self):
        """Verify that forms listed in KSP_LOGIN_PROFILE_FORMS work.
        """
        response = self.social_testing_login()
        # A registration form is displayed to the user.
        self.assertRedirects(response, '/account/register/')
        # The registration form includes additional fields from the
        # UserProfileForm defined in this testing app.
        self.assertContains(
            response,
            b'<input type="text" name="birthday" id="id_birthday" />',
            html=True,
        )
        # The type of an NumberInput has changed in 1.6, which means we
        # need to render it manually here.
        expected = IntegerField().widget.render('shoe_size', None, {'id': 'id_shoe_size'})
        self.assertContains(
            response,
            expected.encode('utf-8'),
            html=True,
        )
        # Submit the registration form...
        data = {
            'username': 'koniiiik',
            'email': 'b@a.com',
            'first_name': 'Colleague',
            'last_name': 'Knuk',
            'birthday': '2014-01-10',
            'shoe_size': 47,
        }
        response = self.client.post('/account/register/', data,
                                    follow=True)
        # The account settings page should also contain the additional
        # form, pre-filled with previously submitted values.
        response = self.client.get('/account/')
        self.assertContains(
            response,
            b'<input type="text" value="2014-01-10" name="birthday" id="id_birthday" />',
            html=True,
        )
        expected = IntegerField().widget.render('shoe_size', 47, {'id': 'id_shoe_size'})
        self.assertContains(
            response,
            expected.encode('utf-8'),
            html=True,
        )

    def test_unique_input_id(self):
        """Verify that we don't get duplicate IDs for input elements.

        On the login page, the same login form is displayed twice -- once
        in the main content and once in the hidden modal form. Ensure the
        IDs don't clash.
        """
        response = self.client.get('/account/login/')

        parser = IDAttributeCounter()
        parser.feed(force_text(response.content))
        for elem_id, count in parser.id_counter.items():
            self.assertEquals(count, 1, "'id' value of '%s' used %d times" % (
                elem_id, count
            ))

    def test_settings_redirect(self):
        user = self.create_user()
        self.login()

        response = self.client.get('/account/settings/')
        self.assertRedirects(response, '/account/', status_code=301)

    def test_password_reset(self):
        """Verify the full password reset workflow.
        """
        user = self.create_user()

        # The index page should contain a link to password reset.
        response = self.client.get('/')
        self.assertContains(
            response,
            '<a href="/account/password-reset/">Forgotten password</a>',
            html=True,
        )

        # The initial password reset page displays an email form.
        response = self.client.get('/account/password-reset/')
        self.assertContains(
            response,
            b'<input id="id_email" maxlength="254" name="email" type="email" />',
            html=True,
        )

        # Submit the email address...
        data = {
            'email': 'a@b.com',
        }
        response = self.client.post('/account/password-reset/', data,
                                    follow=True)
        self.assertRedirects(response, '/account/password-reset/done/')
        # TODO: maybe test the confirmation page, too?
        self.assertEqual(len(mail.outbox), 1)
        pwmail = mail.outbox[0]
        match = re.search(
            r'^(?P<protocol>http(?:s?))://(?P<domain>[^/]*)(?P<uri>.*)$',
            pwmail.body,
            re.MULTILINE,
        )
        self.assertIsNotNone(match)

        pw_reset_uri = match.group('uri')

        # If we modify the token, we get an error page.
        bad_reset_uri = list(pw_reset_uri)
        bad_reset_uri[-3] = 'a' if bad_reset_uri[-3].isdigit() else '0'
        bad_reset_uri = ''.join(bad_reset_uri)
        response = self.client.get(bad_reset_uri)
        self.assertContains(response, 'Password reset unsuccessful')

        # The correct URI displays a form to set a new password.
        response = self.client.get(pw_reset_uri)
        self.assertContains(
            response,
            b'<input id="id_new_password1" name="new_password1" type="password" />',
            html=True,
        )

        # We can now set a new password.
        data = {
            'new_password1': "This one I won't forget!",
            'new_password2': "This one I won't forget!",
        }
        response = self.client.post(pw_reset_uri, data, follow=True)
        self.assertRedirects(response, '/account/reset/done/')
        # TODO: maybe test the confirmation page, too?

        # At last, the password has been changed successfully.
        self.assertFalse(
            self.client.login(username='koniiiik',
                              password='secret'),
        )
        self.assertTrue(
            self.client.login(username='koniiiik',
                              password="This one I won't forget!"),
        )

    def test_password_reset_works_for_active_without_password(self):
        user = self.create_user()
        user.set_unusable_password()
        user.save()

        data = {
            'email': 'a@b.com',
        }
        response = self.client.post('/account/password-reset/', data,
                                    follow=True)
        self.assertRedirects(response, '/account/password-reset/done/')
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_does_not_work_for_inactive(self):
        user = self.create_user()
        user.is_active = False
        user.save()

        data = {
            'email': 'a@b.com',
        }
        response = self.client.post('/account/password-reset/', data,
                                    follow=True)
        self.assertRedirects(response, '/account/password-reset/done/')
        self.assertEqual(len(mail.outbox), 0)
