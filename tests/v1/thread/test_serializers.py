from tests.utils.TestCase import SerializerTestCase
from tests.v1.thread.test_models import AttachementFactory, LikeFactory, PlayListFactory, CommentFactory
from thread.api.v1.serializers import LikeSerializer, PlayListSerializer, CommentSerializer
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


class CommentSerializerTests(SerializerTestCase):

    def setUp(self) -> None:
        self.serializer = CommentSerializer
        self.user = UserFactory().create(email='user@example.com')

        http_request = HttpRequest()
        self.request = Request(http_request)
        self.request.user = self.user

        self.playlist1 = PlayListFactory.create(created_by=self.user)
        self.playlist2 = PlayListFactory.create(
            created_by=self.user, title='playlist-2')

        self.comment1 = CommentFactory.create(
            created_by=self.user, playlist=self.playlist1)
        self.comment2 = CommentFactory.create(
            created_by=self.user, playlist=self.playlist2)

        self.INVALID_DATA = [
            {
                'data': {
                    'playlist': self.playlist1.id,
                    'replying': self.comment2.id,
                    'content': 'Yada',
                },
                'errors': {
                    'non_field_errors': [
                        'can not reply a comment from another playlist.'
                    ]
                },
                'label': 'can not reply a comment from another playlist.'
            },
        ]

        self.VALID_DATA = [
            {
                'playlist': self.playlist1.id,
                'content': 'Yada',

            },
            {
                'playlist': self.playlist1.id,
                'replying': self.comment1.id,
                'content': 'Yada',
            },
        ]

        self.REQUIRED_FIELDS = ['playlist', 'content']
        self.NON_REQUIREDS_FIELDS = [
            'date_created', 'attachments', 'replying', 'id', 'content', 'created_by']

    def test_required_fields(self) -> None:
        self.check_required_fields(self.serializer, self.REQUIRED_FIELDS)

    def test_non_required_fields(self) -> None:
        self.check_non_required_fields(
            self.serializer, self.NON_REQUIREDS_FIELDS)

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={'request': self.request})

    def test_invalid_data(self) -> None:
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={'request': self.request})

    def test_to_representation(self) -> None:
        comment = CommentFactory.create(
            created_by=self.user, playlist=self.playlist1, replying=self.comment1)
        serializer = self.serializer(instance=self.comment1)
        expected_data = {
            'id': self.comment1.id,
            'created_by': self.user.id,
            'playlist': self.playlist1.id,
            'replying': None,
            'content': self.comment1.content,
            'attachments': [],
            'date_created': serializer.data['date_created'],
            'replies': [comment.id]
        }
        self.assertDictEqual(expected_data, serializer.data)
