from django.core.exceptions import ValidationError
from django.core.files.base import File
from django.test import TestCase

from thread.validators import BYTE_PER_MB, file_size_validator


class FileType:
    size: int = None
    name: str = None


class TestFileSizeValidator(TestCase):
    def test_validation_successful(self):
        f = FileType
        f.size = BYTE_PER_MB * 10  # 10 mb file
        f.name = "attachment.txt"
        file = File(f, f.name)
        exception = None

        try:
            file_size_validator(file)
        except ValidationError as err:
            exception = True

        self.assertIsNone(exception)
        self.assertIsNotNone(file_size_validator(file))

    def test_validation_failed(self):
        f = FileType
        f.size = BYTE_PER_MB * 21  # 21 mb file
        f.name = "attachment.txt"
        file = File(f, f.name)
        exception = None

        try:
            file_size_validator(file)
        except ValidationError as err:
            exception = True

        self.assertIsNotNone(exception)
