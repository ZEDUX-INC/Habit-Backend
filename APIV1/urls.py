from django.urls import path

from rest_framework import routers
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from drf_yasg.views import get_schema_view

from .views import UserViewset, ResetPasswordViewset

router  = routers.DefaultRouter()
router.register('users', UserViewset)
router.register('account', ResetPasswordViewset, "reset-password")


urlpatterns = [
  *router.urls,
  path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

