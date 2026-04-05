#############################################################################################################
from django.core.management import BaseCommand

from materials.models import Course, Lesson
from users.models import User


class Command(BaseCommand):
    help = "Создание курсов и уроков"

    def create_lessons(self, course, user, num_lessons=6):
        """Метод для создания серии уроков"""
        for i in range(num_lessons):
            lesson = Lesson.objects.create(
                title=f"{course.title} урок {i + 1}",
                description=f"Описание к {course.title} урок {i + 1}",
                course=course,
                owner=course.owner,
                is_active=True,
                price=20000,
            )
            self.stdout.write(f"Урок успешно создан: {lesson.title}")

    def handle(self, *args, **options):
        # Получаем или создаем пользователя с id=1
        try:
            admin = User.objects.get(id="1")
            moderator = User.objects.get(id="2")
            any_user = User.objects.get(id="3")
        except User.DoesNotExist:
            User.objects.create_user(username="new_user", password="qwer1234", email="new_user@example.com")
            raise ValueError("Один из указанных пользователей отсутствует!")
        try:
            courses_data = [
                ("Python", "Освоение профессии разработчика на Python"),
                ("C++", "Освоение профессии разработчика на C++"),
                ("Java", "Освоение профессии разработчика на Java"),
            ]

            for name, desc in courses_data:
                if name == "Python":
                    user = any_user
                elif name == "C++":
                    user = admin
                elif name == "Java":
                    user = moderator
                else:
                    user = User.objects.get(username="new_user")

                course = Course.objects.create(title=name, description=desc, owner=user, is_active=True, price=120000)
                self.stdout.write(f"Курс успешно создан: {name}")

                # Создание уроков для текущего курса
                self.create_lessons(course, user)

        except User.DoesNotExist:
            self.stderr.write("Пользователь с указанным ID не найден.")
        except Exception as e:
            self.stderr.write(str(e))


#############################################################################################################
