import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.status import *
from tests.v1.account.test_models import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken
import pytest


@pytest.mark.django_db
class TestAuthViews(TestCase):
    pytestmark = pytest.mark.django_db
    user = None
    client = APIClient()

    def setup(self):
        self.user = UserFactory().create(is_active=True)

    def test_signup(self):
        """Test user signup endpoint."""
        data = {
            'username': 'jason',
            'first_name': 'magin',
            'last_name': 'modi',
            'email': 'user2@example.com',
            'password': '12345678',
        }

        response = self.client.post(
            reverse('apiv1:auth-views-list'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # assert that the user created is inactive
        user = UserFactory.model.objects.get(id=response.data['id'])
        self.assertEqual(user.is_active, False)

    def test_logout(self):
        """Test user logout."""

        user = UserFactory().create(is_active=True)
        token = RefreshToken.for_user(user)
        # print(token.access_token)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' +
                           str(token.access_token))
        data = json.dumps({'refresh_token': str(token)})
        response = client.post(
            reverse('apiv1:logout-user'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_deactivate(self):
        """Test deactivating a user."""

        user = UserFactory().create(is_active=True)
        token = RefreshToken.for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' +
                           str(token.access_token))

        response = client.post(
            reverse('apiv1:auth-views-deactivate', kwargs={'pk': user.id}),
            None,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.is_active, False)

    def test_activate_email(self):
        """Test activate user email endpoint."""
        user = UserFactory().create(is_active=False)
        response = self.client.get(reverse(
            'apiv1:auth-views-activate', kwargs={'pk': user.id}), None, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.is_active, True)


@pytest.mark.django_db
class TestResetPasswordViewset(TestCase):
    pytestmark = pytest.mark.django_db
    user = None
    client = APIClient()

    def test_generate_token(self):
        """Test generate reset password token view."""
        user = UserFactory().create(is_active=True)
        data = {'email': user.email}

        response = self.client.post(
            reverse('apiv1:reset-password-gettoken'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)

        user.refresh_from_db()
        self.assertIsNotNone(user.reset_token)

    def test_validate_token(self):
        """Test Validate reset password token view."""
        user = UserFactory().create(is_active=True)
        raw_token, token = user.generate_resettoken()
        user.reset_token = token
        user.save()
        data = {'token': raw_token, 'email': user.email}

        response = self.client.post(reverse(
            'apiv1:reset-password-validatetoken'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_resetpassword(self):
        """Test reset user password with token."""
        user = UserFactory().create(is_active=True)
        raw_token, token = user.generate_resettoken()
        user.reset_token = token
        user.save()
        data = {'token': raw_token, 'email': user.email,
                'password': '1122334455'}

        response = self.client.post(reverse(
            'apiv1:reset-password-resetpassword'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)
        user.refresh_from_db()
        self.assertIsNone(user.reset_token)


class TestUserFollowerViews(TestCase):
    def setUp(self) -> None:
        return super().setUp()
