from django.db import models
from django.utils import timezone
from account.models import CustomUser
from thread.validators import file_size_validator, file_type_validator
# Create your models here.


class Attachment(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to='media/attachement/',
        validators=[
            file_size_validator,
            file_type_validator
        ]
    )
    type = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'attachement {self.id}-{self.name} added by {self.created_by.email}'


class Message(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    edited = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)

    def __str__(self) -> str:
        return f'message {self.id} sent by {self.created_by.email}'
