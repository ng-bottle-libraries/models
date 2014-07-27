from __future__ import print_function
from sys import stderr

from mongoengine import connect, Document
from mongoengine.connection import ConnectionError
from mongoengine.fields import (StringField, ListField, ReferenceField,
                                ImageField, DynamicField, BinaryField,
                                FileField)

try:
    connect('namespace_blobs')
except ConnectionError:
    print("Could not connect to MongoDB", file=stderr)


class UserBlob(Document):
    title = StringField(primary_key=True, unique_with='self.associated_with')
    associated_with = ListField(ReferenceField('User'))
    image = ImageField()
    dyn_payload = DynamicField()
    bin_payload = BinaryField()
    file_payload = FileField()

    def clean(self):
        pass
