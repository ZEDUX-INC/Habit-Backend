from typing import Dict, Any
from django.db import models
from account.models import CustomUser
from thread.validators import file_size_validator, file_type_validator
from thread import constants as thread_constants
from django.db.utils import IntegrityError

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


class Thread(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.OneToOneField(
        Message, on_delete=models.CASCADE, null=True)
    type = models.CharField(
        max_length=250, choices=thread_constants.THREAD_TYPES, default=thread_constants.POST_THREAD)
    reply_setting = models.CharField(
        max_length=250, choices=thread_constants.THREAD_REPLY_SETTINGS, default=thread_constants.ALLOW_REPLY_FROM_ALL)
    replying = models.ForeignKey(
        'Thread', on_delete=models.CASCADE, null=True, related_name='replies')
    sharing = models.ForeignKey(
        'Thread', on_delete=models.CASCADE, null=True, related_name='shares')
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']
        constraints = [
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_can\'t set sharing field and replying field at the same time',
                check=(
                    models.Q(
                        replying__isnull=True,
                        sharing__isnull=False
                    ) | models.Q(
                        replying__isnull=False,
                        sharing__isnull=True
                    ) | models.Q(
                        replying__isnull=True,
                        sharing__isnull=True
                    )
                )
            ),
            models.CheckConstraint(
                name='%(app_label)s_%(class)s_message field can not be null in reply thread',
                check=(
                    models.Q(
                        replying__isnull=False,
                        message__isnull=False
                    ) | models.Q(
                        replying__isnull=True,
                        message__isnull=False
                    ) | models.Q(
                        replying__isnull=True,
                        message__isnull=True
                    )
                )
            )
        ]

    def __str__(self) -> str:
        return f'thread {self.id} created by {self.created_by.email}'


class Like(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name='likes')
    date_created = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'user {self.created_by.email} liked thread {self.thread.id}'

    def save(self, **kwargs: Dict[Any, Any]) -> None:
        if self.created_by == self.thread.created_by:
            raise IntegrityError('created_by == thread__created_by')
        return super().save(**kwargs)
