from typing import Any, Dict

from django.db import DatabaseError
from notifications.models import Notification
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import CustomUser, UserFollowing


class UserSerializer(serializers.ModelSerializer):

    token = None

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "cover",
            "location",
            "bio",
            "date_of_birth",
            "profile_picture",
            "date_joined",
            "last_login",
        ]

        read_only_fields = ["id", "date_joined", "last_login"]
        extra_kwargs = {"password": {"write_only": True}}

    def change_password(self, user: CustomUser, password: str) -> CustomUser:
        if password:
            user.set_password(password)
            user.save()
        return user

    def generate_username(self, user: CustomUser) -> None:

        if not user.username:
            user.username = f'{str(user.email).split("@")[0]}-{user.id}'

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        user = super().create(validated_data)
        self.generate_username(user)
        self.change_password(user, validated_data.get("password", None))
        user.is_active = True
        user.save()
        refresh_token = RefreshToken.for_user(user)

        self.token = {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }

        return user

    def update(
        self, instance: CustomUser, validated_data: Dict[str, Any]
    ) -> CustomUser:
        user = super().update(instance, validated_data)
        self.change_password(user, validated_data.get("password", None))
        return user

    def to_representation(self, instance: CustomUser) -> Dict[str, Any]:
        data = {**super().to_representation(instance)}

        if self.token:
            data.update({"auth_token": self.token})

        return data


class RPEmailSerializer(serializers.Serializer):
    # reset password email serializer
    email = serializers.EmailField(allow_blank=False, required=True)


class RPTokenSerializer(serializers.Serializer):
    # reset password token serializer
    token = serializers.CharField(max_length=6, allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False, required=True)


class RPPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, allow_blank=False)
    email = serializers.EmailField(allow_blank=False, required=True)
    password = serializers.CharField(max_length=100, allow_blank=False, required=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def save(self) -> None:
        token = RefreshToken(token=self.validated_data["refresh_token"], verify=False)
        token.blacklist()

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        RefreshToken(token=attrs["refresh_token"], verify=False)
        return attrs


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ["date_created", "blocked", "user"]
        read_only_fields = ["date_created", "user"]

    def to_representation(self, instance: UserFollowing) -> Dict[str, Any]:
        return {
            "user": UserSerializer(instance=instance.user).data,
            "following_since": instance.date_created,
            "blocked": instance.blocked,
        }


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ["date_created", "followed_user", "blocked"]
        read_only_fields = ["date_created"]

    def create(self, validated_data: Dict[str, Any]) -> UserFollowing:
        user = self.context.get("user")

        if not user:
            raise DatabaseError(
                f"Authenticatetd User must be added to {self.__class__.__name__} context."
            )  # pragma: no cover

        follower_transaction = UserFollowing.objects.create(
            user=user, followed_user=validated_data.get("followed_user")
        )
        return follower_transaction

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        user = self.context.get("user")

        if not user:
            raise DatabaseError(
                f"Authenticatetd User must be added to {self.__class__.__name__} context."
            )  # pragma: no cover

        followed_user = attrs.get("followed_user")

        if UserFollowing.objects.filter(user=user, followed_user=followed_user):
            raise ValidationError({"followed_user": "User is already being followed."})

        return attrs

    def to_representation(self, instance: UserFollowing) -> Dict[str, Any]:
        return {
            "user": UserSerializer(instance=instance.followed_user).data,
            "following_since": instance.date_created,
            "blocked": instance.blocked,
        }


class NotificationSerializer(serializers.ModelSerializer):
    data = serializers.JSONField(read_only=True)

    class Meta:
        model = Notification

        fields = [
            "id",
            "data",
            "unread",
            "timestamp",
        ]

        read_only_fields = [
            "id",
            "data",
            "timestamp",
        ]

        extra_kwargs = {"unread": {"required": True}}
