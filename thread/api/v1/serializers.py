from typing import Dict, Any
from rest_framework import serializers
from django.db import DatabaseError
from thread.models import Attachment, Message


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

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['date_created', 'date_edited', 'created_by']

    def create(self, validated_data: Dict[str, Any]) -> Attachment:
        user = self.context.get('request').user

        obj = Message.objects.create(
            **validated_data,
            created_by=user
        )

        return obj
