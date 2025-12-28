#############################################################################################################
from django.core.management import BaseCommand

from materials.models import Course, Lesson
from users.models import User


class Command(BaseCommand):
    help = "Создание курсов и уроков"

    def create_lessons(self, course, num_lessons=6):
        user = User.objects.filter(pk=1).exists()
        """Метод для создания серии уроков"""
        for i in range(num_lessons):
            lesson = Lesson.objects.create(
                title=f"Урок {i + 1}",
                description=f"Урок {i + 1}",
                course=course,
                owner=user
            )
            self.stdout.write(f"Урок успешно создан: {lesson.title}")

    def handle(self, *args, **options):
        try:
            courses_data = [
                ("Python", "Освоение профессии разработчика на Python"),
                ("C++", "Освоение профессии разработчика на C++"),
                ("Java", "Освоение профессии разработчика на Java")
            ]

            for name, desc in courses_data:
                course = Course.objects.create(title=name, description=desc, owner=1)
                self.stdout.write(f"Курс успешно создан: {name}")

                # Создание уроков для текущего курса
                self.create_lessons(course)

        except Exception as e:
            self.stderr.write(str(e))


#############################################################################################################
