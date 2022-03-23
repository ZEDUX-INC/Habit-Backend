import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.status import *
from account.api.v1.serializers import UserFollowerSerializer
from account.models import UserFollowing
from tests.v1.account.test_models import UserFactory
from rest_framework_simplejwt.tokens import RefreshToken
import pytest
import mock


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
            reverse('api-account-v1:auth-views-list'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # assert that the user created is inactive
        user = UserFactory.model.objects.get(id=response.data['id'])
        self.assertEqual(user.is_active, False)

    def test_logout(self):
        """Test user logout."""

        user = UserFactory().create(is_active=True)
        token = RefreshToken.for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' +
                           str(token.access_token))
        data = json.dumps({'refresh_token': str(token)})
        response = client.post(
            reverse('api-account-v1:logout-user'), data, content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_deactivate(self):
        """Test deactivating a user."""

        user = UserFactory().create(is_active=True)
        token = RefreshToken.for_user(user)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' +
                           str(token.access_token))

        response = client.post(
            reverse('api-account-v1:auth-views-deactivate',
                    kwargs={'pk': user.id}),
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
            'api-account-v1:auth-views-activate', kwargs={'pk': user.id}), None, content_type='application/json')
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

        with mock.patch('account.api.v1.tasks.send_reset_password_otp_to_user_email_task.delay') as email_task:
            response = self.client.post(reverse(
                'api-account-v1:reset-password-gettoken'), data, content_type='application/json')

        email_task.assert_called_once()
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
            'api-account-v1:reset-password-validatetoken'), data, content_type='application/json')
        print(data)
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
            'api-account-v1:reset-password-resetpassword'), data, content_type='application/json')

        self.assertEqual(response.status_code, HTTP_200_OK)
        user.refresh_from_db()
        self.assertIsNone(user.reset_token)


@pytest.mark.django_db
class TestListFollowersView(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory().create()
        self.followed_user = UserFactory().create(email='follwed@gmail.com')

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))

    def test_list_followers_success(self):
        """Test followers found 200."""
        follower_transaction = UserFollowing.objects.create(
            user=self.followed_user, followed_user=self.user)
        url = reverse('api-account-v1:followers-list',
                      kwargs={'id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_followers_user_empty(self):
        """Test followers found not found."""
        url = reverse('api-account-v1:followers-list',
                      kwargs={'id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


@pytest.mark.django_db
class TestRetrieveFollowerView(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory().create()
        self.followed_user = UserFactory().create(email='follwed@gmail.com')

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))

    def test_retrieve_follower_found(self):
        """Test Retrieve Follower 200"""
        follower_transaction = UserFollowing.objects.create(
            user=self.followed_user, followed_user=self.user)
        url = reverse('api-account-v1:follower-details',
                      kwargs={'id': self.user.id, 'follower_id': self.followed_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        serializer = UserFollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_retrieve_follower_not_found(self):
        url = reverse('api-account-v1:follower-details',
                      kwargs={'id': self.user.id, 'follower_id': self.followed_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.data, {'detail': 'Follower with this id not found.'})


@pytest.mark.django_db
class TestBlockFollowerView(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory().create()
        self.follower_user = UserFactory().create(email='follwer@gmail.com')

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))

    def test_block_follower_success(self):
        """Test Retrieve Follower 201"""
        follower_transaction = UserFollowing.objects.create(
            followed_user=self.user, user=self.follower_user)
        url = reverse('api-account-v1:toggle-block-follower',
                      kwargs={'id': self.user.id, 'follower_id': self.follower_user.id})
        data = {'blocked': True}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_200_OK)
        follower_transaction.refresh_from_db()
        serializer = UserFollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_block_follower_not_found(self):
        url = reverse('api-account-v1:toggle-block-follower',
                      kwargs={'id': self.user.id, 'follower_id': self.follower_user.id})
        data = {'blocked': True}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.data, {'detail': 'You are not presently following this user.'})

    def test_block_follower_not_permitted(self):
        url = reverse('api-account-v1:toggle-block-follower',
                      kwargs={'id': self.follower_user.id, 'follower_id': self.user.id})
        data = {'blocked': True}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestListCreateFollowingView(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory().create()
        self.followed_user = UserFactory().create(email='follwing@gmail.com')

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))

    def test_list_followed_users_success(self):
        UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-list',
                      kwargs={'id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_list_followed_users_not_found(self):
        UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-list', kwargs={'id': 20})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_follow_user_success(self):
        url = reverse('api-account-v1:following-list',
                      kwargs={'id': self.user.id})
        data = {'followed_user': self.followed_user.id}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        follower_transaction = UserFollowing.objects.get(
            followed_user=response.data['user'].get('id'))
        serializer = UserFollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_follow_user_faliure(self):
        """Ensure failure when trying to follow already followed user."""
        UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-list',
                      kwargs={'id': self.user.id})
        data = {'followed_user': self.followed_user.id}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_follow_user_not_permitted(self):
        url = reverse('api-account-v1:following-list',
                      kwargs={'id': self.followed_user.id})
        data = {'followed_user': self.followed_user.id}
        response = self.client.post(url, data=json.dumps(
            data), content_type='application/json')
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestRetrieveRemoveFollowingView(TestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = UserFactory().create()
        self.followed_user = UserFactory().create(email='follwing@gmail.com')

        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' +
                                str(token.access_token))

    def test_retrieve_followed_user_success(self):
        follower_transaction = UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-details',
                      kwargs={'id': self.user.id, 'followed_id': self.followed_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        follower_transaction.refresh_from_db()
        serializer = UserFollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_retrieve_followed_user_not_found(self):
        url = reverse('api-account-v1:following-details',
                      kwargs={'id': self.user.id, 'followed_id': self.followed_user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_delete_followed_user_success(self):
        """Unfollow a followed user."""
        UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-details',
                      kwargs={'id': self.user.id, 'followed_id': self.followed_user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_followed_user_not_permitted(self):
        UserFollowing.objects.create(
            user=self.user, followed_user=self.followed_user)
        url = reverse('api-account-v1:following-details',
                      kwargs={'id': self.followed_user.id, 'followed_id': self.user.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)
