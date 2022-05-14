from typing import Mapping, Sequence, Any
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from tests.v1.account.test_models import UserFactory


class SerializerTestCase(TestCase):
    """Custom Test Case for Serializers."""

    def check_required_fields(self, serializer: serializers.Serializer, fields: Sequence[str]) -> None:
        """
            Check if a list of fields is required in a form.

            :param serializer: form to be checked
            :param fields: list of fields to check
        """
        for field_name, field_instance in serializer().get_fields().items():
            if field_instance.required:
                self.assertIn(field_name, fields)

    def check_non_required_fields(self, serializer: serializers.Serializer, fields: Sequence[str]) -> None:
        """
            Check if a list of fields is not required in a form.

            :param serializer: form to be checked
            :param fields: list of fields to check
        """
        for field_name, field_instance in serializer().get_fields().items():
            if not field_instance.required:
                self.assertIn(field_name, fields)

    def check_valid_data(self, serializer: serializers.Serializer, entries: Sequence[Mapping[str, Any]], **kwargs: dict[str, Any]) -> None:
        """
            Test data entries for validity in a form
            :param  entries: data entries to be checked
            :param serializer: Form to check validity on
        """
        for data in entries:
            serial = serializer(data=data, **kwargs)
            self.assertTrue(serial.is_valid(True))

    def check_invalid_data(self, serializer: serializers.Serializer, entries: Sequence[Mapping[str, Any]], **kwargs: dict[str, Any]) -> None:
        """
            Test data entries for invalidity in a form
            :param entries: data entries to be checked
            :param serializer: Form to check invalidity on
        """
        i = 0
        for entry in entries:
            serial = serializer(data=entry['data'], **kwargs)
            self.assertFalse(serial.is_valid(), msg=entry.get('label'))
            self.assertDictEqual(serial.errors, entry['errors'])


class ViewTestCase(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory().create()
        self.client = APIClient()
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))
