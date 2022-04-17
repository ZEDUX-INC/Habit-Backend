from tests.utils.TestCase import SerializerTestCase
from tests.v1.thread.test_models import LikeFactory
from thread.api.v1.serializers import LikeSerializer, ThreadSerializer
from account.models import CustomUser
from thread.models import Thread
from rest_framework.request import Request
from django.http import HttpRequest
from tests.v1.account.test_models import UserFactory


class TestThreadSerializer(SerializerTestCase):

    def setUp(self) -> None:
        self.serializer = ThreadSerializer

        self.user = CustomUser.objects.create(
            email='user@example.com',
            password='12345678'
        )

        http_request = HttpRequest()
        self.request = Request(http_request)
        self.request.user = self.user

        self.thread = Thread.objects.create(
            created_by=self.user,
        )

        self.INVALID_DATA = [
            {
                'data': {
                    'replying': self.thread.id,
                    'sharing': self.thread.id,
                },
                'errors': {
                    'non_field_errors': [
                        'Thread can not be a reply and a share at the same time.'
                    ]
                },
                'label': 'Thread Can Not Reply and Share at the same time'
            },
            {
                'data': {
                    'replying': self.thread.id,
                },
                'errors': {
                    'non_field_errors': [
                        'Thread reply must have a message.'
                    ]
                },
                'label': 'Message Field in require in Thread Reply.'
            },
        ]

        self.VALID_DATA = [
            {
                'message': {
                    'content': 'This is a reply to a thread',
                    'attachments': []
                },
                'replying': self.thread.id,
            },
            {
                'message': {
                    'content': 'This is a cc to a thread',
                    'attachments': []
                },
                'sharing': self.thread.id,
            },
            {
                'message': {
                    'content': 'This is a thread',
                    'attachments': []
                },
            }
        ]

    def test_valid_data(self) -> None:
        self.check_valid_data(
            self.serializer, entries=self.VALID_DATA, context={'request': self.request})

    def test_invalid_data(self) -> None:
        self.check_invalid_data(
            self.serializer, entries=self.INVALID_DATA, context={'request': self.request})


class TestLikeSerializer(SerializerTestCase):

    def setUp(self) -> None:
        self.serializer = LikeSerializer
        self.user = UserFactory().create(email='user@example.com')

        http_request = HttpRequest()
        self.request = Request(http_request)
        self.request.user = self.user

        user_2 = UserFactory().create(email='jagaja@example.com')

        self.thread = Thread.objects.create(created_by=user_2)
        thread_2 = Thread.objects.create(created_by=self.user)
        liked_thread = Thread.objects.create(created_by=user_2)
        LikeFactory().create(created_by=self.user, thread=liked_thread)

        self.INVALID_DATA = [
            {
                'data': {
                    'thread': thread_2.id,
                },
                'errors': {
                    'non_field_errors': [
                        'User can not like their own threads.'
                    ]
                },
                'label': 'User can not like their own threads.'
            },
            {
                'data': {
                    'thread': liked_thread.id,
                },
                'errors': {
                    'non_field_errors': [
                        'User has already liked this thread.'
                    ]
                },
                'label': 'User has already liked this thread.'
            }
        ]

        self.VALID_DATA = [
            {
                'thread': self.thread.id
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
            data={'thread': self.thread.id}, context={'request': self.request})
        serializer.is_valid()
        like = serializer.save()
        data = {
            'id': like.id,
            'created_by': self.user.id,
            'date_created': serializer.data['date_created'],
            'thread': ThreadSerializer(instance=self.thread).data
        }

        self.assertDictEqual(data, serializer.data)
