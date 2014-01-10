from __future__ import unicode_literals
import re
from django.contrib.auth.models import User
from django.forms.fields import EmailField, IntegerField
from django.test import TestCase
from social.backends import utils


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

        self.assertIsNot(match1, None)
        self.assertIsNot(match2, None)
        self.assertIsNot(match3, None)
        self.assertIsNot(match4, None)
        self.assertIsNot(match5, None)

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

            self.assertIsNot(match1, None)
            self.assertIsNot(match2, None)
            self.assertIsNot(match3, None)
            self.assertIsNot(match4, None)
            self.assertIsNot(match5, None)

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
        self.assertRedirects(response, '/account/complete/test1/',
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
        # need to render it manually here.
        expected = EmailField().widget.render('email', 'b@a.com', {'maxlength': 75, 'id': 'id_email'})
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
        self.assertEqual(response.redirect_chain,
                         [('http://testserver/account/complete/test1/', 302),
                         ('http://testserver/account/', 302)])
        # The resulting page shows the user logged in and with a social
        # association.
        self.assertIn(b'Logged in as', response.content)
        self.assertIn(b'<a href="/account/">koniiiik</a>', response.content)
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
        """Verify that signal-based registration/profile form gathering works.
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
