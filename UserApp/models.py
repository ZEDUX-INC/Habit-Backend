from django.conf import settings
from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.conf import settings


DEFAULT = {
    "email": {
        "verbose_name": _('email address'),
        "unique": True,
        "blank": False,
        "error_messages":{
            'unique': _("A user with that email address already exists."),
        }

    },

    "username": {
        "verbose_name": _('username'),
        "max_length":150,
        "unique":True,
        "help_text":_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        "validators":[UnicodeUsernameValidator()],
        "error_messages":{
            'unique': _("A user with that username already exists."),
        }
    },

    "first_name": {
        "verbose_name": _('first name'),
        "max_length": 50,
        "blank": True,
    },

    "last_name": {
        "verbose_name": _('last name'),
        "max_length": 50,
        "blank": True,
    },

    "is_active": {
        "verbose_name": _('active'),
        "default": False,
        "help_text":_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    },

    "is_staff": {
        "verbose_name": _('staff status'),
        "default": False,
        "help_text":_(
            'Designates whether the user can log into this admin site.'
        )
    },

    "date_joined": {
        "verbose_name": _('date joined'),
        "default": timezone.now
    }
}

class AccountMananger(UserManager):

    def find_by_username(self, username:str):
        queryset = self.get_queryset()
        return queryset.filter(username=username)


def get_fields_data():
    try:
        setting = settings.__getattr__(
            "CUSTOM_USER_CONFIG"
        )
        assert type(setting) == dict
    except (AttributeError, AssertionError) :
        setting = {}
    
    fields = setting.get(
        "fields", {}
    )

    out = DEFAULT.copy()
    out.update(fields)
    return out 


class UserAccount(AbstractUser):

    field_data = get_fields_data()

    username =  models.CharField(**field_data.get("username"))
    first_name =  models.CharField(**field_data.get("first_name"))
    last_name = models.CharField(**field_data.get("last_name"))
    email = models.EmailField(**field_data.get("email"))
    is_active = models.BooleanField(**field_data.get("is_active"))
    is_staff =  models.BooleanField(**field_data.get("is_staff"))
    date_joined =  models.DateTimeField(**field_data.get("date_joined"))

    objects = AccountMananger()


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False



