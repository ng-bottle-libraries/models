from unittest import TestCase, main as unittest_main
from mongoengine.errors import NotUniqueError, ValidationError

from namespace_models.User import User
from rfc6749.oauth2_errors import OAuth2Error


class TestUsers(TestCase):
    users = {'email': 'bar@foo.com', 'password': 'sap'}, {'email': 'bar', 'password': 'foo'}

    def test_0_register_failure(self):
        self.assertRaises(OAuth2Error, lambda: User(email=self.users[1]['email']).register())
        self.assertRaises(ValidationError, lambda: User(email=self.users[1]['email'],
                                                        password=self.users[1]['password']).register())

    def test_0_register_success(self):
        self.assertRaises(OAuth2Error, lambda: User(email=self.users[0]['email']).register())
        User(email=self.users[0]['email'], password=self.users[0]['password']).register(force_insert=True)
        self.assertRaises(NotUniqueError, lambda: User(email=self.users[0]['email'],
                                                       password=self.users[0]['password']).register())

    def test_1_login_logout(self):
        def login_failure():
            self.assertFalse(User(email=self.users[0]['email'], password='bad_pass').login())

        def login_success():
            self.assertTrue(User(email=self.users[0]['email'], password=self.users[0]['password']).login())
            self.users[0]['access_token'] = User(email=self.users[0]['email'],
                                                 password=self.users[0]['password']).login()
            self.assertIn('access_token', self.users[0])
            self.assertIn('access_token', self.users[0]['access_token'])
            self.assertIn('expires_in', self.users[0]['access_token'])

        def logout_failure():
            self.assertRaises(OAuth2Error, lambda: User().logout(access_token='ab35k6'))

        def logout_success():
            self.assertRaises(OAuth2Error, lambda: User().logout(access_token=self.users[0]['access_token']))

        login_failure()
        login_success()
        logout_failure()
        logout_success()

    def test_3_fail_unregister(self):
        assert not User(email=self.users[0]['email'], password='bad_pass').unregister()

    @classmethod
    def tearDownClass(cls):
        User(email=cls.users[0]['email'], password=cls.users[0]['password']).unregister()


if __name__ == '__main__':
    unittest_main()
