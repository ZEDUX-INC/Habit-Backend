import mock
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from freezegun import freeze_time
from notifications.models import Notification
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from account.api.v1.serializers import FollowerSerializer, FollowingSerializer
from account.models import CustomUser, UserFollowing
from tests.utils.TestCase import ViewTestCase
from tests.v1.account.test_models import (
    NotificationFactory,
    UserFactory,
    UserFollowingFactory,
)


class AuthViewsTests(APITestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_signup(self):
        """Test user signup endpoint."""
        data = {
            "username": "jason",
            "first_name": "magin",
            "last_name": "modi",
            "email": "user2@example.com",
            "password": "12345678",
        }

        response = self.client.post(
            reverse("api-account-v1:auth-views-list"),
            data,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert that the user created is active
        user = CustomUser.objects.get(id=response.data["id"])
        self.assertEqual(user.is_active, True)

    def test_logout_successful(self):
        """Test user logout."""
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + str(token.access_token))
        url = reverse("api-account-v1:logout-user")

        response = self.client.post(
            path=url,
            data={"refresh_token": str(token)},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ResetPasswordViewsetTests(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()

    def test_generate_token(self):
        """Test generate reset password token view."""
        data = {"email": self.user.email}

        with mock.patch(
            "account.api.v1.tasks.send_reset_password_otp_to_user_email_task.delay"
        ) as email_task:
            response = self.client.post(
                reverse("api-account-v1:reset-password-gettoken"),
                data,
            )

        email_task.assert_called_once()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.reset_token)

    def test_validate_token__successful(self):
        """Test Validate reset password token view."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {"token": unsigned_token, "email": self.user.email}

        response = self.client.post(
            reverse("api-account-v1:reset-password-validatetoken"),
            data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_validate_token__failed_invalid_token(self):
        """Test validate reset password fails if wrong token is sent."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {"token": unsigned_token + 1, "email": self.user.email}

        response = self.client.post(
            reverse("api-account-v1:reset-password-validatetoken"),
            data,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["Invalid token"]})

    @freeze_time("2022-09-21 01:00:00")
    def test_validate_token__failed_expired_token(self):
        """Test validate reset password fails if token is expired."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {"token": unsigned_token, "email": self.user.email}

        with freeze_time("2022-09-21 02:00:00"):
            response = self.client.post(
                reverse("api-account-v1:reset-password-validatetoken"),
                data,
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, {"status": "failure", "message": "token has expired"}
        )

    def test_resetpassword_successful(self):
        """Test reset user password with token."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {
            "token": unsigned_token,
            "email": self.user.email,
            "password": "1122334455",
        }

        response = self.client.post(
            reverse("api-account-v1:reset-password-resetpassword"),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.reset_token)

    def test_resetpassword_failed_invalid_token(self):
        """Test reset user password with token fails if wrong token is sent."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {
            "token": unsigned_token + 1,
            "email": self.user.email,
            "password": "1122334455",
        }

        response = self.client.post(
            reverse("api-account-v1:reset-password-resetpassword"),
            data,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"token": ["Invalid token"]})

    @freeze_time("2022-09-21 01:00:00")
    def test_resetpassword__failed_expired_token(self):
        """Test reset user password with token fails if token is expired.."""
        unsigned_token, signed_token = self.user.generate_resettoken()
        self.user.reset_token = signed_token
        self.user.save()
        data = {
            "token": unsigned_token,
            "email": self.user.email,
            "password": "1122334455",
        }

        with freeze_time("2022-09-21 02:00:00"):
            response = self.client.post(
                reverse("api-account-v1:reset-password-resetpassword"),
                data,
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data, {"status": "failure", "message": "token has expired"}
        )


class ListFollowersViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.followed_user = UserFactory.create(email="follwed@gmail.com")
        self.url = reverse("api-account-v1:followers-list", kwargs={"id": self.user.id})

    def test_list_followers_success(self):
        """Test followers found."""
        UserFollowingFactory.create(user=self.followed_user, followed_user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)

    def test_list_followers_user_empty(self):
        """Test followers found not found."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 0)


class RetrieveFollowerViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.followed_user = UserFactory.create(email="follwed@gmail.com")
        self.url = reverse(
            "api-account-v1:follower-details",
            kwargs={"id": self.user.id, "follower_id": self.followed_user.id},
        )

    def test_retrieve_follower_found(self):
        """Test Retrieve Follower 200"""
        follower_transaction = UserFollowingFactory.create(
            user=self.followed_user, followed_user=self.user
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = FollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_retrieve_follower_not_found(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.data, {"detail": "Follower with this id not found."}
        )


class BlockFollowerViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.follower_user = UserFactory.create(email="follwer@gmail.com")
        self.url = reverse(
            "api-account-v1:follower-details",
            kwargs={"id": self.user.id, "follower_id": self.follower_user.id},
        )

    def test_block_follower_success(self):
        """Test Retrieve Follower 201"""
        follower_transaction = UserFollowingFactory.create(
            followed_user=self.user, user=self.follower_user
        )

        data = {"blocked": True}
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        follower_transaction.refresh_from_db()
        serializer = FollowerSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_block_follower_not_found(self):
        """Test retrieve follower not found."""
        data = {"blocked": True}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(
            response.data, {"detail": "Follower with this id not found."}
        )

    def test_block_follower_not_permitted(self):
        url = reverse(
            "api-account-v1:follower-details",
            kwargs={"id": self.follower_user.id, "follower_id": self.user.id},
        )
        data = {"blocked": True}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ListCreateFollowingViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.followed_user = UserFactory.create(email="follwing@gmail.com")
        self.url = reverse("api-account-v1:following-list", kwargs={"id": self.user.id})

    def test_list_followed_users_success(self):
        UserFollowingFactory.create(user=self.user, followed_user=self.followed_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual(len(results), 1)

    def test_follow_user_success(self):
        data = {"followed_user": self.followed_user.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        follower_transaction = UserFollowing.objects.get(
            followed_user=response.data["user"].get("id")
        )
        serializer = FollowingSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_follow_user_faliure(self):
        """Ensure failure when trying to follow already followed user."""
        UserFollowingFactory.create(user=self.user, followed_user=self.followed_user)

        data = {"followed_user": self.followed_user.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_follow_user_not_permitted(self):
        url = reverse(
            "api-account-v1:following-list", kwargs={"id": self.followed_user.id}
        )

        data = {"followed_user": self.followed_user.id}

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RetrieveRemoveFollowingViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.followed_user = UserFactory.create(email="follwing@gmail.com")
        self.url = reverse(
            "api-account-v1:following-details",
            kwargs={"id": self.user.id, "followed_id": self.followed_user.id},
        )

    def test_retrieve_followed_user_success(self):
        follower_transaction = UserFollowingFactory.create(
            user=self.user, followed_user=self.followed_user
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        follower_transaction.refresh_from_db()
        serializer = FollowingSerializer(instance=follower_transaction)
        self.assertDictEqual(response.data, serializer.data)

    def test_retrieve_followed_user_not_found(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_followed_user_success(self):
        """Unfollow a followed user."""
        UserFollowingFactory.create(user=self.user, followed_user=self.followed_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_followed_user__failed_not_permitted(self):
        UserFollowingFactory.create(user=self.user, followed_user=self.followed_user)
        url = reverse(
            "api-account-v1:following-details",
            kwargs={"id": self.followed_user.id, "followed_id": self.user.id},
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_followed_user__failed_user_not_found(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data, {"detail": "You are not presently following this user."}
        )


class ListNotificationsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user_2 = UserFactory.create(email="another@example.com")

        NotificationFactory.create_batch(
            size=2,
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
        )

        NotificationFactory.create_batch(
            size=2,
            recipient=self.user_2,
            actor_content_type=ContentType.objects.get_for_model(self.user_2),
        )

    def test_list_notifications(self):
        """Test to assert that only authenticated user's notifications are returned."""

        url = reverse("api-account-v1:list-notifications")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 2)


class NotificationsDetailViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.notification = NotificationFactory.create(
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
            unread=True,
        )

        self.url = reverse(
            "api-account-v1:notification-details", kwargs={"pk": self.notification.id}
        )

    def test_retrieve_notification_detail(self):

        expected_data = {
            "id": self.notification.id,
            "data": self.notification.data,
            "unread": self.notification.unread,
            "timestamp": self.notification.timestamp.isoformat().replace("+00:00", "Z"),
        }

        response = self.client.get(path=self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)

    def test_update_notification_detail(self):

        data = {"unread": False}

        response = self.client.put(path=self.url, data=data)

        expected_data = {
            "id": self.notification.id,
            "data": self.notification.data,
            "unread": False,
            "timestamp": self.notification.timestamp.isoformat().replace("+00:00", "Z"),
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)

        self.notification.refresh_from_db()
        self.assertFalse(self.notification.unread, False)

    def test_delete_notification(self):
        response = self.client.delete(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.user.notifications.exists(), False)


class MarkAllNotificationsAsReadViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.notifications = NotificationFactory.create_batch(
            size=4,
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
        )

        NotificationFactory.create_batch(
            size=4,
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
            actor_object_id=self.user.id,
            unread=False,
        )

        self.url = reverse("api-account-v1:mark-all-notifications-as-read")

    def test_mark_all_notifications_as_read(self):

        expected_data = {"status": True, "marked_notifications": 4}

        response = self.client.post(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)
        self.assertEqual(
            0, Notification.objects.filter(recipient=self.user, unread=True).count()
        )


class DeleteAllNotificationsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.notifications = NotificationFactory.create_batch(
            size=4,
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
        )

        NotificationFactory.create_batch(
            size=4,
            recipient=self.user,
            actor_content_type=ContentType.objects.get_for_model(self.user),
            actor_object_id=self.user.id,
            unread=False,
        )

        self.url = reverse("api-account-v1:delete-all-notifications")

    def test_delete_all_notifications(self):

        response = self.client.delete(path=self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, Notification.objects.filter(recipient=self.user).count())
