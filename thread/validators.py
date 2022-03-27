from django.core.exceptions import ValidationError
from django.core.files.base import File
from typing import Union


BYTE_PER_MB = 1048576


def file_size_validator(file: File) -> Union[File, None]:
    """Validate file size."""
    file_size = file.size
    max_file_size = BYTE_PER_MB * 20

    if file_size > max_file_size:
        raise ValidationError('Max Upload File Size Exceed.')

    return file


def file_type_validator(file: File) -> Union[File, None]:
    """Validate File type."""
    return file
