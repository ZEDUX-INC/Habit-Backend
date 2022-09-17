from datetime import timedelta

import pytest
from django.core import signing
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from factory.django import DjangoModelFactory
from notifications.models import Notification

from account.models import CustomUser, UserFollowing


class UserFactory(DjangoModelFactory):
    email = "user@example.com"
    username = "johndoe"
    password = "111"
    is_active = True

    class Meta:
        model = CustomUser


class NotificationFactory(DjangoModelFactory):
    unread = True
    data = {"message": "This is a notification testcase."}

    class Meta:
        model = Notification


class UserFollowingFactory(DjangoModelFactory):
    class Meta:
        model = UserFollowing


class TestCustomUserModel(TestCase):
    def test_generate_resettoken(self):
        user = UserFactory.create()
        self.assertIsNone(user.reset_token)

        raw_token, token = user.generate_resettoken()

        # assert that the generated token is six digits
        self.assertEqual(len(str(raw_token)), 6)

        signer = signing.TimestampSigner()
        data = signer.unsign_object(token, max_age=timedelta(minutes=10))

        self.assertEqual(data["email"], user.email)
        self.assertEqual(data["token"], raw_token)


class TestUserFollowingModel(TestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory.create()
        self.user2 = UserFactory.create(email="user2@example.com")
        return super().setUp()

    def test_user_following_contstraint(self):
        UserFollowingFactory.create(user=self.user1, followed_user=self.user2)
        UserFollowingFactory.create(user=self.user2, followed_user=self.user1)

        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                UserFollowingFactory.create,
                user=self.user1,
                followed_user=self.user2,
            )

        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                UserFollowingFactory.create,
                user=self.user2,
                followed_user=self.user1,
            )

        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                UserFollowingFactory.create,
                user=self.user1,
                followed_user=self.user1,
            )
