from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Subscription, Lesson
from users.models import User


class SubscriptionTest(APITestCase):
    """Тест эндпоинта для создания и удаления подписки"""

    def setUp(self):
        """Заполнение временной базы данных."""
        self.course = Course.objects.create(title="C++")
        self.user = User.objects.create_user(username="user@example.com", password="qwer1234")
        self.client.force_authenticate(user=self.user)
        self.url = "/subscribe/"

    def test_add_subscription(self):
        data = {"course_id": self.course.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.json(), {"message": "Подписка добавлена."})
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_remove_subscription(self):
        Subscription.objects.create(user=self.user, course=self.course)
        data = {"course_id": self.course.id}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.json(), {"message": "Подписка удалена."})
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())


class LessonTests(APITestCase):
    """Тестирование CRUD уроков"""

    def setUp(self):
        """Заполнение временной базы данных."""
        self.user = User.objects.create_user(username="user@example.com", password="qwer1234")
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Тестовый курс",
        )
        self.data = {
            "title": "Тестовый урок",
            "description": "Тестовый урок",
            "course": self.course.id,
            "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        self.bead_data = {
            "title": "Тестовый урок",
            "description": "Тестовый урок",
            "course": self.course.id,
            "link": "https://rutube.ru/video/93f91984a87c22413467c28e8dd4af07/?r=wd",
        }
        self.patch_lesson_data = {"title": "patch_lesson_data", "description": "patch_lesson_data"}

    def test_create_lesson(self):
        """Тест правильного создания урока."""
        response = self.client.post("/lesson/create/", data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.json(),
            {
                "id": 1,
                "title": "Тестовый урок",
                "preview": None,
                "description": "Тестовый урок",
                "is_active": False,
                "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "course": self.course.id,
                "owner": self.user.id,
            },
        )

    def test_create_bead_lesson(self):
        """Тест создания урока неправильной интернет ссылкой."""
        response = self.client.post("/lesson/create/", data=self.bead_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["Ссылка должна вести на ресурс YouTube."]})

    def test_list_lessons(self):
        """Тест вывода списка уроков"""
        lesson = Lesson.objects.create(title="list test", description="list test", owner=self.user, course=self.course)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "id": lesson.id,
                        "title": "list test",
                        "preview": None,
                        "description": "list test",
                        "is_active": False,
                        "link": None,
                        "course": self.course.id,
                        "owner": self.user.id,
                    }
                ],
            },
        )

    def test_first_lesson(self):
        """Тест вывода первого урока"""
        lesson = Lesson.objects.create(
            title="first lesson test", description="first lesson test", owner=self.user, course=self.course
        )
        response = self.client.get(f"/lesson/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": lesson.id,
                "title": "first lesson test",
                "preview": None,
                "description": "first lesson test",
                "is_active": False,
                "link": None,
                "course": self.course.id,
                "owner": self.user.id,
            },
        )

    def test_patch_lesson(self):
        """Тест редактирования урока владельцем"""
        # Создаем урок от имени текущего пользователя
        lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Тестовый урок",
            course=self.course,
            owner=self.user,
        )
        lesson_id = lesson.id
        response = self.client.patch(f"/lesson/update/{lesson_id}/", data=self.patch_lesson_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": lesson_id,
                "title": "patch_lesson_data",
                "preview": None,
                "description": "patch_lesson_data",
                "is_active": False,
                "link": None,
                "course": self.course.id,
                "owner": self.user.id,
            },
        )

    def test_patch_lesson_by_non_owner_user(self):
        """Тест на изменение урока пользователем, не являющимся владельцем."""
        # Создаем урок от имени текущего пользователя
        lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Тестовый урок",
            course=self.course,
            owner=self.user,
        )

        # Создаем нового пользователя и аутентифицируем его
        another_user = User.objects.create_user(
            username="another@example.com", email="another@example.com", password="qwer1234"
        )
        self.client.force_authenticate(user=another_user)
        # Попытка изменить урок
        lesson_id = lesson.id
        response = self.client.patch(f"/lesson/update/{lesson_id}/", data=self.patch_lesson_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Возвращаем аутентификацию к первоначальному пользователю
        self.client.force_authenticate(user=self.user)

    def test_remove_lesson(self):
        """Тест удаления урока"""
        lesson = Lesson.objects.create(
            title="removing lesson test",
            description="removing lesson test",
            course=self.course,
            owner=self.user,
        )
        response = self.client.delete(f"/lesson/delete/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_remove_lesson_by_non_owner_user(self):
        """Тест удаления урока"""
        lesson = Lesson.objects.create(
            title="removing lesson test",
            description="removing lesson test",
            course=self.course,
            owner=self.user,
        )

        # Создаем нового пользователя и аутентифицируем его
        another_user = User.objects.create_user(
            username="another@example.com", email="another@example.com", password="qwer1234"
        )
        self.client.force_authenticate(user=another_user)
        # Попытка удалить урок
        response = self.client.delete(f"/lesson/delete/{lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Возвращаем аутентификацию к первоначальному пользователю
        self.client.force_authenticate(user=self.user)
