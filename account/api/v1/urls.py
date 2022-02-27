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
    UserFollowingListCreateView,
    UserFollowingRetrieveDestroyView,
)

router = routers.DefaultRouter()
router.register('account', ResetPasswordViewset, 'reset-password')
router.register('account/users', AuthViewset, 'auth-views')
router.register('account/users', UserViewset, 'user-views')

app_name = 'apiv1'

urlpatterns = [
    *router.urls,
    path(
        'account/users/<int:id>/followers/',
        UserFollowingListCreateView.as_view(),
        name='followers-list-create'
    ),
    path(
        'account/users/<int:id>/followers/<int:follower_id>/',
        UserFollowingRetrieveDestroyView.as_view(),
        name='follower-retreive-destroy'
    ),
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
]
