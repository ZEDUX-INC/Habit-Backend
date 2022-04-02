from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework import permissions

from thread.models import Attachment, Thread
from thread.api.v1.permissions import IsCreatorOrReadOnly
from thread.api.v1.serializers import AttachmentSerializer, ThreadSerializer


class AttachmentListView(generics.ListCreateAPIView):
    '''
        To upload a file send the payload as a
        multipart-form-data.
    '''
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Attachment.objects.all()
    lookup_field = 'id'


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


class ThreadDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ThreadSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    queryset = Thread.objects.all()
    lookup_field = 'id'
