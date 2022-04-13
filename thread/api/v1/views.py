from rest_framework import generics
from rest_framework import permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from thread.models import Attachment, Like, Thread
from thread.api.v1.permissions import IsCreatorOrReadOnly
from thread.api.v1.serializers import AttachmentSerializer, ThreadSerializer, LikeSerializer
from django.db.models import Q


class AttachmentListView(generics.ListCreateAPIView):
    '''
        To upload a file send the payload as a
        multipart-form-data.
    '''
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Attachment.objects.all()
    lookup_field = 'id'
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type']
    search_fields = ['name']
    ordering_fields = ['date_created']
    ordering = ordering_fields


class AttachmentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    queryset = Attachment.objects.all()
    lookup_field = 'id'


class ThreadListView(generics.ListCreateAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Thread.objects.all()
    lookup_field = 'id'
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type']
    search_fields = ['message__content']
    ordering_fields = ['date_created']
    ordering = ordering_fields


class ThreadDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    queryset = Thread.objects.all()
    lookup_field = 'id'


class UserThreadListView(generics.ListAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['type']
    search_fields = ['message__content']
    ordering_fields = ['date_created']
    ordering = ordering_fields

    def get_queryset(self):
        user = self.request.user
        return Thread.objects.filter(
            Q(created_by=user)
            | Q(created_by__following__user=user)
            | Q(created_by__follower__followed_user=user))


class LikeListView(generics.ListCreateAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['date_created', 'created_by']
    search_fields = []
    ordering_fields = ['date_created']
    ordering = ordering_fields


class UserLikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'id'
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ['date_created']
    search_fields = []
    ordering_fields = ['date_created']
    ordering = ordering_fields

    def get_queryset(self):
        return Like.objects.filter(
            created_by=self.request.user
        )


class LikeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    lookup_field = 'id'
