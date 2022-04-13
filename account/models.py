import random
from typing import Any, Sequence, Tuple

from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import signing
from django.db import models
from django.db.models import F, Q, QuerySet
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):

    username_validator = UnicodeUsernameValidator()

    id = models.AutoField(primary_key=True, unique=True)
    email = models.EmailField(
        _('email address'),
        blank=False,
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists'),
        }
    )
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        null=True,
        blank=True
    )
    date_of_birth = models.DateField(
        verbose_name='Date of Birth', null=True, blank=True)
    bio = models.TextField(default='', null=True, blank=True)
    profile_picture = models.FileField(
        upload_to='media/profile/', null=True, blank=True)
    cover = models.FileField(upload_to='media/profile/',
                             verbose_name='Profile Cover Photo', null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    reset_token = models.CharField(max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = CustomUserManager()

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
    id = models.AutoField(primary_key=True, unique=True, null=False)
    user = models.ForeignKey(
        CustomUser, related_name='follower', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(
        CustomUser, related_name='following', on_delete=models.CASCADE)
    blocked = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-date_created']
        constraints = [
            models.UniqueConstraint(
                condition=~Q(user=F('followed_user')),
                fields=['user', 'followed_user'], name='unique_followers',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user.email} follows {self.followed_user.email}'

    def save(self, **kwargs) -> None:
        if self.followed_user.id == self.user.id:
            raise IntegrityError('unique_followers')
        return super().save(**kwargs)
