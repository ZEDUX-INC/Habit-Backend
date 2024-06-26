from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.core import signing
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from notifications.models import Notification
from rest_framework import (
    exceptions,
    generics,
    mixins,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from account.api.v1.permissions import IsUserOrReadOnly
from account.api.v1.serializers import (
    FollowerSerializer,
    FollowingSerializer,
    LogoutSerializer,
    NotificationSerializer,
    RPEmailSerializer,
    RPPasswordSerializer,
    RPTokenSerializer,
    UserSerializer,
)
from account.api.v1.tasks import send_reset_password_otp_to_user_email_task
from account.models import CustomUser, UserFollowing


class AuthViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.filter(is_staff=False, is_superuser=False)
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):

    queryset = CustomUser.objects.filter(
        is_staff=False, is_superuser=False, is_active=True
    )
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["date_of_birth"]
    search_fields = ["username", "email", "date_of_birth"]
    ordering_fields = ["date_joined"]
    ordering = ordering_fields


class LogoutView(views.APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id="logout",
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response("Response", None, {"status": "success"}),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_name="logout",
        url_path="logout",
        queryset=CustomUser.objects.filter(is_staff=False, is_superuser=False),
    )
    def post(
        self, request: Request, *args: List[Any], **kwargs: Dict[Any, Any]
    ) -> Response:
        """Log user out"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={"status": "success"}, status=status.HTTP_200_OK)


class ResetPasswordViewset(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(
        operation_id="gettoken",
        request_body=RPEmailSerializer,
        responses={
            200: openapi.Response("Response", RPTokenSerializer),
            400: openapi.Response("Error Response", RPEmailSerializer),
        },
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="resetpassword/gettoken",
        url_name="gettoken",
    )
    def get_token(self, request: Request) -> Response:
        """Generate reset password token."""
        serializer = RPEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mail = serializer.validated_data.get("email")
        user = get_object_or_404(CustomUser, email=mail)
        raw_token, token = user.generate_resettoken()
        user.reset_token = token
        user.save()
        send_reset_password_otp_to_user_email_task.delay(user.email, raw_token)
        return Response(data={"token": raw_token}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="validatetoken",
        request_body=RPTokenSerializer,
        responses={
            200: openapi.Response("Response", RPTokenSerializer),
            403: openapi.Response("Error Response", RPTokenSerializer),
        },
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path=r"resetpassword/validatetoken",
        url_name="validatetoken",
    )
    def validate_token(self, request: Request) -> Response:
        """confirm that a token is valid."""
        serializer = RPTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(CustomUser, email=serializer.data.get("email"))

        try:
            max_age = timedelta(minutes=10)
            signer = signing.TimestampSigner()
            data = signer.unsign_object(user.reset_token, max_age=max_age)
            if str(serializer.data.get("token")) != str(data.get("token")):
                raise exceptions.ValidationError({"token": ["Invalid token"]})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except signing.SignatureExpired:
            user.reset_token = None
            user.save()
            return Response(
                data={"status": "failure", "message": "token has expired"},
                status=status.HTTP_403_FORBIDDEN,
            )

    @swagger_auto_schema(
        operation_id="resetpassword",
        request_body=RPPasswordSerializer,
        responses={
            200: openapi.Response("Response", RPTokenSerializer),
            403: openapi.Response("Error Response", RPPasswordSerializer),
        },
    )
    @action(
        detail=False,
        methods=["POST"],
        url_path="resetpassword",
        url_name="resetpassword",
    )
    def reset_password(self, request: Request) -> Response:
        """Reset Users Password using generated token."""
        serializer = RPPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = self.validate_token(request)

        if response.status_code == 200:
            user = get_object_or_404(CustomUser, email=serializer.data.get("email"))
            user.set_password(serializer.validated_data.get("password"))
            user.reset_token = None
            user.save()
            return Response(
                {"status": "success", "message": "Password reset"},
                status=status.HTTP_200_OK,
            )
        else:
            return response


class ListFollowersView(generics.ListAPIView):
    serializer_class = FollowerSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["blocked"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields

    def get_queryset(self) -> QuerySet[UserFollowing]:
        return UserFollowing.objects.filter(
            user__is_active=True,
            followed_user__is_active=True,
            followed_user__id=self.kwargs.get("id"),
        )

    @swagger_auto_schema(
        operation_id="follower-list",
    )
    def get(
        self, request: Request, *args: list[Any], **kwargs: dict[str, Any]
    ) -> Response:
        return super().get(request, *args, **kwargs)


class RetrieveFollowerView(generics.GenericAPIView):
    """Retrieve and block followers."""

    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[UserFollowing]:
        return UserFollowing.objects.filter(
            user__is_active=True, followed_user__is_active=True
        )

    def get_object(self) -> Optional[CustomUser]:
        try:
            user = CustomUser.objects.get(id=self.kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return None
        return user

    def get_follower_contract(self, user_id: int, follower_id: int) -> UserFollowing:
        try:
            follower_contract = UserFollowing.objects.get(
                user__id=follower_id, followed_user__id=user_id
            )
        except UserFollowing.DoesNotExist:
            raise exceptions.NotFound("Follower with this id not found.")

        return follower_contract

    @swagger_auto_schema(
        operation_id="follower-detail",
    )
    def get(self, request: Request, id: int, follower_id: int) -> Response:
        """Retrieve single follower."""
        follower_contract = self.get_follower_contract(
            user_id=id, follower_id=follower_id
        )
        serializer = self.serializer_class(instance=follower_contract)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="toggle-block-follower",
        request_body=FollowerSerializer,
    )
    def post(self, request: Request, id: int, follower_id: int) -> Response:
        """Block/unblock Follower."""

        follower_contract = self.get_follower_contract(
            user_id=id, follower_id=follower_id
        )
        follower_contract.blocked = True if request.data.get("blocked") else False
        follower_contract.save(update_fields=["blocked"])

        serializer = self.serializer_class(
            instance=follower_contract,
            context={"user": follower_contract.user},
        )

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ListCreateFollowingView(generics.ListCreateAPIView):
    """List and follow new users."""

    serializer_class = FollowingSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_fields = ["blocked"]
    ordering_fields = ["date_created"]
    ordering = ordering_fields

    def get_queryset(self) -> QuerySet[UserFollowing]:
        return UserFollowing.objects.filter(
            user__is_active=True,
            followed_user__is_active=True,
            user__id=self.kwargs.get("id"),
        )

    def get_object(self) -> QuerySet[CustomUser]:
        try:
            user = CustomUser.objects.get(id=self.kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return None
        return user

    @swagger_auto_schema(
        operation_id="list-followed-users",
    )
    def get(
        self, request: Request, *args: list[Any], **kwargs: dict[str, Any]
    ) -> Response:
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="add-user-to-following-list",
        request_body=FollowingSerializer,
    )
    def post(
        self, request: Request, id: str, *args: list[Any], **kwargs: dict[str, Any]
    ) -> Response:
        """Follow new user"""
        serializer = self.serializer_class(
            data=request.data, context={"user": self.request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class RetrieveRemoveFollowingView(generics.GenericAPIView):
    serializer_class = FollowingSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]
    lookup_field = "id"

    def get_queryset(self) -> QuerySet[UserFollowing]:
        return UserFollowing.objects.filter(
            user__is_active=True, followed_user__is_active=True
        )

    def get_object(self) -> Optional[CustomUser]:
        try:
            user = CustomUser.objects.get(id=self.kwargs.get("id"))
        except CustomUser.DoesNotExist:
            return None
        return user

    @swagger_auto_schema(
        operation_id="followed-user-detail",
    )
    def get(self, request: Request, id: str, followed_id: str) -> Response:
        """Retreive followed user"""
        try:
            follower_contract = UserFollowing.objects.get(
                user__id=id, followed_user__id=followed_id
            )
        except UserFollowing.DoesNotExist:
            raise exceptions.NotFound("Followed user with this id not found")

        serializer = self.serializer_class(instance=follower_contract)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id="remove-user-from-following-list",
        request_body=FollowingSerializer,
    )
    def delete(self, request: Request, id: str, followed_id: str) -> Response:
        """Unfollow a user."""

        try:
            follower_contract = UserFollowing.objects.get(
                user=request.user, followed_user__id=followed_id
            )
        except UserFollowing.DoesNotExist:
            raise exceptions.NotFound("You are not presently following this user.")

        follower_contract.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListNotificationsView(generics.ListAPIView):
    """List all user's notifications"""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["timestamp", "unread"]
    ordering = ordering_fields
    filter_fields = ["unread", "timestamp"]

    def get_queryset(self) -> QuerySet[Notification]:
        return self.request.user.notifications.all()


class NotificationsDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Notification]:
        return self.request.user.notifications.unread()


class MarkAllNotificationsAsReadView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Mark all notifications as read."""
        notifications = Notification.objects.filter(
            recipient=self.request.user, unread=True
        )
        count = notifications.mark_all_as_read()
        return Response(data={"status": True, "marked_notifications": count})


class DeleteAllNotificationsView(APIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Notification]:
        return self.request.user.notifications.all()

    def delete(self, request: Request) -> Response:
        """Mark all notifications as read."""
        notifications = self.get_queryset()
        notifications.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
