from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from services.stripe_service import StripeService

from .models import Course, Lesson, Payment, Subscription
from .paginators import CoursePaginator, LessonPaginator
from .permissions import IsModerator, IsOwner
from .serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from .tasks import send_course_update_notification


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        """Разные permissions для разных действий"""
        if self.action in ["update", "partial_update", "retrieve"]:
            permission_classes = [IsModerator | IsOwner]
        elif self.action == "destroy":
            permission_classes = [IsOwner]
        elif self.action == "create":
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """При создании назначаем владельца"""
        serializer.save(owner=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_update(self, serializer):
        """При обновлении курса запускаем рассылку"""
        instance = serializer.save()
        send_course_update_notification.delay(instance.id)
        return instance

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk=None):
        course = self.get_object()
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, course=course
        )
        if created:
            return Response({"status": "subscribed"})
        return Response({"status": "already subscribed"})

    @action(detail=True, methods=["post"])
    def unsubscribe(self, request, pk=None):
        course = self.get_object()
        Subscription.objects.filter(user=request.user, course=course).delete()
        return Response({"status": "unsubscribed"})


class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator


class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModerator | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsOwner]


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]
    ordering_fields = ["payment_date"]

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get("ordering")

        if ordering == "payment_date":
            return queryset.order_by("payment_date")
        elif ordering == "-payment_date":
            return queryset.order_by("-payment_date")

        return queryset

    @swagger_auto_schema(
        operation_description="Создание сессии оплаты курса",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["course_id"],
            properties={
                "course_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID курса"
                ),
                "amount": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Сумма в рублях",
                    default=1000,
                ),
            },
        ),
        responses={
            200: openapi.Response(
                "Success",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "session_id": openapi.Schema(type=openapi.TYPE_STRING),
                        "url": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
        },
    )
    @action(detail=False, methods=["post"])
    def buy_course(self, request):
        course_id = request.data.get("course_id")
        amount = request.data.get("amount", 1000)

        try:
            course = Course.objects.get(id=course_id)
            product = StripeService.create_product(f"Course: {course.title}")
            price = StripeService.create_price(amount, product.id)
            session = StripeService.create_checkout_session(price.id, course_id)

            Payment.objects.create(
                user=request.user,
                paid_course=course,
                amount=amount,
                payment_method="transfer",
                stripe_session_id=session.id,
            )

            return Response({"session_id": session.id, "url": session.url})
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    @action(detail=False, methods=["get"])
    def payment_status(self, request):
        """Проверяет статус платежа"""
        session_id = request.query_params.get("session_id")

        try:
            status = StripeService.get_session_status(session_id)
            return Response({"status": status})
        except Exception as e:
            return Response({"error": str(e)}, status=400)
