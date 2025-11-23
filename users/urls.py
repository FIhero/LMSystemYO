from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (UserCreateAPIView, UserListAPIView, UserRetrieveAPIView,
                    UserUpdateAPIView)

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", UserCreateAPIView.as_view(), name="user-register"),
    path("", UserListAPIView.as_view(), name="user-list"),
    path("profile/", UserUpdateAPIView.as_view(), name="user-profile"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
]
