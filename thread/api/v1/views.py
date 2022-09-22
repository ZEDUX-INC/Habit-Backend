from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.filters import OrderingFilter, SearchFilter

from thread.api.v1.permissions import IsCreatorOrReadOnly
from thread.api.v1.serializers import (
    AttachmentSerializer,
    CommentSerializer,
    LikeSerializer,
    PlayListCategorySerializer,
    PlayListSerializer,
)
from thread.models import Attachment, Comment, Like, PlayList, PlayListCategory


class AttachmentListView(generics.ListCreateAPIView):
    """
    To upload a file send the payload as a
    multipart-form-data.
    """

    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Attachment.objects.all()
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["type"]
    search_fields = ["name"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields


class AttachmentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    queryset = Attachment.objects.all()
    lookup_field = "id"


class LikeListView(generics.ListCreateAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created", "created_by"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields


class UserLikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields

    def get_queryset(self) -> QuerySet[Like]:
        return Like.objects.filter(created_by=self.request.user)


class LikeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    lookup_field = "id"


class PlaylistListView(generics.ListCreateAPIView):
    serializer_class = PlayListSerializer
    queryset = PlayList.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created", "categories__title", "views"]
    search_fields = ["title"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields


class PlayListDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PlayListSerializer
    queryset = PlayList.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    lookup_field = "id"


class UserPlaylistView(generics.ListAPIView):
    serializer_class = PlayListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created", "categories__title", "views"]
    search_fields = ["title"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields

    def get_queryset(self) -> QuerySet:
        return PlayList.objects.filter(created_by=self.request.user)


class PlayListCategoryListView(generics.ListAPIView):
    serializer_class = PlayListCategorySerializer
    queryset = PlayListCategory.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "id"
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created"]
    search_fields = ["title"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields


class PlayListCommentListView(generics.ListCreateAPIView):
    """Retrieve all non reply comments associated with a specific PlayList"""

    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_created"]
    search_fields = ["content"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields
    lookup_field = "id"

    def get_object(self) -> PlayList:
        return get_object_or_404(PlayList, id=self.kwargs["id"])

    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(playlist=self.get_object(), replying=None)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)

    def get_object(self) -> Comment:
        playlist_id = self.kwargs.get("id")
        comment_id = self.kwargs.get("comment_id")
        obj = get_object_or_404(Comment, id=comment_id, playlist__id=playlist_id)
        return obj
