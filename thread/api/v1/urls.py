from django.urls import path

from thread.api.v1.views import (
    AttachmentDetailView,
    AttachmentListView,
)

app_name = 'api-thread-v1'

urlpatterns = [
    path('attachments/', AttachmentListView.as_view(), name='attachment-list'),
    path('attachments/<str:id>/', AttachmentDetailView.as_view(),
         name='attachment-detail'),
]
