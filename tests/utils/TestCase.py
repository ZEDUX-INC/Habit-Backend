from typing import Any, Sequence
from django.test import TestCase
from rest_framework import serializers


class SerializerTestCase(TestCase):
    """Custom Test Case for Serializers."""

    def check_required_fields(self, serializer: serializers.Serializer,fields:Sequence[str]):
        """
            Check if a list of fields is required in a form.

            :param serializer: form to be checked
            :param fields: list of fields to check
        """
        for field_name, field_instance in serializer().get_fields().items():
            if field_instance.required:
                self.assertIn(field_name, fields)
    
    def check_non_required_fields(self, serializer: serializers.Serializer,fields:Sequence[str]):
        """
            Check if a list of fields is not required in a form.

            :param serializer: form to be checked
            :param fields: list of fields to check
        """
        for field_name, field_instance in serializer().get_fields().items():
            if not field_instance.required:
                self.assertIn(field_name, fields)

    def check_valid_data(self, serializer: serializers.Serializer, entries: Sequence[dict], **kwargs) -> None:
        """
            Test data entries for validity in a form
            :param  entries: data entries to be checked
            :param serializer: Form to check validity on
        """
        for data in entries:
            serial = serializer(data, **kwargs)
            self.assertTrue(serial.is_valid(True))

    def check_invalid_data(self, serializer: serializers.Serializer, entries: Sequence[dict], **kwargs) -> None:
        """
            Test data entries for invalidity in a form
            :param  entries: data entries to be checked
            :param serializer: Form to check invalidity on
        """
        for entry in entries:
            serial = serializer(entries=entry.get('data'), **kwargs)
            self.assertFalse(serial.is_valid(), msg=entries['label'])
            self.assertEqual(serial.errors[entries['error'][0]], entries['error'][1], msg=entries['label'])