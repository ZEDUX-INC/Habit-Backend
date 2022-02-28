import pytest
from datetime import timedelta

from UserApp.models import CustomUser
from django.test import TestCase
from django.core import signing


@pytest.mark.django_db
class UserFactory:
    model = CustomUser
    email = 'user@example.com'
    username = 'johndoe'
    password = '111'
    pytestmark = pytest.mark.django_db

    def create(self, **kwargs) -> CustomUser:
        return self.model.objects.create(
            email=self.email,
            username=self.username,
            password=self.password,
            **kwargs
        )


@pytest.mark.django_db
class TestCustomUserModel(TestCase):
    pytestmark = pytest.mark.django_db

    def test_generate_resettoken(self):
        user = UserFactory().create()
        self.assertIsNone(user.reset_token)

        raw_token, token = user.generate_resettoken()

        # assert that the generated token is six digits
        self.assertEqual(len(str(raw_token)), 6)

        signer = signing.TimestampSigner()
        data = signer.unsign_object(token, max_age=timedelta(minutes=10))

        self.assertEqual(data['email'], user.email)
        self.assertEqual(data['token'], raw_token)
