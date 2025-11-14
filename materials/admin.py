from django.contrib import admin

from .models import Course, Lesson, Payment


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "updated_at", "lesson_count")
    list_filter = ("created_at", "owner")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")

    def lesson_count(self, obj):
        return obj.lessons.count()

    lesson_count.short_description = "Количество уроков"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "owner", "created_at", "video_link")
    list_filter = ("course", "owner", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "paid_course",
        "paid_lesson",
        "amount",
        "payment_method",
        "payment_date",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = ("user__email", "paid_course__title")
    readonly_fields = ("payment_date",)
