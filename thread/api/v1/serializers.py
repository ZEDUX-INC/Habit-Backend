from typing import Dict, Any
from django.forms import ValidationError
from rest_framework import serializers
from thread.models import Attachment, Message, Thread
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
