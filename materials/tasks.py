from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from config import settings
from materials.models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """Отправляет уведомления, если курс не обновлялся более 4 часов"""
    try:
        course = Course.objects.get(id=course_id)
        four_hours_ago = timezone.now() - timedelta(hours=4)
        if course.updated_at > four_hours_ago:
            return "Курс обновлялся недавно, уведомление не отправлено"

        subscribers = Subscription.objects.filter(course=course)

        for subscription in subscribers:
            send_mail(
                subject=f"Обновление курса: {course.title}",
                message=f'В курсе "{course.title}" появились новые материалы!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[subscription.user.email],
                fail_silently=False,
            )

        return f"Уведомления отправлены {subscribers.count()} подписчикам"
    except Course.DoesNotExist:
        return "Курс не найден"
