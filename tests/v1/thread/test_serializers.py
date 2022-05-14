from tests.utils.TestCase import SerializerTestCase
from tests.v1.thread.test_models import AttachementFactory, LikeFactory, PlayListFactory
from thread.api.v1.serializers import LikeSerializer, PlayListSerializer
from rest_framework.request import Request
from django.http import HttpRequest
from tests.v1.account.test_models import UserFactory


class LikeSerializerTest(SerializerTestCase):

    def setUp(self) -> None:
        self.serializer = LikeSerializer
        self.user = UserFactory().create(email='user@example.com')

        http_request = HttpRequest()
        self.request = Request(http_request)
        self.request.user = self.user

        user_2 = UserFactory().create(email='jagaja@example.com')

        self.playlist = PlayListFactory.create(
            created_by=user_2, title='Valkrie')
        playlist_2 = PlayListFactory.create(
            created_by=self.user, title='Magnum')
        liked_playlist = PlayListFactory.create(
            created_by=user_2, title='Valdor')
        LikeFactory.create(created_by=self.user, playlist=liked_playlist)

        self.INVALID_DATA = [
            {
                'data': {
                    'playlist': playlist_2.id,
                },
                'errors': {
                    'non_field_errors': [
                        'User can not like their own playlist.'
                    ]
                },
                'label': 'User can not like their own playlist.'
            },
            {
                'data': {
                    'playlist': liked_playlist.id,
                },
                'errors': {
                    'non_field_errors': [
                        'User has already liked this playlist.'
                    ]
                },
                'label': 'User has already liked this playlist.'
            }
        ]

        self.VALID_DATA = [
            {
                'playlist': self.playlist.id
            },
        ]

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={'request': self.request})

    def test_invalid_data(self) -> None:
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={'request': self.request})

    def test_to_representation(self) -> None:
        serializer = self.serializer(
            data={'playlist': self.playlist.id}, context={'request': self.request})

        serializer.is_valid()
        like = serializer.save()

        expected_data = {
            'id': like.id,
            'created_by': self.user.id,
            'date_created': serializer.data['date_created'],
            'playlist': PlayListSerializer(instance=self.playlist).data,
            'comment': None
        }

        self.assertDictEqual(expected_data, serializer.data)


class PlayListSerializerTests(SerializerTestCase):

    def setUp(self) -> None:
        self.serializer = PlayListSerializer
        self.user = UserFactory().create(email='user@example.com')

        http_request = HttpRequest()
        self.request = Request(http_request)
        self.request.user = self.user

        self.playlist = PlayListFactory.create(created_by=self.user)
        song = AttachementFactory.create(created_by=self.user)

        self.INVALID_DATA = [
            {
                'data': {
                    'title': 'Nagni is home',
                    'categories': [],
                    'songs': [],
                    'active_hours': 24,
                    'short_description': 'Holla',
                },
                'errors': {
                    'songs': [
                        'This list may not be empty.'
                    ]
                },
                'label': 'Song Field is required.'
            },
            {
                'data': {
                    'title': self.playlist.title,
                    'categories': [],
                    'songs': [song.id],
                    'active_hours': 24,
                    'short_description': 'Holla',
                },
                'errors': {
                    'title': [
                        'PlayList with this title already exists.'
                    ]
                },
                'label': 'Playlist Title already exists.'
            },
        ]

        self.VALID_DATA = [
            {
                'title': 'My Major jams',
                'categories': [],
                'songs': [song.id],
                'active_hours': 24,
                'short_description': 'Holla',
            },
        ]

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={'request': self.request})

    def test_invalid_data(self) -> None:
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={'request': self.request})
