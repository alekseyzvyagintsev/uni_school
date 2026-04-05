from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from materials.serializer import CourseSerializer, LessonSerializer
from users.models import User


class PaymentTests(APITestCase):
    """Тестирование платежей"""

    def setUp(self):
        """Заполнение временной базы данных."""
        # Создаем пользователя
        self.user = User.objects.create_user(username="user@example.com", password="qwer1234")
        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)
        # Создаем курс
        self.course = Course.objects.create(
            owner=self.user, title="Тестовый курс", description="Тестовый курс", price=120000
        )
        # Создаем урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Тестовый урок",
            course=self.course,
            link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            price=20000,
        )

    def test_create_course_payment_transfer(self):
        """Тест создания платежа за курс трансфером"""
        course_serializer = CourseSerializer(self.course)
        course_data = course_serializer.data
        course_data["method"] = "transfer"
        course_data["user"] = self.user.id
        course_data["product"] = type(self.course).__name__
        response = self.client.post("/payment/create/", course_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_course_payment_cash(self):
        """Тест создания платежа за курс кэшем"""
        course_serializer = CourseSerializer(self.course)
        course_data = course_serializer.data
        course_data["method"] = "cash"
        course_data["user"] = self.user.id
        course_data["product"] = type(self.course).__name__
        response = self.client.post("/payment/create/", course_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_payment_transfer(self):
        """Тест создания платежа за урок трансфером"""
        lesson_serializer = LessonSerializer(self.lesson)
        lesson_data = lesson_serializer.data
        lesson_data["method"] = "transfer"
        lesson_data["user"] = self.user.id
        lesson_data["product"] = type(self.lesson).__name__
        response = self.client.post("/payment/create/", lesson_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_payment_cash(self):
        """Тест создания платежа за урок кэшем"""
        lesson_serializer = LessonSerializer(self.lesson)
        lesson_data = lesson_serializer.data
        lesson_data["method"] = "cash"
        lesson_data["user"] = self.user.id
        lesson_data["product"] = type(self.lesson).__name__
        response = self.client.post("/payment/create/", lesson_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
