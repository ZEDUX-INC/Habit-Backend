from datetime import timedelta

from django.core import signing
from django.contrib.auth import logout

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import exceptions

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from UserApp.models import CustomUser

from .serializers import RPPasswordSerializer, RPTokenSerializer, UserSerializer, RPEmailSerializer


class UserViewset(viewsets.ModelViewSet):
    # use this to remove admin and staff from customer api
    queryset = CustomUser.objects.filter(is_staff=False, is_superuser=False, is_active=True)
    serializer_class = UserSerializer

    @action(
        detail=True, 
        methods=['get'], 
        url_name="activate", 
        url_path="activate", 
        queryset=CustomUser.objects.filter(is_staff=False, is_superuser=False)
    )
    def activate_email(self, request, *args, **kwargs):
        """Activate User Email Before Login is Allowed"""
        user = self.get_object()
        user.is_active = True
        user.save()
        serializer = self.serializer_class(instance=user)
        return Response(serializer.data, status=HTTP_200_OK) 
    
    @action(detail=False, methods=['post'])
    def logout(self, request, *args, **kwargs):
        """Log user out"""
        if request.user.is_authenticated:
            logout(request.user)
        return Response(data={"status": "success"}, status=HTTP_200_OK)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class ResetPasswordViewset(viewsets.ViewSet):

    @swagger_auto_schema(
        operation_id="resetpassword_gettoken",
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
    def get_token(self, request):
        """Generate reset password token."""
        serializer = RPEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # probably send an email signal at this point
        mail =  serializer.validated_data.get("email")
        user = get_object_or_404(CustomUser, email=mail)
        raw_token, token = user.generate_resettoken()
        user.reset_token = token
        user.save()
        return Response(data={"token": raw_token}, status=HTTP_200_OK)

    
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
    def validate_token(self, request):
        """confirm that a token is valid."""
        serializer =  RPTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(CustomUser, email=serializer.data.get("email"))

        try:
            max_age = timedelta(minutes=10)
            signer = signing.TimestampSigner()
            data = signer.unsign_object(user.reset_token, max_age=max_age)
            if (serializer.data.get("token") == data.get("token")) :
                raise exceptions.ValidationError({"token": ["Invalid token"]})
            return Response(data=serializer.data, status=HTTP_200_OK)
        except signing.SignatureExpired:
            user.reset_token = None
            user.save()
            return Response(data={"status": "failure", "message":"token has expired"}, status=HTTP_403_FORBIDDEN)


    @swagger_auto_schema(
        operation_id="resetpassword",
        request_body=RPPasswordSerializer,
        responses={
            200: openapi.Response("Response", RPTokenSerializer),
            403: openapi.Response("Error Response", RPPasswordSerializer),
        },
    )
    @action (
        detail=False,
        methods=["POST"],
        url_path="resetpassword",
        url_name="resetpassword",
    )
    def reset_password(self, request):
        """Reset Users Password using generated token."""
        serializer = RPPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.validate_token(request)

        if (res.status_code == 200):
            user = get_object_or_404(CustomUser, email=serializer.data.get("email"))
            user.set_password(serializer.validated_data.get("password"))
            user.reset_token = None
            user.save()
            return Response({"status": "success", "message": "Password reset"}, status=HTTP_200_OK)
        else :
            return res



