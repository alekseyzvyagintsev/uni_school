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
                title=f"Урок {i + 1}", description=f"Урок {i + 1}", course=course, owner=user
            )
            self.stdout.write(f"Урок успешно создан: {lesson.title}")

    def handle(self, *args, **options):
        try:
            # Получаем или создаем пользователя с id=1
            user = User.objects.get(id=1)

            courses_data = [
                ("Python", "Освоение профессии разработчика на Python"),
                ("C++", "Освоение профессии разработчика на C++"),
                ("Java", "Освоение профессии разработчика на Java"),
            ]

            for name, desc in courses_data:
                course = Course.objects.create(title=name, description=desc, owner=user)
                self.stdout.write(f"Курс успешно создан: {name}")

                # Создание уроков для текущего курса
                self.create_lessons(course, user)

        except User.DoesNotExist:
            self.stderr.write("Пользователь с указанным ID не найден.")
        except Exception as e:
            self.stderr.write(str(e))


#############################################################################################################
