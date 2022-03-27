from rest_framework import serializers
from thread.models import Attachment, Message


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'
        read_only_fields = ['date_created']


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['date_created', 'date_edited']
