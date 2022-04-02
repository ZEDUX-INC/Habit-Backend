from django.db.utils import IntegrityError
from django.test import TestCase
from thread.models import Thread, Message
from account.models import CustomUser
from django.db import transaction


class TestThreadModel(TestCase):

    def setUp(self) -> None:
        self.user = CustomUser.objects.create(
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
