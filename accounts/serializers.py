from rest_framework import serializers
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ("id", "username","email", "mobile", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user
