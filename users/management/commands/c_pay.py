#############################################################################################################
from django.core.management import BaseCommand
from django.utils.timezone import now
from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = 'Создать платежи пользователей'

    def handle(self, *args, **options):
        try:
            # Получаем пользователя
            user = User.objects.get(id=1)

            # Платеж за курс
            course_payment = Payment.objects.create(
                user=user,
                date=now(),  # получение текущего времени
                paid_course=Course.objects.get(id=2),
                amount='100.00',  # Сумма платежа
                method='cash'  # Метод оплаты
            )
            self.stdout.write(f"Платеж за курс успешно создан {course_payment}")

            # Платеж за урок
            lesson_payment = Payment.objects.create(
                user=user,
                date=now(),
                paid_lesson=Lesson.objects.get(id=2),
                amount='10.00',
                method='cash'
            )
            self.stdout.write(f"Платеж за урок успешно создан {lesson_payment}")

        except Exception as e:
            self.stderr.write(str(e))



#############################################################################################################
