from email import message
from tests.utils.TestCase import SerializerTestCase
from thread.api.v1.serializers import ThreadSerializer
from account.models import CustomUser
from thread.models import Thread
import pytest
from rest_framework.request import Request
from django.http import HttpRequest


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
