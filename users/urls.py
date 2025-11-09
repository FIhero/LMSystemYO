from django.urls import path
from .views import UserUpdateAPIView

urlpatterns = [
    path('profile/update/', UserUpdateAPIView.as_view(), name='user-update'),
]