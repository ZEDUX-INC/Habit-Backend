from django.db.models import fields
from rest_framework import serializers
from UserApp.models import CustomUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields =  [
            "id", "username", "first_name",
             "last_name", "email", "password",
             "cover", "location", "bio",
             "dob", "profile_picture", "date_joined",
             "last_login",
        ]
        read_only_fields =  ["id"]
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        temp =  {**validated_data}
        temp.pop("password", None)
        
        user = self.Meta.model(**temp)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def change_password(self, user, password):
        if password:
            user.set_password(password)
            user.save()
            #TODO: you can a change password signal here
        return user
    
    def create(self, validated_data):
        user = super().create(validated_data)
        self.change_password(user, validated_data.get("password", None))
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        self.change_password(user, validated_data.get("password", None))
        return user


class RPEmailSerializer(serializers.Serializer):
    # reset password email serializer
    email = serializers.EmailField(allow_blank=False,  required=True)


class RPTokenSerializer(serializers.Serializer):
    # reset password token serializer
    token = serializers.CharField(max_length=150, allow_blank=False, required=True)
    email = serializers.EmailField(allow_blank=False,  required=True)


class RPPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=150, allow_blank=False)
    email = serializers.EmailField(allow_blank=False,  required=True)
    password = serializers.CharField(min_length=8, max_length=100, allow_blank=False,  required=True)


