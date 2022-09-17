from rest_framework.status import *

from account.api.v1.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    RPEmailSerializer,
    RPPasswordSerializer,
    RPTokenSerializer,
    UserSerializer,
)
from account.models import CustomUser
from tests.utils.TestCase import SerializerTestCase
from tests.v1.account.test_models import UserFactory, UserFollowingFactory


class TestUserSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.serializer = UserSerializer

    def test_create(self) -> None:
        data = {
            "username": "Joseph",
            "email": "john@example.com",
            "password": "12345678",
        }

        form = self.serializer(data=data)

        form.is_valid(raise_exception=True)
        user = form.save()

        self.assertIsNotNone(form.token)
        self.assertEqual(CustomUser.objects.get(email=data["email"]), user)

    def test_to_representation(self) -> None:
        serializer = self.serializer(instance=self.user)
        data = serializer.to_representation(instance=self.user)
        self.assertIsNone(data.get("auth_token"))

        serializer = self.serializer(
            data={"email": "john@example.com", "password": "12345678"}
        )
        serializer.is_valid()
        new_user = serializer.save()
        data = serializer.to_representation(instance=new_user)
        self.assertIsNotNone(data.get("auth_token"))


class TestRPEmailSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.required_fields = ["email"]
        self.non_required_fields = []
        self.serializer = RPEmailSerializer

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(self.serializer, self.non_required_fields)


class TestRPTokenSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.required_fields = ["email", "token"]
        self.non_required_fields = []
        self.serializer = RPTokenSerializer

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(self.serializer, self.non_required_fields)


class TestRPPasswordSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.required_fields = ["email", "token", "password"]
        self.non_required_fields = []
        self.serializer = RPPasswordSerializer

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(self.serializer, self.non_required_fields)


class TestFollowingSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.follower_user = UserFactory.create(email="user2@gmail.com")
        self.serializer = FollowingSerializer

        self.INVALID_DATA = [
            {
                "data": {"followed_user": self.follower_user.id},
                "errors": {"followed_user": ["User is already being followed."]},
                "label": "invalid follower",
            },
        ]

        self.VALID_DATA = [
            {"followed_user": self.follower_user.id},
        ]

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={"user": self.user}
        )

    def test_invalid_data(self) -> None:
        UserFollowingFactory.create(user=self.user, followed_user=self.follower_user)
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={"user": self.user}
        )

    def test_to_representation(self) -> None:
        serializer = self.serializer(
            data={"followed_user": self.follower_user.id}, context={"user": self.user}
        )
        serializer.is_valid()
        follower_transaction = serializer.save()

        data = {
            "user": UserSerializer(instance=self.follower_user).data,
            "following_since": follower_transaction.date_created,
            "blocked": follower_transaction.blocked,
        }

        self.assertDictEqual(data, serializer.data)


class TestFollowerSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.follower_user = UserFactory.create(email="user2@gmail.com")
        self.serializer = FollowerSerializer

    def test_to_representation(self) -> None:
        follower_transaction = UserFollowingFactory.create(
            user=self.follower_user, followed_user=self.user
        )
        serializer = self.serializer(
            instance=follower_transaction, context={"user": self.user}
        )

        data = {
            "user": UserSerializer(instance=follower_transaction.user).data,
            "following_since": follower_transaction.date_created,
            "blocked": follower_transaction.blocked,
        }

        self.assertDictEqual(
            data, serializer.to_representation(instance=follower_transaction)
        )
