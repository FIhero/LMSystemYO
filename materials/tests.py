from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonTestCase(TestCase):
    def setUp(self):
        """Подготовка данных для тестов"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(
            title="Test Course", description="Test Description", owner=self.user
        )

        self.lesson_data = {
            "title": "Test Lesson",
            "description": "Test Lesson Description",
            "video_link": "https://youtube.com/watch?v=test123",
            "course": self.course.id,
        }

    def test_create_lesson(self):
        """Тест создания урока"""
        response = self.client.post("/api/lessons/create/", data=self.lesson_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(Lesson.objects.get().title, "Test Lesson")

    def test_create_lesson_invalid_link(self):
        """Тест создания урока с невалидной ссылкой"""
        invalid_data = self.lesson_data.copy()
        invalid_data["video_link"] = "https://vk.com/video123"

        response = self.client.post("/api/lessons/create/", data=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_link", response.data)


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.course = Course.objects.create(title="Test Course", owner=self.user)

    def test_subscribe_to_course(self):
        """Тест подписки на курс"""
        response = self.client.post(f"/api/courses/{self.course.id}/subscribe/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса"""
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.post(f"/api/courses/{self.course.id}/unsubscribe/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )
