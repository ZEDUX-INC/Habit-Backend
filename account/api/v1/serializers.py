from typing import Any, Dict
from django.db import DatabaseError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from account.models import CustomUser, UserFollowing

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(
    #     min_length=8, max_length=100, write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name',
            'last_name', 'email', 'password',
            'cover', 'location', 'bio',
            'dob', 'profile_picture', 'date_joined',
            'last_login',
        ]

        read_only_fields = ['id', 'date_joined', 'last_login']
        extra_kwargs = {'password': {'write_only': True}}

    def change_password(self, user: CustomUser, password: str) -> CustomUser:
        if password:
            user.set_password(password)
            user.save()
        return user

    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        user = super().create(validated_data)
        self.change_password(user, validated_data.get('password', None))
        user.is_active = False
        user.save()
        return user

    def update(self, instance: CustomUser, validated_data: Dict[str, Any]) -> CustomUser:
        user = super().update(instance, validated_data)
        self.change_password(user, validated_data.get('password', None))
        return user


class RPEmailSerializer(serializers.Serializer):
    # reset password email serializer
    email = serializers.EmailField(allow_blank=False, required=True)


class RPTokenSerializer(serializers.Serializer):
    # reset password token serializer
    token = serializers.CharField(
        max_length=6, allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False, required=True)


class RPPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=6, allow_blank=False)
    email = serializers.EmailField(allow_blank=False, required=True)
    password = serializers.CharField(
        max_length=100, allow_blank=False, required=True)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def save(self):
        token = RefreshToken(self.validated_data['refresh_token'])
        token.blacklist()

    def validate(self, attrs):
        try:
            RefreshToken(attrs['refresh_token'])
        except TokenError:
            raise ValidationError(
                {'refresh_token': 'Token is invalid or expired'})

        return attrs


class UserFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ['date_created', 'followed_user', 'blocked']
        read_only_fields = ['date_created']

    def create(self, validated_data):
        user = self.context.get('user')

        if not user:
            raise DatabaseError(
                f'Authenticatetd User must be added to {self.__class__.__name__} context.')  # pragma: no cover

        follower_transaction = UserFollowing.objects.create(
            user=user, followed_user=validated_data.get('followed_user'))
        return follower_transaction

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        user = self.context.get('user')

        if not user:
            raise DatabaseError(
                f'Authenticatetd User must be added to {self.__class__.__name__} context.')  # pragma: no cover

        followed_user = attrs.get('followed_user')

        if UserFollowing.objects.filter(user=user, followed_user=followed_user):
            raise ValidationError(
                {'followed_user': 'User is already being followed.'})

        return attrs

    def to_representation(self, instance):
        return {
            'user': UserSerializer(instance=instance.followed_user).data,
            'following_since': instance.date_created,
            'blocked': instance.blocked
        }
