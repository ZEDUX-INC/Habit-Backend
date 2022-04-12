from django.urls import path

from thread.api.v1.views import (
    AttachmentDetailView,
    AttachmentListView,
    ThreadListView,
    ThreadDetailView,
    UserThreadListView,
)

app_name = 'api-thread-v1'

urlpatterns = [
    path('attachments/', AttachmentListView.as_view(), name='attachment-list'),
    path('attachments/<str:id>/', AttachmentDetailView.as_view(),
         name='attachment-detail'),
    path('threads/', ThreadListView.as_view(), name='thread-list'),
    path('threads/me', UserThreadListView.as_view(), name='user-threads'),
    path('threads/<str:id>/', ThreadDetailView.as_view(), name='thread-detail'),
]
