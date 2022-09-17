from typing import Any, Mapping, Sequence

from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from tests.v1.account.test_models import UserFactory


class SerializerTestCase(TestCase):
    """Custom Test Case for Serializers."""

    def check_required_fields(
        self, serializer: serializers.Serializer, fields: Sequence[str]
    ) -> None:

        for field_name, field_instance in serializer().get_fields().items():
            if field_instance.required:
                self.assertIn(field_name, fields)

    def check_non_required_fields(
        self, serializer: serializers.Serializer, fields: Sequence[str]
    ) -> None:

        for field_name, field_instance in serializer().get_fields().items():
            if not field_instance.required:
                self.assertIn(field_name, fields)

    def check_valid_data(
        self,
        serializer: serializers.Serializer,
        entries: Sequence[Mapping[str, Any]],
        **kwargs: dict[str, Any]
    ) -> None:

        for data in entries:
            serial = serializer(data=data, **kwargs)
            self.assertTrue(serial.is_valid(True))

    def check_invalid_data(
        self,
        serializer: serializers.Serializer,
        entries: Sequence[Mapping[str, Any]],
        **kwargs: dict[str, Any]
    ) -> None:

        for entry in entries:
            serial = serializer(data=entry["data"], **kwargs)
            self.assertFalse(serial.is_valid(), msg=entry.get("label"))
            self.assertDictEqual(serial.errors, entry["errors"])


class ViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + str(token.access_token))
