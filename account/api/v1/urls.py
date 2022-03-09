from django.urls import path

from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from account.api.v1.views import (
    UserViewset,
    AuthViewset,
    ResetPasswordViewset,
    LogoutView,
    ListFollowersView,
    RetrieveFollowerView,
    BlockFollowerView,
    ListCreateFollowingView,
    RetrieveRemoveFollowingView,
)

router = routers.DefaultRouter()
router.register('account', ResetPasswordViewset, 'reset-password')
router.register('account/users', AuthViewset, 'auth-views')
router.register('account/users', UserViewset, 'user-views')

app_name = 'api-account-v1'

urlpatterns = [
    *router.urls,
    path(
        'account/logout/',
        LogoutView.as_view(),
        name='logout-user'
    ),
    path(
        'account/login/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'account/login/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path(
        'users/<str:id>/followers/',
        ListFollowersView.as_view(),
        name='followers-list'
    ),
    path(
        'users/<str:id>/followers/<str:follower_id>/',
        RetrieveFollowerView.as_view(),
        name='follower-details'
    ),
    path(
        'users/<str:id>/followers/<str:follower_id>/block/',
        BlockFollowerView.as_view(),
        name='toggle-block-follower'
    ),
    path(
        'users/<str:id>/following/',
        ListCreateFollowingView.as_view(),
        name='following-list'
    ),
    path(
        'users/<str:id>/following/<str:followed_id>/',
        RetrieveRemoveFollowingView.as_view(),
        name='following-details'
    ),
]
