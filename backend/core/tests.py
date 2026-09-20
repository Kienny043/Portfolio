"""Schema-level guards. No DB access: the tables are unmanaged and live on Aiven."""
from django.test import SimpleTestCase
from rest_framework import serializers as drf

from . import serializers
from .models import Users
from .serializers import FORBIDDEN_FIELDS, SafeModelSerializer


def all_serializers():
    return [
        obj for obj in vars(serializers).values()
        if isinstance(obj, type) and issubclass(obj, drf.ModelSerializer)
        and obj not in (drf.ModelSerializer, SafeModelSerializer)
    ]


class NoPasswordLeakTests(SimpleTestCase):
    def test_every_serializer_is_safe_and_hides_password(self):
        for cls in all_serializers():
            self.assertTrue(issubclass(cls, SafeModelSerializer), cls.__name__)
            names = set(cls().fields)
            self.assertFalse(FORBIDDEN_FIELDS & names, f"{cls.__name__}: {names}")

    def test_no_serializer_targets_users_model(self):
        for cls in all_serializers():
            self.assertNotEqual(cls.Meta.model._meta.db_table, "users", cls.__name__)

    def test_guard_rejects_password(self):
        class Bad(SafeModelSerializer):
            class Meta:
                model = Users
                fields = ["email", "password"]

        with self.assertRaises(AssertionError):
            Bad().fields
