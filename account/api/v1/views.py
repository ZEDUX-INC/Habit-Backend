from datetime import timedelta
from typing import Any, Dict, List

from django.core import signing
from django.db.models import QuerySet

from rest_framework.decorators import action
from rest_framework import viewsets, generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework import mixins, views
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.models import CustomUser, UserFollowing

from account.api.v1.permissions import IsUserOrReadOnly
from account.api.v1.serializers import (
    RPPasswordSerializer,
    RPTokenSerializer,
    UserSerializer,
    RPEmailSerializer,
    LogoutSerializer,
    UserFollowerSerializer,
)


class AuthViewset(mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=True,
        methods=['get'],
        url_name='activate',
        url_path='activate',
        queryset=CustomUser.objects.filter(is_staff=False, is_superuser=False),
    )
    def activate_email(self, request: Request, *args: List[Any], **kwargs: Dict[Any, Any]) -> Response:
        """Activate User Email Before Login is Allowed"""
        user = self.get_object()
        user.is_active = True
        user.save()
        serializer = self.serializer_class(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        url_name='deactivate',
        url_path='deactivate',
        queryset=CustomUser.objects.filter(is_staff=False, is_superuser=False),
        serializer_class=None,
        permission_classes=[permissions.IsAuthenticated]
    )
    def deactivate_user(self, request: Request, *args: List[Any], **kwargs: Dict[Any, Any]) -> Response:
        """Activate User Email Before Login is Allowed"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class UserViewset(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):

    queryset = CustomUser.objects.filter(
        is_staff=False, is_superuser=False, is_active=True)
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsUserOrReadOnly)


class LogoutView(views.APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @swagger_auto_schema(
        operation_id='logout',
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response('Response', None, {'status': 'success'}),
        },
    )
    @action(
        detail=True,
        methods=['post'],
        url_name='logout',
        url_path='logout',
        queryset=CustomUser.objects.filter(is_staff=False, is_superuser=False),
    )
    def post(self, request: Request, *args: List[Any], **kwargs: Dict[Any, Any]) -> Response:
        """Log user out"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data={'status': 'success'}, status=status.HTTP_200_OK)


class ResetPasswordViewset(viewsets.ViewSet):

    @swagger_auto_schema(
        operation_id='gettoken',
        request_body=RPEmailSerializer,
        responses={
            200: openapi.Response('Response', RPTokenSerializer),
            400: openapi.Response('Error Response', RPEmailSerializer),
        },
    )
    @action(
        detail=False,
        methods=['POST'],
        url_path='resetpassword/gettoken',
        url_name='gettoken',
    )
    def get_token(self, request: Request) -> Response:
        """Generate reset password token."""
        serializer = RPEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mail = serializer.validated_data.get('email')
        user = get_object_or_404(CustomUser, email=mail)
        raw_token, token = user.generate_resettoken()
        user.reset_token = token
        user.save()
        # TODO: send email contaiing otp to the user at this point
        return Response(data={'token': raw_token}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='validatetoken',
        request_body=RPTokenSerializer,
        responses={
            200: openapi.Response('Response', RPTokenSerializer),
            403: openapi.Response('Error Response', RPTokenSerializer),
        },
    )
    @action(
        detail=False,
        methods=['POST'],
        url_path=r'resetpassword/validatetoken',
        url_name='validatetoken',
    )
    def validate_token(self, request: Request) -> Response:
        """confirm that a token is valid."""
        serializer = RPTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            CustomUser, email=serializer.data.get('email'))

        try:
            max_age = timedelta(minutes=10)
            signer = signing.TimestampSigner()
            data = signer.unsign_object(  # type:ignore
                user.reset_token, max_age=max_age)
            if (serializer.data.get('token') == data.get('token')):
                raise exceptions.ValidationError({'token': ['Invalid token']})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except signing.SignatureExpired:
            user.reset_token = None
            user.save()
            return Response(data={'status': 'failure', 'message': 'token has expired'}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_id='resetpassword',
        request_body=RPPasswordSerializer,
        responses={
            200: openapi.Response('Response', RPTokenSerializer),
            403: openapi.Response('Error Response', RPPasswordSerializer),
        },
    )
    @action(
        detail=False,
        methods=['POST'],
        url_path='resetpassword',
        url_name='resetpassword',
    )
    def reset_password(self, request: Request) -> Response:
        """Reset Users Password using generated token."""
        serializer = RPPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.validate_token(request)

        if (res.status_code == 200):
            user = get_object_or_404(
                CustomUser, email=serializer.data.get('email'))
            user.set_password(serializer.validated_data.get('password'))
            user.reset_token = None
            user.save()
            return Response({'status': 'success', 'message': 'Password reset'}, status=status.HTTP_200_OK)
        else:
            return res


class UserFollowingListCreateView(generics.ListCreateAPIView):
    serializer_class = UserFollowerSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]

    def get_queryset(self):
        return UserFollowing.objects.filter(user__is_active=True, following_user__is_active=True)

    def get(self, request, id, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=id)
        queryset = self.get_queryset().filter(user=user)
        serializer = self.serializer_class(instance=queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={
                                           'user': self.request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserFollowingRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = UserFollowerSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]
    lookup_field = 'id'

    def get_queryset(self):
        return UserFollowing.objects.filter(user__is_active=True, following_user__is_active=True)

    def get(self, request, id, follower_id, *args, **kwargs):
        try:
            follower_contract = UserFollowing.objects.get(
                user=request.user, following_user__id=follower_id)
        except UserFollowing.DoesNotExist:
            raise exceptions.NotFound('Following user with this id not found')

        serializer = self.serializer_class(instance=follower_contract)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id, follower_id, *args, **kwargs):

        try:
            follower_contract = UserFollowing.objects.get(
                user=request.user, following_user__id=follower_id)
        except UserFollowing.DoesNotExist:
            raise exceptions.NotFound('Following user with this id not found')

        follower_contract.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
