from thread.models import Attachment, Like, PlayList, PlayListCategory, Comment
from tests.v1.account.test_models import UserFactory
from factory.django import DjangoModelFactory
from django.test import TestCase
from django.db import IntegrityError, transaction


class AttachementFactory(DjangoModelFactory):
    file = None
    type = ''
    name = 'test_file'

    class Meta:
        model = Attachment


class TestAttachmentModel(TestCase):
    def test_unicode(self) -> None:
        user = UserFactory().create()
        obj = AttachementFactory.create(created_by=user)
        self.assertEqual(
            str(obj), f'Attachement {obj.id}-{obj.name} added by {user.email}')


class PlayListCategoryFactory(DjangoModelFactory):
    title = 'Pop'

    class Meta:
        model = PlayListCategory
        django_get_or_create = ('title',)


class TestPlayListCategoryModel(TestCase):
    def test_unicode(self) -> None:
        obj = PlayListCategoryFactory.create()
        self.assertEqual(str(obj), f'PlayListCategory - {obj.title}')


class CommentFactory(DjangoModelFactory):
    content = 'This is a comment by some dork'
    replying = None

    class Meta:
        model = Comment


class PlayListFactory(DjangoModelFactory):
    title = 'Sabaton'
    cover_image = None
    short_description = 'This playlist is a Jem'

    class Meta:
        model = PlayList


class TestPlayListModel(TestCase):
    def test_constraints(self) -> None:
        with transaction.atomic():
            raised_exception = None
            user = UserFactory().create()
            playlist = PlayListFactory.create(created_by=user)

            try:
                PlayList.objects.create(title=playlist.title, created_by=user)
            except IntegrityError as err:
                raised_exception = True

        self.assertTrue(raised_exception)


class LikeFactory(DjangoModelFactory):
    class Meta:
        model = Like


class TestLikeModel(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory().create()
        self.other_user = UserFactory().create(email='TestLikeModel@example.com')
        self.playlist = PlayListFactory.create(created_by=self.other_user)
        self.comment = CommentFactory.create(
            created_by=self.other_user, playlist=self.playlist)

    def test_constraints(self) -> None:

        # test that a like must have either comment or playlist fields
        with transaction.atomic():
            raised_exception = None
            try:
                LikeFactory.create(created_by=self.user)
            except IntegrityError as err:
                raised_exception = True
            self.assertTrue(raised_exception)

        with transaction.atomic():
            raised_exception = None

            try:
                LikeFactory.create(created_by=self.user,
                                   playlist=self.playlist, comment=self.comment)
            except IntegrityError as err:
                raised_exception = True
            self.assertTrue(raised_exception)

        with transaction.atomic():
            raised_exception = None

            try:
                LikeFactory.create(created_by=self.user,
                                   playlist=self.playlist)
                LikeFactory.create(created_by=self.user, comment=self.comment)
            except IntegrityError as err:
                raised_exception = True
            self.assertIsNone(raised_exception)

        # test that a user can't like thier own playlist
        with transaction.atomic():
            raised_exception = None
            playlist = PlayListFactory.create(created_by=self.user)

            try:
                LikeFactory.create(created_by=self.user, playlist=playlist)
            except IntegrityError as err:
                raised_exception = True
            self.assertTrue(raised_exception)

        # test that a user can't like thier own comment
        with transaction.atomic():
            raised_exception = None
            comment = CommentFactory.create(
                created_by=self.user, playlist=self.playlist)

            try:
                LikeFactory.create(created_by=self.user, comment=comment)
            except IntegrityError as err:
                raised_exception = True
            self.assertTrue(raised_exception)
