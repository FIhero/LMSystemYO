from rest_framework import serializers

from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "phone", "city", "avatar"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
            avatar=validated_data.get("avatar"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра/редактирования"""

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "first_name", "last_name"]
