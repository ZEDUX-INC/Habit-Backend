import random
from datetime import timedelta

from django.core import signing

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from UserApp.models import CustomUser

from .serializers import RPPasswordSerializer, RPTokenSerializer, UserSerializer, RPEmailSerializer

class UserViewset(viewsets.ModelViewSet):
    # use this to remove admin and staff from customer api
    # queryset = CustomUser.objects.filter(is_staff=False, is_superuser=False)
    queryset =  CustomUser.objects.all()
    serializer_class =  UserSerializer


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
        url_name="resetpassword_gettoken",
    )
    def email(self, request):
        serializer  =  RPEmailSerializer(data=request.data)
        if serializer.is_valid():
            # probably send an email signal at this point
            mail =  serializer.validated_data.get("email")
            user = get_object_or_404(CustomUser, email=mail)
            unsigned_token = random.randint(100000, 999999)
            signer = signing.TimestampSigner()
            signed_token = signer.sign_object({"token": unsigned_token, "email": mail})
            user.reset_token = signed_token
            user.save()
            return Response(data={"token": unsigned_token}, status=HTTP_200_OK)
        return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

    
    @swagger_auto_schema(
        operation_id="resetpassword_validatetoken",
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
        url_name="resetpassword_validatetoken",
    )
    def validate_token(self, request):
        serializer =  RPTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                max_age =  timedelta(minutes=5)
                signer = signing.TimestampSigner()
                user = get_object_or_404(CustomUser,email=serializer.data.get("email"))
                data =  signer.unsign_object(user.reset_token, max_age=max_age)
                assert ((serializer.data.get("token") == data.get("token")), "Invalid token")
                return Response(data=serializer.data, status=HTTP_200_OK)
            except signing.SignatureExpired:
                return Response(data={"status": "failure", "message":"token has expired"}, status=HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=HTTP_403_FORBIDDEN)


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
        serializer = RPPasswordSerializer(data=request.data)
        if serializer.is_valid():
            res = self.validate_token(request)
            if (res.status_code == 200):
                user = get_object_or_404(CustomUser, email=serializer.data.get("email"))
                user.set_password(serializer.validated_data.get("password"))
                user.save()
                return Response({"status": "success", "message": "Password reset"}, status=HTTP_202_ACCEPTED)
            else :
                return res
        else:
            return  Response(serializer.errors, status=HTTP_403_FORBIDDEN)



