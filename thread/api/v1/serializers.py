from typing import Dict, Any
from attr import attr
from django.forms import ValidationError
from rest_framework import serializers
from thread.models import Attachment, Like, PlayList, PlayListCategory


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['date_created', 'created_by']

    def create(self, validated_data: Dict[str, Any]) -> Attachment:
        user = self.context.get('request').user

        obj = Attachment.objects.create(
            **validated_data,
            created_by=user
        )

        return obj


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['created_by', 'date_created']

    def validate(self, attrs) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        user = self.context.get('request').user
        playlist = attrs['playlist']

        if user == playlist.created_by:
            raise ValidationError({
                'non_field_errors': [
                    'User can not like their own playlist.'
                ]
            })

        if Like.objects.filter(playlist=playlist, created_by=user).exists():
            raise ValidationError({
                'non_field_errors': [
                    'User has already liked this playlist.'
                ]
            })

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Like:
        user = self.context.get('request').user

        instance = Like.objects.create(
            **validated_data,
            created_by=user
        )

        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({
            'playlist': PlayListSerializer(instance=instance.playlist).data
        })

        return data


class PlayListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayListCategory
        fields = ['id', 'title']


class PlayListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlayList
        fields = '__all__'
        read_only_fields = ['created_by', 'date_created', 'views']

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        attrs = super().validate(attrs)
        user = self.context.get('request').user

        if PlayList.objects.filter(created_by=user, title=attrs['title']).exists():
            raise ValidationError({
                'title': [
                    'PlayList with this title already exists.'
                ]
            })

        return attrs

    def create(self, validated_data: dict[str, Any]) -> PlayList:
        user = self.context.get('request').user
        categories = validated_data.pop('categories', [])
        songs = validated_data.pop('songs', [])

        instance = PlayList.objects.create(
            **validated_data,
            created_by=user
        )

        instance.categories.set(categories)
        instance.songs.set(songs)
        instance.save()

        return instance

    def to_representation(self, instance: PlayList) -> dict[str, Any]:
        data = super().to_representation(instance)
        data.update({
            'categories': PlayListCategorySerializer(instance=instance.categories, many=True).data,
            'songs': AttachmentSerializer(instance=instance.songs, many=True).data
        })
        return data
