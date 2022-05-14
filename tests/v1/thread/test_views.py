import pytest
from django.urls import reverse
from rest_framework.status import *
from account.models import UserFollowing
from tests.v1.account.test_models import UserFactory
from tests.v1.thread.test_models import AttachementFactory, LikeFactory, PlayListFactory
from tests.utils.TestCase import ViewTestCase


class AttachmentListCreateViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.attachment = AttachementFactory.create(created_by=self.user)
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
        results = response.data['results']
        self.assertEqual(len(results), 1)

    # def test_create_attachement_view(self) -> None:
    #     url = reverse('api-thread-v1:attachment-list')
    #     data = {
    #         'file': self.file,
    #         'type': 'image',
    #         'name': 'test_file'
    #     }
    #     response = self.client.post(url, data=data)
    #     self.assertEqual(response.status_code, HTTP_201_CREATED)
    #     self.assertGreater(len(response.data), 1)


class AttachmentDetailViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.attachment = AttachementFactory.create(created_by=self.user)
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
        attachment = AttachementFactory.create(created_by=self.user)
        url = reverse('api-thread-v1:attachment-detail',
                      kwargs={'id': attachment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_attacment_view_permission_denied(self):
        """Test delete an attachment by unpermitted user."""
        user = UserFactory().create(email='nagni@yoda.com')
        attachment = AttachementFactory.create(created_by=user)
        url = reverse('api-thread-v1:attachment-detail',
                      kwargs={'id': attachment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class LikeListViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.user_2 = UserFactory().create(email='ragna@gmail.com')
        self.playlist = PlayListFactory.create(created_by=self.user)
        self.like = LikeFactory.create(
            created_by=self.user_2, playlist=self.playlist)
        self.url = reverse('api-thread-v1:like-list')

    def test_list_like_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)

    def test_create_like_view(self) -> None:
        playlist = PlayListFactory.create(
            created_by=self.user_2, title='test_create_thread_view')

        data = {
            'playlist': playlist.id,
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertGreater(len(response.data), 1)


class LikeDetailViewTest(ViewTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.user_2 = UserFactory().create(email='ragna@gmail.com')
        self.playlist = PlayListFactory.create(created_by=self.user_2)
        self.like = LikeFactory.create(
            created_by=self.user, playlist=self.playlist)
        self.url = reverse('api-thread-v1:like-detail',
                           kwargs={'id': self.like.id})

    def test_retreive_like_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_like_view(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_like_view_permission_denied(self):
        """Test delete a thread by unpermitted user."""
        playlist = PlayListFactory.create(
            created_by=self.user, title='test_delete_like_view_permission_denied')
        like = LikeFactory.create(created_by=self.user_2, playlist=playlist)
        url = reverse('api-thread-v1:like-detail', kwargs={'id': like.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class UserLikeListViewTest(ViewTestCase):

    def test_view(self):
        user_2 = UserFactory().create(email='follower@gmail.com')
        user_3 = UserFactory().create(email='ragnarok@gmail.com')
        playlist = PlayListFactory.create(created_by=user_2)
        LikeFactory.create(created_by=self.user, playlist=playlist)
        LikeFactory.create(created_by=user_3, playlist=playlist)
        url = reverse('api-thread-v1:user-likes')

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)


class PlayListListViewTest(ViewTestCase):
    pytestmark = pytest.mark.django_db

    def setUp(self) -> None:
        super().setUp()
        self.user_2 = UserFactory().create(email='ragna@gmail.com')
        self.playlist = PlayListFactory.create(created_by=self.user)
        self.url = reverse('api-thread-v1:playlist-list')

    def test_list_playlist_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)

    # def test_create_playlist_view(self) -> None:
    #     data = {
    #         'title': 'My Major jams',
    #         'songs': [],
    #         'categories': [],
    #         'active_hours': 24,
    #         'short_description': 'Holla',
    #     }

    #     response = self.client.post(self.url, data=data)
    #     self.assertEqual(response.status_code, HTTP_201_CREATED)
    #     self.assertGreater(len(response.data), 1)


class PlayListDetailViewTest(ViewTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.playlist = PlayListFactory.create(created_by=self.user)
        self.url = reverse('api-thread-v1:playlist-detail',
                           kwargs={'id': self.playlist.id})

    def test_retreive_playlist_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_playlist_view(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_playlist_view_permission_denied(self):
        """Test delete a Playlist by unpermitted user."""
        user = UserFactory().create(email='myvoice@example.com')
        playlist = PlayListFactory.create(
            created_by=user, title='test_delete_playlist_view_permission_denied')
        url = reverse('api-thread-v1:playlist-detail',
                      kwargs={'id': playlist.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)


class UserPlayListListViewTest(ViewTestCase):

    def test_view(self):
        user_2 = UserFactory().create(email='follower@gmail.com')
        PlayListFactory.create(created_by=user_2)
        PlayListFactory.create(created_by=self.user)
        url = reverse('api-thread-v1:user-playlist')

        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
