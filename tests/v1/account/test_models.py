import pytest
from datetime import timedelta

from account.models import CustomUser, UserFollowing
from django.test import TestCase
from django.core import signing
from django.db.utils import IntegrityError
from django.db import transaction


@pytest.mark.django_db
class UserFactory:
    model = CustomUser
    email = 'user@example.com'
    username = 'johndoe'
    password = '111'
    is_active = True
    pytestmark = pytest.mark.django_db

    def create(self, **kwargs) -> CustomUser:
        options = {
            'email': self.email,
            'username': self.username,
            'password': self.password
        }
        options.update(**kwargs)
        return self.model.objects.create(**options)


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


@pytest.mark.django_db
class TestUserFollowingModel(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.user1 = UserFactory().create()
        self.user2 = UserFactory().create(email='user2@example.com')
        return super().setUp()

    def test_user_following_contstraint(self):
        UserFollowing.objects.create(user=self.user1, followed_user=self.user2)
        UserFollowing.objects.create(user=self.user2, followed_user=self.user1)
        raised_exception = False

        try:
            with transaction.atomic():
                UserFollowing.objects.create(
                    user=self.user1, followed_user=self.user2)
        except IntegrityError:
            raised_exception = True

        self.assertTrue(raised_exception)
        raised_exception = False

        try:
            with transaction.atomic():
                UserFollowing.objects.create(
                    user=self.user2, followed_user=self.user1)
        except IntegrityError:
            raised_exception = True

        self.assertTrue(raised_exception)
        raised_exception = False

        try:
            with transaction.atomic():
                UserFollowing.objects.create(
                    user=self.user1, followed_user=self.user1)
        except IntegrityError:
            raised_exception = True

        self.assertTrue(raised_exception)
        raised_exception = False
