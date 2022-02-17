import random
from typing import Tuple
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from django.core import signing

class CustomUser(AbstractUser):
    
    id =  models.AutoField(primary_key=True)
    email = models.EmailField(
        _('email address'), 
        blank=False, 
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists"),
        }
    )

    dob =  models.DateField(verbose_name="Date of Birth", null=True, blank=True)
    bio = models.TextField(default="", null=True, blank=True)
    profile_picture =  models.FileField(upload_to="media/profile/", null=True, blank=True)
    cover = models.FileField(upload_to="media/profile/", verbose_name="Profile Cover Photo", null=True, blank=True)
    location =  models.CharField(max_length=100, null=True, blank=True)
    reset_token =  models.CharField(max_length=150, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta(AbstractUser.Meta):
        abstract = False

    def generate_resettoken(self) -> Tuple[str, str]:
        unsigned_token = random.randint(100000, 999999)
        signer = signing.TimestampSigner()
        signed_token = signer.sign_object({"token": unsigned_token, "email": self.email})
        return unsigned_token, signed_token


