from django.db import IntegrityError, transaction
from django.test import TestCase
from factory.django import DjangoModelFactory

from tests.v1.account.test_models import UserFactory
from thread.models import Attachment, Comment, Like, PlayList, PlayListCategory


class AttachementFactory(DjangoModelFactory):
    file = None
    type = ""
    name = "test_file"

    class Meta:
        model = Attachment


class TestAttachmentModel(TestCase):
    def test_unicode(self) -> None:
        user = UserFactory.create()
        obj = AttachementFactory.create(created_by=user)
        self.assertEqual(
            str(obj), f"Attachement {obj.id}-{obj.name} added by {user.email}"
        )


class PlayListCategoryFactory(DjangoModelFactory):
    title = "Pop"

    class Meta:
        model = PlayListCategory
        django_get_or_create = ("title",)


class TestPlayListCategoryModel(TestCase):
    def test_unicode(self) -> None:
        obj = PlayListCategoryFactory.create()
        self.assertEqual(str(obj), f"PlayListCategory - {obj.title}")


class CommentFactory(DjangoModelFactory):
    content = "This is a comment by some dork"
    replying = None

    class Meta:
        model = Comment


class PlayListFactory(DjangoModelFactory):
    title = "Sabaton"
    cover_image = None
    short_description = "This playlist is a Jem"

    class Meta:
        model = PlayList


class LikeFactory(DjangoModelFactory):
    class Meta:
        model = Like


class TestPlayListModel(TestCase):
    def test_constraints(self) -> None:
        user = UserFactory.create()
        playlist = PlayListFactory.create(created_by=user)

        self.assertRaises(
            IntegrityError,
            PlayListFactory.create,
            title=playlist.title,
            created_by=user,
        )


class TestLikeModel(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory.create()
        self.other_user = UserFactory.create(email="TestLikeModel@example.com")
        self.playlist = PlayListFactory.create(created_by=self.other_user)
        self.comment = CommentFactory.create(
            created_by=self.other_user, playlist=self.playlist
        )

    def test_constraints(self) -> None:

        # test that a like must have either comment or playlist fields but not both
        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                LikeFactory.create,
                created_by=self.user,
            )

        with transaction.atomic():
            self.assertRaises(
                IntegrityError,
                LikeFactory.create,
                created_by=self.user,
                playlist=self.playlist,
                comment=self.comment,
            )

        with transaction.atomic():
            raise_exception = False

            try:
                LikeFactory.create(playlist=self.playlist, created_by=self.user)
                LikeFactory.create(comment=self.comment, created_by=self.user)
            except IntegrityError:
                raise_exception = True

            self.assertFalse(raise_exception)

        # test that a user can't like thier own playlist
        with transaction.atomic():
            playlist = PlayListFactory.create(created_by=self.user)

            self.assertRaises(
                IntegrityError,
                LikeFactory.create,
                created_by=self.user,
                playlist=playlist,
            )

        # test that a user can't like thier own comment
        with transaction.atomic():
            comment = CommentFactory.create(
                created_by=self.user, playlist=self.playlist
            )

            self.assertRaises(
                IntegrityError,
                LikeFactory.create,
                created_by=self.user,
                comment=comment,
            )
