from __future__ import unicode_literals
import re
from django.test import TestCase
from django.utils.datastructures import SortedDict
from social.backends import utils


class KspLoginTests(TestCase):
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

