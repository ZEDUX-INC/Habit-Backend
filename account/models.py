import random
from typing import Sequence, Tuple, Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

from django.core import signing


class CustomUser(AbstractUser):

    id = models.AutoField(primary_key=True)

    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists'),
        }
    )

    dob = models.DateField(verbose_name='Date of Birth', null=True, blank=True)
    bio = models.TextField(default='', null=True, blank=True)
    profile_picture = models.FileField(
        upload_to='media/profile/', null=True, blank=True)
    cover = models.FileField(upload_to='media/profile/',
                             verbose_name='Profile Cover Photo', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    reset_token = models.CharField(max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    class Meta(AbstractUser.Meta):
        abstract = False

    def generate_resettoken(self) -> Tuple[int, str]:
        unsigned_token = random.randint(100000, 999999)
        signer = signing.TimestampSigner()
        signed_token = signer.sign_object(  # type:ignore
            {'token': unsigned_token, 'email': self.email})
        return unsigned_token, signed_token

    def add_followers(self, followers: Sequence[Any]) -> None:
        for follower in followers:
            UserFollowing.objects.create(user=self, following_user=follower)

    def remove_followers(self, followers: Sequence[Any]) -> None:
        UserFollowing.objects.filter(
            user=self, following_user__in=followers).delete()

    def get_followers(self) -> QuerySet:
        return UserFollowing.objects.filter(user=self)


class UserFollowing(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser, related_name='following', on_delete=models.CASCADE)
    following_user = models.ForeignKey(
        CustomUser, related_name='followers', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following_user'], name='unique_followers')
        ]
        ordering = ['-date_created']

    def __str__(self) -> str:
        return f'{self.user.email} follows {self.following_user.email}'
