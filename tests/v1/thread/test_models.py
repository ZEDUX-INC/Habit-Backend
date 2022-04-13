import pytest
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from thread.models import Thread, Message, Attachment, Like
from tests.v1.account.test_models import UserFactory


@pytest.mark.django_db
class AttachementFactory:
    pytestmark = pytest.mark.django_db
    file = None
    type = ''
    name = 'test_file'
    model = Attachment
    created_by = None

    @pytest.mark.django_db
    def create(self, **kwargs) -> Attachment:
        options = {
            'created_by': self.created_by,
            'file': self.file,
            'type': self.type,
            'name': self.name,
        }

        options.update(**kwargs)
        return self.model.objects.create(**options)


@pytest.mark.django_db
class ThreadFactory:
    pytestmark = pytest.mark.django_db
    type = '0'
    reply_setting = '0'
    replying = None
    sharing = None
    model = Thread
    created_by = None

    @pytest.mark.django_db
    def create(self, **kwargs) -> Thread:
        options = {
            'created_by': self.created_by,
            'type': self.type,
            'reply_setting': self.reply_setting,
            'replying': self.replying,
            'sharing': self.sharing
        }

        options.update(**kwargs)
        return self.model.objects.create(**options)


@pytest.mark.django_db
class LikeFactory:
    pytestmark = pytest.mark.django_db
    thread = None
    model = Like
    created_by = None

    @pytest.mark.django_db
    def create(self, **kwargs) -> Thread:
        options = {
            'created_by': self.created_by,
            'thread': self.thread
        }

        options.update(**kwargs)
        return self.model.objects.create(**options)


class TestThreadModel(TestCase):

    def setUp(self) -> None:
        self.user = UserFactory().create(
            email='user@example.com',
            password='12345678'
        )

        self.message = Message.objects.create(
            created_by=self.user
        )

        self.thread = Thread.objects.create(
            created_by=self.user,
        )

    def test_reply_share_constraint(self) -> None:

        with transaction.atomic() as db_transaction:
            raised_exception = None
            try:
                Thread.objects.create(
                    replying=self.thread,
                    sharing=self.thread,
                    message=self.message
                )
            except IntegrityError as error:
                raised_exception = True

            self.assertIsNotNone(raised_exception)

        with transaction.atomic() as db_transaction:
            raised_exception = None

            try:
                Thread.objects.create(
                    created_by=self.user,
                    replying=self.thread,
                    message=self.message
                )
            except IntegrityError as error:
                raised_exception = True

            self.assertIsNone(raised_exception)

            try:
                Thread.objects.create(
                    created_by=self.user,
                    sharing=self.thread,
                )
            except IntegrityError as error:
                raised_exception = True

            self.assertIsNone(raised_exception)
