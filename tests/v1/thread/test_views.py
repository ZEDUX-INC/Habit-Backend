import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.status import *
from account.models import UserFollowing
from tests.v1.account.test_models import UserFactory
from tests.v1.thread.test_models import AttachementFactory, ThreadFactory
from tests.utils.TestCase import ViewTestCase


class AttachmentListCreateViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.attachment = AttachementFactory().create(created_by=self.user)
        file = open('testfile.txt', 'w')
        file.write('This is a test file')
        file.close()
        self.file = open('testfile.txt', 'rb')

    def tearDown(self) -> None:
        self.file.close()
        return super().tearDown()

    def test_list_attachments_view(self) -> None:
        url = reverse('api-thread-v1:attachment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_attachement_view(self) -> None:
        url = reverse('api-thread-v1:attachment-list')
        data = {
            'file': self.file,
            'type': 'image',
            'name': 'test_file'
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertGreater(len(response.data), 1)


class AttachmentDetailViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.attachment = AttachementFactory().create(created_by=self.user)
        file = open('testfile.txt', 'w')
        file.write('This is a test file')
        file.close()
        self.file = open('testfile.txt', 'rb')

    def test_retrieve_attachement_view(self):
        url = reverse('api-thread-v1:attachment-detail',
                      kwargs={'id': self.attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_attacment_view(self):
        attachment = AttachementFactory().create(created_by=self.user)
        url = reverse('api-thread-v1:attachment-detail',
                      kwargs={'id': attachment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_attacment_view_permission_denied(self):
        """Test delete an attachment by unpermitted user."""
        user = UserFactory().create(email='nagni@yoda.com')
        attachment = AttachementFactory().create(created_by=user)
        url = reverse('api-thread-v1:attachment-detail',
                      kwargs={'id': attachment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class ThreadListCreateViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.thread = ThreadFactory().create(created_by=self.user)

    def test_list_thread_view(self) -> None:
        url = reverse('api-thread-v1:thread-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_thread_view(self) -> None:
        url = reverse('api-thread-v1:thread-list')
        data = {
            'sharing': self.thread.id,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertGreater(len(response.data), 1)


class ThreadDetailViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.thread = ThreadFactory().create(created_by=self.user)
        self.url = reverse('api-thread-v1:thread-detail',
                           kwargs={'id': self.thread.id})

    def test_retreive_thread_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_thread_view(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_thread_view_permission_denied(self):
        """Test delete a thread by unpermitted user."""
        user = UserFactory().create(email='nagni@yoda.com')
        thread = ThreadFactory().create(created_by=user)
        url = reverse('api-thread-v1:thread-detail', kwargs={'id': thread.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class UserThreadListView(ViewTestCase):
    def test_view(self):
        my_follower = UserFactory().create(email='follower@gmail.com')
        my_followed = UserFactory().create(email='followed@gmail.com')
        UserFollowing.objects.create(user=my_follower, followed_user=self.user)
        UserFollowing.objects.create(user=self.user, followed_user=my_followed)

        my_thread = ThreadFactory().create(created_by=self.user)
        my_follower_thread = ThreadFactory().create(created_by=my_follower)
        my_followed_thread = ThreadFactory().create(created_by=my_followed)
        url = reverse('api-thread-v1:user-threads')

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
