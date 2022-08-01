from django.db import models
from django.db.models import Q
from account.models import CustomUser
from thread.validators import file_size_validator, file_type_validator
from django.db.utils import IntegrityError, DatabaseError
from typing import Optional, Iterable


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
        return f'Attachement {self.id}-{self.name} added by {self.created_by.email}'


class Like(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    playlist = models.ForeignKey(
        'PlayList', on_delete=models.CASCADE, related_name='likes', null=True)
    comment = models.ForeignKey(
        'Comment', on_delete=models.CASCADE, related_name='likes', null=True)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']
        constraints = [
            models.CheckConstraint(
                name='Like must have either comment or playlist',
                check=Q(
                    Q(playlist__isnull=False, comment__isnull=True) | Q(
                        playlist__isnull=True, comment__isnull=False)
                )
            )
        ]

    def __str__(self) -> str:
        return f'user {self.created_by.email} liked thread {self.playlist.id}'

    def save(
            self,
            force_insert: bool = False,
            force_update: bool = False,
            using: Optional[str] = None,
            update_fields: Optional[Iterable[str]] = None) -> None:

        if self.playlist:
            if self.created_by == self.playlist.created_by:
                raise IntegrityError(
                    'created_by__id and playlist__created_by__id must be unique')
        elif self.comment:
            if self.created_by == self.comment.created_by:
                raise IntegrityError(
                    'created_by__id and comment__created_by__id must be unique')

        return super().save(force_insert, force_update, using, update_fields)


class Comment(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    playlist = models.ForeignKey(
        'PlayList', on_delete=models.CASCADE, related_name='comments')
    replying = models.ForeignKey(
        'Comment', on_delete=models.CASCADE, related_name='replies', null=True)
    content = models.TextField(null=False)
    attachments = models.ManyToManyField(Attachment, blank=True)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']


class PlayListCategory(models.Model):
    title = models.CharField(max_length=120, default='',
                             db_index=True, unique=True, editable=False)
    date_created = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return f'PlayListCategory - {self.title}'


class PlayList(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, default='', db_index=True)
    categories = models.ManyToManyField(PlayListCategory, blank=True)
    cover_image = models.ImageField(null=True)
    songs = models.ManyToManyField(Attachment)
    date_created = models.DateTimeField(auto_now=True)
    active_hours = models.IntegerField(default=24)
    views = models.BigIntegerField(default=0)
    short_description = models.TextField(default='')

    class Meta:
        ordering = ['-date_created']
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'created_by'), name='name must be unqiue')
        ]
