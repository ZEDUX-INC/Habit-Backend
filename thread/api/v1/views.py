from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework import permissions

from thread.models import Attachment
from thread.api.v1.serializers import AttachmentSerializer
from thread.api.v1.permissions import IsCreatorOrReadOnly


class AttachmentListView(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Attachment.objects.all()
    lookup_field = 'id'


class AttachmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = (permissions.IsAuthenticated, IsCreatorOrReadOnly)
    queryset = Attachment.objects.all()
    lookup_field = 'id'
