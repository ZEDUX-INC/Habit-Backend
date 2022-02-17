import pytest

from rest_framework.status import *
from UserApp.models import CustomUser
from tests.v1.userapp.test_models import UserFactory
from tests.utils.TestCase import SerializerTestCase

from APIV1.UserApp.serializers import (
    RPEmailSerializer, 
    UserSerializer, 
    RPTokenSerializer,
    RPPasswordSerializer
)


@pytest.mark.django_db
class TestUserSerializer(SerializerTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.user = UserFactory().create()
        self.serializer =  UserSerializer
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
        self.check_non_required_fields(self.serializer, self.non_required_fields)


class TestRPTokenSerializer(SerializerTestCase):

    def setUp(self) -> None:
        self.required_fields = ['email', 'token']
        self.non_required_fields = []
        self.serializer = RPTokenSerializer
        return super().setUp()
    
    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(self.serializer, self.non_required_fields)


class TestRPPasswordSerializer(SerializerTestCase):
    def setUp(self) -> None:
        self.required_fields = ['email', 'token', 'password']
        self.non_required_fields = []
        self.serializer = RPPasswordSerializer
        return super().setUp()
    
    def test_required_fields(self):
        self.check_required_fields(self.serializer, self.required_fields)

    def test_non_required_fields(self):
        self.check_non_required_fields(self.serializer, self.non_required_fields)
