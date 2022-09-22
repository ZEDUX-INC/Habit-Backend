from django.urls import path

from thread.api.v1.views import (
    AttachmentDetailView,
    AttachmentListView,
    CommentDetailView,
    LikeDetailView,
    LikeListView,
    PlayListCategoryListView,
    PlayListCommentListView,
    PlayListDetailView,
    PlaylistListView,
    UserLikeListView,
    UserPlaylistView,
)

app_name = "api-thread-v1"

urlpatterns = [
    path("attachments/", AttachmentListView.as_view(), name="attachment-list"),
    path(
        "attachments/<str:id>/",
        AttachmentDetailView.as_view(),
        name="attachment-detail",
    ),
    path("likes/", LikeListView.as_view(), name="like-list"),
    path("likes/me/", UserLikeListView.as_view(), name="user-likes"),
    path("likes/<str:id>/", LikeDetailView.as_view(), name="like-detail"),
    path("playlist/", PlaylistListView.as_view(), name="playlist-list"),
    path("playlist/me/", UserPlaylistView.as_view(), name="user-playlist"),
    path("playlist/<str:id>/", PlayListDetailView.as_view(), name="playlist-detail"),
    path(
        "playlist/<str:id>/comments/",
        PlayListCommentListView.as_view(),
        name="playlist-comments",
    ),
    path(
        "playlist/<str:id>/comments/<str:comment_id>/",
        CommentDetailView.as_view(),
        name="playlist-comment-detail",
    ),
    path(
        "playlist-categories/",
        PlayListCategoryListView.as_view(),
        name="playlist-category-list",
    ),
]
