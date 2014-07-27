from __future__ import print_function
from sys import stderr
from random import randint

from mongoengine import connect, Document
from mongoengine.connection import ConnectionError
from mongoengine.fields import StringField, EmailField
from mongoengine.errors import NotUniqueError

try:
    from flask_scrypt import generate_random_salt, generate_password_hash, check_password_hash
except ImportError:
    print("Warning: Could not get scrypt; falling back.", file=stderr)
    from _fallback_hash_lib import generate_random_salt, generate_password_hash, check_password_hash

from rfc6749.oauth2_errors import OAuth2Error
from rfc6749.Tokens import AccessToken

try:
    connect('namespace_users')
except ConnectionError:
    print("Could not connect to MongoDB", file=stderr)


class User(Document):
    email = EmailField(required=True, primary_key=True)
    password = StringField(required=True)
    _salt = StringField()
    role = StringField(required=False)

    register = (lambda self, force_insert=False, validate=True, clean=True,
                       write_concern=None, cascade=None, cascade_kwargs=None,
                       _refs=None, **kwargs: self.save(force_insert, validate, clean,
                                                       write_concern, cascade, cascade_kwargs,
                                                       _refs, **kwargs))

    def clean(self):
        if self.email:
            self.email = self.email.lower()
        if not self.email or not self.password:
            raise OAuth2Error('invalid_client', 'Invalid email or password.')
        if self.role and self.role not in ('admin', ):
            raise OAuth2Error('invalid_client', 'Invalid role provided.')
        if User.objects(email=self.email).first():
            raise NotUniqueError()
        self._salt = generate_random_salt()
        self.password = generate_password_hash(self.password, self._salt)

    def login(self, email=None, password=None):
        email = email or self.email
        password = str(password or self.password)
        user = User.objects(email=email).first()
        if not user or not check_password_hash(password, user.password, user._salt):
            return False

        tok = AccessToken(user=self).generate()
        return {'access_token': tok.token,
                'expires_in': randint(0, 200)}
        #'expires_in': tok.meta['indexes']['expireAfterSeconds'] - randint(5, 17)}

    def logout(self, access_token=None):
        if AccessToken(user=self).invalidate(access_token=access_token):
            return
        raise OAuth2Error('invalid_client', 'Access token invalid')

    def unregister(self, email=None, password=None):
        self.email = email or self.email
        self.password = str(password or self.password)

        if self.login():
            User.objects(email=self.email).delete()
            return True
        return False

