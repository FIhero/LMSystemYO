from rest_framework import generics, permissions

from .models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация пользователя"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserListAPIView(generics.ListAPIView):
    """Список пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Страница просмотра профиля"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
