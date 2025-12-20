from rest_framework import serializers


def validate_youtube_link(value):
    """Проверяет что ссылка ведет на youtube.com"""
    if value and "youtube.com" not in value:
        raise serializers.ValidationError("Разрешены только ссылки на youtube.com")
    return value
