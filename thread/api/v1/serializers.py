from typing import Dict, Any
from attr import attr
from django.forms import ValidationError
from rest_framework import serializers
from thread.models import Attachment, Message, Thread, Like
from django.db import transaction


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


class MessageSerializer(serializers.ModelSerializer):
    attachments = serializers.PrimaryKeyRelatedField(
        queryset=Attachment.objects.all(), many=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['date_created', 'date_edited', 'created_by']

    def create(self, validated_data: Dict[str, Any]) -> Attachment:
        user = self.context.get('request').user
        attachments = validated_data.pop('attachments', [])
        obj = Message.objects.create(
            **validated_data,
            created_by=user,
        )
        obj.attachments.set(attachments)

        return obj


class ThreadSerializer(serializers.ModelSerializer):
    message = MessageSerializer(required=False)

    class Meta:
        model = Thread
        fields = '__all__'
        read_only_fields = ['date_created', 'created_by']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        attrs = super().validate(attrs)

        message = attrs.get('message', None)
        replying = attrs.get('replying', None)
        sharing = attrs.get('sharing', None)

        if replying and sharing:
            raise ValidationError({
                'non_field_errors': [
                    'Thread can not be a reply and a share at the same time.'
                ]
            })

        if replying and not message:
            raise ValidationError({
                'non_field_errors': [
                    'Thread reply must have a message.'
                ]
            })

        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Thread:
        user = self.context.get('request').user

        msg_data = validated_data.pop('message', None)
        message = None

        if msg_data:
            msg_serializer = MessageSerializer(
                data=msg_data, context=self.context)
            msg_serializer.is_valid(True)
            message = msg_serializer.save()

        with transaction.atomic():
            obj = Thread.objects.create(
                **validated_data,
                message=message,
                created_by=user
            )

            return obj

    def to_representation(self, instance: Thread) -> Dict[str, Any]:
        data = super().to_representation(instance)
        likes = instance.likes.count()
        data.update({'likes': likes})
        return data


class LikeSerializer(serializers.ModelSerializer):
    thread = serializers.PrimaryKeyRelatedField(queryset=Thread.objects.all())

    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['created_by', 'date_created']

    def validate(self, attrs) -> Dict[str, Any]:
        attrs = super().validate(attrs)
        user = self.context.get('request').user
        thread = attrs['thread']

        if user == thread.created_by:
            raise ValidationError({
                'non_field_errors': [
                    'You cant like your own thread.'
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

    def to_representation(self, instance: Like) -> Dict[str, Any]:
        data = super().to_representation(instance)
        thread = instance.thread
        thread_data = ThreadSerializer(instance=thread).data
        data.update({'thread': thread_data})
        return data
