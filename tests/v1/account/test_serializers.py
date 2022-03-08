import email
import pytest

from rest_framework.status import *
from account.models import CustomUser
from tests.v1.account.test_models import UserFactory
from tests.utils.TestCase import SerializerTestCase

from account.api.v1.serializers import (
    RPEmailSerializer,
    UserFollowerSerializer,
    UserSerializer,
    RPTokenSerializer,
    RPPasswordSerializer
)

from account.models import UserFollowing


@pytest.mark.django_db
class TestUserSerializer(SerializerTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.user = UserFactory().create()
        self.serializer = UserSerializer
        return super().setUp()

    def test_create(self):
        data = {
            'username': 'Joseph', 'email': 'john@example.com', 'password': '12345678'
        }
        form = self.serializer(data=data)
        form.is_valid(raise_exception=True)
        user = form.save()
        self.assertEqual(CustomUser.objects.get(email=data['email']), user)


class TestRPEmailSerializer(SerializerTestCase):

    def setUp(self) -> None:
        self.required_fields = ['email']
        self.non_required_fields = []
        self.serializer = RPEmailSerializer
        return super().setUp()

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(
            self.serializer, self.non_required_fields)


class TestRPTokenSerializer(SerializerTestCase):

    def setUp(self) -> None:
        self.required_fields = ['email', 'token']
        self.non_required_fields = []
        self.serializer = RPTokenSerializer
        return super().setUp()

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(
            self.serializer, self.non_required_fields)


class TestRPPasswordSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.required_fields = ['email', 'token', 'password']
        self.non_required_fields = []
        self.serializer = RPPasswordSerializer
        return super().setUp()

    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(
            self.serializer, self.non_required_fields)


@pytest.mark.django_db
class TestUserFollowerSerializer(SerializerTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.user = UserFactory().create()
        self.follower_user = UserFactory().create(email='user2@gmail.com')
        self.serializer = UserFollowerSerializer

        self.INVALID_DATA = [
            {
                'data': {'followed_user': self.follower_user.id},
                'errors': {
                    'followed_user': ['User is already being followed.']
                },
                'label': 'invalid follower'
            },
        ]

        self.VALID_DATA = [
            {'followed_user': self.follower_user.id},
        ]
        return super().setUp()

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={'user': self.user})

    def test_invalid_data(self) -> None:
        temp = UserFollowing.objects.create(
            user=self.user, followed_user=self.follower_user)
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={'user': self.user})
        temp.delete()

    def test_to_representation(self) -> None:
        serializer = self.serializer(
            data={'followed_user': self.follower_user.id}, context={'user': self.user})
        serializer.is_valid()
        follower_transaction = serializer.save()

        data = {
            'user': UserSerializer(instance=self.follower_user).data,
            'following_since': follower_transaction.date_created,
            'blocked': follower_transaction.blocked
        }

        self.assertDictEqual(data, serializer.data)
        follower_transaction.delete()
